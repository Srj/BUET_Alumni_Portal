from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from Alumni_Portal.utils import db,encrypt_password
from django.urls import reverse
import datetime
from django.core.files.storage import FileSystemStorage
from django.utils.safestring import mark_safe
from datetime import date
import json
from django import forms


class DPForm(forms.Form):
    file = forms.FileField()

def description_after_text_search(desc, text):
    len_search = len(text)
    search_pos = desc.find(text)
    updated_desc = desc.replace(text, f'<mark>{text}</mark>')

    if search_pos + len_search < 100 :
        selected = (updated_desc[:100 + 13] + "...").replace("\n", "  ")
        #selected = selected.replace('/^"(.*)"$/', '$1')
        return mark_safe(selected)
    else:
        remaining = 100 - (len_search + 12)
        start = search_pos - remaining//2
        end = search_pos + len_search + 13 + remaining//2

        if end > len(desc):
            starting = start - remaining//2
        else:
            starting = start

        if start <= 0:
            ending = end + remaining//2
        else:
            ending = end

        if starting <= 0:
            if ending > len(desc):
                selected = updated_desc
            else:
                selected = updated_desc[:ending] + "..."
        else:
            if ending > len(desc):
                selected = "..." + updated_desc[starting:]
            else:
                selected = "..." + updated_desc[starting:ending] + "..."
        selected = selected.replace("\n", "  ")
        return mark_safe(selected)

def home(request, my_groups_start, other_groups_start, comm_search_change, post_start, post_change):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()

        user_id = request.session.get('std_id')

        #================== Search for community ====================
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

        #===================== Search for Post ============================
        if post_change == 0:
            # set to default
            request.session['comm_search_std_id'] = ''
            request.session['comm_search_post_typ'] = None
            search_post_typ = None
            search_std_id = ''
        elif post_change == 1:
            #dont change
            search_post_typ = request.session['comm_search_post_typ']
            search_std_id = request.session['comm_search_std_id']
        elif post_change == 2:
            #update
            search_std_id = request.GET.get('comm_search_std_id')
            search_post_typ = request.GET.get('comm_search_post_typ')

            request.session['comm_search_std_id'] = search_std_id
            request.session['comm_search_post_typ'] = search_post_typ

        
            

        #-------------------------------------Profile Card---------------------------------
        sql = """ SELECT * from USER_PROFILE WHERE STD_ID = %(std_id)s"""
        c.execute(sql,{'std_id':request.session.get('std_id')})
        row = c.fetchone()
        columnNames = [d[0].upper() for d in c.description]
        
        try:
            data = dict(zip(columnNames,row))
        except:
            print('Cannot Parse Profile')

        #-----------------------------------Skills------------------------------------
        sql = """ SELECT EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
                EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = %(std_id)s GROUP BY EXPERTISE.TOPIC"""
        c.execute(sql,{'std_id':request.session.get('std_id')})
        rows = c.fetchall()
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
        dp_form = DPForm()

        #--------------------------------------Job History--------------------------------
        sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID = %(std_id)s ORDER BY FROM_ DESC"""
        c.execute(sql,{'std_id':request.session.get('std_id')})
        jobs = c.fetchall()
        columnNames = [d[0].upper() for d in c.description]
        job_list = []
        for job in jobs:
            try:
                job_list.append(dict(zip(columnNames,job)))
            except:
                print('NULL')


        #=================================MY GROUPS INFO===================================
        if (comm_search_name is None) or (len(comm_search_name) == 0):
            sql = "SELECT COUNT(*) FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s"
            c.execute(sql, {"user_id":user_id})
        else:
            sql = '''SELECT COUNT(*) 
                    FROM COMM_MEMBERS CM, COMMUNITY C 
                    WHERE (CM.USER_ID = %(user_id)s) AND (CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )'''
            c.execute(sql, {"comm_search_name":comm_search_name, "user_id":user_id})
        rows = c.fetchall()
        for row in rows:
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
                                    WHERE (CM.USER_ID = %(user_id)s) AND (CM.COMMUNITY_ID = C.COMMUNITY_ID)
                                    ORDER BY COUNT_COMM_MEMBER(C.COMMUNITY_ID) DESC, C.DATE_OF_CREATION 
                                ) A
                            WHERE ROWNUM < %(end_community)s
                        ) DUMMY
                    WHERE RNUM >= %(begin_community)s'''

            c.execute(sql, {"end_community":end_my_comm, "begin_community":begin_my_comm, "user_id":user_id})
        else:
            sql = ''' 
                    SELECT * 
                    FROM(
                            SELECT A.*, ROWNUM RNUM
                            FROM (
                                    SELECT C.COMMUNITY_ID, C.COMMUNITY_NAME, COUNT_COMM_MEMBER(C.COMMUNITY_ID) AS NUM_MEMBERS, TIME_DIFF(C.DATE_OF_CREATION) 
                                    FROM COMMUNITY C, COMM_MEMBERS CM 
                                    WHERE (CM.USER_ID = %(user_id)s) AND (CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                                    ORDER BY COUNT_COMM_MEMBER(C.COMMUNITY_ID) DESC, C.DATE_OF_CREATION 
                                ) A
                            WHERE ROWNUM < %(end_community)s
                        )
                    WHERE RNUM >= %(begin_community)s'''

            c.execute(sql, {"end_community":end_my_comm, "begin_community":begin_my_comm, "user_id":user_id, "comm_search_name":comm_search_name})
        
        my_communities_infos = []
        rows = c.fetchall()
        for row in rows:
            community_dict = {}
            community_dict['community_id'] = row[0]
            community_dict['community_name'] = row[1]
            community_dict["num_members"] = row[2]
            community_dict["created"] = row[3]

            my_communities_infos.append(community_dict)


        #================================Groups I am not in (joinable groups) =======================================
        

        if (comm_search_name is None) or (len(comm_search_name) == 0):
            sql = '''
                    SELECT COUNT(*)
                    FROM COMMUNITY
                    WHERE COMMUNITY_ID IN ( SELECT DISTINCT C.COMMUNITY_ID FROM COMMUNITY C, COMM_MEMBERS CM WHERE ( CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( CM.COMMUNITY_ID NOT IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) )
                '''
            c.execute(sql, {"user_id":user_id})
        else:
            sql = '''
                    SELECT COUNT(*)
                    FROM COMMUNITY
                    WHERE COMMUNITY_ID IN ( SELECT DISTINCT C.COMMUNITY_ID FROM COMMUNITY C, COMM_MEMBERS CM WHERE ( CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( CM.COMMUNITY_ID NOT IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) ) AND ( STRPOS(COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                '''
            c.execute(sql, {"comm_search_name":comm_search_name, "user_id":user_id})

        rows = c.fetchall()
        for row in rows:
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
                                    WHERE COMMUNITY_ID IN ( SELECT DISTINCT C.COMMUNITY_ID FROM COMMUNITY C, COMM_MEMBERS CM WHERE ( CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( CM.COMMUNITY_ID NOT IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) )
                                    ORDER BY COUNT_COMM_MEMBER(COMMUNITY_ID) DESC, DATE_OF_CREATION 
                                ) A
                            WHERE ROWNUM < %(end_community)s
                        )
                    WHERE RNUM >= %(begin_community)s'''

            c.execute(sql, {"end_community":end_other_comm, "begin_community":begin_other_comm, "user_id":user_id})
        else:
            sql = ''' 
                    SELECT * 
                    FROM(
                            SELECT A.*, ROWNUM RNUM
                            FROM (
                                    SELECT COMMUNITY_ID, COMMUNITY_NAME, COUNT_COMM_MEMBER(COMMUNITY_ID) , TIME_DIFF(DATE_OF_CREATION)
                                    FROM COMMUNITY
                                    WHERE COMMUNITY_ID IN ( SELECT DISTINCT C.COMMUNITY_ID FROM COMMUNITY C, COMM_MEMBERS CM WHERE ( CM.COMMUNITY_ID = C.COMMUNITY_ID) AND ( CM.COMMUNITY_ID NOT IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) ) AND ( STRPOS(COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                                    ORDER BY COUNT_COMM_MEMBER(COMMUNITY_ID) DESC, DATE_OF_CREATION 
                                ) A
                            WHERE ROWNUM < %(end_community)s
                        )
                    WHERE RNUM >= %(begin_community)s'''

            

            c.execute(sql, {"end_community":end_other_comm, "begin_community":begin_other_comm, "user_id":user_id, "comm_search_name":comm_search_name})

        other_communities_infos = []
        rows = c.fetchall()
        for row in rows:
            #print(row)
            community_dict = {}
            community_dict['community_id'] = row[0]
            community_dict['community_name'] = row[1]
            community_dict["num_members"] = row[2]
            community_dict["created"] = row[3]

            other_communities_infos.append(community_dict)


        #======================================== Infos about Post =========================================
        if (comm_search_name is None) or (len(comm_search_name) == 0):

            if (search_post_typ is None) and ( (search_std_id is None) or (len(search_std_id) == 0 ) ):
                c.execute("SELECT COUNT(*) FROM COMMUNITY_USER_POSTS WHERE COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ", {"user_id":user_id})

            if (search_post_typ is None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                sql = '''
                            SELECT COUNT(*) 
                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP
                            WHERE ( CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                            
                        '''
                c.execute(sql, {'search_std_id':search_std_id, "user_id":user_id})

            if (search_post_typ is not None) and ((search_std_id is None) or (len(search_std_id) == 0 )):
                if search_post_typ == 'Help':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_HELP H
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = H.POST_ID)
                            '''
                    c.execute(sql, {"user_id":user_id})

                if search_post_typ == 'Career':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_CAREER C
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = C.POST_ID)
                            '''
                    c.execute(sql, {"user_id":user_id})

                if search_post_typ == 'Research':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_RESEARCH R
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = R.POST_ID)
                            '''
                    c.execute(sql, {"user_id":user_id})

                if search_post_typ == 'Job Post':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_JOB_POST J
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = J.POST_ID)
                            '''
                    c.execute(sql, {"user_id":user_id})

            if (search_post_typ is not None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                if search_post_typ == 'Help':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_HELP H, COMMUNITY_POST CP
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = H.POST_ID) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                            '''
                    c.execute(sql, {'search_std_id':search_std_id, "user_id":user_id})

                if search_post_typ == 'Career':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_CAREER C, COMMUNITY_POST CP
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = C.POST_ID) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                            '''
                    c.execute(sql, {'search_std_id':search_std_id, "user_id":user_id})

                if search_post_typ == 'Research':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_RESEARCH R, COMMUNITY_POST CP
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = R.POST_ID) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                            '''
                    c.execute(sql, {'search_std_id':search_std_id, "user_id":user_id})

                if search_post_typ == 'Job Post':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_JOB_POST J, COMMUNITY_POST CP
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = J.POST_ID) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                            '''
                    c.execute(sql, {'search_std_id':search_std_id, "user_id":user_id})

            rows = c.fetchall()
            for row in rows:
                num_post = row[0]


            begin_post = post_start
            end_post = (post_start + 5) if (post_start + 5) <= num_post else num_post+1
            post_the_end = (num_post == end_post-1)
            post_is_begin = (begin_post == 1 )

            if (search_post_typ is None) and ( (search_std_id is None) or (len(search_std_id) == 0 ) ):
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM (
                                        SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME 
                                        FROM  COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C
                                        WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID)
                                        ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < %(end_post)s
                            )
                        WHERE RNUM >= %(begin_post)s'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id})
                rows = c.fetchall()
                all_post = [row for row in rows]
            
            if (search_post_typ is None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM(
                                        SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                        FROM  COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C
                                        WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                                        ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < %(end_post)s
                            )
                        WHERE RNUM >= %(begin_post)s'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, 'search_std_id':search_std_id, "user_id":user_id})
                rows = c.fetchall()
                all_post = [row for row in rows]
            

            if (search_post_typ is not None) and ((search_std_id is None) or (len(search_std_id) == 0 )):
                if search_post_typ == 'Help':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_HELP H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID)
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Career':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_CAREER H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID)
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Research':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_RESEARCH H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID)
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Job Post':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_JOB_POST H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID)
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]

            if (search_post_typ is not None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                if search_post_typ == 'Help':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_HELP H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "search_std_id":search_std_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Career':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_CAREER H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "search_std_id":search_std_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Research':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_RESEARCH H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "search_std_id":search_std_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Job Post':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_JOB_POST H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "search_std_id":search_std_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]

        else:

            if (search_post_typ is None) and ( (search_std_id is None) or (len(search_std_id) == 0 ) ):
                c.execute("SELECT COUNT(*) FROM COMMUNITY_USER_POSTS CUP, COMMUNITY C WHERE CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 ) ", {"user_id":user_id, "comm_search_name":comm_search_name})

            if (search_post_typ is None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                sql = '''
                            SELECT COUNT(*) 
                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C
                            WHERE ( CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 ) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                            
                        '''
                c.execute(sql, {'search_std_id':search_std_id, "user_id":user_id, "comm_search_name":comm_search_name})

            if (search_post_typ is not None) and ((search_std_id is None) or (len(search_std_id) == 0 )):
                if search_post_typ == 'Help':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_HELP H, COMMUNITY C
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = H.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                            '''
                    c.execute(sql, {"user_id":user_id, "comm_search_name":comm_search_name})

                if search_post_typ == 'Career':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_CAREER C, COMMUNITY C
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = C.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                            '''
                    c.execute(sql, {"user_id":user_id, "comm_search_name":comm_search_name})

                if search_post_typ == 'Research':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_RESEARCH R, COMMUNITY C
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = R.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                            '''
                    c.execute(sql, {"user_id":user_id, "comm_search_name":comm_search_name})

                if search_post_typ == 'Job Post':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_JOB_POST J, COMMUNITY C
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = J.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                            '''
                    c.execute(sql, {"user_id":user_id, "comm_search_name":comm_search_name})

            if (search_post_typ is not None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                if search_post_typ == 'Help':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_HELP H, COMMUNITY_POST CP, COMMUNITY C
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = H.POST_ID) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 ) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                            '''
                    c.execute(sql, {'search_std_id':search_std_id, "user_id":user_id, "comm_search_name":comm_search_name})

                if search_post_typ == 'Career':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_CAREER C, COMMUNITY_POST CP, COMMUNITY C
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = C.POST_ID) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 ) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                            '''
                    c.execute(sql, {'search_std_id':search_std_id, "user_id":user_id, "comm_search_name":comm_search_name})

                if search_post_typ == 'Research':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_RESEARCH R, COMMUNITY_POST CP, COMMUNITY C
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = R.POST_ID) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 ) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                            '''
                    c.execute(sql, {'search_std_id':search_std_id, "user_id":user_id, "comm_search_name":comm_search_name})

                if search_post_typ == 'Job Post':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_JOB_POST J, COMMUNITY_POST CP, COMMUNITY C
                                WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = J.POST_ID) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 ) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                            '''
                    c.execute(sql, {'search_std_id':search_std_id, "user_id":user_id, "comm_search_name":comm_search_name})
            
            rows = c.fetchall()
            for row in rows:
                num_post = row[0]


            begin_post = post_start
            end_post = (post_start + 5) if (post_start + 5) <= num_post else num_post+1
            post_the_end = (num_post == end_post-1)
            post_is_begin = (begin_post == 1 )

            if (search_post_typ is None) and ( (search_std_id is None) or (len(search_std_id) == 0 ) ):
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM (
                                        SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME 
                                        FROM  COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C
                                        WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                                        ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < %(end_post)s
                            )
                        WHERE RNUM >= %(begin_post)s'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "comm_search_name":comm_search_name})
                rows = c.fetchall()
                all_post = [row for row in rpws]
            
            if (search_post_typ is None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM(
                                        SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                        FROM  COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C
                                        WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 ) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                                        ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < %(end_post)s
                            )
                        WHERE RNUM >= %(begin_post)s'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, 'search_std_id':search_std_id, "user_id":user_id, "comm_search_name":comm_search_name})
                rows = c.fetchall()
                all_post = [row for row in rows]
            

            if (search_post_typ is not None) and ((search_std_id is None) or (len(search_std_id) == 0 )):
                if search_post_typ == 'Help':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_HELP H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "comm_search_name":comm_search_name})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Career':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_CAREER H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "comm_search_name":comm_search_name})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Research':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_RESEARCH H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "comm_search_name":comm_search_name})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Job Post':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_JOB_POST H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "comm_search_name":comm_search_name})
                    rows = c.fetchall()
                    all_post = [row for row in rows]

            if (search_post_typ is not None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                if search_post_typ == 'Help':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_HELP H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 ) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "search_std_id":search_std_id, "comm_search_name":comm_search_name})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Career':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_CAREER H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 ) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "search_std_id":search_std_id, "comm_search_name":comm_search_name})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Research':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_RESEARCH H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 ) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "search_std_id":search_std_id, "comm_search_name":comm_search_name})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Job Post':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_JOB_POST H
                                            WHERE (CUP.COMMUNITY_ID IN (SELECT COMMUNITY_ID FROM COMM_MEMBERS WHERE USER_ID = %(user_id)s) ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 ) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(C.COMMUNITY_NAME, %(comm_search_name)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "user_id":user_id, "search_std_id":search_std_id, "comm_search_name":comm_search_name})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
        
        all_post_dicts = []
        for post in all_post:
            post_dict = {}
            post_dict['community_id'] = post[0]
            post_dict['post_id'] = post[1]
            post_dict['date'] = post[2]
            post_dict['desc'] = post[3]
            post_dict['community_name'] = post[4]

            #c.execute("SELECT USER_ID FROM COMMUNITY_USER_POSTS WHERE POST_ID = '"+str(post_dict['post_id'])+"' ")
            sql = "SELECT USER_ID FROM COMMUNITY_USER_POSTS WHERE (POST_ID = %(post_id)s) AND (COMMUNITY_ID = %(community_id)s) "
            c.execute(sql, {'post_id':post_dict['post_id'], "community_id":post_dict['community_id']})
            rows = c.fetchall()
            for row in rows:
                post_dict['user_id'] = row[0]

            c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = '"+str(post_dict['user_id'])+"' ")
            rows = c.fetchall()
            for row in rows:
                post_dict['photo_path'] = row[0]
            
            c.execute("SELECT FULL_NAME FROM USER_TABLE WHERE STD_ID = '"+str(post_dict['user_id'])+"' ")
            rows = c.fetchall()
            for row in rows:
                post_dict['full_name'] = row[0]

            c.execute("SELECT COUNT(*) FROM COMMUNITY_USER_REPLIES WHERE (POST_ID = %(post_id)s) AND (COMMUNITY_ID = %(community_id)s) ", {'post_id':post_dict['post_id'], "community_id":post_dict['community_id']})
            rows = c.fetchall()
            for row in rows:
                post_dict['num_comments'] = row[0]
            

            c.execute("SELECT * FROM COMMUNITY_HELP WHERE POST_ID = '"+str(post_dict['post_id'])+"'")
            rows = c.fetchall()
            for row in rows:
                post_dict['class'] = 'help'

            c.execute("SELECT * FROM COMMUNITY_CAREER WHERE POST_ID = '"+str(post_dict['post_id'])+"'")
            rows = c.fetchall()
            for row in rows:
                post_dict['class'] = 'career'

            c.execute("SELECT * FROM COMMUNITY_RESEARCH WHERE POST_ID = '"+str(post_dict['post_id'])+"'")
            rows = c.fetchall()
            for row in rows:
                post_dict['class'] = 'research'

            c.execute("SELECT * FROM COMMUNITY_JOB_POST WHERE POST_ID = '"+str(post_dict['post_id'])+"'")
            rows = c.fetchall()
            for row in rows:
                post_dict['class'] = 'job'

            if ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                post_dict['desc_selected'] = description_after_text_search(post_dict['desc'], search_std_id) 
                post_dict['query'] = search_std_id

            all_post_dicts.append(post_dict)

        




        context = {
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

            "search_comm_name":comm_search_name,

            "post_dicts":all_post_dicts,
            "next_post":end_post,
            "prev_post":(begin_post - 5) if begin_post > 5 else 0,
            "post_the_end":post_the_end,
            "post_is_begin":post_is_begin,
            "orig_post":post_start,
            'search_post_typ':search_post_typ,
            'search_std_id':search_std_id,
            'doing_text_search':True if ( (search_std_id is not None) and (len(search_std_id) > 0) ) else False,
        }
        return render(request, 'community/home.html', context)
    else:
        return redirect('SignIn:signin')



def create_community(request):
    if "std_id" in request.session:

        conn = db()
        c = conn.cursor()

        user_id = request.session.get('std_id')

        #-------------------------------------Profile Card---------------------------------
        sql = """ SELECT * from USER_PROFILE WHERE STD_ID = %(std_id)s"""
        row =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchone()
        columnNames = [d[0] for d in c.description]
        
        try:
            data = dict(zip(columnNames,row))
        except:
            print('Cannot Parse Profile')

        #-----------------------------------Skills------------------------------------
        sql = """ SELECT EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
                EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = %(std_id)s GROUP BY EXPERTISE.TOPIC"""
        rows =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchall()
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
        dp_form = DPForm()

        #--------------------------------------Job History--------------------------------
        sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID = %(std_id)s ORDER BY FROM_ DESC"""
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

        #print(unfilled_data)
        #print(filled_data)

        if len(unfilled_data) > 0:
            #-------------------------------------Profile Card---------------------------------
            sql = """ SELECT * from USER_PROFILE WHERE STD_ID = %(std_id)s"""
            row =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchone()
            columnNames = [d[0] for d in c.description]
            
            try:
                data = dict(zip(columnNames,row))
            except:
                print('Cannot Parse Profile')

            #-----------------------------------Skills------------------------------------
            sql = """ SELECT EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
                    EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = %(std_id)s GROUP BY EXPERTISE.TOPIC"""
            rows =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchall()
            skills = {}
            for row in rows:
                skills[row[0]] = row[1]
            dp_form = DPForm()

            #--------------------------------------Job History--------------------------------
            sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID = %(std_id)s ORDER BY FROM_ DESC"""
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
            sql = '''INSERT INTO COMMUNITY (COMMUNITY_NAME, DESCRIPTION, CRITERIA, DATE_OF_CREATION) VALUES (%(community_name)s, %(description)s, %(criteria)s, SYSDATE)  '''
            c.execute(sql, {"community_name":community_name, "description":description, "criteria":criteria})
            c.execute("SELECT COMMUNITY_ID FROM (SELECT COMMUNITY_ID FROM COMMUNITY ORDER BY COMMUNITY_ID DESC) WHERE ROWNUM=1")
            rows = c.fetchall()
            for row in rows:
                comm_id = row[0]
            sql = '''INSERT INTO MODERATOR VALUES (%(comm_id)s, %(user_id)s) '''
            c.execute(sql, {"comm_id":comm_id, "user_id":user_id})
            sql = '''INSERT INTO COMM_MEMBERS VALUES (%(comm_id)s, %(user_id)s, SYSDATE) '''
            c.execute(sql, {"comm_id":comm_id, "user_id":user_id})
            c.execute("COMMIT")

            return HttpResponseRedirect(reverse('community:home', args=(1,1,0,1,0)))
    else:
        return redirect('SignIn:signin')



def detail_community(request, community_id, start_member_count, start_requ_count, post_start, post_change):
    if "std_id" in request.session:

        conn = db()
        c = conn.cursor()
        user_id = request.session.get('std_id')

        if post_change == 0:
            # set to default
            request.session['detail_search_std_id'] = ''
            request.session['detail_search_post_typ'] = None
            search_post_typ = None
            search_std_id = ''
        elif post_change == 1:
            #dont change
            search_post_typ = request.session['detail_search_post_typ']
            search_std_id = request.session['detail_search_std_id']
        elif post_change == 2:
            #update
            search_std_id = request.GET.get('detail_search_std_id')
            search_post_typ = request.GET.get('detail_search_post_typ')

            request.session['detail_search_std_id'] = search_std_id
            request.session['detail_search_post_typ'] = search_post_typ

        print(search_std_id)



        #-------------------------------------Profile Card---------------------------------
        sql = """ SELECT * from USER_PROFILE WHERE STD_ID = %(std_id)s"""
        row =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchone()
        columnNames = [d[0] for d in c.description]
        
        try:
            data = dict(zip(columnNames,row))
        except:
            print('Cannot Parse Profile')

        #-----------------------------------Skills------------------------------------
        sql = """ SELECT EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
                EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = %(std_id)s GROUP BY EXPERTISE.TOPIC"""
        rows =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchall()
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
        dp_form = DPForm()

        #--------------------------------------Job History--------------------------------
        sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID = %(std_id)s ORDER BY FROM_ DESC"""
        rows =  c.execute(sql,{'std_id':request.session.get('std_id')})
        jobs = rows.fetchall()
        columnNames = [d[0] for d in c.description]
        job_list = []
        for job in jobs:
            try:
                job_list.append(dict(zip(columnNames,job)))
            except:
                print('NULL')




        c.execute("SELECT COMMUNITY_NAME, DESCRIPTION, CRITERIA, DATE_OF_CREATION, TIME_DIFF(DATE_OF_CREATION) FROM COMMUNITY WHERE COMMUNITY_ID = %(community_id)s", {"community_id":community_id})
        rows = c.fetchall()
        for row in rows:
            community_name = row[0]
            description = row[1]
            criteria = row[2]
            creation = row[3]
            creation_ago = row[4]

        c.execute("SELECT USER_ID FROM COMM_MEMBERS WHERE COMMUNITY_ID = %(community_id)s", {"community_id":community_id})
        members_list = []
        rows = c.fetchall()
        for row in rows:
            idx = row[0]
            members_list.append(idx)
        
        user_is_comm_member = True if user_id in members_list else False
        
        if not user_is_comm_member:
            already_joined = False
            c.execute("SELECT * FROM JOIN_REQUEST WHERE (USER_ID = %(user_id)s) AND (COMMUNITY_ID = %(community_id)s) ", {"user_id":user_id, "community_id":community_id})
            rows = c.fetchall()
            for row in rows:
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

            #=======================Gather Data For Post=========================
            c.execute("SELECT USER_ID FROM MODERATOR WHERE COMMUNITY_ID = %(community_id)s", {"community_id":community_id})
            rows = c.fetchall()
            for row in rows:
                created_by = row[0]

            user_is_admin = True if created_by == user_id else False

            if (search_post_typ is None) and ( (search_std_id is None) or (len(search_std_id) == 0 ) ):
                c.execute("SELECT COUNT(*) FROM COMMUNITY_USER_POSTS WHERE COMMUNITY_ID = %(community_id)s ", {"community_id":community_id})

            if (search_post_typ is None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                sql = '''
                            SELECT COUNT(*) 
                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP
                            WHERE ( CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                            
                        '''
                c.execute(sql, {'search_std_id':search_std_id, "community_id":community_id})

            if (search_post_typ is not None) and ((search_std_id is None) or (len(search_std_id) == 0 )):
                if search_post_typ == 'Help':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_HELP H
                                WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = H.POST_ID)
                            '''
                    c.execute(sql, {"community_id":community_id})

                if search_post_typ == 'Career':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_CAREER C
                                WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = C.POST_ID)
                            '''
                    c.execute(sql, {"community_id":community_id})

                if search_post_typ == 'Research':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_RESEARCH R
                                WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = R.POST_ID)
                            '''
                    c.execute(sql, {"community_id":community_id})

                if search_post_typ == 'Job Post':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_JOB_POST J
                                WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = J.POST_ID)
                            '''
                    c.execute(sql, {"community_id":community_id})

            if (search_post_typ is not None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                if search_post_typ == 'Help':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_HELP H, COMMUNITY_POST CP
                                WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = H.POST_ID) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                            '''
                    c.execute(sql, {'search_std_id':search_std_id, "user_id":user_id})

                if search_post_typ == 'Career':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_CAREER C, COMMUNITY_POST CP
                                WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = C.POST_ID) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                            '''
                    c.execute(sql, {'search_std_id':search_std_id, "user_id":user_id})

                if search_post_typ == 'Research':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_RESEARCH R, COMMUNITY_POST CP
                                WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = R.POST_ID) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                            '''
                    c.execute(sql, {'search_std_id':search_std_id, "community_id":community_id})

                if search_post_typ == 'Job Post':
                    sql = '''
                                SELECT COUNT(*)
                                FROM COMMUNITY_USER_POSTS CUP, COMMUNITY_JOB_POST J, COMMUNITY_POST CP
                                WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = J.POST_ID) AND (CUP.POST_ID = CP.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                            '''
                    c.execute(sql, {'search_std_id':search_std_id, "community_id":community_id})
            rows = c.fetchall()
            for row in rows:
                num_post = row[0]


            begin_post = post_start
            end_post = (post_start + 5) if (post_start + 5) <= num_post else num_post+1
            post_the_end = (num_post == end_post-1)
            post_is_begin = (begin_post == 1 )

            if (search_post_typ is None) and ( (search_std_id is None) or (len(search_std_id) == 0 ) ):
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM (
                                        SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME 
                                        FROM  COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C
                                        WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID)
                                        ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < %(end_post)s
                            )
                        WHERE RNUM >= %(begin_post)s'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "community_id":community_id})
                rows = c.fetchall()
                all_post = [row for row in rows]
            
            if (search_post_typ is None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM(
                                        SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                        FROM  COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C
                                        WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                                        ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < %(end_post)s
                            )
                        WHERE RNUM >= %(begin_post)s'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, 'search_std_id':search_std_id, "community_id":community_id})
                rows = c.fetchall()
                all_post = [row for row in rows]
            

            if (search_post_typ is not None) and ((search_std_id is None) or (len(search_std_id) == 0 )):
                if search_post_typ == 'Help':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_HELP H
                                            WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID)
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "community_id":community_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Career':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_CAREER H
                                            WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID)
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "community_id":community_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Research':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_RESEARCH H
                                            WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID)
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "community_id":community_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Job Post':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_JOB_POST H
                                            WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID)
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "community_id":community_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]

            if (search_post_typ is not None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                if search_post_typ == 'Help':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_HELP H
                                            WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "community_id":community_id, "search_std_id":search_std_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Career':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_CAREER H
                                            WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "community_id":community_id, "search_std_id":search_std_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Research':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_RESEARCH H
                                            WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "community_id":community_id, "search_std_id":search_std_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]
                if search_post_typ == 'Job Post':
                    sql = '''
                            SELECT * 
                            FROM(
                                    SELECT A.*, ROWNUM RNUM
                                    FROM(
                                            SELECT CUP.COMMUNITY_ID, CP.POST_ID, TIME_DIFF(CP.DATE_OF_POST), CP.DESCRIPTION, C.COMMUNITY_NAME
                                            FROM COMMUNITY_POST CP, COMMUNITY_USER_POSTS CUP, COMMUNITY C, COMMUNITY_JOB_POST H
                                            WHERE (CUP.COMMUNITY_ID = %(community_id)s ) AND (CUP.POST_ID = CP.POST_ID) AND (CUP.COMMUNITY_ID = C.COMMUNITY_ID) AND (CUP.POST_ID = H.POST_ID) AND ( STRPOS(CP.DESCRIPTION, %(search_std_id)s) > 0 )
                                            ORDER BY CP.DATE_OF_POST DESC, CP.POST_ID DESC
                                        ) A
                                    WHERE ROWNUM < %(end_post)s
                                )
                            WHERE RNUM >= %(begin_post)s'''

                    c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, "community_id":community_id, "search_std_id":search_std_id})
                    rows = c.fetchall()
                    all_post = [row for row in rows]


            all_post_dicts = []
            for post in all_post:
                post_dict = {}
                post_dict['community_id'] = post[0]
                post_dict['post_id'] = post[1]
                post_dict['date'] = post[2]
                post_dict['desc'] = post[3]
                post_dict['community_name'] = post[4]

                #c.execute("SELECT USER_ID FROM USER_POSTS WHERE POST_ID = '"+str(post_dict['post_id'])+"' ")
                sql = "SELECT USER_ID FROM COMMUNITY_USER_POSTS WHERE (POST_ID = %(post_id)s) AND (COMMUNITY_ID = %(community_id)s) "
                c.execute(sql, {"post_id":post_dict['post_id'], "community_id":community_id})
                rows = c.fetchall()
                for row in rows:
                    post_dict['user_id'] = row[0]

                c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = '"+str(post_dict['user_id'])+"' ")
                rows = c.fetchall()
                for row in rows:
                    post_dict['photo_path'] = row[0]
                
                c.execute("SELECT FULL_NAME FROM USER_TABLE WHERE STD_ID = '"+str(post_dict['user_id'])+"' ")
                rows = c.fetchall()
                for row in rows:
                    post_dict['full_name'] = row[0]

                c.execute("SELECT COUNT(*) FROM COMMUNITY_USER_REPLIES WHERE (POST_ID = %(post_id)s) AND (COMMUNITY_ID = %(community_id)s) ", {'post_id':post_dict['post_id'], "community_id":community_id})
                rows = c.fetchall()
                for row in rows:
                    post_dict['num_comments'] = row[0]
                

                c.execute("SELECT * FROM COMMUNITY_HELP WHERE POST_ID = '"+str(post_dict['post_id'])+"'")
                rows = c.fetchall()
                for row in rows:
                    post_dict['class'] = 'help'

                c.execute("SELECT * FROM COMMUNITY_CAREER WHERE POST_ID = '"+str(post_dict['post_id'])+"'")
                rows = c.fetchall()
                for row in rows:
                    post_dict['class'] = 'career'

                c.execute("SELECT * FROM COMMUNITY_RESEARCH WHERE POST_ID = '"+str(post_dict['post_id'])+"'")
                rows = c.fetchall()
                for row in rows:
                    post_dict['class'] = 'research'

                c.execute("SELECT * FROM COMMUNITY_JOB_POST WHERE POST_ID = '"+str(post_dict['post_id'])+"'")
                rows = c.fetchall()
                for row in rows:
                    post_dict['class'] = 'job'

                if ( (search_std_id is not None) and (len(search_std_id) > 0) ):
                    
                    post_dict['desc_selected'] = description_after_text_search(post_dict['desc'], search_std_id)
                    post_dict['query'] = search_std_id

                all_post_dicts.append(post_dict)

            #==========================Gather Data For Member List==================================

            c.execute("SELECT USER_ID FROM MODERATOR WHERE COMMUNITY_ID = %(community_id)s", {"community_id":community_id})
            rows = c.fetchall()
            for row in rows:
                created_by = row[0]

            user_is_admin = True if created_by == user_id else False

            sql = "SELECT COUNT(*) FROM COMM_MEMBERS WHERE (COMMUNITY_ID = %(community_id)s) AND (USER_ID <> %(user_id)s)"
            c.execute(sql, {"community_id":community_id, "user_id":user_id})
            rows = c.fetchall()
            for row in rows:
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
                                    WHERE (CM.USER_ID = U.STD_ID) AND (CM.USER_ID <> %(user_id)s) AND (CM.COMMUNITY_ID = %(community_id)s)
                                    ORDER BY CM.JOIN_DATE ASC, U.std_id ASC
                                ) A
                            WHERE ROWNUM < %(end_member)s
                        )
                    WHERE RNUM >= %(begin_member)s'''
            
            c.execute(sql, {"end_member":end_member, "begin_member":begin_member, "user_id":user_id, "community_id":community_id})

            members_info = []
            rows = c.fetchall()
            for row in rows:
                member_dict = {}
                member_dict['user_id'] = row[0]
                member_dict['full_name'] = row[1]
                member_dict['joined'] = row[2]

                members_info.append(member_dict)
            
            for idx, member_dict in enumerate(members_info):
                member_dict['photo'] = "dummy_user.png"
                c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = %(user_id)s", {"user_id":member_dict['user_id']})
                rows = c.fetchall()
                for row in rows:
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
                    "post_dicts":all_post_dicts,

                    "is_member_begin":member_is_begin,
                    "is_member_end":member_the_end,
                    "next_member":end_member,
                    "prev_member":(begin_member-5) if begin_member > 5 else 0,
                    "orig_member":start_member_count,

                    "is_requ_begin":0,
                    "is_requ_end":0,
                    "next_requ":0,
                    "prev_requ":0,
                    "orig_requ":0,

                    "is_post_begin":post_is_begin,
                    "is_post_end":post_the_end,
                    "next_post":end_post,
                    "prev_post":(begin_post - 5) if (begin_post > 5) else 0,
                    "orig_post":post_start,
                    "doing_text_search":True if ( (search_std_id is not None) and (len(search_std_id) > 0) ) else False,

                    "search_post_typ":search_post_typ,
                    "search_std_id":search_std_id

                }
                return render(request, "community/detail_community.html", context)
            else:
                c.execute("SELECT COUNT(*) FROM JOIN_REQUEST WHERE COMMUNITY_ID = %(community_id)s ", {"community_id":community_id})
                rows = c.fetchall()
                for row in rows:
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
                                    WHERE (J.USER_ID = U.STD_ID) AND (J.COMMUNITY_ID = %(community_id)s)
                                    ORDER BY J.REQUEST_TIME ASC, U.std_id ASC
                                ) A
                            WHERE ROWNUM < %(end_requ)s
                        )
                    WHERE RNUM >= %(begin_requ)s'''
                
                c.execute(sql, {"end_requ":end_requ, "begin_requ":begin_requ, "community_id":community_id})

                request_infos = []
                rows = c.fetchall()
                for row in rows:
                    request_dict = {}
                    request_dict['user_id'] = row[0]
                    request_dict['full_name'] = row[1]
                    request_dict['time'] = row[2]
                    
                    request_dict['photo'] = "dummy_user.png"

                    

                    request_infos.append(request_dict)

                for idx, request_dict in enumerate(request_infos):
                    request_dict['photo'] = "dummy_user.png"

                    c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = %(user_id)s", {"user_id":request_dict['user_id']})
                    rows = c.fetchall()
                    for row in rows:
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
                    "post_dicts":all_post_dicts,

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

                    "is_post_begin":post_is_begin,
                    "is_post_end":post_the_end,
                    "next_post":end_post,
                    "prev_post":(begin_post - 5) if (begin_post > 5) else 0,
                    "orig_post":post_start,

                    "search_post_typ":search_post_typ,
                    "search_std_id":search_std_id,
                    "doing_text_search":True if ( (search_std_id is not None) and (len(search_std_id) > 0) ) else False,
                }
                return render(request, "community/detail_community.html", context)


            




    else:
        return redirect('SignIn:signin')



def join_request(request, community_id):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()
        user_id = request.session.get('std_id')

        c.execute("INSERT INTO JOIN_REQUEST VALUES (%(community_id)s, %(user_id)s, SYSDATE)", {"community_id":community_id, "user_id":user_id})
        c.execute("COMMIT")

        return HttpResponseRedirect(reverse('community:home', args=(1,1,0,1,0)))
    else:
        return redirect('SignIn:signin')

def cancel_join_request(request, community_id):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()
        user_id = request.session.get('std_id')

        c.execute("DELETE FROM JOIN_REQUEST WHERE (COMMUNITY_ID = %(community_id)s) AND (USER_ID = %(user_id)s) ", {'community_id':community_id, "user_id":user_id})
        c.execute("COMMIT")

        return HttpResponseRedirect(reverse('community:home', args=(1,1,0,1,0)))
    else:
        return redirect('SignIn:signin')

def delete_comment(request, community_id, post_id, comment_id):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()
        user_id = request.session.get('std_id')

        request_from_admin = False
        c.execute("SELECT USER_ID FROM MODERATOR WHERE COMMUNITY_ID = %(community_id)s", {"community_id":community_id})
        rows = c.fetchall()
        for row in rows:
            if user_id == row[0]:
                request_from_admin = True
            else:
                return HttpResponseRedirect(reverse('community:home', args=(1,1,0,1,0)))
        
        if request_from_admin:
            c.execute("DELETE FROM COMMUNITY_USER_REPLIES WHERE USR_REPLS_ROW = %(comment_id)s", {"comment_id":comment_id})
            c.execute("COMMIT")
            return HttpResponseRedirect(reverse('community:detail_post', args=(community_id, post_id, 1)))


    else:
        return redirect('SignIn:signin')

def delete_post(request, community_id, post_id, member_start, requ_start):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()
        user_id = request.session.get('std_id')

        

        request_from_admin = False
        c.execute("SELECT USER_ID FROM MODERATOR WHERE COMMUNITY_ID = %(community_id)s", {"community_id":community_id})
        rows = c.fetchall()
        for row in rows:
            if user_id == row[0]:
                request_from_admin = True
            else:
                return HttpResponseRedirect(reverse('community:home', args=(1,1,0,1,0)))

        if request_from_admin:
            c.execute("DELETE FROM COMMUNITY_POST WHERE POST_ID = %(post_id)s", {"post_id":post_id})
            c.execute("COMMIT")
            return HttpResponseRedirect(reverse('community:detail_community', args=(community_id, member_start, requ_start, 1, 0)))

        
    else:
        return redirect('SignIn:signin')



def delete_group(request, community_id):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()
        user_id = request.session.get('std_id')

        request_from_admin = False
        c.execute("SELECT USER_ID FROM MODERATOR WHERE COMMUNITY_ID = %(community_id)s", {"community_id":community_id})
        rows = c.fetchall()
        for row in rows:
            if user_id == row[0]:
                request_from_admin = True
            else:
                return HttpResponseRedirect(reverse('community:home', args=(1,1,0,1,0)))

        if request_from_admin :
            c.execute("DELETE FROM COMMUNITY WHERE COMMUNITY_ID = %(community_id)s", {'community_id':community_id})
            c.execute("COMMIT")
            return HttpResponseRedirect(reverse('community:home', args=(1,1,0,1,0)))


    else:
        return redirect('SignIn:signin')



def leave_group(request, community_id):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()
        user_id = request.session.get('std_id')

        c.execute("DELETE FROM COMM_MEMBERS WHERE (COMMUNITY_ID = %(community_id)s) AND (USER_ID = %(user_id)s) ", {"community_id":community_id, "user_id":user_id})
        c.execute("COMMIT")

        return HttpResponseRedirect(reverse('community:home', args=(1,1,0,1,0)))
    else:
        return redirect('SignIn:signin')






def join_community(request, community_id, user_id, start_member_count, start_requ_count):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()

        c.execute("INSERT INTO COMM_MEMBERS VALUES (%(community_id)s, %(user_id)s, SYSDATE) ", {"community_id":community_id, "user_id":user_id})
        c.execute("COMMIT")
        return HttpResponseRedirect(reverse('community:detail_community', args=(community_id, start_member_count, start_requ_count, 1, 0)))
    else:
        return redirect('SignIn:signin')

def remove_request(request, community_id, user_id, start_member_count, start_requ_count):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()

        c.execute("DELETE FROM JOIN_REQUEST WHERE (COMMUNITY_ID = %(community_id)s) AND (USER_ID = %(user_id)s) ", {"community_id":community_id, "user_id":user_id})
        c.execute("COMMIT")
        return HttpResponseRedirect(reverse('community:detail_community', args=(community_id, start_member_count, start_requ_count, 1, 0)))
    else:
        return redirect('SignIn:signin')


def make_post(request, community_id):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()
        #-------------------------------------Profile Card---------------------------------
        sql = """ SELECT * from USER_PROFILE WHERE STD_ID = %(std_id)s"""
        row =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchone()
        columnNames = [d[0] for d in c.description]
        
        try:
            data = dict(zip(columnNames,row))
        except:
            print('Cannot Parse Profile')

        #-----------------------------------Skills------------------------------------
        sql = """ SELECT EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
                EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = %(std_id)s GROUP BY EXPERTISE.TOPIC"""
        rows =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchall()
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
        dp_form = DPForm()

        #--------------------------------------Job History--------------------------------
        sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID = %(std_id)s ORDER BY FROM_ DESC"""
        rows =  c.execute(sql,{'std_id':request.session.get('std_id')})
        jobs = rows.fetchall()
        columnNames = [d[0] for d in c.description]
        job_list = []
        for job in jobs:
            try:
                job_list.append(dict(zip(columnNames,job)))
            except:
                print('NULL')

        c.execute("SELECT COMMUNITY_NAME, DESCRIPTION, CRITERIA, DATE_OF_CREATION, TIME_DIFF(DATE_OF_CREATION) FROM COMMUNITY WHERE COMMUNITY_ID = %(community_id)s", {"community_id":community_id})
        rows = c.fetchall()
        for row in rows:
            community_name = row[0]
            description = row[1]
            criteria = row[2]
            creation = row[3]
            creation_ago = row[4]

        context = {
            'unfilled':None, 
            'type':request.GET.get('post_type'), 
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
            "comm_id":community_id
        }        
        return render(request, 'community/make_post.html', context)
    else:
        return redirect('SignIn:signin')


def identify_post_class(request):
    if request.GET.get('reason') is not None :
        return "Help"
    elif request.GET.get('journal') is not None :
        return "Research"
    elif request.GET.get('designation') is not None :
        return "Job Post"
    else:
        return "Career"





def find_unfilled_data(request, post_class, post_attributes):
    unfilled = []
    filled = {}
    for attribute in post_attributes[post_class]:
            if len(request.GET.get(attribute)) == 0:
                unfilled.append(attribute)
            else:
                filled[attribute] = request.GET.get(attribute)
    return unfilled, filled



def form_unfilled_message(unfilled_data):
    txt = ''
    if len(unfilled_data) != 0:
        for attribute in unfilled_data:
            txt += (attribute + ",   ")
        txt += 'missing. Unfilled date data will be filled with SYSDATE.'
    return txt

def modify_c(c):
    rows = c.fetchall()
    data = []
    for row in rows:
        row = str(row)
        for char in "()',":
            row = row.replace(char, "")
        data.append(row)
    return data




def upload_post(request, community_id):

    if "std_id" in request.session:

        conn = db()
        c = conn.cursor()

        user_id = request.session.get('std_id')



        post_attributes = {
            "Help" : ['type_of_help', 'reason', 'cell', 'description'],
            "Career" : ['topic_name', 'description'],
            "Research" : ["topic_name", 'journal', 'doi', 'description'],
            "Job Post" : ['company_name', 'designation', 'location', 'min_requirement', 'description', 'salary']
        }

        post_class = identify_post_class(request)
        
        unfilled_data, filled_data = find_unfilled_data(request, post_class, post_attributes)
        unfilled_data = [data for data in unfilled_data if data != "salary"] 

        cell_wrong_type = False
        salary_wrong_type = False
        if request.GET.get('cell') is not None :
            cell_var = request.GET.get('cell')
            for char in cell_var:
                if char not in "0123456789+-":
                    cell_wrong_type = True
        if request.GET.get('salary') is not None:
            salary_var = request.GET.get('salary')
            for char in salary_var:
                if char not in "1234567890":
                    salary_wrong_type = True


        if (len(unfilled_data) != 0) or (cell_wrong_type) or (salary_wrong_type):
            #-------------------------------------Profile Card---------------------------------
            sql = """ SELECT * from USER_PROFILE WHERE STD_ID = %(std_id)s"""
            row =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchone()
            columnNames = [d[0] for d in c.description]
            
            try:
                data = dict(zip(columnNames,row))
            except:
                print('Cannot Parse Profile')

            #-----------------------------------Skills------------------------------------
            sql = """ SELECT EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
                    EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = %(std_id)s GROUP BY EXPERTISE.TOPIC"""
            rows =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchall()
            skills = {}
            for row in rows:
                skills[row[0]] = row[1]
            dp_form = DPForm()

            #--------------------------------------Job History--------------------------------
            sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID = %(std_id)s ORDER BY FROM_ DESC"""
            rows =  c.execute(sql,{'std_id':request.session.get('std_id')})
            jobs = rows.fetchall()
            columnNames = [d[0] for d in c.description]
            job_list = []
            for job in jobs:
                try:
                    job_list.append(dict(zip(columnNames,job)))
                except:
                    print('NULL')

            c.execute("SELECT COMMUNITY_NAME, DESCRIPTION, CRITERIA, DATE_OF_CREATION, TIME_DIFF(DATE_OF_CREATION) FROM COMMUNITY WHERE COMMUNITY_ID = %(community_id)s", {"community_id":community_id})
            rows = c.fetchall()
            for row in rows:
                community_name = row[0]
                description = row[1]
                criteria = row[2]
                creation = row[3]
                creation_ago = row[4]

            context = {
                'type':post_class,
                'unfilled':True,
                'unfilled_list':unfilled_data,
                'filled_data':filled_data, 
                'cell_wrong':cell_wrong_type, 
                'salary_wrong':salary_wrong_type,
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
                "comm_id":community_id
            }
            return render(request, 'community/make_post.html', context)

        

        date_today = date.today().strftime('%d-%m-%Y')


        if post_class == "Help":
            
            type_of_help = request.GET.get('type_of_help')
            reason = request.GET.get('reason')
            deadline = request.GET.get('deadline')
            cell = request.GET.get('cell')
            description = request.GET.get('description')

            description = description.replace("'", "''")
            reason = reason.replace("'", "''")
            type_of_help = type_of_help.replace("'", "''")

            

            if deadline is None:
                deadline = date_today

            
            #c.execute("INSERT INTO POST (DATE_OF_POST, Description) VALUES (TO_DATE('"+date_today+"', 'dd-mm-yyyy'), '"+description+"')")
            c.execute("INSERT INTO COMMUNITY_POST (DATE_OF_POST, Description) VALUES (SYSDATE, '"+description+"')")
            c.execute("SELECT POST_ID FROM (SELECT POST_ID FROM COMMUNITY_POST ORDER BY POST_ID DESC) WHERE ROWNUM=1")
            post_id = modify_c(c)[0]
            c.execute("INSERT INTO COMMUNITY_USER_POSTS (USER_ID, POST_ID, COMMUNITY_ID) VALUES ('"+str(user_id)+"', '"+post_id+"', '"+str(community_id)+"')")
            c.execute("INSERT INTO COMMUNITY_HELP (POST_ID, TYPE_OF_HELP, REASON, CELL_NO) VALUES ('"+post_id+"', '"+type_of_help+"', '"+reason+"', '"+cell+"')")
            c.execute('COMMIT')

        elif post_class == "Career":
            topic_name = request.GET.get('topic_name')
            description = request.GET.get('description')

            description = description.replace("'", "''")
            topic_name = topic_name.replace("'", "''")


            c.execute("INSERT INTO COMMUNITY_POST (DATE_OF_POST, Description) VALUES (SYSDATE, '"+description+"')")
            c.execute("SELECT POST_ID FROM (SELECT POST_ID FROM COMMUNITY_POST ORDER BY POST_ID DESC) WHERE ROWNUM=1")
            post_id = modify_c(c)[0]
            c.execute("INSERT INTO COMMUNITY_USER_POSTS (USER_ID, POST_ID, COMMUNITY_ID) VALUES ('"+str(user_id)+"', '"+post_id+"', '"+str(community_id)+"')")
            c.execute("INSERT INTO COMMUNITY_CAREER (POST_ID, TOPIC_NAME) VALUES ('"+post_id+"', '"+topic_name+"')")
            c.execute('COMMIT')

        elif post_class == "Research":
            topic_name = request.GET.get('topic_name')
            description = request.GET.get('description')
            description = description.replace("'", "''")
            journal = request.GET.get('journal')
            doi = request.GET.get('doi')
            print(date_of_publication)
            topic_name = topic_name.replace("'", "''")
            journal = journal.replace("'", "''")
            doi = doi.replace("'", "''")

            if (date_of_publication is None) or (len(date_of_publication) == 0):
                date_of_publication = date_today
                date_of_publication = str(date_of_publication)
            else :
                date_of_publication = date_of_publication[8:10] + '-' + date_of_publication[5:7] + '-' + date_of_publication[:4]
            



            c.execute("INSERT INTO COMMUNITY_POST (DATE_OF_POST, Description) VALUES (SYSDATE, '"+description+"')")
            c.execute("SELECT POST_ID FROM (SELECT POST_ID FROM COMMUNITY_POST ORDER BY POST_ID DESC) WHERE ROWNUM=1")
            post_id = modify_c(c)[0]
            c.execute("INSERT INTO COMMUNITY_USER_POSTS (USER_ID, POST_ID, COMMUNITY_ID) VALUES ('"+str(user_id)+"', '"+post_id+"', '"+str(community_id)+"')")
            c.execute("INSERT INTO COMMUNITY_RESEARCH (POST_ID, TOPIC_NAME, DATE_OF_PUBLICATION, JOURNAL, DOI) VALUES ('"+post_id+"', '"+topic_name+"', TO_DATE('"+date_of_publication+"', 'dd-mm-yyyy'), '"+journal+"', '"+doi+"')")
            c.execute('COMMIT')
        else:
            company_name = request.GET.get('company_name')
            designation = request.GET.get('designation')
            location = request.GET.get('location')
            min_requirement = request.GET.get('min_requirement')
            salary = request.GET.get('salary')
            description = request.GET.get('description')
            description = description.replace("'", "''")

            c.execute("INSERT INTO COMMUNITY_POST (DATE_OF_POST, Description) VALUES (SYSDATE, '"+description+"')")
            c.execute("SELECT POST_ID FROM (SELECT POST_ID FROM COMMUNITY_POST ORDER BY POST_ID DESC) WHERE ROWNUM=1")
            post_id = modify_c(c)[0]
            c.execute("INSERT INTO COMMUNITY_USER_POSTS (USER_ID, POST_ID, COMMUNITY_ID) VALUES ('"+str(user_id)+"', '"+post_id+"', '"+str(community_id)+"')")
            c.execute("INSERT INTO COMMUNITY_JOB_POST (POST_ID, COMPANY_NAME, DESIGNATION, LOCATION, REQUIREMENTs, SALARY) VALUES ('"+post_id+"', '"+company_name+"', '"+designation+"', '"+location+"', '"+min_requirement+"', '"+salary+"')")
            c.execute('COMMIT')

        conn.close()

        

        return HttpResponseRedirect(reverse('community:detail_community', args=(community_id, 1, 1, 1, 0)))
    else:
        return redirect('SignIn:signin')


def upload_comment(request, community_id, post_id):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()
        print(community_id)

        user_id = request.session.get('std_id')

        comment_body = request.GET.get('comment_body')
        comment_body = comment_body.replace("'", "''")
        if len(comment_body) != 0:
            c.execute("INSERT INTO COMMUNITY_USER_REPLIES (USER_ID, POST_ID, COMMUNITY_ID, TEXT, TIMESTAMP) VALUES ('"+str(user_id)+"', '"+str(post_id)+"', '"+str(community_id)+"', '"+comment_body+"', SYSDATE)")
            c.execute('COMMIT')

        return HttpResponseRedirect(reverse('community:detail_post', args=(community_id, post_id, 1)))
    else:
        return redirect('SignIn:signin')



def detail_post(request, community_id, post_id, start_from):
    if "std_id" in request.session:
        conn = db()
        c = conn.cursor()

        user_id = request.session.get('std_id')

        c.execute('SELECT COUNT(*) FROM COMMUNITY_USER_REPLIES WHERE POST_ID = %(post_id)s', {'post_id':post_id})
        rows = c.fetchall()
        for row in rows:
            num_comments = row[0]

        begin_comment = start_from
        end_comment = (start_from + 10) if (start_from + 10) <= num_comments else num_comments+1
        the_end = (num_comments == end_comment-1)
        is_begin = (begin_comment == 1 )


        date_today = date.today().strftime('%d-%m-%Y')
                        

        sql= '''SELECT * 
                FROM(
                        SELECT A.*, ROWNUM RNUM
                        FROM (SELECT USR_REPLS_ROW, USER_ID, POST_ID, COMMUNITY_ID, TEXT, TIME_DIFF(TIMESTAMP) FROM COMMUNITY_USER_REPLIES  WHERE POST_ID = %(post_id)s ORDER BY TIMESTAMP DESC, POST_ID DESC) A
                        WHERE ROWNUM < %(end_comment)s
                    )
                WHERE RNUM >= %(begin_comment)s'''

        c.execute(sql, {'post_id':post_id, 'end_comment':end_comment, 'begin_comment':begin_comment})

        comment_dicts = []
        rows = c.fetchall()
        for row in rows:
            comment_dict = {}
            comment_dict['comment_id'] = row[0]
            comment_dict['user_id'] = row[1]
            comment_dict['post_id'] = row[2]
            comment_dict['community_id'] = row[3]
            comment_dict['text'] = row[4]
            comment_dict['timestamp'] = row[5]
    
            comment_dicts.append(comment_dict)
        
        for i in range(len(comment_dicts)):

            c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = '"+str(comment_dicts[i]['user_id'])+"' ")
            rows = c.fetchall()
            for row in rows:
                comment_dicts[i]['photo_path'] = row[0]
            
            c.execute("SELECT FULL_NAME FROM USER_TABLE WHERE STD_ID = '"+str(comment_dicts[i]['user_id'])+"' ")
            rows = c.fetchall()
            for row in rows:
                comment_dicts[i]['full_name'] = row[0]

        c.execute("SELECT * FROM COMMUNITY_POST WHERE POST_ID = '"+str(post_id)+"' ")

        post_detail = {}
        rows = c.fetchall()
        for row in rows:
            post_detail['date'] = row[1]
            post_detail['desc'] = row[2]
            post_detail['post_id'] = post_id

        c.execute("SELECT USER_ID FROM COMMUNITY_USER_POSTS WHERE POST_ID = '"+str(post_id)+"' ")
        rows = c.fetchall()
        for row in rows:
            post_detail['user_id'] = row[0]
        
        
        
        c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = '"+str(post_detail['user_id'])+"' ")
        rows = c.fetchall()
        for row in rpws:
            post_detail['photo_path'] = row[0]

        c.execute("SELECT FULL_NAME FROM USER_TABLE WHERE STD_ID = '"+str(post_detail['user_id'])+"' ")
        rows = c.fetchall()
        for row in rows:
            post_detail['full_name'] = row[0]

        c.execute("SELECT * FROM COMMUNITY_HELP WHERE POST_ID = '"+str(post_id)+"'")
        rows = c.fetchall()
        for row in rows:
            post_detail['type_of_help'] = row[1]
            post_detail['reason'] = row[2]
            post_detail['cell'] = row[3]
            post_detail['class'] = 'Help'

        c.execute("SELECT * FROM COMMUNITY_CAREER WHERE POST_ID = '"+str(post_id)+"'")
        rows = c.fetchall()
        for row in rows:
            post_detail['topic_name'] = row[1]
            post_detail['class'] = 'Career'

        c.execute("SELECT * FROM COMMUNITY_RESEARCH WHERE POST_ID = '"+str(post_id)+"'")
        rows = c.fetchall()
        for row in rows:
            post_detail['topic_name'] = row[1]
            post_detail['date_of_publication'] = row[2]
            post_detail['journal'] = row[3]
            post_detail['doi'] = row[4]
            post_detail['class'] = 'Research'

        c.execute("SELECT * FROM COMMUNITY_JOB_POST WHERE POST_ID = '"+str(post_id)+"'")
        rows = c.fetchall()
        for row in rows:
            post_detail['company_name'] = row[1]
            post_detail['location'] = row[2]
            post_detail['requirements'] = row[3]
            post_detail['designation'] = row[4]
            post_detail['salary'] = row[5]
            post_detail['class'] = 'Job'

        c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = %(std_id)s", {'std_id': user_id})
        rows = c.fetchall()
        for row in rows:
            post_detail['commenter_photo'] = row[0]
        #-------------------------------------Profile Card---------------------------------
        sql = """ SELECT * from USER_PROFILE WHERE STD_ID = %(std_id)s"""
        row =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchone()
        columnNames = [d[0] for d in c.description]
        
        try:
            data = dict(zip(columnNames,row))
        except:
            print('Cannot Parse Profile')

        #-----------------------------------Skills------------------------------------
        sql = """ SELECT EXPERTISE.TOPIC, COUNT( ENDORSE.GIVER_ID) AS C from EXPERTISE LEFT JOIN ENDORSE ON 
                EXPERTISE.STD_ID = ENDORSE.TAKER_ID AND EXPERTISE.TOPIC = ENDORSE.TOPIC WHERE EXPERTISE.STD_ID = %(std_id)s GROUP BY EXPERTISE.TOPIC"""
        rows =  c.execute(sql,{'std_id':request.session.get('std_id')}).fetchall()
        skills = {}
        for row in rows:
            skills[row[0]] = row[1]
        dp_form = DPForm()

        #--------------------------------------Job History--------------------------------
        sql = """ SELECT * from WORKS JOIN INSTITUTE USING(INSTITUTE_ID) WHERE STD_ID = %(std_id)s ORDER BY FROM_ DESC"""
        rows =  c.execute(sql,{'std_id':request.session.get('std_id')})
        jobs = rows.fetchall()
        columnNames = [d[0] for d in c.description]
        job_list = []
        for job in jobs:
            try:
                job_list.append(dict(zip(columnNames,job)))
            except:
                print('NULL')


        #======================COMMUNITY INFO=================
        c.execute("SELECT COMMUNITY_NAME, DESCRIPTION, CRITERIA, TIME_DIFF(DATE_OF_CREATION) FROM COMMUNITY WHERE COMMUNITY_ID = %(community_id)s", {"community_id":community_id})
        for row in c:
            community_name = row[0]
            description = row[1]
            criteria = row[2]
            created = row[3]

        user_is_admin = False
        c.execute("SELECT USER_ID FROM MODERATOR WHERE COMMUNITY_ID = %(community_id)s", {'community_id':community_id})
        for row in c:
            if user_id == row[0]:
                user_is_admin = True
        
        context = {
            'detail':post_detail, 
            'comment_dicts':comment_dicts,
            'is_begin':is_begin,
            'the_end':the_end,
            'next_id':end_comment,
            'prev_id':(begin_comment-10) if begin_comment > 10 else 0,
            'post_id':post_id,
            'data':data,
            'skills':skills,
            'edit':True,
            'dp':dp_form,
            'job':job_list,
            "comm_id":community_id,
            "community_name":community_name,
            "description":description,
            "criteria":criteria,
            "created":created,
            "is_admin":user_is_admin,
        }

        return render(request, 'community/detail_post.html', context)
    else:
        return redirect('SignIn:signin')