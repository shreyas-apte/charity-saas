# In campaigns/views.py

from django.shortcuts import render
from .models import Campaign
from donors.models import Donor

def dashboard(request):
    campaigns = Campaign.objects.all()
    donors = Donor.objects.all()
    tenant = request.tenant
    return render(request, 'tenant/dashboard.html', {
        'campaigns': campaigns,
        'donors': donors,
        'tenant': tenant
    })