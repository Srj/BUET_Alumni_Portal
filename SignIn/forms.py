from django import forms

class SignInForm(forms.Form):
    std_id = forms.IntegerField(label='Student ID',required=True)
    password = forms.CharField(label=('Enter Password'),widget=forms.PasswordInput,required = True)