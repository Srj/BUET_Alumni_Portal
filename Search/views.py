from django.shortcuts import render
from .forms import SearchForm
from Alumni_Portal.utils import db
# Create your views here.


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
            c = conn.cursor()
            results = []
            sql = """ 
                SELECT DISTINCT * FROM USER_PROFILE WHERE STD_ID IN (
                """
            sql1 = """SELECT STD_ID from USER_TABLE WHERE LOWER(FULL_NAME) LIKE :name OR LOWER(NICK_NAME) LIKE :name OR STD_ID LIKE :name 
                 INTERSECT """

            sql2 ="""SELECT STD_ID from  PROFILE WHERE LOWER(PROFILE.COUNTRY) LIKE :location OR LOWER(PROFILE.CITY) LIKE :location 
                    OR LOWER(HOME_TOWN) LIKE :location 
                INTERSECT """

            sql3 ="""SELECT STD_ID from EXPERTISE WHERE LOWER(TOPIC) LIKE LOWER(:interest) 
                INTERSECT """

            sql4 ="""SELECT STD_ID from PROFILE WHERE LOWER(DEPT) LIKE LOWER(:dept) 
                INTERSECT """

            sql5 ="""SELECT STD_ID from PROFILE WHERE LOWER(HALL) LIKE LOWER(:hall) 
                INTERSECT """

            sql6 ="""SELECT STD_ID from PROFILE WHERE LOWER(LVL) LIKE LOWER(:lvl) 
                INTERSECT """
            sql7 ="""SELECT STD_ID from WORKS LEFT JOIN INSTITUTE USING(INSTITUTE_ID)  
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
                return render(request,'Search/search.html',{'form':form, 'msg' : message})
            rows =  c.execute(sql,values).fetchall()
            rows = rows

            print("Result Found : " + str(len(rows)))
            if len(rows) ==  0 :
                message = "No Result Found"
                return render(request,'Search/search.html',{'form':form, 'msg' : message})
            else:
                for row in rows:
                    columnNames = [d[0] for d in c.description]
                    data = (zip(columnNames,row))
                    results.append(dict(data))
                return render(request,'Search/search.html',{'form':form, 'msg' : message,'data':results,'count':len(results)})
                    
    else:
        form = SearchForm()
    return render(request,'Search/search.html',{'form':form, 'msg' : message})