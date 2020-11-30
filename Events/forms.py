from django import forms

class EventForm(forms.Form):
    text = forms.CharField(required=False)
    name = forms.CharField(required=False)
    location = forms.CharField(required=False)
    time = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}),required=False)

class CreateEventForm(forms.Form):
    name = forms.CharField(required=True)
    location = forms.CharField(required=True)
    start_date = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}),required=True)
    end_date = forms.DateTimeField(widget=forms.widgets.DateInput(attrs={'type': 'date'}),required=True)
    about = forms.CharField(required=False)