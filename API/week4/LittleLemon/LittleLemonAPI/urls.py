from django.urls import path
from . import views
from rest_framework.authtoken.views import obtain_auth_token


urlpatterns = [
    path('category', views.CategoriesView.as_view()),
    path('menu-items', views.MenuItemsView.as_view()),
    path('menu-items/<int:pk>', views.SingleMenuItemView.as_view()),
    path('api-token-auth/', obtain_auth_token),
    path('groups/manager/users', views.managers),
    path('groups/delivery-crew/users', views.delivery_crews),
    path('cart/menu-items', views.CartItemsView.as_view()),
    path('orders', views.OrdersView.as_view()),
    path('orders/<int:pk>', views.OrderItemView.as_view()),
    ]
'''
path('cart/menu-items', views.MenuItemsView.as_view()),
path('orders', views.OrdersView.as_view()),
path('orders/<int:pk>', views.SingleOrderView.as_view()),
'''

