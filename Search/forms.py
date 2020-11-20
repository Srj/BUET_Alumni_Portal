from django import forms

class SearchForm(forms.Form):
    name = forms.CharField(required=False)
    location = forms.CharField(required=False)
    institution = forms.CharField(required=False)
    interest = forms.CharField(required=False)
    dept = forms.CharField(required=False)
    hall = forms.CharField(required=False)
    term = forms.CharField(required=False)