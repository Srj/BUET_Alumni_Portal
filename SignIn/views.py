from django.shortcuts import render,redirect
from passlib.context import CryptContext
from django import forms
import cx_Oracle
pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)

def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)


class SignInForm(forms.Form):
    std_id = forms.IntegerField(label='Student ID',required=True)
    password = forms.CharField(label=('Enter Password'),widget=forms.PasswordInput,required = True)

def SignIn(request):
    std_id = None
    message = ""
    form = SignInForm()
    if request.method == 'GET':
        if 'std_id' in request.session:
            std_id = request.session['std_id']
            print(request.session.get_expiry_date())


        if 'action' in request.GET:
                action = request.GET.get('action')
                if action == 'logout':
                    if request.session.has_key('std_id'):
                        request.session.flush()
                    return redirect('SignIn:signin')

    elif request.method == 'POST':
        form = SignInForm(request.POST)
        
        print(form.is_valid())
        if form.is_valid():
            std_id = form.cleaned_data['std_id']
            password = form.cleaned_data['password']
            dsn_tns = cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
            conn =cx_Oracle.connect(user='PROJECT',password='1234',dsn=dsn_tns)
            c = conn.cursor()
            sql = """ SELECT password from PROJECT.USER_REC WHERE USER_ID = :std_id"""
            row =  c.execute(sql,{'std_id':std_id}).fetchone()
            if row is None:
                message = "User Doesn\'t exists ..."
                return render(request,'SignIn/SignIn.html',{'form':form, 'msg' : message,'std_id': None})
            else:
                if check_encrypted_password(password,row[0]):
                    request.session['std_id'] = std_id
                else:
                    message = "Invalid Password"
                    std_id = None
            conn.close()

    return render(request,'SignIn/SignIn.html',{'form':form, 'msg' : message,'std_id': std_id})
