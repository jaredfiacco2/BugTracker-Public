"""
Definition of views.
"""

from datetime import datetime
from django.shortcuts import render
from django.http import HttpRequest
from .models import ContactInfo, Usecases
from django.core import serializers
from django.http import HttpResponse

##################################### User Views #################################
def home(request):
    """Renders the home page."""
    assert isinstance(request, HttpRequest)
    return render(
        request,
        'app/index.html',
        {
            'title':'Home Page',
            'year':datetime.now().year,
        }
    )

def about(request):
    """Renders the about page."""
    contact = ContactInfo.objects.all()
    usecase = Usecases.objects.all()
    context = {
        "contact" : contact,
        "usecase" : usecase,
    }
    assert isinstance(request, HttpRequest)
    return render(request, 'app/about.html', context)
