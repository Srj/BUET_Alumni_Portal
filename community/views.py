from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from Alumni_Portal.utils import db,encrypt_password
from django.urls import reverse
import cx_Oracle
import datetime
from django.core.files.storage import FileSystemStorage
from datetime import date
import json
from django import forms


class DPForm(forms.Form):
    file = forms.FileField()

def home(request, my_groups_start, other_groups_start, comm_search_change):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()

        user_id = request.session.get('std_id')

        if comm_search_change == 0:
            # set to default
            request.session['comm_search_name'] = ''
            comm_search_name = ''
        elif comm_search_change == 1:
            #dont change
            comm_search_name = request.session['comm_search_name']
        elif comm_search_change == 2:
            #update
            comm_search_name = request.GET.get('comm_name_search')
            request.session['comm_search_name'] = comm_search_name
            

        #-------------------------------------Profile Card---------------------------------
        sql = """ SELECT * from USER_PROFILE WHERE STD_ID = :std_id"""
        row =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchone()
        columnNames = [d[0] for d in c.description]
        
        try:
            data = dict(zip(columnNames,row))
        except:
            print('Cannot Parse Profile')

        #-----------------------------------Skills------------------------------------
        sql = """ SELECT EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
                EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = :std_id GROUP BY EXPERTISE.TOPIC"""
        rows =  c.execute(sql,{'std_id':request.session.get('std_id')})
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
        dp_form = DPForm()

        #--------------------------------------Job History--------------------------------
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


        #=================================MY GROUPS INFO===================================
        if (comm_search_name is None) or (len(comm_search_name) == 0):
            sql = "SELECT COUNT(*) FROM COMM_MEMBERS WHERE USER_ID = :user_id"
            c.execute(sql, {"user_id":user_id})
        else:
            sql = '''SELECT COUNT(*) 
                    FROM COMM_MEMBERS CM, COMMUNITY C 
                    WHERE (CM.USER_ID = :user_id) AND (CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( INSTR(C.COMMUNITY_NAME, :comm_search_name) > 0 )'''
            c.execute(sql, {"comm_search_name":comm_search_name, "user_id":user_id})

        for row in c:
            num_my_comms = row[0]

        

        begin_my_comm = my_groups_start
        end_my_comm = (my_groups_start + 5) if (my_groups_start + 5) <= num_my_comms else num_my_comms+1
        my_comm_the_end = (num_my_comms == end_my_comm-1)
        my_comm_is_begin = (begin_my_comm == 1 )
        
        if (comm_search_name is None) or (len(comm_search_name) == 0):
            sql = ''' 
                    SELECT * 
                    FROM(
                            SELECT A.*, ROWNUM RNUM
                            FROM (
                                    SELECT C.COMMUNITY_ID, C.COMMUNITY_NAME, COUNT_COMM_MEMBER(C.COMMUNITY_ID) AS NUM_MEMBERS, TIME_DIFF(C.DATE_OF_CREATION) 
                                    FROM COMMUNITY C, COMM_MEMBERS CM 
                                    WHERE (CM.USER_ID = :user_id) AND (CM.COMMUNITY_ID = C.COMMUNITY_ID)
                                    ORDER BY COUNT_COMM_MEMBER(C.COMMUNITY_ID) DESC, C.DATE_OF_CREATION 
                                ) A
                            WHERE ROWNUM < :end_community
                        )
                    WHERE RNUM >= :begin_community'''

            c.execute(sql, {"end_community":end_my_comm, "begin_community":begin_my_comm, "user_id":user_id})
        else:
            sql = ''' 
                    SELECT * 
                    FROM(
                            SELECT A.*, ROWNUM RNUM
                            FROM (
                                    SELECT C.COMMUNITY_ID, C.COMMUNITY_NAME, COUNT_COMM_MEMBER(C.COMMUNITY_ID) AS NUM_MEMBERS, TIME_DIFF(C.DATE_OF_CREATION) 
                                    FROM COMMUNITY C, COMM_MEMBERS CM 
                                    WHERE (CM.USER_ID = :user_id) AND (CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( INSTR(C.COMMUNITY_NAME, :comm_search_name) > 0 )
                                    ORDER BY COUNT_COMM_MEMBER(C.COMMUNITY_ID) DESC, C.DATE_OF_CREATION 
                                ) A
                            WHERE ROWNUM < :end_community
                        )
                    WHERE RNUM >= :begin_community'''

            c.execute(sql, {"end_community":end_my_comm, "begin_community":begin_my_comm, "user_id":user_id, "comm_search_name":comm_search_name})
        
        my_communities_infos = []
        for row in c:
            community_dict = {}
            community_dict['community_id'] = row[0]
            community_dict['community_name'] = row[1]
            community_dict["num_members"] = row[2]
            community_dict["created"] = row[3]

            my_communities_infos.append(community_dict)


        #================================Groups I am not in (joinable groups) =======================================

        if (comm_search_name is None) or (len(comm_search_name) == 0):
            sql = "SELECT COUNT(*) FROM COMM_MEMBERS WHERE USER_ID <> :user_id"
            c.execute(sql, {"user_id":user_id})
        else:
            sql = '''SELECT COUNT(*) 
                    FROM COMM_MEMBERS CM, COMMUNITY C 
                    WHERE (CM.USER_ID <> :user_id) AND (CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( INSTR(C.COMMUNITY_NAME, :comm_search_name) > 0 )'''
            c.execute(sql, {"comm_search_name":comm_search_name, "user_id":user_id})

        for row in c:
            num_other_comms = row[0]
        
        
        
        
        begin_other_comm = other_groups_start
        end_other_comm = (other_groups_start + 5) if (other_groups_start + 5) <= num_other_comms else num_other_comms+1
        other_comm_the_end = (num_other_comms == end_other_comm-1)
        other_comm_is_begin = (begin_other_comm == 1 )

        if (comm_search_name is None) or (len(comm_search_name) == 0):
            sql = ''' 
                    SELECT * 
                    FROM(
                            SELECT A.*, ROWNUM RNUM
                            FROM (
                                    SELECT C.COMMUNITY_ID, C.COMMUNITY_NAME, COUNT_COMM_MEMBER(C.COMMUNITY_ID) AS NUM_MEMBERS, TIME_DIFF(C.DATE_OF_CREATION) 
                                    FROM COMMUNITY C, COMM_MEMBERS CM 
                                    WHERE (CM.USER_ID <> :user_id) AND (CM.COMMUNITY_ID = C.COMMUNITY_ID)
                                    ORDER BY COUNT_COMM_MEMBER(C.COMMUNITY_ID) DESC, C.DATE_OF_CREATION 
                                ) A
                            WHERE ROWNUM < :end_community
                        )
                    WHERE RNUM >= :begin_community'''

            c.execute(sql, {"end_community":end_other_comm, "begin_community":begin_other_comm, "user_id":user_id})
        else:
            sql = ''' 
                    SELECT * 
                    FROM(
                            SELECT A.*, ROWNUM RNUM
                            FROM (
                                    SELECT C.COMMUNITY_ID, C.COMMUNITY_NAME, COUNT_COMM_MEMBER(C.COMMUNITY_ID) AS NUM_MEMBERS, TIME_DIFF(C.DATE_OF_CREATION) 
                                    FROM COMMUNITY C, COMM_MEMBERS CM 
                                    WHERE (CM.USER_ID <> :user_id) AND (CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( INSTR(C.COMMUNITY_NAME, :comm_search_name) > 0 )
                                    ORDER BY COUNT_COMM_MEMBER(C.COMMUNITY_ID) DESC, C.DATE_OF_CREATION 
                                ) A
                            WHERE ROWNUM < :end_community
                        )
                    WHERE RNUM >= :begin_community'''

            

            c.execute(sql, {"end_community":end_other_comm, "begin_community":begin_other_comm, "user_id":user_id, "comm_search_name":comm_search_name})

        other_communities_infos = []
        for row in c:
            print(row)
            community_dict = {}
            community_dict['community_id'] = row[0]
            community_dict['community_name'] = row[1]
            community_dict["num_members"] = row[2]
            community_dict["created"] = row[3]

            other_communities_infos.append(community_dict)



        show = {
            'data':data,
            'skills':skills,
            'edit':True,
            'dp':dp_form,
            'job':job_list,
            "my_communitiy_info_list":my_communities_infos,
            "is_my_comm_begin":my_comm_is_begin,
            "is_my_comm_end":my_comm_the_end,
            "next_my_comm":end_my_comm,
            "prev_my_comm":(begin_my_comm-5) if begin_my_comm > 5 else 0,
            "orig_my_grp_strt":my_groups_start,
            "other_community_info_list":other_communities_infos,
            "is_other_comm_begin":other_comm_is_begin,
            "is_other_comm_end":other_comm_the_end,
            "next_other_comm":end_other_comm,
            "prev_other_comm":(begin_other_comm-5) if begin_other_comm > 5 else 0,
            "orig_other_grp_strt":other_groups_start,
            "search_comm_name":comm_search_name
        }
        return render(request, 'community/home.html', show)
    else:
        return redirect('SignIn:signin')



def create_community(request):
    if "std_id" in request.session:

        conn = db()
        c = conn.cursor()

        user_id = request.session.get('std_id')

        #-------------------------------------Profile Card---------------------------------
        sql = """ SELECT * from USER_PROFILE WHERE STD_ID = :std_id"""
        row =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchone()
        columnNames = [d[0] for d in c.description]
        
        try:
            data = dict(zip(columnNames,row))
        except:
            print('Cannot Parse Profile')

        #-----------------------------------Skills------------------------------------
        sql = """ SELECT EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
                EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = :std_id GROUP BY EXPERTISE.TOPIC"""
        rows =  c.execute(sql,{'std_id':request.session.get('std_id')})
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
        dp_form = DPForm()

        #--------------------------------------Job History--------------------------------
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

        show = {
            'data':data,
            'skills':skills,
            'edit':True,
            'dp':dp_form,
            'job':job_list,
            'unfilled':False
        }


        return render(request, "community/create_community.html", show)
    else:
        return redirect('SignIn:signin')


def create_comm_upload(request):
    if "std_id" in request.session:

        conn = db()
        c = conn.cursor()

        user_id = request.session.get('std_id')


        community_name  = request.GET.get('community_name')
        description = request.GET.get('description')
        criteria = request.GET.get('criteria')
        

        unfilled_data = []
        filled_data = {}
        for name in ["community_name", "description", "criteria"]:
            value = request.GET.get(name)
            if len(value) == 0:
                unfilled_data.append(name)
            else:
                filled_data[name] = value

        print(unfilled_data)
        print(filled_data)

        if len(unfilled_data) > 0:
            #-------------------------------------Profile Card---------------------------------
            sql = """ SELECT * from USER_PROFILE WHERE STD_ID = :std_id"""
            row =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchone()
            columnNames = [d[0] for d in c.description]
            
            try:
                data = dict(zip(columnNames,row))
            except:
                print('Cannot Parse Profile')

            #-----------------------------------Skills------------------------------------
            sql = """ SELECT EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
                    EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = :std_id GROUP BY EXPERTISE.TOPIC"""
            rows =  c.execute(sql,{'std_id':request.session.get('std_id')})
            skills = {}
            for row in rows:
                skills[row[0]] = row[1]
            dp_form = DPForm()

            #--------------------------------------Job History--------------------------------
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

            show = {
                'data':data,
                'skills':skills,
                'edit':True,
                'dp':dp_form,
                'job':job_list,
                'unfilled':True,
                'unfilled_list':unfilled_data,
                'filled_data':filled_data
            }
            return render(request, "community/create_community.html", show)
        else:
            sql = '''INSERT INTO COMMUNITY (COMMUNITY_NAME, DESCRIPTION, CRITERIA, DATE_OF_CREATION) VALUES (:community_name, :description, :criteria, SYSDATE)  '''
            c.execute(sql, {"community_name":community_name, "description":description, "criteria":criteria})
            c.execute("SELECT COMMUNITY_ID FROM (SELECT COMMUNITY_ID FROM COMMUNITY ORDER BY COMMUNITY_ID DESC) WHERE ROWNUM=1")
            for row in c:
                comm_id = row[0]
            sql = '''INSERT INTO MODERATOR VALUES (:comm_id, :user_id) '''
            c.execute(sql, {"comm_id":comm_id, "user_id":user_id})
            sql = '''INSERT INTO COMM_MEMBERS VALUES (:comm_id, :user_id, SYSDATE) '''
            c.execute(sql, {"comm_id":comm_id, "user_id":user_id})
            c.execute("COMMIT")

            return HttpResponseRedirect(reverse('community:home'))
    else:
        return redirect('SignIn:signin')

