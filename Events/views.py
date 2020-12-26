from django.shortcuts import render
from django.http import HttpResponse
from django.http import Http404
from django.shortcuts import render,redirect
from django.core.exceptions import ValidationError
from django import forms
from django.http import HttpResponse,HttpResponseRedirect
from django.shortcuts import render
from .forms import EventForm, CreateEventForm
from Alumni_Portal.utils import db
from django.urls import reverse
from psycopg2 import IntegrityError
# Create your views here.

def index(request):
    conn = db()
    message = ""
    if request.method == 'POST':
        form = EventForm(request.POST)
        if form.is_valid():
            info = {
            'text': form.cleaned_data['text'],
            'name' : form.cleaned_data['name'],
            'location' : form.cleaned_data['location'],
            'time_period' : form.cleaned_data['time'],
            
            }
            
            if not info['name'] is '':
                info['name'] = '%' + info['name'].lower() + '%'
            if not info['location'] is '':
                info['location'] = '%' + info['location'].lower() + '%'
            if not info['text'] is '':
                info['text'] = '%' + info['text'].lower() + '%'

            values = {}
            c = conn.cursor()
            results = []
            sql = """ 
                SELECT DISTINCT * FROM EVENT WHERE EVENT_ID IN (
                """
            sql1 = """SELECT EVENT_ID from EVENT WHERE LOWER(DESCRIPTION) LIKE %(text)s OR LOWER(EVENT_NAME) LIKE %(text)s OR  LOWER(LOCATION) LIKE %(text)s
                 INTERSECT """

            sql2 ="""SELECT EVENT_ID from EVENT WHERE LOWER(EVENT_NAME) LIKE %(name)s
                INTERSECT """

            sql3 ="""SELECT EVENT_ID from EVENT WHERE LOWER(LOCATION) LIKE %(location)s
                INTERSECT """

            sql4 ="""SELECT EVENT_ID from EVENT WHERE to_date(%(time_period)s,'yyyy-mm-dd') BETWEEN EVENT_START AND EVENT_END
                INTERSECT """

           
                
            if not info['text'] is '':
                sql += sql1
                values['text'] = info['text']
            if not info['name'] is '':
                sql +=sql2
                values['name'] =info['name']
            if not info['location'] is '':
                sql+=sql3
                values['location'] = info['location']
            if not info['time_period'] is None:
                sql+=sql4
                values['time_period'] = info['time_period']

            if sql.endswith('INTERSECT '):
                sql = sql[:-len('INTERSECT ')]+ ')'
                print(sql)                
            else:
                msg = 'Please Type'
                return render(request,'Events/index.html',{'form':form, 'msg' : message})
            c.execute(sql,values)
            rows = c.fetchall()
            print(rows)

            
            if len(rows) ==  0 :
                message = "No Result Found"
                return render(request,'Events/index.html',{'form':form, 'msg' : message})
            else:
                for row in rows:
                    print(row)
                    columnNames = [d[0].upper() for d in c.description]
                    data = (zip(columnNames,row))
                    results.append(dict(data))
                    print(results)
                return render(request,'Events/index.html',{'form':form, 'msg' : message,'data':results,'count':len(results)})
                    
    else:
        form = EventForm()
        sql = """SELECT DISTINCT * FROM EVENT"""
        c = conn.cursor()
        c.execute(sql)
        rows = c.fetchall()
        results = []
        print("Result Found : " + str(len(rows)))
        if len(rows) ==  0 :
            message = "No Result Found"
            return render(request,'Events/index.html',{'form':form, 'msg' : message})
        else:
            for row in rows:
                columnNames = [d[0].upper() for d in c.description]
                data = (zip(columnNames,row))
                results.append(dict(data))
        return render(request,'Events/index.html',{'form':form,'data':results, 'msg' : message})

def visit_event(request,event_id):
    if 'std_id' in request.session:
        data =None
        conn = db()
        c = conn.cursor()
        sql = """SELECT * from EVENT WHERE EVENT_ID = %(event_id)s"""
        c.execute(sql,{'event_id':event_id})
        row = c.fetchone()
        columnNames = [d[0].upper() for d in c.description]
        print(row)
        try:
            data = dict(zip(columnNames,row))
        except:
            print('cannot Visit Event')
        sql = """SELECT COUNT(USER_ID) from EVENT_PARTICIPATES WHERE EVENT_ID = %(event_id)s"""
        c.execute(sql,{'event_id':event_id})
        row = c.fetchone()
        joined = row[0]
        print(row)
            
        sql = """SELECT FULL_NAME from USER_TABLE WHERE STD_ID = (SELECT USER_ID FROM EVENT_ARRANGE WHERE EVENT_ID = %(event_id)s)"""
        c.execute(sql,{'event_id':event_id})
        row = c.fetchone()
        columnNames = [d[0] for d in c.description]
        print(row)
        sql = """SELECT * from EVENT_PARTICIPATES WHERE EVENT_ID = %(event_id)s AND USER_ID = %(std_id)s"""
        c.execute(sql,{'event_id':event_id,'std_id':request.session['std_id']})
        user_join = c.fetchone()
       
        return render(request,'Events/Events.html',{'data':data,'Organizer':row[0],'Joined':joined, 'user_join':user_join})


        

def make_event(request):
    conn = db()
    message = ""
    if request.method == 'POST':
        form = CreateEventForm(request.POST)
        if form.is_valid():
            info = {
                'name': form.cleaned_data['name'],
                'location':form.cleaned_data['location'],
                'start_date': form.cleaned_data['start_date'].strftime('%Y-%m-%d'),
                'end_date': form.cleaned_data['end_date'].strftime('%Y-%m-%d'),
                'description': form.cleaned_data['about']
            }
            print(info)

            c = conn.cursor()
            sql = """ INSERT INTO EVENT (EVENT_NAME,LOCATION,EVENT_START,EVENT_END,DESCRIPTION)
                        VALUES(%(name)s,%(location)s,to_date(%(start_date)s,'yyyy-mm-dd'),to_date(%(end_date)s,'yyyy-mm-dd'),%(description)s)"""
            try:
                c.execute(sql,info)
                conn.commit()
                print('Registered Event')
            except IntegrityError:
                message = "Event already exists ..."
                print('"Event already exists ...')

            c = conn.cursor()
            sql = """ INSERT INTO EVENT_ARRANGE (EVENT_ID ,USER_ID)
                        VALUES((SELECT EVENT_ID FROM EVENT WHERE EVENT_NAME = %(name)s), %(std_id)s)"""
            c.execute(sql,{'std_id':request.session['std_id'],'name':form.cleaned_data['name']})
            conn.commit()
            conn.close()
            print('Registered Event')
            return redirect('SignIn:signin')
            
    else:
        form = CreateEventForm()
    return render(request,'Events/create.html',{'form':form, 'msg' : message})

def join_event(request,event_id):
    if 'std_id' in request.session:
        conn = db()
        message = ""
        c = conn.cursor()
        try:
            sql = """ INSERT INTO EVENT_PARTICIPATES (EVENT_ID ,USER_ID)
                        VALUES(%(event_id)s, %(std_id)s)"""
            c.execute(sql,{'std_id':request.session['std_id'],'event_id':event_id})
            conn.commit()
            conn.close()
            print('Joined Event')
        except IntegrityError:
            msg = 'Already Joined'
        return HttpResponseRedirect(reverse('Events:visit_event', args=(event_id,)))


