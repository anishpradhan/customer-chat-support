from django.contrib import admin
from django.urls import path, include
from . import views as account_views

app_name = 'account'
urlpatterns = [
    path('register/', account_views.registration_view, name="register"),
    path('login/', account_views.login_view, name="login"),
    path('logout/', account_views.logout_view, name="logout"),
    path('index/', account_views.index, name="index"),
]