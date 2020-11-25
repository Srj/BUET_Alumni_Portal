from django.shortcuts import render,redirect
from django.http import HttpResponse, HttpResponseRedirect, QueryDict
from Alumni_Portal.utils import db,encrypt_password
from django.urls import reverse
import cx_Oracle
import datetime
from django.core.files.storage import FileSystemStorage
from datetime import date
import json
# Create your views here.


def modify_c(c):
    data = []
    for row in c:
        row = str(row)
        for char in "()',":
            row = row.replace(char, "")
        data.append(row)
    return data


def all_post(request, start_from, change):

    conn = db()
    c = conn.cursor()

    user_id = request.session.get('std_id')

    if change == 0:
        # set to default
        request.session['search_std_id'] = ''
        request.session['search_post_typ'] = None
        search_post_typ = None
        search_std_id = ''
    elif change == 1:
        #dont change
        search_post_typ = request.session['search_post_typ']
        search_std_id = request.session['search_std_id']
    elif change == 2:
        #update
        search_std_id = request.GET.get('search_std_id')
        search_post_typ = request.GET.get('search_post_typ')

        request.session['search_std_id'] = search_std_id
        request.session['search_post_typ'] = search_post_typ


    #search_std_id = request.GET.get('search_std_id')
    #search_post_typ = request.GET.get('search_post_typ')
    print(search_post_typ)
    
    if (search_post_typ is None) and ( (search_std_id is None) or (len(search_std_id) == 0 ) ):
        c.execute('Select count(*) from post')

    if (search_post_typ is None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
        sql = '''SELECT COUNT(*) FROM USER_POSTS WHERE USER_ID = :search_std_id'''
        c.execute(sql, {'search_std_id':search_std_id})

    if (search_post_typ is not None) and ((search_std_id is None) or (len(search_std_id) == 0 )):
        if search_post_typ == 'Help':
            c.execute('SELECT COUNT(*) FROM HELP')
        if search_post_typ == 'Career':
            c.execute('SELECT COUNT(*) FROM CAREER')
        if search_post_typ == 'Research':
            c.execute('SELECT COUNT(*) FROM RESEARCH')
        if search_post_typ == 'Job Post':
            c.execute('SELECT COUNT(*) FROM JOB_POST')

    if (search_post_typ is not None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
        if search_post_typ == 'Help':
            sql = '''SELECT COUNT(*) FROM USER_POSTS U, HELP H WHERE (H.POST_ID = U.POST_ID) AND (U.USER_ID = :search_std_id)'''
            c.execute(sql, {'search_std_id':search_std_id})
        if search_post_typ == 'Career':
            sql = '''SELECT COUNT(*) FROM USER_POSTS U, CAREER C WHERE (C.POST_ID = U.POST_ID) AND (U.USER_ID = :search_std_id)'''
            c.execute(sql, {'search_std_id':search_std_id})
        if search_post_typ == 'Research':
            sql = '''SELECT COUNT(*) FROM USER_POSTS U, RESEARCH R WHERE (R.POST_ID = U.POST_ID) AND (U.USER_ID = :search_std_id)'''
            c.execute(sql, {'search_std_id':search_std_id})
        if search_post_typ == 'Job Post':
            sql = '''SELECT COUNT(*) FROM USER_POSTS U, JOB_POST J WHERE (j.POST_ID = U.POST_ID) AND (U.USER_ID = :search_std_id)'''
            c.execute(sql, {'search_std_id':search_std_id})
    
    num_post = modify_c(c)[0]
    if num_post == '0':
        show = {
            #'user':user,
            'no_post':True,
        }
        return render(request, 'post/all_post.html', show)

    else:
        num_post = int(num_post)

        begin_post = start_from
        end_post = (start_from + 10) if (start_from + 10) <= num_post else num_post+1
        the_end = (num_post == end_post-1)
        is_begin = (begin_post == 1 )

        if (search_post_typ is None) and ( (search_std_id is None) or (len(search_std_id) == 0 ) ):
            sql = '''
                    SELECT * 
                    FROM(
                            SELECT A.*, ROWNUM RNUM
                            FROM (SELECT POST_ID, TIME_DIFF(DATE_OF_POST), DESCRIPTION FROM POST ORDER BY DATE_OF_POST DESC, POST_ID DESC) A
                            WHERE ROWNUM < :end_post
                        )
                    WHERE RNUM >= :begin_post'''

            c.execute(sql, {'end_post':end_post, 'begin_post':begin_post})
            all_post = [row for row in c]
        
        if (search_post_typ is None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
            sql = '''
                    SELECT * 
                    FROM(
                            SELECT A.*, ROWNUM RNUM
                            FROM(
                                    SELECT P.POST_ID, TIME_DIFF(P.DATE_OF_POST), P.DESCRIPTION
                                    FROM POST P, USER_POSTS U
                                    WHERE (P.POST_ID = U.POST_ID) AND (U.USER_ID = :search_std_id)
                                    ORDER BY P.DATE_OF_POST DESC, P.POST_ID DESC
                                ) A
                            WHERE ROWNUM < :end_post
                        )
                    WHERE RNUM >= :begin_post'''

            c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, 'search_std_id':search_std_id})
            all_post = [row for row in c]
        

        if (search_post_typ is not None) and ((search_std_id is None) or (len(search_std_id) == 0 )):
            if search_post_typ == 'Help':
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM(
                                        SELECT P.POST_ID, TIME_DIFF(P.DATE_OF_POST), P.DESCRIPTION
                                        FROM POST P, HELP H
                                        WHERE (P.POST_ID = H.POST_ID)
                                        ORDER BY P.DATE_OF_POST DESC, P.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < :end_post
                            )
                        WHERE RNUM >= :begin_post'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post})
                all_post = [row for row in c]
            if search_post_typ == 'Career':
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM(
                                        SELECT P.POST_ID, TIME_DIFF(P.DATE_OF_POST), P.DESCRIPTION
                                        FROM POST P, CAREER C
                                        WHERE (P.POST_ID = C.POST_ID)
                                        ORDER BY P.DATE_OF_POST DESC, P.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < :end_post
                            )
                        WHERE RNUM >= :begin_post'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post})
                all_post = [row for row in c]
            if search_post_typ == 'Research':
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM(
                                        SELECT P.POST_ID, TIME_DIFF(P.DATE_OF_POST), P.DESCRIPTION
                                        FROM POST P, RESEARCH R
                                        WHERE (P.POST_ID = R.POST_ID)
                                        ORDER BY P.DATE_OF_POST DESC, P.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < :end_post
                            )
                        WHERE RNUM >= :begin_post'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post})
                all_post = [row for row in c]
            if search_post_typ == 'Job Post':
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM(
                                        SELECT P.POST_ID, TIME_DIFF(P.DATE_OF_POST), P.DESCRIPTION
                                        FROM POST P, JOB_POST J
                                        WHERE (P.POST_ID = J.POST_ID)
                                        ORDER BY P.DATE_OF_POST DESC, P.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < :end_post
                            )
                        WHERE RNUM >= :begin_post'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post})
                all_post = [row for row in c]

        if (search_post_typ is not None) and ( (search_std_id is not None) and (len(search_std_id) > 0) ):
            if search_post_typ == 'Help':
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM(
                                        SELECT P.POST_ID, TIME_DIFF(P.DATE_OF_POST), P.DESCRIPTION
                                        FROM POST P, HELP H, USER_POSTS U
                                        WHERE (P.POST_ID = H.POST_ID) AND (P.POST_ID = U.POST_ID) AND (U.USER_ID = :search_std_id)
                                        ORDER BY P.DATE_OF_POST DESC, P.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < :end_post
                            )
                        WHERE RNUM >= :begin_post'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, 'search_std_id':search_std_id})
                all_post = [row for row in c]
            if search_post_typ == 'Career':
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM(
                                        SELECT P.POST_ID, TIME_DIFF(P.DATE_OF_POST), P.DESCRIPTION
                                        FROM POST P, CAREER C, USER_POSTS U
                                        WHERE (P.POST_ID = C.POST_ID) AND (P.POST_ID = U.POST_ID) AND (U.USER_ID = :search_std_id)
                                        ORDER BY P.DATE_OF_POST DESC, P.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < :end_post
                            )
                        WHERE RNUM >= :begin_post'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, 'search_std_id':search_std_id})
                all_post = [row for row in c]
            if search_post_typ == 'Research':
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM(
                                        SELECT P.POST_ID, TIME_DIFF(P.DATE_OF_POST), P.DESCRIPTION
                                        FROM POST P, RESEARCH R, USER_POSTS U
                                        WHERE (P.POST_ID = R.POST_ID) AND (P.POST_ID = U.POST_ID) AND (U.USER_ID = :search_std_id)
                                        ORDER BY P.DATE_OF_POST DESC, P.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < :end_post
                            )
                        WHERE RNUM >= :begin_post'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, 'search_std_id':search_std_id})
                all_post = [row for row in c]
            if search_post_typ == 'Job Post':
                sql = '''
                        SELECT * 
                        FROM(
                                SELECT A.*, ROWNUM RNUM
                                FROM(
                                        SELECT P.POST_ID, TIME_DIFF(P.DATE_OF_POST), P.DESCRIPTION
                                        FROM POST P, JOB_POST J, USER_POSTS U
                                        WHERE (P.POST_ID = J.POST_ID) AND (P.POST_ID = U.POST_ID) AND (U.USER_ID = :search_std_id)
                                        ORDER BY P.DATE_OF_POST DESC, P.POST_ID DESC
                                    ) A
                                WHERE ROWNUM < :end_post
                            )
                        WHERE RNUM >= :begin_post'''

                c.execute(sql, {'end_post':end_post, 'begin_post':begin_post, 'search_std_id':search_std_id})
                all_post = [row for row in c]
        

        all_post_dicts = []
        for post in all_post:
            post_dict = {}
            post_dict['post_id'] = post[0]
            post_dict['date'] = post[1]
            post_dict['desc'] = post[2]

            c.execute("SELECT USER_ID FROM USER_POSTS WHERE POST_ID = '"+str(post_dict['post_id'])+"' ")
            for row in c:
                user_id = row[0]
                post_dict['user_id'] = user_id

            c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = '"+str(user_id)+"' ")
            for row in c:
                post_dict['photo_path'] = row[0]
            
            c.execute("SELECT FULL_NAME FROM USER_TABLE WHERE STD_ID = '"+str(user_id)+"' ")
            for row in c:
                post_dict['full_name'] = row[0]

            c.execute("SELECT COUNT(*) FROM USER_REPLIES WHERE POST_ID = :post_id", {'post_id':post_dict['post_id']})
            for row in c:
                post_dict['num_comments'] = row[0]
            

            c.execute("SELECT * FROM HELP WHERE POST_ID = '"+str(post_dict['post_id'])+"'")
            for row in c:
                post_dict['class'] = 'help'

            c.execute("SELECT * FROM CAREER WHERE POST_ID = '"+str(post_dict['post_id'])+"'")
            for row in c:
                post_dict['class'] = 'career'

            c.execute("SELECT * FROM RESEARCH WHERE POST_ID = '"+str(post_dict['post_id'])+"'")
            for row in c:
                post_dict['class'] = 'research'

            c.execute("SELECT * FROM JOB_POST WHERE POST_ID = '"+str(post_dict['post_id'])+"'")
            for row in c:
                post_dict['class'] = 'job'

            all_post_dicts.append(post_dict)

        
        show = {
            'no_post':False,
            'post_dicts':all_post_dicts,
            'is_begin':is_begin,
            'the_end':the_end,
            'next_id':end_post,
            'prev_id':(begin_post-10) if begin_post > 10 else 0,
            'search_post_typ':search_post_typ,
            'search_std_id':search_std_id,
        }
        
        return render(request, 'post/all_post.html', show)






def upload_comment(request, post_id):
    conn = db()
    c = conn.cursor()

    user_id = request.session.get('std_id')

    comment_body = request.GET.get('comment_body')
    comment_body = comment_body.replace("'", "''")
    if len(comment_body) != 0:
        c.execute("INSERT INTO USER_REPLIES (USER_ID, POST_ID, TEXT, TIMESTAMP) VALUES ('"+str(user_id)+"', '"+str(post_id)+"', '"+comment_body+"', SYSDATE)")
        c.execute('COMMIT')

    return HttpResponseRedirect(reverse('post:detail_post', args=(post_id, 1)))



def detail_post(request, post_id, start_from):
    conn = db()
    c = conn.cursor()

    user_id = request.session.get('std_id')

    c.execute('SELECT COUNT(*) FROM USER_REPLIES WHERE POST_ID = :post_id', {'post_id':post_id})
    for row in c:
        num_comments = row[0]

    begin_comment = start_from
    end_comment = (start_from + 10) if (start_from + 10) <= num_comments else num_comments+1
    the_end = (num_comments == end_comment-1)
    is_begin = (begin_comment == 1 )


    date_today = date.today().strftime('%d-%m-%Y')
                    

    sql= '''SELECT * 
            FROM(
                    SELECT A.*, ROWNUM RNUM
                    FROM (SELECT USR_REPLS_ROW, USER_ID, POST_ID, TEXT, TIME_DIFF(TIMESTAMP) FROM USER_REPLIES  WHERE POST_ID = :post_id ORDER BY TIMESTAMP DESC, POST_ID DESC) A
                    WHERE ROWNUM < :end_comment
                )
            WHERE RNUM >= :begin_comment'''

    c.execute(sql, {'post_id':post_id, 'end_comment':end_comment, 'begin_comment':begin_comment})

    comment_dicts = []
    for row in c:
        comment_dict = {}
        comment_dict['user_id'] = row[1]
        comment_dict['post_id'] = row[2]
        comment_dict['text'] = row[3]
        comment_dict['timestamp'] = row[4]
 
        comment_dicts.append(comment_dict)
    
    for i in range(len(comment_dicts)):

        c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = '"+str(comment_dicts[i]['user_id'])+"' ")
        for row in c:
            comment_dicts[i]['photo_path'] = row[0]
        
        c.execute("SELECT FULL_NAME FROM USER_TABLE WHERE STD_ID = '"+str(comment_dicts[i]['user_id'])+"' ")
        for row in c:
            comment_dicts[i]['full_name'] = row[0]

    c.execute("SELECT * FROM POST WHERE POST_ID = '"+str(post_id)+"' ")

    post_detail = {}
    for row in c:
        post_detail['date'] = row[1]
        post_detail['desc'] = row[2]
        post_detail['post_id'] = post_id

    c.execute("SELECT USER_ID FROM USER_POSTS WHERE POST_ID = '"+str(post_id)+"' ")
    for row in c:
        post_detail['user_id'] = row[0]
    
    
    
    c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = '"+str(post_detail['user_id'])+"' ")
    for row in c:
        post_detail['photo_path'] = row[0]

    c.execute("SELECT FULL_NAME FROM USER_TABLE WHERE STD_ID = '"+str(post_detail['user_id'])+"' ")
    for row in c:
        post_detail['full_name'] = row[0]

    c.execute("SELECT * FROM HELP WHERE POST_ID = '"+str(post_id)+"'")
    for row in c:
        post_detail['type_of_help'] = row[1]
        post_detail['reason'] = row[2]
        post_detail['cell'] = row[3]
        post_detail['class'] = 'Help'

    c.execute("SELECT * FROM CAREER WHERE POST_ID = '"+str(post_id)+"'")
    for row in c:
        post_detail['photo'] = row[1]
        post_detail['class'] = 'Career'

    c.execute("SELECT * FROM RESEARCH WHERE POST_ID = '"+str(post_id)+"'")
    for row in c:
        post_detail['topic_name'] = row[1]
        post_detail['date_of_publication'] = row[2]
        post_detail['journal'] = row[3]
        post_detail['doi'] = row[4]
        post_detail['class'] = 'Research'

    c.execute("SELECT * FROM JOB_POST WHERE POST_ID = '"+str(post_id)+"'")
    for row in c:
        post_detail['company_name'] = row[1]
        post_detail['location'] = row[2]
        post_detail['requirements'] = row[3]
        post_detail['designation'] = row[4]
        post_detail['salary'] = row[5]
        post_detail['class'] = 'Job'

    c.execute("SELECT PHOTO FROM PROFILE WHERE STD_ID = :std_id", {'std_id': user_id})
    for row in c:
        post_detail['commenter_photo'] = row[0]
    
    


    return render(request, 
                'post/detail_post.html', 
                {
                    'detail':post_detail, 
                    'comment_dicts':comment_dicts,
                    'is_begin':is_begin,
                    'the_end':the_end,
                    'next_id':end_comment,
                    'prev_id':(begin_comment-10) if begin_comment > 10 else 0,
                    'post_id':post_id
                }
            )






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

def make_post(request):
    return render(request, 'post/make_post.html', {'type':request.GET.get('post_type'), 'unfilled':None})


def upload_post(request):

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
        return render(request, 'post/make_post.html', {'type':post_class, 'unfilled':True, 'unfilled_list':unfilled_data, 'filled_data':filled_data, 'cell_wrong':cell_wrong_type, 'salary_wrong':salary_wrong_type})

    

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
        c.execute("INSERT INTO POST (DATE_OF_POST, Description) VALUES (SYSDATE, '"+description+"')")
        c.execute("SELECT POST_ID FROM (SELECT POST_ID FROM POST ORDER BY POST_ID DESC) WHERE ROWNUM=1")
        post_id = modify_c(c)[0]
        c.execute("INSERT INTO USER_POSTS (USER_ID, POST_ID) VALUES ('"+str(user_id)+"', '"+post_id+"')")
        c.execute("INSERT INTO HELP (POST_ID, TYPE_OF_HELP, REASON, CELL_NO) VALUES ('"+post_id+"', '"+type_of_help+"', '"+reason+"', '"+cell+"')")
        c.execute('COMMIT')

    elif post_class == "Career":
        topic_name = request.GET.get('topic_name')
        description = request.GET.get('description')

        description = description.replace("'", "''")
        topic_name = topic_name.replace("'", "''")


        c.execute("INSERT INTO POST (DATE_OF_POST, Description) VALUES (SYSDATE, '"+description+"')")
        c.execute("SELECT POST_ID FROM (SELECT POST_ID FROM POST ORDER BY POST_ID DESC) WHERE ROWNUM=1")
        post_id = modify_c(c)[0]
        c.execute("INSERT INTO USER_POSTS (USER_ID, POST_ID) VALUES ('"+str(user_id)+"', '"+post_id+"')")
        c.execute("INSERT INTO CAREER (POST_ID) VALUES ('"+post_id+"')")
        c.execute('COMMIT')

    elif post_class == "Research":
        topic_name = request.GET.get('topic_name')
        description = request.GET.get('description')
        description = description.replace("'", "''")
        journal = request.GET.get('journal')
        doi = request.GET.get('doi')
        date_of_publication = request.GET.get('date_of_publication')
        topic_name = topic_name.replace("'", "''")
        journal = journal.replace("'", "''")
        doi = doi.replace("'", "''")

        if date_of_publication is None:
            date_of_publication = date_today
        else :
            date_of_publication = date_of_publication[8:10] + '-' + date_of_publication[5:7] + '-' + date_of_publication[:4]



        c.execute("INSERT INTO POST (DATE_OF_POST, Description) VALUES (SYSDATE, '"+description+"')")
        c.execute("SELECT POST_ID FROM (SELECT POST_ID FROM POST ORDER BY POST_ID DESC) WHERE ROWNUM=1")
        post_id = modify_c(c)[0]
        c.execute("INSERT INTO USER_POSTS (USER_ID, POST_ID) VALUES ('"+str(user_id)+"', '"+post_id+"')")
        c.execute("INSERT INTO RESEARCH (POST_ID, TOPIC_NAME, DATE_OF_PUBLICATION, JOURNAL, DOI) VALUES ('"+post_id+"', '"+topic_name+"', TO_DATE('"+date_of_publication+"', 'dd-mm-yyyy'), '"+journal+"', '"+doi+"')")
        c.execute('COMMIT')
    else:
        company_name = request.GET.get('company_name')
        designation = request.GET.get('designation')
        location = request.GET.get('location')
        min_requirement = request.GET.get('min_requirement')
        salary = request.GET.get('salary')
        description = request.GET.get('description')
        description = description.replace("'", "''")

        c.execute("INSERT INTO POST (DATE_OF_POST, Description) VALUES (SYSDATE, '"+description+"')")
        c.execute("SELECT POST_ID FROM (SELECT POST_ID FROM POST ORDER BY POST_ID DESC) WHERE ROWNUM=1")
        post_id = modify_c(c)[0]
        c.execute("INSERT INTO USER_POSTS (USER_ID, POST_ID) VALUES ('"+str(user_id)+"', '"+post_id+"')")
        c.execute("INSERT INTO JOB_POST (POST_ID, COMPANY_NAME, DESIGNATION, LOCATION, REQUIREMENTs, SALARY) VALUES ('"+post_id+"', '"+company_name+"', '"+designation+"', '"+location+"', '"+min_requirement+"', '"+salary+"')")
        c.execute('COMMIT')

    conn.close()

    

    return HttpResponseRedirect(reverse('post:all_post', args=(1, 0)))
