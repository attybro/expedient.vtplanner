'''
Created on Jul 23, 2013

@author: atty
'''
from django import forms
from models import Vslice
from django.conf import settings

class VsliceCrudForm(forms.ModelForm):
    class Meta:
        model = Vslice
        exclude = ["project", "aggregates", "owner", "reserved", "expiration_date"]
        
class ContactForm(forms.Form):
    subject = forms.CharField()
