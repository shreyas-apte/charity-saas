# In public/views.py

from django.shortcuts import render
from tenants.models import Client

def home(request):
    clients = Client.objects.all()
    return render(request, 'public/home.html', {'clients': clients})