from django.shortcuts import render
from django.http import HttpResponse
from Alumni_Portal.utils import db,encrypt_password
import cx_Oracle
from .forms import EditForm
# Create your views here.



def index(request):
    if 'std_id' in request.session:
        std_id = request.session['std_id']
        data =None
        conn = db()
        c = conn.cursor()
        sql = """ SELECT * from USER_TABLE JOIN PROFILE USING(STD_ID) JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD USING(STD_ID) WHERE STD_ID = :std_id"""
        row =  c.execute(sql,{'std_id':std_id}).fetchone()
        columnNames = [d[0] for d in c.description]
        print(row)
        try:
            data = dict(zip(columnNames,row))
        except:
            print('NULL')
        sql = """ SELECT  TOPIC, COUNT(GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE USING(TOPIC) WHERE USER_ID = :std_id GROUP BY TOPIC"""
        rows =  c.execute(sql,{'std_id':std_id})
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
    return render(request,'Profile/profile.html',{'data':data,'skills':skills})


def edit(request):
    #return render(request,'Profile/edit.html')
    conn = db()
    c = conn.cursor()
    message = ""
    sql = """ SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD USING(STD_ID) WHERE STD_ID = :std_id"""
    row =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchone()
    columnNames = [d[0] for d in c.description]
    data = dict(zip(columnNames,row))
    form_signup = EditForm(initial={'fullname':data['FULL_NAME'],'nickname':data['NICK_NAME'],'email':data['EMAIL'],
                                                 'mobile':data['MOBILE'],'birthdate':data['DATE_OF_BIRTH'],'dept':data['DEPT'],
                                                 'hall':data['HALL'],'level':data['LVL'],'term':data['TERM'],'msc':data['MSC'],
                                                 'phd':data['PHD'],'house':data['HOUSE_NO'],'road':data['ROAD_NO'],'zipcode':data['ZIP_CODE'],
                                                 'city':data['CITY'],'country':data['COUNTRY'],'hometown':data['HOME_TOWN']})
    if request.method == 'POST':
        form_signup = EditForm(request.POST)
        if form_signup.is_valid():

            user = {
            'std_id' : request.session.get('std_id'),
            'fullname' : form_signup.cleaned_data['fullname'],
            'nickname' : form_signup.cleaned_data['nickname'],
            'email' : form_signup.cleaned_data['email'],
            'mobile' : form_signup.cleaned_data['mobile'],
            'birthdate': form_signup.cleaned_data['birthdate'],
            }
            undergrad = {
                'std_id' : request.session.get('std_id'),
                'hall' : form_signup.cleaned_data['hall'],
                'dept' : form_signup.cleaned_data['dept'],
                'lvl': form_signup.cleaned_data['level'],
                'term' : form_signup.cleaned_data['term']

            }
            postgrad = {
                'std_id' : request.session.get('std_id'),
                'msc' : form_signup.cleaned_data['msc'],
                'phd' : form_signup.cleaned_data['phd']
            }
            profile = {
                'std_id' : request.session.get('std_id'),
                'house': form_signup.cleaned_data['house'],
                'road': form_signup.cleaned_data['road'],
                'zip': form_signup.cleaned_data['zipcode'],
                'city': form_signup.cleaned_data['city'],
                'country': form_signup.cleaned_data['country'],
                'hometown': form_signup.cleaned_data['hometown']
            }
            print('HEERE')
            print(undergrad)
            sql = """ UPDATE USER_TABLE SET FULL_NAME = :fullname, NICK_NAME = :nickname,EMAIL=:email,MOBILE=:mobile,DATE_OF_BIRTH=:birthdate WHERE STD_ID=:std_id"""
            try:
                c.execute(sql,user)
                conn.commit()
                print('Updated User')
            except cx_Oracle.IntegrityError:
                message = "User already exists ..."
                print('Error')
            #-----------------Update Profile---------------------
            sql = """ SELECT * from PROFILE WHERE STD_ID = :std_id"""
            row =  c.execute(sql,{'std_id':user['std_id']}).fetchone()
            if row is None:
                sql = """ INSERT INTO PROFILE (STD_ID,HOUSE_NO,ROAD_NO,ZIP_CODE,CITY,COUNTRY,HOME_TOWN)
                        VALUES(:std_id,:house,:road,:zip,:city,:country,:hometown)"""
                try:
                    c.execute(sql,profile)
                    conn.commit()
                    print('Inserted Profile')
                except cx_Oracle.IntegrityError:
                    message = "User already exists ..."
                    print('Error')
            else:
                sql = """ UPDATE PROFILE SET HOUSE_NO = :house,ROAD_NO = :road, ZIP_CODE = :zip,CITY = :city,COUNTRY = :country,HOME_TOWN = :hometown
                        WHERE STD_ID = :std_id"""
                try:
                    c.execute(sql,profile)
                    conn.commit()
                    print('Updated User')
                except cx_Oracle.IntegrityError:
                    message = "User already exists ..."
                    print('Error')

            #------------------------Update Undergrad----------------------
            sql = """ SELECT * from UNDERGRAD WHERE STD_ID = :std_id"""
            row =  c.execute(sql,{'std_id':user['std_id']}).fetchone()
            if row is None:
                sql = """ INSERT INTO UNDERGRAD (STD_ID,HALL,DEPT,LVL,TERM)
                        VALUES(:std_id,:hall,:dept,:lvl,:term)"""
                try:
                    c.execute(sql,undergrad)
                    conn.commit()
                    print('Inserted UnderGrad')
                except cx_Oracle.IntegrityError:
                    message = "User already exists ..."
                    print('Error')
            else:
                sql = """ UPDATE UNDERGRAD SET HALL =:hall,DEPT=:dept,LVL=:lvl,TERM=:term
                        WHERE STD_ID =:std_id"""
                try:
                    c.execute(sql,undergrad)
                    conn.commit()
                    print('Updated Undergrad')
                except cx_Oracle.IntegrityError:
                    message = "User already exists ..."
                    print('Error')

            #-----------------Update Postgrad ----------------------------
            sql = """ SELECT * from POSTGRAD WHERE STD_ID = :std_id"""
            row =  c.execute(sql,{'std_id':user['std_id']}).fetchone()
            if row is None:
                sql = """ INSERT INTO POSTGRAD (STD_ID,MSC,PHD)
                        VALUES(:std_id,:msc,:phd)"""
                try:
                    c.execute(sql,postgrad)
                    conn.commit()
                    print('Inserted PostGrad')
                except cx_Oracle.IntegrityError:
                    message = "User already exists ..."
                    print('Error')
            else:
                sql = """ UPDATE POSTGRAD SET MSC=:msc,PHD=:phd
                        WHERE STD_ID = :std_id"""
                try:
                    c.execute(sql,postgrad)
                    conn.commit()
                    print('Updated PostGrad')
                except cx_Oracle.IntegrityError:
                    message = "User already exists ..."
                    print('Error')
        else:
            print('Invalid')

    return render(request,'Profile/edit.html',{'form':form_signup,'data':data, 'msg' : message})