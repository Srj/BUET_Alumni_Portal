from django.shortcuts import render,redirect
from django.http import HttpResponse,HttpResponseRedirect
from Alumni_Portal.utils import db,encrypt_password
from django.urls import reverse
import cx_Oracle
import datetime
from .forms import EditForm,DPForm,ExpertForm,SearchForm,JobForm
from django.core.files.storage import FileSystemStorage


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
        
        return render(request,'Timeline/index.html',{'data':data,'skills':skills,'edit':True,'dp':dp_form,'current':current,'job':job_list})
    else:
        return redirect('SignIn:signin')
