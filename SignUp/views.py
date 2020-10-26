from django.shortcuts import render,redirect
from django.core.exceptions import ValidationError
from django import forms
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
import cx_Oracle
from passlib.context import CryptContext
# Create your views here.


pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)

def encrypt_password(password):
    return pwd_context.encrypt(password)


def password_validator(password):
    try:
        password = str(password)
    except :
        return 'Wrong Password'

    if len(password) < 6:
        return 'Password too short'
    if len(password) > 20:
        return 'Password too long'
    return 'Success'



class SignUpForm(forms.Form):
    std_id = forms.IntegerField(label='Student ID',required=True)
    fullname = forms.CharField(label=('Full Name'),required=True)
    nickname = forms.CharField(label=('Nick Name'))
    password = forms.CharField(label=('Enter Password'),widget=forms.PasswordInput,required = True)
    password_again = forms.CharField(label=('Retype Password'),widget=forms.PasswordInput,required=True) 
    email = forms.EmailField(label=('Email'),widget=forms.EmailInput,required=True)
    mobile = forms.IntegerField(label='Cell No')
    birthdate = forms.DateTimeField(label=('Date of Birth'),widget=forms.widgets.DateInput(attrs={'type': 'date'}),required=True)

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password2 = cleaned_data.get('password_again')
        email = cleaned_data.get('email')
        if password_validator(password) != 'Success':
            self.add_error('password', password_validator(password))

        if password2 != password:
            self.add_error('password_again','Password don\'t Match.')
            return password


def index(request):
    dsn_tns = cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
    conn =cx_Oracle.connect(user='PROJECT',password='1234',dsn=dsn_tns)
    c = conn.cursor()
    print(c)
    c.execute("SELECT * from PROJECT.USER_REC")   
    out = ''
    print(c)
    for row in c : 
        out +=str(row) + ' \n '
    conn.close()
    return HttpResponse(out,content_type="text/plain")
def SignUp(request):
    form_signup = SignUpForm()
    message = ""
    if request.method == 'POST':
        form_signup = SignUpForm(request.POST)
        if form_signup.is_valid():
            info = {
            'std_id' : form_signup.cleaned_data['std_id'],
            'fullname' : form_signup.cleaned_data['fullname'],
            'nickname' : form_signup.cleaned_data['nickname'],
            'password' : encrypt_password(form_signup.cleaned_data['password']),
            'email' : form_signup.cleaned_data['email'],
            'mobile' : form_signup.cleaned_data['mobile'],
            'birthdate': form_signup.cleaned_data['birthdate'],
            }
            dsn_tns = cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
            conn =cx_Oracle.connect(user='PROJECT',password='1234',dsn=dsn_tns)
            c = conn.cursor()
            sql = """ INSERT INTO PROJECT.USER_REC (USER_ID,FULL_NAME,NICK_NAME,EMAIL,MOBILE,DATE_OF_BIRTH,PASSWORD) VALUES(:std_id,:fullname,:nickname,:email,:mobile,to_date(:birthdate,'yyyy-mm-dd'),:password)"""
            try:
                c.execute(sql,info)
                conn.commit()
                conn.close()
            except cx_Oracle.IntegrityError:
                message = "User already exists ..."
    return render(request,'SignUp/SignUp.html',{'form':form_signup, 'msg' : message})


