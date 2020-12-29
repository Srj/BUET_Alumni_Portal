from passlib.context import CryptContext
from  django.contrib.auth.password_validation import CommonPasswordValidator
import psycopg2 
from psycopg2 import Error


#------------------------Encryption Metadata-----------------------------
pwd_context = CryptContext(
        schemes=["pbkdf2_sha256"],
        default="pbkdf2_sha256",
        pbkdf2_sha256__default_rounds=30000
)

#--------------------------Connect Database----------------------------- 
def db():
        conn = psycopg2.connect(
                    user="postgres",
                    password= "postgres",
                    # host= "127.0.0.1",    
                    host="database",
                    port="5432",
                    database="django_db"
        )
        return conn

#----------------Logged In----------------
logged_in = False


#---------------------------------Password Validation----------------------------
def encrypt_password(password):
    return pwd_context.hash(password)
    # return pwd_context.encrypt(password)     ----Deprecated

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