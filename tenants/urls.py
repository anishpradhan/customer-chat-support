from django.contrib import admin
from django.urls import path, include
from . import views
from . import api

app_name = 'tenants'

urlpatterns = [
    path('create-tenant/', views.create_tenant, name='create_tenant'),
    path('api/get_tenant_uuid/', api.get_tenent_uuid, name='get-tenant-uuid'),

]
