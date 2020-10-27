from django.shortcuts import render,redirect
from django.core.exceptions import ValidationError
from django import forms
from django.http import HttpResponse,HttpResponseRedirect
from django.urls import reverse
import cx_Oracle
from Alumni_Portal.utils import password_validator,encrypt_password,db
from .forms import SignUpForm

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
            'birthdate': form_signup.cleaned_data['birthdate'],
            }

            c = conn.cursor()
            sql = """ INSERT INTO USER_TABLE (STD_ID,FULL_NAME,NICK_NAME,EMAIL,MOBILE,DATE_OF_BIRTH,PASSWORD)
                        VALUES(:std_id,:fullname,:nickname,:email,:mobile,to_date(:birthdate,'yyyy-mm-dd'),:password)"""
            try:
                c.execute(sql,info)
                conn.commit()
                conn.close()
                print('Registered')
            except cx_Oracle.IntegrityError:
                message = "User already exists ..."
                print('Error')
    else:
        form_signup = SignUpForm()
    return render(request,'SignUp/index.html',{'form':form_signup, 'msg' : message})


