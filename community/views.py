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
        '''SELECT COMMUNITY_ID, COMMUNITY_NAME, COUNT_COMM_MEMBER(COMMUNITY_ID) , TIME_DIFF(DATE_OF_CREATION)
        FROM COMMUNITY
        WHERE COMMUNITY_ID IN ( SELECT DISTINCT C.COMMUNITY_ID FROM COMMUNITY C, COMM_MEMBERS CM WHERE ( CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( CM.COMMUNITY_ID NOT IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = :user_id) ) )

        SELECT COMMUNITY_ID, COMMUNITY_NAME, COUNT_COMM_MEMBER(COMMUNITY_ID) , TIME_DIFF(DATE_OF_CREATION)
        FROM COMMUNITY
        WHERE COMMUNITY_ID IN ( SELECT DISTINCT C.COMMUNITY_ID FROM COMMUNITY C, COMM_MEMBERS CM WHERE ( CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( CM.COMMUNITY_ID NOT IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = :user_id) ) ) AND ( INSTR(COMMUNITY_NAME, :comm_search_name) > 0 )'''

        if (comm_search_name is None) or (len(comm_search_name) == 0):
            sql = '''
                    SELECT COUNT(*)
                    FROM COMMUNITY
                    WHERE COMMUNITY_ID IN ( SELECT DISTINCT C.COMMUNITY_ID FROM COMMUNITY C, COMM_MEMBERS CM WHERE ( CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( CM.COMMUNITY_ID NOT IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = :user_id) ) )
                '''
            c.execute(sql, {"user_id":user_id})
        else:
            sql = '''
                    SELECT COUNT(*)
                    FROM COMMUNITY
                    WHERE COMMUNITY_ID IN ( SELECT DISTINCT C.COMMUNITY_ID FROM COMMUNITY C, COMM_MEMBERS CM WHERE ( CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( CM.COMMUNITY_ID NOT IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = :user_id) ) ) AND ( INSTR(COMMUNITY_NAME, :comm_search_name) > 0 )
                '''
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
                                    SELECT COMMUNITY_ID, COMMUNITY_NAME, COUNT_COMM_MEMBER(COMMUNITY_ID) , TIME_DIFF(DATE_OF_CREATION)
                                    FROM COMMUNITY
                                    WHERE COMMUNITY_ID IN ( SELECT DISTINCT C.COMMUNITY_ID FROM COMMUNITY C, COMM_MEMBERS CM WHERE ( CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( CM.COMMUNITY_ID NOT IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = :user_id) ) )
                                    ORDER BY COUNT_COMM_MEMBER(COMMUNITY_ID) DESC, DATE_OF_CREATION 
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
                                    SELECT COUNT(*)
                                    FROM COMMUNITY
                                    WHERE COMMUNITY_ID IN ( SELECT DISTINCT C.COMMUNITY_ID FROM COMMUNITY C, COMM_MEMBERS CM WHERE ( CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( CM.COMMUNITY_ID NOT IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = :user_id) ) ) AND ( INSTR(COMMUNITY_NAME, :comm_search_name) > 0 )
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

            return HttpResponseRedirect(reverse('community:home', args=(1,1,0)))
    else:
        return redirect('SignIn:signin')



def detail_community(request, community_id, start_member_count, start_requ_count):
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




        c.execute("SELECT COMMUNITY_NAME, DESCRIPTION, CRITERIA, DATE_OF_CREATION, TIME_DIFF(DATE_OF_CREATION) FROM COMMUNITY WHERE COMMUNITY_ID = :community_id", {"community_id":community_id})
        for row in c:
            community_name = row[0]
            description = row[1]
            criteria = row[2]
            creation = row[3]
            creation_ago = row[4]

        c.execute("SELECT USER_ID FROM COMM_MEMBERS WHERE COMMUNITY_ID = :community_id", {"community_id":community_id})
        members_list = []
        for row in c:
            idx = row[0]
            members_list.append(idx)
        
        user_is_comm_member = True if user_id in members_list else False
        
        if not user_is_comm_member:
            already_joined = False
            c.execute("SELECT * FROM JOIN_REQUEST WHERE (USER_ID = :user_id) AND (COMMUNITY_ID = :community_id) ", {"user_id":user_id, "community_id":community_id})
            for row in c:
                already_joined = True
            context = {
                'data':data,
                'skills':skills,
                'edit':True,
                'dp':dp_form,
                'job':job_list,
                "community_name":community_name,
                "description":description,
                "criteria":criteria,
                "creation":creation,
                "creation_ago":creation_ago,
                "not_comm_member":True,
                "comm_id":community_id,
                "already_joined":already_joined
            }
            return render(request, "community/detail_community.html", context)

        else:
            c.execute("SELECT USER_ID FROM MODERATOR WHERE COMMUNITY_ID = :community_id", {"community_id":community_id})
            for row in c:
                created_by = row[0]

            user_is_admin = True if created_by == user_id else False

            sql = "SELECT COUNT(*) FROM COMM_MEMBERS WHERE (COMMUNITY_ID = :community_id) AND (USER_ID <> :user_id)"
            c.execute(sql, {"community_id":community_id, "user_id":user_id})
            for row in c:
                num_members = row[0]

            begin_member = start_member_count
            end_member = (start_member_count + 5) if (start_member_count + 5) <= num_members else num_members+1
            member_the_end = (num_members == end_member-1)
            member_is_begin = (begin_member == 1 )


            sql = ''' 
                    SELECT * 
                    FROM(
                            SELECT A.*, ROWNUM RNUM
                            FROM (
                                    SELECT U.STD_ID, U.FULL_NAME, TIME_DIFF(CM.JOIN_DATE)
                                    FROM USER_TABLE U, COMM_MEMBERS CM
                                    WHERE (CM.USER_ID = U.STD_ID) AND (CM.USER_ID <> :user_id) AND (CM.COMMUNITY_ID = :community_id)
                                    ORDER BY CM.JOIN_DATE ASC, U.std_id ASC
                                ) A
                            WHERE ROWNUM < :end_member
                        )
                    WHERE RNUM >= :begin_member'''
            
            c.execute(sql, {"end_member":end_member, "begin_member":begin_member, "user_id":user_id, "community_id":community_id})

            members_info = []
            for row in c:
                member_dict = {}
                member_dict['user_id'] = row[0]
                member_dict['full_name'] = row[1]
                member_dict['joined'] = row[2]

                members_info.append(member_dict)
            
            for idx, member_dict in enumerate(members_info):
                member_dict['photo'] = "dummy_user.png"
                c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = :user_id", {"user_id":member_dict['user_id']})
                for row in c:
                    member_dict['photo'] = row[0]
                members_info[idx] = member_dict
            
            if not user_is_admin:
                context = {
                    'data':data,
                    'skills':skills,
                    'edit':True,
                    'dp':dp_form,
                    'job':job_list,

                    "community_name":community_name,
                    "description":description,
                    "criteria":criteria,
                    "creation":creation,
                    "creation_ago":creation_ago,

                    "not_comm_member":False,
                    "not_admin":True,
                    "member_dicts":members_info,
                    "comm_id":community_id,

                    "is_member_begin":member_is_begin,
                    "is_member_end":member_the_end,
                    "next_member":end_member,
                    "prev_member":(begin_member-5) if begin_member > 5 else 0,
                    "orig_member":start_member_count,
                }
                return render(request, "community/detail_community.html", context)
            else:
                c.execute("SELECT COUNT(*) FROM JOIN_REQUEST WHERE COMMUNITY_ID = :community_id ", {"community_id":community_id})
                for row in c:
                    num_requ = row[0]

                begin_requ = start_requ_count
                end_requ = (start_requ_count + 5) if (start_requ_count + 5) <= num_requ else num_requ+1
                requ_the_end = (num_requ == end_requ-1)
                requ_is_begin = (begin_requ == 1 )

                

                sql = ''' 
                    SELECT * 
                    FROM(
                            SELECT A.*, ROWNUM RNUM
                            FROM (
                                    SELECT U.STD_ID, U.FULL_NAME, TIME_DIFF(J.REQUEST_TIME)
                                    FROM USER_TABLE U, JOIN_REQUEST J
                                    WHERE (J.USER_ID = U.STD_ID) AND (J.COMMUNITY_ID = :community_id)
                                    ORDER BY J.REQUEST_TIME ASC, U.std_id ASC
                                ) A
                            WHERE ROWNUM < :end_requ
                        )
                    WHERE RNUM >= :begin_requ'''
                
                c.execute(sql, {"end_requ":end_requ, "begin_requ":begin_requ, "community_id":community_id})

                request_infos = []
                for row in c:
                    request_dict = {}
                    request_dict['user_id'] = row[0]
                    request_dict['full_name'] = row[1]
                    request_dict['time'] = row[2]
                    
                    request_dict['photo'] = "dummy_user.png"

                    

                    request_infos.append(request_dict)

                for idx, request_dict in enumerate(request_infos):
                    request_dict['photo'] = "dummy_user.png"

                    c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = :user_id", {"user_id":request_dict['user_id']})
                    for row in c:
                        request_dict['photo'] = row[0]
                    request_infos[idx] = request_dict



                context = {
                    'data':data,
                    'skills':skills,
                    'edit':True,
                    'dp':dp_form,
                    'job':job_list,

                    "community_name":community_name,
                    "description":description,
                    "criteria":criteria,
                    "creation":creation,
                    "creation_ago":creation_ago,

                    "not_comm_member":False,
                    "not_admin":False,
                    "member_dicts":members_info,
                    "request_dicts":request_infos,
                    "comm_id":community_id,

                    "is_member_begin":member_is_begin,
                    "is_member_end":member_the_end,
                    "next_member":end_member,
                    "prev_member":(begin_member-5) if begin_member > 5 else 0,
                    "orig_member":start_member_count,

                    "is_requ_begin":requ_is_begin,
                    "is_requ_end":requ_the_end,
                    "next_requ":end_requ,
                    "prev_requ":(begin_requ-5) if begin_requ > 5 else 0,
                    "orig_requ":start_requ_count,
                }
                return render(request, "community/detail_community.html", context)


            




    else:
        return redirect('SignIn:signin')



def join_request(request, community_id):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()
        user_id = request.session.get('std_id')

        c.execute("INSERT INTO JOIN_REQUEST VALUES (:community_id, :user_id, SYSDATE)", {"community_id":community_id, "user_id":user_id})
        c.execute("COMMIT")

        return HttpResponseRedirect(reverse('community:home', args=(1,1,0)))
    else:
        return redirect('SignIn:signin')


def join_community(request, community_id, user_id, start_member_count, start_requ_count):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()

        c.execute("INSERT INTO COMM_MEMBERS VALUES (:community_id, :user_id, SYSDATE) ", {"community_id":community_id, "user_id":user_id})
        c.execute("COMMIT")
        return HttpResponseRedirect(reverse('community:detail_community', args=(community_id, start_member_count, start_requ_count)))
    else:
        return redirect('SignIn:signin')

def remove_request(request, community_id, user_id, start_member_count, start_requ_count):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()

        c.execute("DELETE FROM JOIN_REQUEST WHERE (COMMUNITY_ID = :community_id) AND (USER_ID = :user_id) ", {"community_id":community_id, "user_id":user_id})
        c.execute("COMMIT")
        return HttpResponseRedirect(reverse('community:detail_community', args=(community_id, start_member_count, start_requ_count)))
    else:
        return redirect('SignIn:signin')

