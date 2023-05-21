from .models import Category, MenuItem, Cart, Order, OrderItem
from rest_framework import serializers
from rest_framework.validators import UniqueTogetherValidator 
from django.contrib.auth.models import User
from decimal import Decimal


class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'title']

class MenuItemSerializer(serializers.ModelSerializer):
    category_id = serializers.IntegerField(write_only = True)
    category = CategorySerializer(read_only = True)
    class Meta:
        model = MenuItem
        fields = ['title', 'price', 'featured', 'category', 'category_id']
        extra_kwargs = {
            'price': {'min_value': 0}
        }
class CartHelpSerializer(serializers.ModelSerializer):
    class Meta():
        model = MenuItem
        fields = ['id','title','price']
        
class CartItemSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField( 
        queryset=User.objects.all(), 
        default=serializers.CurrentUserDefault() 
    )
    menuitem = CartHelpSerializer()
    class Meta:
        model = Cart
        fields = ['user', 'menuitem', 'quantity', 'unit_price', 'price']
        extra_kwargs = {
            'quantity': {'min_value': 1}
        }

class CartAddSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menuitem','quantity']
        extra_kwargs = {
            'quantity': {'min_value': 1},
        }
class CartRemoveSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cart
        fields = ['menuitem']

class UserSerializer(serializers.ModelSerializer):
    class Meta():
        model = User
        fields = ['username']


class OrderSerializer(serializers.ModelSerializer):
    user = serializers.PrimaryKeyRelatedField( 
        queryset=User.objects.all(), 
        default=serializers.CurrentUserDefault() 
    )
    delivery_crew = serializers.PrimaryKeyRelatedField( 
        queryset=User.objects.filter(groups__name='delivery crew'), 
        default=None
    )
    id = serializers.IntegerField(read_only = True)

    status = serializers.BooleanField(read_only=True)
    date = serializers.DateField(read_only=True)
    total = serializers.DecimalField(max_digits=6, decimal_places=2, read_only=True)
    class Meta:
        model = Order
        fields = ['id', 'user', 'delivery_crew', 'status', 'total', 'date']


class OrderItemSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only = True)
    order_id = serializers.IntegerField(read_only = True)
    menuitem = MenuItemSerializer(read_only = True)
    quantity = serializers.IntegerField(read_only = True)
    price = serializers.DecimalField(max_digits=6, decimal_places=2, read_only = True)
    class Meta:
        model = OrderItem
        fields = ['order', 'menuitem', 'order_id', 'quantity','price']