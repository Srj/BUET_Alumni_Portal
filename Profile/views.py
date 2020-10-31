from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from Alumni_Portal.utils import db,encrypt_password
from django.urls import reverse
import cx_Oracle
from .forms import EditForm,DPForm,ExpertForm,SearchForm
from django.core.files.storage import FileSystemStorage
# Create your views here.

skill_error = None

def index(request):
    if 'std_id' in request.session:
        std_id = request.session['std_id']
        data =None
        conn = db()
        c = conn.cursor()
        sql = """ SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD USING(STD_ID) WHERE STD_ID = :std_id"""
        row =  c.execute(sql,{'std_id':std_id}).fetchone()
        columnNames = [d[0] for d in c.description]
        print(row)
        try:
            data = dict(zip(columnNames,row))
        except:
            print('NULL')
        print(data)
        sql = """ SELECT  TOPIC, COUNT(GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE USING(TOPIC) WHERE STD_ID = :std_id GROUP BY TOPIC"""
        rows =  c.execute(sql,{'std_id':std_id})
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
        dp_form = DPForm()
    return render(request,'Profile/profile.html',{'data':data,'skills':skills,'edit':True,'dp':dp_form})

def search(request):
    conn = db()
    message = ""
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            info = {
            'name' : form.cleaned_data['name'],
            'location' : form.cleaned_data['location'],
            #'institute': form.cleaned_data['institution'],
            'interest': form.cleaned_data['interest']
            }
            
            if not info['name'] is '':
                info['name'] = '%' + info['name'].lower() + '%'
            if not info['location'] is '':
                info['location'] = '%' + info['location'].lower() + '%'
            if not info['interest'] is '':
                info['interest'] = '%' + info['interest'].lower() + '%'
            values = {}
            print(info)
            c = conn.cursor()
            results = []
            sql = """ 
                SELECT DISTINCT STD_ID,FULL_NAME,DEPT,FACEBOOK,TWITTER,GOOGLE_SCHOLAR,PHOTO,LINKEDIN  FROM (
                """
            sql1 = """SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID)
                LEFT JOIN POSTGRAD USING(STD_ID) LEFT JOIN EXPERTISE USING(STD_ID) WHERE LOWER(FULL_NAME) LIKE :name OR LOWER(NICK_NAME) LIKE :name OR STD_ID LIKE :name
                 UNION """

            sql2 ="""SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN 
                UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD USING(STD_ID) LEFT JOIN EXPERTISE USING(STD_ID) WHERE LOWER(COUNTRY) 
                LIKE :location OR LOWER(CITY) LIKE :location OR LOWER(HOME_TOWN) LIKE :location UNION """

            sql3 ="""SELECT DISTINCT *  from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD
                USING(STD_ID) LEFT JOIN EXPERTISE USING(STD_ID) WHERE LOWER(TOPIC) LIKE LOWER(:interest) UNION """
                
            if not info['name'] is '':
                sql += sql1
                values['name'] = info['name']
            if not info['location'] is '':
                sql +=sql2
                values['location'] =info['location']
            if not info['interest'] is '':
                sql+=sql3
                values['interest'] = info['interest']
            if sql.endswith('UNION '):
                sql = sql[:-6]+ ')'
                print(sql)
            else:
                msg = 'Please Type'
                return render(request,'Profile/search.html',{'form':form, 'msg' : message})
            rows =  c.execute(sql,values).fetchall()

            print(rows)
            if len(rows) ==  0 :
                message = "No Result Found"
                return render(request,'Profile/search.html',{'form':form, 'msg' : message})
            else:
                for row in rows:
                    columnNames = [d[0] for d in c.description]
                    data = (zip(columnNames,row))
                    results.append(dict(data))
                print(results)
                return render(request,'Profile/search.html',{'form':form, 'msg' : message,'data':results,'count':len(results)})
                    
    else:
        form = SearchForm()
    return render(request,'Profile/search.html',{'form':form, 'msg' : message})
def edit(request):
    #return render(request,'Profile/edit.html')
    conn = db()
    c = conn.cursor()
    message = ""
    sql = """ SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD USING(STD_ID) WHERE STD_ID = :std_id"""
    row =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchone()
    columnNames = [d[0] for d in c.description]
    data = dict(zip(columnNames,row))
    dp_form = DPForm()
    
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
                return redirect('Profile:profile')
        else:
            print('Invalid')
    expertise = ExpertForm()
    sql = """ SELECT  TOPIC, COUNT(GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE USING(TOPIC) WHERE STD_ID = :std_id GROUP BY TOPIC"""
    rows =  c.execute(sql,{'std_id':request.session.get('std_id')})
    skills = {}
    for row in rows:
        skills[row[0]] = row[1]
    return render(request,'Profile/edit.html',{'form':form_signup,'data':data,'skills':skills, 'msg' : message,'dp':dp_form,'expert':expertise,'skill_error':skill_error})

def visit_profile(request,std_id):
    if 'std_id' in request.session:
        user = request.session['std_id']
        enable_edit = False
        if user == std_id:
            enable_edit = True
            return redirect('Profile:profile')
        data =None
        conn = db()
        c = conn.cursor()
        sql = """ SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD USING(STD_ID) WHERE STD_ID = :std_id"""
        row =  c.execute(sql,{'std_id':std_id}).fetchone()
        columnNames = [d[0] for d in c.description]
        print(row)
        try:
            data = dict(zip(columnNames,row))
        except:
            print('NULL')
        sql = """ SELECT  TOPIC, COUNT(GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE USING(TOPIC) WHERE STD_ID = :std_id GROUP BY TOPIC"""
        rows =  c.execute(sql,{'std_id':std_id})
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
    return render(request,'Profile/profile.html',{'data':data,'skills':skills,'edit':enable_edit})

def edit_photo(request):
    if request.method == 'POST':
        if 'std_id' in request.session:
            user = request.session['std_id']
            myfile = request.FILES['file']
            fs = FileSystemStorage()
            print(myfile.name)
            filename = fs.save(myfile.name, myfile)
            conn = db()
            c = conn.cursor()
            sql = """ SELECT * from PROFILE WHERE STD_ID = :std_id"""
            row =  c.execute(sql,{'std_id':user}).fetchone()
            if row is None:
                sql = """ INSERT INTO PROFILE (STD_ID,PHOTO)
                        VALUES(:std_id,:photo)"""
                try:
                    c.execute(sql,{'std_id':user,"photo":myfile.name})
                    conn.commit()
                    print('Inserted DP')
                except cx_Oracle.IntegrityError:
                    print('Error')
            else:
                sql = """ UPDATE PROFILE SET PHOTO=:photo
                            WHERE STD_ID = :std_id"""
                try:
                    c.execute(sql,{'photo':myfile.name,'std_id':user})
                    conn.commit()
                    print('Updated DP')
                except cx_Oracle.IntegrityError:
                    message = "User already exists ..."
                    print('Error')
    return redirect('Profile:profile')

def edit_expertise(request):
    if request.method == 'POST':
        if 'std_id' in request.session:
            user = request.session['std_id']
            form = ExpertForm(request.POST)
            if form.is_valid():
                topic = form.cleaned_data['topic']
                conn = db()
                c = conn.cursor()
                sql = """ SELECT TOPIC from EXPERTISE WHERE STD_ID = :std_id AND TOPIC =:topic"""
                row =  c.execute(sql,{'std_id':user,'topic':topic}).fetchone()
                if row is None:
                    sql = """ INSERT INTO EXPERTISE (STD_ID,TOPIC)
                            VALUES(:std_id,:topic)"""
                    try:
                        c.execute(sql,{'std_id':user,"topic":topic})
                        conn.commit()
                        print('Inserted Skill')
                    except cx_Oracle.IntegrityError:
                        print('Error')
                else:
                    print('Exists')
                    skill_error = "Already Exists"
    

    return redirect('Profile:edit_profile')
def delete_expertise(request):
    if request.method == 'POST':
        if 'std_id' in request.session:
            user = request.session['std_id']
            form = ExpertForm(request.POST)
            if form.is_valid():
                topic = form.cleaned_data['topic']
                conn = db()
                c = conn.cursor()
                sql = """ SELECT TOPIC from EXPERTISE WHERE STD_ID = :std_id AND TOPIC =:topic"""
                row =  c.execute(sql,{'std_id':user,'topic':topic}).fetchone()
                if not row is None:
                    sql = """ DELETE FROM EXPERTISE WHERE STD_ID =:std_id AND TOPIC=:topic"""
                    try:
                        c.execute(sql,{'std_id':user,"topic":topic})
                        conn.commit()
                        print('Inserted Skill')
                    except cx_Oracle.IntegrityError:
                        print('Error')
                    sql = """ DELETE FROM ENDORSE WHERE TAKER_ID =:std_id AND TOPIC=:topic"""
                    try:
                        c.execute(sql,{'std_id':user,"topic":topic})
                        conn.commit()
                        print('Inserted Skill')
                    except cx_Oracle.IntegrityError:
                        print('Error')
                else:
                    print('Exists')
                    skill_error = "Not Exists"
    

    return redirect('Profile:edit_profile')
    
            