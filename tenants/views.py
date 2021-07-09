from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
import requests
# Create your views here.
from .models import Client, Domain
from django.db import connection
from account.models import Account


def create_tenant(request):
    if request.method == 'POST':
        schema_name = request.POST['name']
        if schema_name == 'public':
            return HttpResponse('<h1>This name ' + schema_name + ' is not available. Please choose another name</h1>')
        name = request.POST['name'].upper()
        domain = request.POST['domain']
        tenant = Client(schema_name=schema_name,
                        name=name)
        tenant.save()
        set_domain = Domain()
        set_domain.domain = domain
        set_domain.tenant = tenant
        set_domain.is_primary = True
        set_domain.save()
        admin_email = f'admin@{schema_name}.com'
        admin_username = f'admin_{schema_name}'
        admin_firstname = f'{schema_name}'
        admin_lastname = f'admin'
        admin_tenant = tenant
        admin_password = f'admin_{schema_name}'

        create_admin = Account(email=admin_email,username=admin_username,first_name=admin_firstname,
                               last_name=admin_lastname,tenant=admin_tenant, is_admin=True, is_active=True,
                               is_staff=True, is_superuser=True)
        create_admin.set_password(admin_password)
        create_admin.save()
        from django_tenants.utils import schema_context
        with schema_context(tenant.schema_name):
            create_admin = Account(email=admin_email,username=admin_username,first_name=admin_firstname,
                                   last_name=admin_lastname,tenant=admin_tenant, is_admin=True, is_active=True,
                                   is_staff=True, is_superuser=True)
            create_admin.set_password(admin_password)
            create_admin.save()


        response = HttpResponseRedirect(reverse('account:login'))

        # response.headers['X-DTS-SCHEMA'] = tenant.tenant_uuid
        return response
    return render(request, 'register_tenant.html')
