from django.shortcuts import render,redirect
from django.core.exceptions import ValidationError
from django import forms
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
from Alumni_Portal.utils import password_validator,encrypt_password,db
from .forms import SignUpForm
from psycopg2 import IntegrityError
import psycopg2
def index(request):
    conn = db()
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
            'birthdate': str(form_signup.cleaned_data['birthdate'].strftime('%Y-%m-%d')) if form_signup.cleaned_data['birthdate'] is not None else None ,

            }
            print(info)

            c = conn.cursor()
            sql = """ INSERT INTO USER_TABLE (STD_ID,FULL_NAME,NICK_NAME,EMAIL,MOBILE,DATE_OF_BIRTH,PASSWORD)
                        VALUES(%(std_id)s,%(fullname)s,%(nickname)s,%(email)s,%(mobile)s,to_date(%(birthdate)s,'yyyy-mm-dd'),%(password)s)"""
            try:
                c.execute(sql,info)
                conn.commit()
                conn.close()
                print('Registered User' + str(info['std_id']))
                return redirect('SignIn:signin')
            except  IntegrityError:
                message = "User already exists ..."
                print('"User already exists ...')
    else:
        form_signup = SignUpForm()
    return render(request,'SignUp/index.html',{'form':form_signup, 'msg' : message})


