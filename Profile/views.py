from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from Alumni_Portal.utils import db,encrypt_password
from django.urls import reverse
from psycopg2 import IntegrityError
import datetime
from .forms import EditForm,DPForm,ExpertForm,JobForm
from django.core.files.storage import FileSystemStorage
# Create your views here.

skill_error = None
  
def index(request):
    if 'std_id' in request.session:
        std_id = request.session['std_id']
        data =None
        conn = db()
        c = conn.cursor()
        #------------------------Fetch Profile Information-----------------------------
        sql = """ SELECT * from USER_PROFILE WHERE STD_ID = %(std_id)s"""
        c.execute(sql,{'std_id':std_id})
        row = c.fetchone()
        columnNames = [d[0].upper() for d in c.description]
        
        try:
            data = dict(zip(columnNames,row))
        except:
            print('Cannot Parse Profile')

        #-----------------------------------Skills------------------------------------
        sql = """ SELECT EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
    EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = %(std_id)s GROUP BY EXPERTISE.TOPIC"""
        c.execute(sql,{'std_id':std_id})
        rows = c.fetchall()
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
        dp_form = DPForm()

        #--------------------------------------Job History--------------------------------
        sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID = %(std_id)s ORDER BY FROM_ DESC"""
        rows =  c.execute(sql,{'std_id':std_id})
        jobs = c.fetchall()
        columnNames = [d[0].upper() for d in c.description]
        job_list = []
        for job in jobs:
            try:
                job_list.append(dict(zip(columnNames,job)))
            except:
                print('NULL')
        print(data)
        # return render(request,'Profile/profile.html',{'data':data,'skills':skills,'edit':True,'dp':dp_form,'job':job_list})
        return redirect('SignIn:signin')
    else:
        return redirect('SignIn:signin')








def edit(request):
    conn = db()
    c = conn.cursor()
    message = ""
    sql = """SELECT * from USER_PROFILE WHERE STD_ID = %(std_id)s"""
    c.execute(sql,{'std_id':request.session.get('std_id')})
    row = c.fetchone()
    columnNames = [d[0].upper() for d in c.description]
    data = dict(zip(columnNames,row))
    print(data)
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
            'birthdate': form_signup.cleaned_data['birthdate'].strftime('%Y-%m-%d'),
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
            sql = """ UPDATE USER_TABLE SET FULL_NAME = %(fullname)s, NICK_NAME = %(nickname)s,EMAIL=%(email)s,MOBILE=%(mobile)s,DATE_OF_BIRTH=to_date(%(birthdate)s,'yyyy-mm-dd') WHERE STD_ID=%(std_id)s"""
            try:
                c.execute(sql,user)
                conn.commit()
                print('Updated User')
            except IntegrityError:
                message = "User already exists ..."
                print('Error Updating User')
            #-----------------Update Profile---------------------
            sql = """ SELECT * from PROFILE WHERE STD_ID = %(std_id)s"""
            print(profile)
            c.execute(sql,{'std_id':user['std_id']})
            row = c.fetchone()
            if row is None:
                sql = """ INSERT INTO PROFILE (STD_ID,HOUSE_NO,ROAD_NO,ZIP_CODE,CITY,COUNTRY,HOME_TOWN,ABOUT,FACEBOOK,TWITTER, LINKEDIN ,RESEARCHGATE, GOOGLE_SCHOLAR)
                        VALUES(%(std_id)s,%(house)s,%(road)s,%(zip)s,%(city)s,%(country)s,%(hometown)s,%(about)s,%(fb)s,%(twitter)s,%(linkedin)s,%(rg)s,%(google)s)"""
                try:
                    c.execute(sql,profile)
                    conn.commit()
                    print('Inserted Profile')
                except  IntegrityError:
                    message = "User already exists ..."
                    print('Error Updating Profile 1')
            else:
                sql = """ UPDATE PROFILE SET HOUSE_NO = %(house)s,ROAD_NO = %(road)s, ZIP_CODE = %(zip)s,CITY = %(city)s,COUNTRY = %(country)s,HOME_TOWN = %(hometown)s,ABOUT=%(about)s,
                        FACEBOOK=%(fb)s,TWITTER=%(twitter)s, LINKEDIN=%(linkedin)s, RESEARCHGATE=%(rg)s,GOOGLE_SCHOLAR=%(google)s
                        WHERE STD_ID = %(std_id)s"""
                try:
                    c.execute(sql,profile)
                    conn.commit()
                    print('Updated User')
                except  IntegrityError:
                    message = "User already exists ..."
                    print('Error Updating Profile 2')

            #------------------------Update Undergrad----------------------
            sql = """ SELECT * from UNDERGRAD WHERE STD_ID = %(std_id)s"""
            c.execute(sql,{'std_id':user['std_id']})
            row = c.fetchone()
            if row is None:
                sql = """ INSERT INTO UNDERGRAD (STD_ID,HALL,DEPT,LVL,TERM)
                        VALUES(%(std_id)s,%(hall)s,%(dept)s,%(lvl)s,%(term)s)"""
                try:
                    c.execute(sql,undergrad)
                    conn.commit()
                    print('Inserted UnderGrad')
                except  IntegrityError:
                    message = "User already exists ..."
                    print('Error Updating Undergrad 1')
            else:
                sql = """ UPDATE UNDERGRAD SET HALL =%(hall)s,DEPT=%(dept)s,LVL=%(lvl)s,TERM=%(term)s
                        WHERE STD_ID =%(std_id)s"""
                try:
                    c.execute(sql,undergrad)
                    conn.commit()
                    print('Updated Undergrad')
                except  IntegrityError:
                    message = "User already exists ..."
                    print('Error Updating Undergrad 2')

            #-----------------Update Postgrad ----------------------------
            sql = """ SELECT * from POSTGRAD WHERE STD_ID = %(std_id)s"""
            c.execute(sql,{'std_id':user['std_id']})
            row = c.fetchone()
            if row is None:
                sql = """ INSERT INTO POSTGRAD (STD_ID,MSC,PHD)
                        VALUES(%(std_id)s,%(msc)s,%(phd)s)"""
                try:
                    c.execute(sql,postgrad)
                    conn.commit()
                    print('Inserted PostGrad')
                except  IntegrityError:
                    message = "User already exists ..."
                    print('Error Updating PostGrad 1')
            else:
                sql = """ UPDATE POSTGRAD SET MSC=%(msc)s,PHD=%(phd)s
                        WHERE STD_ID = %(std_id)s"""
                try:
                    c.execute(sql,postgrad)
                    conn.commit()
                    print('Updated PostGrad')
                except  IntegrityError:
                    message = "User already exists ..."
                    print('Error Updating PostGrad 2')
                return redirect('Profile:profile')
        else:
            print('Error While Editing Profile')
    expertise = ExpertForm()
    sql = """SELECT  EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
    EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = %(std_id)s GROUP BY EXPERTISE.TOPIC"""
    c.execute(sql,{'std_id':request.session.get('std_id')})
    rows = c.fetchall()
    skills = {}
    for row in rows:
        skills[row[0]] = row[1]
    job_form = JobForm()
#------------------------------------Job History---------------------------------
    sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID = %(std_id)s ORDER BY FROM_ DESC"""
    c.execute(sql,{'std_id':request.session.get('std_id')})
    jobs = c.fetchall()
    columnNames = [d[0].upper() for d in c.description]
    job_list = []
    for job in jobs:
        try:
            job_list.append(dict(zip(columnNames,job)))
        except:
            print('Cannot Parse Job')

    return render(request,'Profile/edit.html',{'form':form_signup,'data':data,'jobs':job_list,'skills':skills, 'job':job_form,'msg' : message,'dp':dp_form,'expert':expertise,'skill_error':skill_error})

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
        sql = """SELECT * from USER_PROFILE WHERE STD_ID = %(std_id)s"""
        c.execute(sql,{'std_id':std_id})
        row = c.fetchone()
        columnNames = [d[0].upper() for d in c.description]
        print(row)
        try:
            data = dict(zip(columnNames,row))
        except:
            print('cannot Visit User')
        #---------------------------------Expertise with Endorse Count----------------------------------
        sql = """ SELECT  EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
        EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = %(std_id)s GROUP BY EXPERTISE.TOPIC"""
        c.execute(sql,{'std_id':std_id})
        rows = c.fetchall()
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
        print(skills)

        #Job----------------------------------
        sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID =%(std_id)s ORDER BY FROM_ DESC"""
        c.execute(sql,{'std_id':std_id})
        jobs = c.fetchall()
        columnNames = [d[0].upper() for d in c.description]
        job_list = []
       
        for job in jobs:
            try:
                job_list.append(dict(zip(columnNames,job)))
            except:
                print('Cannot Parse Job')
        print(job_list)
    return render(request,'Profile/profile.html',{'data':data,'skills':skills,'edit':enable_edit,'job':job_list})



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
            sql = """ SELECT * from PROFILE WHERE STD_ID = %(std_id)s"""
            c.execute(sql,{'std_id':user})
            row = c.fetchone()
            if row is None:
                sql = """ INSERT INTO PROFILE (STD_ID,PHOTO)
                        VALUES(%(std_id)s,%(photo)s)"""
                try:
                    c.execute(sql,{'std_id':user,"photo":filename})
                    conn.commit()
                    print('Inserted DP')
                except  IntegrityError:
                    print('Error')
            else:
                sql = """ UPDATE PROFILE SET PHOTO=%(photo)s
                            WHERE STD_ID = %(std_id)s"""
                try:
                    c.execute(sql,{'photo':filename,'std_id':user})
                    conn.commit()
                    print('Updated DP')
                except  IntegrityError:
                    message = "User already exists ..."
                    print('Error Updating DP')
    return redirect('Profile:profile')



def edit_expertise(request):
    if request.method == 'POST':
        if 'std_id' in request.session:
            user = request.session['std_id']
            form = ExpertForm(request.POST)
            print(form)
            if form.is_valid():
                topic = form.cleaned_data['topic']
                conn = db()
                c = conn.cursor()
                sql = """ SELECT TOPIC from EXPERTISE WHERE STD_ID = %(std_id)s AND TOPIC =%(topic)s"""
                c.execute(sql,{'std_id':user,'topic':topic})
                row = c.fetchone()
                if row is None:
                    sql = """ INSERT INTO EXPERTISE (STD_ID,TOPIC)
                            VALUES(%(std_id)s,%(topic)s)"""
                    try:
                        c.execute(sql,{'std_id':user,"topic":topic})
                        conn.commit()
                        print('Inserted Skill')
                    except  IntegrityError:
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
            print(form)
            if form.is_valid():
                topic = form.cleaned_data['topic']
                conn = db()
                c = conn.cursor()
                sql = """ SELECT TOPIC from EXPERTISE WHERE STD_ID = %(std_id)s AND TOPIC =%(topic)s"""
                c.execute(sql,{'std_id':user,'topic':topic})
                row = c.fetchone()
                print(row)
                if not row is None:
                    sql = """ DELETE FROM EXPERTISE WHERE STD_ID =%(std_id)s AND TOPIC=%(topic)s"""
                    # try:
                    c.execute(sql,{'std_id':user,"topic":topic})
                    conn.commit()
                    print('Deleted Skill')
                    # except  IntegrityError:
                        # print('Error Deleting Skill')
                    
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
                sql = """SELECT INSTITUTE_ID FROM INSTITUTE WHERE NAME=%(name)s"""
                c.execute(sql,{'name':name})
                ins_id = c.fetchone()
                print(ins_id)
                if ins_id is None:
                    print('No Institute')
                    sql = "INSERT INTO INSTITUTE (NAME) VALUES( %(name)s);"
                    c.execute(sql,{'name':name})
                    conn.commit()

                sql = """SELECT INSTITUTE_ID FROM INSTITUTE WHERE NAME=%(name)s"""
                c.execute(sql,{'name':name})
                ins_id = c.fetchone()

                sql = """ SELECT STD_ID,INSTITUTE_ID,FROM_ from WORKS WHERE STD_ID =%(std_id)s AND INSTITUTE_ID = %(ins_id)s AND FROM_ =%(from_)s"""

                c.execute(sql,{'std_id':user,'ins_id':ins_id,'from_':from_})
                row = c.fetchone()
                if row is None:
                    sql = """ INSERT INTO WORKS (STD_ID,INSTITUTE_ID,FROM_,TO_,DESIGNATION)
                            VALUES(%(std_id)s,%(ins_id)s,%(from_)s,%(to_)s,UPPER(%(designation)s))"""
                    # try:
                    print({'std_id':user,'ins_id':ins_id,'from_':from_,'to_':to_,'designation':designation})
                    c.execute(sql,{'std_id':user,'ins_id':ins_id,'from_':from_,'to_':to_,'designation':designation})
                    conn.commit()
                    print('Inserted Job')
                    # except  IntegrityError:
                        # print('Error')
                else:
                    print('Exists')
                    job_error = "Already Exists"
    return redirect('Profile:edit_profile')




def delete_job(request):
    if request.method == 'POST':
        if 'std_id' in request.session:
            user = request.session['std_id']
            form = JobForm(request.POST)
            print(form)
            if form.is_valid():
                name = form.cleaned_data['name']
                from_ = form.cleaned_data['from_'].strftime('%Y-%m-%d')
                designation = form.cleaned_data['designation']
                print('Accquired Delete Req')
                conn = db()
                c = conn.cursor()
                sql = """SELECT INSTITUTE_ID FROM INSTITUTE WHERE NAME=%(name)s"""
                c.execute(sql,{'name':name})
                ins_id = c.fetchone()
                if ins_id is None:
                    print('No Institute')
                    return redirect('Profile:edit_profile')
                else:
                    sql = """ SELECT STD_ID,INSTITUTE_ID,FROM_,DESIGNATION from WORKS WHERE STD_ID =%(std_id)s 
                    AND INSTITUTE_ID = %(ins_id)s AND FROM_ =%(from_)s AND DESIGNATION=UPPER(%(designation)s)"""
                    c.execute(sql,{'std_id':user,'ins_id':ins_id[0],'from_':from_,'designation':designation})
                    row = c.fetchone()
                    print(row)
                    if row is not None:
                        sql = """ DELETE FROM WORKS WHERE STD_ID =%(std_id)s AND INSTITUTE_ID = %(ins_id)s AND FROM_ = TO_DATE(%(from_)s,'YYYY-MM-DD') AND DESIGNATION=UPPER(%(designation)s)"""
                        try:
                            c.execute(sql,{'std_id':user,'ins_id':ins_id[0],'from_':from_,'designation':designation})
                            conn.commit()
                            print('Deleted Job')
                        except  IntegrityError:
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
        sql = """ SELECT * from ENDORSE WHERE GIVER_ID = %(user_id)s AND TAKER_ID =%(std_id)s AND TOPIC =%(topic)s"""
        c.execute(sql,{'user_id':user,'std_id':std_id,'topic':topic})
        row = c.fetchone()
        if row is None:
                sql = """ INSERT INTO ENDORSE (GIVER_ID,TAKER_ID,TOPIC)
                        VALUES(%(user_id)s,%(std_id)s,%(topic)s)"""
                try:
                    c.execute(sql,{'user_id':user,'std_id':std_id,'topic':topic})
                    conn.commit()
                    print('Endorsed')
                except  IntegrityError:
                    print('Error in Endorsing')
        else:
            print('Endorse Exists')
            skill_error = "Already Exists"

    return HttpResponseRedirect(reverse('Profile:visit_profile', args=(std_id,)))
            