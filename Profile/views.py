from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from Alumni_Portal.utils import db,encrypt_password
from django.urls import reverse
import cx_Oracle
import datetime
from .forms import EditForm,DPForm,ExpertForm,SearchForm,JobForm
from django.core.files.storage import FileSystemStorage
# Create your views here.

skill_error = None
  
def calculateAge(birthDate): 
    today = datetime.date.today() 
    print(birthDate.year)
    age = today.year - birthDate.year - ((today.month, today.day) < (birthDate.month, birthDate.day))  
    return age

def index(request):
    if 'std_id' in request.session:
        std_id = request.session['std_id']
        data =None
        conn = db()
        c = conn.cursor()
        sql = """ SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD USING(STD_ID) WHERE STD_ID = :std_id"""
        row =  c.execute(sql,{'std_id':std_id}).fetchone()
        columnNames = [d[0] for d in c.description]
        # print(row)
        
        try:
            data = dict(zip(columnNames,row))
            data['AGE'] = calculateAge(data['DATE_OF_BIRTH'])
            print(calculateAge(data['DATE_OF_BIRTH']))
        except:
            print('NULL')
        # print(data)

        #--------------Skills--------------
        sql = """ SELECT  EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
    EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = :std_id GROUP BY EXPERTISE.TOPIC"""
        rows =  c.execute(sql,{'std_id':std_id})
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
        dp_form = DPForm()

        #--------------Job History---------------------
        sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID = :std_id ORDER BY FROM_ DESC"""
        rows =  c.execute(sql,{'std_id':std_id})
        jobs = rows.fetchall()
        columnNames = [d[0] for d in c.description]
        job_list = []
        for job in jobs:
            try:
                job_list.append(dict(zip(columnNames,job)))
            except:
                print('NULL')
        # print(job_list)

        sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID = :std_id AND TO_ IS NULL ORDER BY FROM_"""
        rows =  c.execute(sql,{'std_id':std_id})
        current = rows.fetchone()
        columnNames = [d[0] for d in c.description]  
        try:
            current = dict(zip(columnNames,current))          
        except:
            print('NULL')
        
        return render(request,'Profile/profile.html',{'data':data,'skills':skills,'edit':True,'dp':dp_form,'current':current,'job':job_list})
    else:
        return redirect('SignIn:signin')


def search(request):
    conn = db()
    message = ""
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            info = {
            'name' : form.cleaned_data['name'],
            'location' : form.cleaned_data['location'],
            'institute': form.cleaned_data['institution'],
            'interest': form.cleaned_data['interest'],
            'hall':form.cleaned_data['hall'],
            'term':form.cleaned_data['term'],
            'dept':form.cleaned_data['dept'],
            }
            
            if not info['name'] is '':
                info['name'] = '%' + info['name'].lower() + '%'
            if not info['location'] is '':
                info['location'] = '%' + info['location'].lower() + '%'
            if not info['interest'] is '':
                info['interest'] = '%' + info['interest'].lower() + '%'

            if not info['hall'] is '':
                info['hall'] = '%' + info['hall'].lower() + '%'
            if not info['term'] is '':
                info['term'] = '%' + info['term'].lower() + '%'
            if not info['dept'] is '':
                info['dept'] = '%' + info['dept'].lower() + '%'
            if not info['institute'] is '':
                info['institute'] = '%' + info['institute'].lower() + '%'
            values = {}
            print(info)
            c = conn.cursor()
            results = []
            sql = """ 
                SELECT DISTINCT STD_ID ,FULL_NAME,DEPT,FACEBOOK,TWITTER,GOOGLE_SCHOLAR,PHOTO,LINKEDIN FROM (
                """
            sql1 = """SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID)LEFT JOIN POSTGRAD 
                USING(STD_ID) LEFT JOIN EXPERTISE USING(STD_ID) LEFT JOIN (WORKS LEFT JOIN INSTITUTE USING(INSTITUTE_ID)) USING(STD_ID) 
                WHERE LOWER(FULL_NAME) LIKE :name OR LOWER(NICK_NAME) LIKE :name OR STD_ID LIKE :name 
                 INTERSECT """

            sql2 ="""SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD
                USING(STD_ID) LEFT JOIN EXPERTISE USING(STD_ID) LEFT JOIN (WORKS LEFT JOIN INSTITUTE USING(INSTITUTE_ID)) USING(STD_ID) 
                WHERE LOWER(PROFILE.COUNTRY) LIKE :location OR LOWER(PROFILE.CITY) LIKE :location OR LOWER(HOME_TOWN) LIKE :location 
                INTERSECT """

            sql3 ="""SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD
                USING(STD_ID) LEFT JOIN EXPERTISE USING(STD_ID) LEFT JOIN (WORKS LEFT JOIN INSTITUTE USING(INSTITUTE_ID)) USING(STD_ID) 
                WHERE LOWER(TOPIC) LIKE LOWER(:interest) 
                INTERSECT """

            sql4 ="""SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD
                USING(STD_ID) LEFT JOIN EXPERTISE USING(STD_ID) LEFT JOIN (WORKS LEFT JOIN INSTITUTE USING(INSTITUTE_ID)) USING(STD_ID) 
                WHERE LOWER(DEPT) LIKE LOWER(:dept) 
                INTERSECT """

            sql5 ="""SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD
                USING(STD_ID) LEFT JOIN EXPERTISE USING(STD_ID) LEFT JOIN (WORKS LEFT JOIN INSTITUTE USING(INSTITUTE_ID)) USING(STD_ID) 
                WHERE LOWER(HALL) LIKE LOWER(:hall) 
                INTERSECT """

            sql6 ="""SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD
                USING(STD_ID) LEFT JOIN EXPERTISE USING(STD_ID) LEFT JOIN (WORKS LEFT JOIN INSTITUTE USING(INSTITUTE_ID)) USING(STD_ID) 
                WHERE LOWER(LVL) LIKE LOWER(:lvl) 
                INTERSECT """
            sql7 ="""SELECT * from USER_TABLE LEFT JOIN PROFILE USING(STD_ID) LEFT JOIN UNDERGRAD USING(STD_ID) LEFT JOIN POSTGRAD
                USING(STD_ID) LEFT JOIN EXPERTISE USING(STD_ID) LEFT JOIN (WORKS LEFT JOIN INSTITUTE USING(INSTITUTE_ID)) USING(STD_ID) 
                WHERE LOWER(NAME) LIKE LOWER(:institute)
                INTERSECT """
                
            if not info['name'] is '':
                sql += sql1
                values['name'] = info['name']
            if not info['location'] is '':
                sql +=sql2
                values['location'] =info['location']
            if not info['interest'] is '':
                sql+=sql3
                values['interest'] = info['interest']
            if not info['dept'] is '':
                sql+=sql4
                values['dept'] = info['dept']
            if not info['hall'] is '':
                sql+=sql5
                values['hall'] = info['hall']
            if not info['term'] is '':
                sql+=sql6
                values['lvl'] = info['term']
            if not info['institute'] is '':
                sql+=sql7
                values['institute'] = info['institute']
            if sql.endswith('INTERSECT '):
                sql = sql[:-len('INTERSECT ')]+ ')'
                print(sql)
            else:
                msg = 'Please Type'
                return render(request,'Profile/search.html',{'form':form, 'msg' : message})
            rows =  c.execute(sql,values).fetchall()
            rows = rows

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
                                                 'city':data['CITY'],'country':data['COUNTRY'],'hometown':data['HOME_TOWN'],'about':data['ABOUT'],
                                                 'fb':data['FACEBOOK'],'twitter':data['TWITTER'],'linkedin':data['LINKEDIN'],'google':data['GOOGLE_SCHOLAR'],
                                                 'rg':data['RESEARCHGATE']})
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
                'hometown': form_signup.cleaned_data['hometown'],
                'about':form_signup.cleaned_data['about'],
                 'fb': form_signup.cleaned_data['fb'],
                'twitter' : form_signup.cleaned_data['twitter'],          
                'linkedin' :form_signup.cleaned_data['linkedin'],
                 'rg' : form_signup.cleaned_data['rg'],
                'google' :form_signup.cleaned_data['google'],
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
            print(profile)
            row =  c.execute(sql,{'std_id':user['std_id']}).fetchone()
            if row is None:
                sql = """ INSERT INTO PROFILE (STD_ID,HOUSE_NO,ROAD_NO,ZIP_CODE,CITY,COUNTRY,HOME_TOWN,ABOUT,FACEBOOK,TWITTER, LINKEDIN ,RESEARCHGATE, GOOGLE_SCHOLAR)
                        VALUES(:std_id,:house,:road,:zip,:city,:country,:hometown,:about,:fb,:twitter,:linkedin,:rg,:google)"""
                try:
                    c.execute(sql,profile)
                    conn.commit()
                    print('Inserted Profile')
                except cx_Oracle.IntegrityError:
                    message = "User already exists ..."
                    print('Error')
            else:
                sql = """ UPDATE PROFILE SET HOUSE_NO = :house,ROAD_NO = :road, ZIP_CODE = :zip,CITY = :city,COUNTRY = :country,HOME_TOWN = :hometown,ABOUT=:about,
                        FACEBOOK=:fb,TWITTER=:twitter, LINKEDIN=:linkedin, RESEARCHGATE=:rg,GOOGLE_SCHOLAR=:google
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
    sql = """SELECT  EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
    EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = :std_id GROUP BY EXPERTISE.TOPIC"""
    rows =  c.execute(sql,{'std_id':request.session.get('std_id')})
    skills = {}
    for row in rows:
        skills[row[0]] = row[1]
    job_form = JobForm()
#------------------------------------Job History---------------------------------
    sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID = :std_id ORDER BY FROM_ DESC"""
    rows =  c.execute(sql,{'std_id':request.session.get('std_id')})
    jobs = rows.fetchall()
    columnNames = [d[0] for d in c.description]
    job_list = []
    for job in jobs:
        try:
            job_list.append(dict(zip(columnNames,job)))
        except:
            print('NULL')

    return render(request,'Profile/edit.html',{'form':form_signup,'data':data,'jobs':job_list,'skills':skills, 'job':job_form,'msg' : message,'dp':dp_form,'expert':expertise,'skill_error':skill_error})

def visit_profile(request, std_id):
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
        sql = """ SELECT  EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
        EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = :std_id GROUP BY EXPERTISE.TOPIC"""
        rows =  c.execute(sql,{'std_id':std_id})
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
        print(skills)
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
                    c.execute(sql,{'std_id':user,"photo":filename})
                    conn.commit()
                    print('Inserted DP')
                except cx_Oracle.IntegrityError:
                    print('Error')
            else:
                sql = """ UPDATE PROFILE SET PHOTO=:photo
                            WHERE STD_ID = :std_id"""
                try:
                    c.execute(sql,{'photo':filename,'std_id':user})
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

def edit_job(request):
    if request.method == 'POST':
        if 'std_id' in request.session:
            print('Addding Jopbss')
            user = request.session['std_id']
            form = JobForm(request.POST)
            print('form')
            if form.is_valid():
                print('validated Job')
                name = form.cleaned_data['name']
                from_ = form.cleaned_data['from_']
                to_ = form.cleaned_data['to_']
                designation = form.cleaned_data['designation']
                conn = db()
                c = conn.cursor()
                sql = """SELECT INSTITUTE_ID FROM INSTITUTE WHERE NAME=:name"""
                ins_id =  c.execute(sql,{'name':name}).fetchone()
                print(ins_id)
                if ins_id is None:
                    print('No Institute')
                    return redirect('Profile:edit_profile')
                else:

                    sql = """ SELECT STD_ID,INSTITUTE_ID,FROM_ from WORKS WHERE STD_ID = :std_id AND INSTITUTE_ID = : ins_id AND FROM_ = :from_"""

                    row =  c.execute(sql,{'std_id':user,'ins_id':ins_id[0],'from_':from_}).fetchone()
                    if row is None:
                        sql = """ INSERT INTO WORKS (STD_ID,INSTITUTE_ID,FROM_,TO_,DESIGNATION)
                                VALUES(:std_id,:ins_id,:from_,:to_,UPPER(:designation))"""
                        try:
                            print({'std_id':user,'ins_id':ins_id[0],'from_':from_,'to_':to_,'designation':designation})
                            c.execute(sql,{'std_id':user,'ins_id':ins_id[0],'from_':from_,'to_':to_,'designation':designation})
                            conn.commit()
                            print('Inserted Job')
                        except cx_Oracle.IntegrityError:
                            print('Error')
                    else:
                        print('Exists')
                        job_error = "Already Exists"
    return redirect('Profile:edit_profile')


def delete_job(request):
    if request.method == 'POST':
        if 'std_id' in request.session:
            user = request.session['std_id']
            form = JobForm(request.POST)
            if form.is_valid():
                name = form.cleaned_data['name']
                from_ = form.cleaned_data['from_']
                designation = form.cleaned_data['designation']
                print('Accquired Delete Req')
                conn = db()
                c = conn.cursor()
                sql = """SELECT INSTITUTE_ID FROM INSTITUTE WHERE NAME=:name"""
                ins_id =  c.execute(sql,{'name':name}).fetchone()
                if ins_id is None:
                    print('No Institute')
                    return redirect('Profile:edit_profile')
                else:

                    sql = """ SELECT STD_ID,INSTITUTE_ID,FROM_,DESIGNATION from WORKS WHERE STD_ID = :std_id 
                    AND INSTITUTE_ID = : ins_id AND FROM_ = :from_ AND DESIGNATION=UPPER(:designation)"""
                    row =  c.execute(sql,{'std_id':user,'ins_id':ins_id[0],'from_':from_,'designation':designation}).fetchone()
                    print(row)
                    if row is not None:
                        sql = """ DELETE FROM WORKS WHERE STD_ID =:std_id AND INSTITUTE_ID = : ins_id AND FROM_ = :from_ AND DESIGNATION=UPPER(:designation)"""
                        try:
                            c.execute(sql,{'std_id':user,'ins_id':ins_id[0],'from_':from_,'designation':designation})
                            conn.commit()
                            print('Deleted Job')
                        except cx_Oracle.IntegrityError:
                            print('Error')
                    else:
                        print('Don\'t Exists')
                        job_error = "Already Exists"
    return redirect('Profile:edit_profile')
    
def endorse(request,std_id,topic):
    if 'std_id' in request.session:
        user = request.session['std_id']
        conn = db()
        c = conn.cursor()
        print({'user':user,'std_id':std_id,'topic':topic})
        sql = """ SELECT * from ENDORSE WHERE GIVER_ID = :user_id AND TAKER_ID =:std_id AND TOPIC =:topic"""
        row =  c.execute(sql,{'user_id':user,'std_id':std_id,'topic':topic}).fetchone()
        if row is None:
                sql = """ INSERT INTO ENDORSE (GIVER_ID,TAKER_ID,TOPIC)
                        VALUES(:user_id,:std_id,:topic)"""
                try:
                    c.execute(sql,{'user_id':user,'std_id':std_id,'topic':topic})
                    conn.commit()
                    print('Endorsed')
                except cx_Oracle.IntegrityError:
                    print('Error')
        else:
            print('Exists')
            skill_error = "Already Exists"

    return HttpResponseRedirect(reverse('Profile:visit_profile', args=(std_id,)))
            