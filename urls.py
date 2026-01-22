from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),

    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),

    path('flowers/', views.flowers, name='flowers'),
    path('shopplants/', views.shopplants, name='shopplants'),
    path('weddings/', views.weddings, name='weddings'),
    path('workshop/', views.workshop, name='workshop'),

    path('orders/', views.orders, name='orders'),
    path('map/', views.map, name='map'),
    path('contact/', views.contact, name='contact'),

    path('cart/', views.cart_view, name='cart'),
    path('checkout/', views.checkout, name='checkout'),   # 🆕 NEW
    path('payment/', views.payment, name='payment'),
    path('payment-success/', views.payment_success, name='payment_success'),


    path('add/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('remove/<int:product_id>/', views.remove_from_cart, name='remove_from_cart'),

    path('buy/<int:flower_id>/', views.buy_now, name='buy_now'),
]
