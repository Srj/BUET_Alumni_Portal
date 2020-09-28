from django.shortcuts import render
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

dsn_tns = cx_Oracle.makedsn('localhost','1521',service_name='ORCL')
conn =cx_Oracle.connect(user='PROJECT',password='1234',dsn=dsn_tns)

def encrypt_password(password):
    return pwd_context.encrypt('007007')


def check_encrypted_password(password, hashed):
    return pwd_context.verify(password, hashed)

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
def SignUpPage(request):
    return render(request,'SignIn/SignUp.html')

def SignUp(request):
    try:
        id_ = request.POST['ID']
        name =request.POST['Name']
        nickname =request.POST['nickname']
        password = request.POST['Pass']
        password2 = request.POST['pass_again']
        email = request.POST['email']
        mobile = request.POST['mobile']
        birth = request.POST['birth']
        print(name,nickname,password,password2,email, mobile,birth)
    except KeyError:
        return HttpResponseRedirect(reverse('SignIn:signuppage'))


    if not password_validator(password) == 'Success':
        return HttpResponse('Invalid Password')
    if not password == password2:
        return HttpResponse('Password doesn\'t Match')

    password = encrypt_password(password)

    c = conn.cursor()
    print("INSERT INTO PROJECT.USER_REC (USER_ID,FULL_NAME,NICK_NAME,EMAIL,MOBILE,DATE_OF_BIRTH,PASSWORD) VALUES(" + id_ + ",\'" + name + "\',\'" +\
                                                            nickname+ "\',\'" + email+ "\',\'" +mobile+ "\',\'" + birth+ "\',\'" +password+"\');")
    c.execute("INSERT INTO PROJECT.USER_REC (USER_ID,FULL_NAME,NICK_NAME,EMAIL,MOBILE,PASSWORD) VALUES(" + id_ + ",\'" + name + "\',\'" +\
                                                            nickname+ "\',\'" + email+ "\',\'" +mobile+ "\',\'" +password+"\')")   
    
    conn.commit()
    conn.close()
    print(password)
    return HttpResponse('Success')