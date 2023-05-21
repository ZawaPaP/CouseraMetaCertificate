from django.shortcuts import render, get_object_or_404
from .models import Category, MenuItem, Cart, Order, OrderItem
from .serializers import MenuItemSerializer, CategorySerializer, CartItemSerializer, CartAddSerializer, OrderSerializer, OrderItemSerializer
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes, throttle_classes
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from django.contrib.auth.models import User, Group
import math
from datetime import date
from django.db.models import Sum

# Create your views here.
class CategoriesView(generics.ListCreateAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    
class MenuItemsView(generics.ListCreateAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    def get_permissions(self):
        if(self.request.method=='GET'):
            return []

        return [IsAdminUser()]

class SingleMenuItemView(generics.RetrieveUpdateDestroyAPIView):
    queryset = MenuItem.objects.all()
    serializer_class = MenuItemSerializer
    
    def get_permissions(self):
        if(self.request.method=='GET'):
            return []
        return [IsAdminUser()]

class CartItemsView(generics.ListCreateAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self, *args, **kwargs):
        cart = Cart.objects.filter(user=self.request.user)
        return cart

    def post(self, request, *arg, **kwargs):
        serialized_item = CartAddSerializer(data=request.data)
        serialized_item.is_valid(raise_exception=True)
        id = request.data['menuitem']
        quantity = request.data['quantity']
        item = get_object_or_404(MenuItem, id=id)
        price = int(quantity) * item.price
        try:
            Cart.objects.create(user=request.user, quantity=quantity, unit_price=item.price, price=price, menuitem_id=id)
        except:
            return Response({"message": "already in cart"}, status.HTTP_400_BAD_REQUEST)
        return Response({"message": "Successfully added!"}, status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *arg, **kwargs):
        Cart.objects.filter(user=request.user).delete()
        return Response({"message": "Successfully removed"}, status.HTTP_400_BAD_REQUEST)

class OrdersView(generics.ListCreateAPIView):
    serializer_class = OrderSerializer
        
    def get_queryset(self, *args, **kwargs):
        if self.request.user.groups.filter(name='Managers').exists() or self.request.user.is_superuser == True :
            query = Order.objects.all()
        elif self.request.user.groups.filter(name='Delivery crew').exists():
            query = Order.objects.filter(delivery_crew=self.request.user)
        else:
            query = Order.objects.filter(user=self.request.user)
        return query

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        data = {
            'data': serializer.data,
        }
        return Response(data)
        
    def post(self, request, *arg, **kwargs):
        cart = Cart.objects.filter(user = request.user)
        item = cart.values_list()
        time = date.today()
        total = sum(item['price'] for item in cart.values('price'))
        if request.data['delivery_crew']:
            crew = User.objects.get(id=request.data['delivery_crew'])
        else:
            crew = None
        if item:
            order = Order.objects.create(user=request.user, status=False, delivery_crew = crew, total=total, date=time)
            for i in cart.values():
                menuitem = get_object_or_404(MenuItem, id=i['menuitem_id'])
                total_price = int(i['quantity']) * i['unit_price']
                order_item = OrderItem.objects.create(order=order, menuitem=menuitem, quantity=i['quantity'], unit_price =i['unit_price'], price = total_price)
                order_item.save()
            cart.delete()
            return Response(status=201, data={'message':'Your order has been placed! Your order number is {}'.format(str(order.id))})
        else:
            return Response({"message": "No item in the cart"}, status.HTTP_400_BAD_REQUEST)

class OrderItemView(generics.ListAPIView):
    serializer_class = OrderItemSerializer
    
    def get_permissions(self):
        order = Order.objects.get(pk=self.kwargs['pk'])
        if self.request.user == order.user and self.request.method == 'GET':
            permission_classes = [IsAuthenticated]
        elif self.request.method == 'PUT' or self.request.method == 'DELETE':
            permission_classes = [IsAdminUser]
        else:
            if self.request.user.groups.filter(name='delivery crew').exists() or self.request.user.groups.filter(name='Managers').exists():
                permission_classes = [IsAuthenticated]
            else:
                permission_classes = []
        return [permission() for permission in permission_classes]

    def get_queryset(self):
        items = OrderItem.objects.all()
        order_id = self.kwargs['pk']
        query = items.filter(order__id=order_id)
        return query
        
    def put(self, request, *args, **kwargs):
        order_id = kwargs['pk']
        crew_name = request.data['delivery_crew']
        if 'delivery_crew' not in request.data:
            return Response(status=400, data={'message': 'delivery_crew field is required'})
        
        order = get_object_or_404(Order, pk=order_id)
        crew = get_object_or_404(User, username=crew_name)
        
        if crew.groups.filter(name='delivery crew').exists():
            order.delivery_crew = crew
            order.save()
            return Response(status=201, data={'message':str(crew.username)+' was assigned to order #'+str(order.id)})
        else:
            return Response(status=401, data={'message':'Assigned user is not delivery crew'})


    def patch(self, request, *args, **kwargs):
        order = Order.objects.get(pk=self.kwargs['pk'])
        order.status = not order.status
        order.save()
        return Response(status=200, data={'message':'Status of order #'+ str(order.id)+' changed to '+str(order.status)})

    def delete(self):
        order =  OrderItem.objects.filter(order__id = self.kwargs['pk'])
        if order:
            order_number = str(order.id)
            order.delete()
            return Response(status=200, data={'message':'Order #{} was deleted'.format(order_number)})
        return Response({"message": "there is no order with the id"}, status.HTTP_400_BAD_REQUEST)


@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAdminUser])
def managers(request):
    managers = Group.objects.get(name = "Manager")
    if request.method == "GET":
        serialized_managers = {
            'name': managers.name,
            'users': list(managers.user_set.values('id', 'username'))
        }
        return Response({"managers": serialized_managers})
    else:
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            if request.method == "POST":
                managers.user_set.add(user)
                return Response({'message': 'User Successfully changed to managers'})
            elif request.method == "DELETE":
                managers.user_set.remove(user)
                return Response({'message': 'User Successfully Deleted from manager group'})
    
    return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'POST', 'DELETE'])
@permission_classes([IsAdminUser])
def delivery_crews(request):
    crews = Group.objects.get(name = "delivery crew")
    if request.method == "GET" and crews:
        serialized_crews = {
            'name': crews.name,
            'users': list(crews.user_set.values('id', 'username'))
        }
        return Response({"managers": serialized_crews})
    else:
        username = request.data['username']
        if username:
            user = get_object_or_404(User, username=username)
            if request.method == "POST":
                crews.user_set.add(user)
                return Response({'message': 'User Successfully changed to crews'})
            elif request.method == "DELETE":
                crews.user_set.remove(user)
                return Response({'message': 'User Successfully Deleted from crews group'})
    
    return Response({"message": "error"}, status.HTTP_400_BAD_REQUEST)
