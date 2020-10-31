from django import forms
from Alumni_Portal.utils import password_validator,db

from django.core.validators import validate_email


class EditForm(forms.Form):
    fullname = forms.CharField(label=('Full Name'))
    nickname = forms.CharField(label=('Nick Name'),required=False)
    email = forms.EmailField(label=('Email'),widget=forms.EmailInput)
    mobile = forms.IntegerField(label='Cell No',required=False)
    birthdate = forms.DateTimeField(label=('Date of Birth'),widget=forms.widgets.DateInput(attrs={'type': 'date'}),required=False)
    dept =forms.CharField(label=('dept'),required=False)
    hall =forms.CharField(label=('hall'),required=False)
    level = forms.IntegerField(label=('level'),required=False)
    term = forms.IntegerField(label=('term'),required=False)
    msc =forms.CharField(label=('msc'),required=False)
    phd = forms.CharField(label=('phd'),required=False)
    house = forms.IntegerField(label=('house'),required=False)
    road =forms.IntegerField(label=('road'),required=False)
    zipcode = forms.IntegerField(label=('zip'),required=False)
    city = forms.CharField(label=('city'),required=False)
    country = forms.CharField(label=('country'),required=False)
    hometown = forms.CharField(label=('home'),required=False)

class DPForm(forms.Form):
     file = forms.FileField()

class ExpertForm(forms.Form):
    topic = forms.CharField(required=True)

class SearchForm(forms.Form):
    name = forms.CharField(required=False)
    location = forms.CharField(required=False)
    institution = forms.CharField(required=False)
    interest = forms.CharField(required=False)

        