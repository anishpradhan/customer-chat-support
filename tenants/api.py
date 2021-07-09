from .serializers import *
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from django.http import JsonResponse, HttpResponse
import json


@api_view(['GET'])
def get_tenent_uuid(request):
    if request.method == 'GET':
        schema_name = request.GET['schema_name']
        queryset = Client.objects.get(schema_name=schema_name)
        response = {
            'tenant_uuid': str(queryset.tenant_uuid),
            'tenant_name': queryset.schema_name,
            # 'domain':
        }
        return JsonResponse(response, safe=False)
