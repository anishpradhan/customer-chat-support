from django.shortcuts import render
# from django.contrib.auth.decorators import login_required
from tenants.models import Client



def main_index(request):
    tenants = Client.objects.all().exclude(schema_name='public')
    print(request.tenant)
    context = {
        'tenants': tenants,
    }
    return render(request, 'main_index.html', context=context)
