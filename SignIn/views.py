from django.shortcuts import render,redirect
from passlib.context import CryptContext
from Alumni_Portal.utils import check_encrypted_password,db
import cx_Oracle
from .forms import SignInForm
from django.http import HttpResponseRedirect
def index(request):
    conn = db()
    std_id = None
    message = ""
    form = SignInForm()
    if request.method == 'GET':
        if 'std_id' in request.session:
            print('Cannot Log Out')
            return redirect('Profile:profile')

        else:
            return render(request,'SignIn/index.html',{'form':form, 'msg' : 'Please Sign In','std_id': None})


    elif request.method == 'POST':
        form = SignInForm(request.POST)
        
        print(form.is_valid())
        if form.is_valid():
            std_id = form.cleaned_data['std_id']
            password = form.cleaned_data['password']
            c = conn.cursor()
            sql = """ SELECT password from USER_TABLE WHERE STD_ID = :std_id"""
            row =  c.execute(sql,{'std_id':std_id}).fetchone()
            if row is None:
                message = "User Doesn\'t exists ..."
                return render(request,'SignIn/index.html',{'form':form, 'msg' : message,'std_id': None})
            else:
                if check_encrypted_password(password,row[0]):
                    request.session['std_id'] = std_id
                    return HttpResponseRedirect('/profile')
                else:
                    message = "Invalid Password"
                    std_id = None
            conn.close()
    return render(request,'SignIn/index.html',{'form':form, 'msg' : message,'std_id': None})
    #return render(request,'SignIn/SignIn.html',{'form':form, 'msg' : message,'std_id': std_id})

def logout(request):
    print('In LogOuts')
    if 'std_id' in request.session:
        try:
            del request.session['std_id']
        except KeyError:
            print('Logged Out Not ')
    return redirect('/')
