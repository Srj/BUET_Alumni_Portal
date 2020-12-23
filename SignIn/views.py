from django.shortcuts import render,redirect
from passlib.context import CryptContext
from Alumni_Portal.utils import check_encrypted_password,db
from .forms import SignInForm
from django.http import HttpResponseRedirect
from django.urls import reverse

def index(request):
    conn = db()
    std_id = None
    message = ""
    form = SignInForm()
    if request.method == 'GET':
        if 'std_id' in request.session:
            print('Signed In' + str(request.session['std_id']))
            #return redirect('Profile:profile')
            return HttpResponseRedirect(reverse('post:all_post', args=(1, 0)))

        else:
            return render(request,'SignIn/index.html',{'form':form, 'msg' : 'Please Sign In','std_id': None})


    elif request.method == 'POST':
        form = SignInForm(request.POST)
        
        print(form.is_valid())
        if form.is_valid():
            std_id = form.cleaned_data['std_id']
            password = form.cleaned_data['password']
            c = conn.cursor()
            sql = """ SELECT password from USER_TABLE WHERE STD_ID = %(std_id)s;"""
            c.execute(sql,{'std_id':std_id})
            row = c.fetchone()
            if row is None:
                message = "User Doesn\'t exists ..."
                return render(request,'SignIn/index.html',{'form':form, 'msg' : message,'std_id': None})
            else:
                if check_encrypted_password(password,row[0]):
                    request.session['std_id'] = std_id
                    print('Signed In' + str(request.session['std_id']))
                    #return HttpResponseRedirect('/profile')
                    return HttpResponseRedirect(reverse('post:all_post', args=(1, 0)))
                else:
                    message = "Invalid Password"
                    std_id = None
            conn.close()
    return render(request,'SignIn/index.html',{'form':form, 'msg' : message,'std_id': None})
    
   

def logout(request):
   
    if 'std_id' in request.session:
        try:
            del request.session['std_id']
            print('Logged Out' + str(request.session['std_id']))
        except KeyError:
            print('Cannot Log out')
    return redirect('/')
