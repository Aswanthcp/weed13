from django.urls import path

from . import views

app_name = 'accounts'


urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_page, name='login_page'),
    path('logout/', views.logout, name='logout'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('otplogin/', views.otplogin, name='otplogin'),
    path('verify/', views.verify_code, name="verify"),
    path('verifyotp/', views.verifyotp, name="verifyotp"),

    path('activate/<uidb64>/<token>/', views.activate, name='activate'),
    path('add_address/', views.add_address, name="add_address"),
    path('address_list/', views.address_list, name="address_list"),
    path('edit_address/<int:address_id>', views.edit_address, name='edit_address'),
    path('edit_profile/', views.edit_profile, name='edit_profile'),
    path('change_password/', views.change_password, name='change_password'),
    path('order_detail/<str:tracking_no>',
         views.order_detail, name="order_detail"),

]
