from django.shortcuts import render
import psycopg2
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
import jwt
from resource_allocation.auth_middelware import *

#------DATABASE_CONNECTION--------
conn = psycopg2.connect(
    dbname="dwr_staging",
    user="root",
    password="password",
    host="localhost",
    port="5432"
)

def get_token(request):
    try:
        token_Get=request.headers['Authorization'].split("Bearer ")[1]
        secret_key =  'dSUNYPjdhqSqRrowcRuR30uSiHNw'

        decoded_token = jwt.decode(token_Get, secret_key, algorithms='HS256')
        decoded_token = str(decoded_token['id'])

        return decoded_token
    except Exception as e:
            return JsonResponse({"Error":e})



data_list = []
database = conn.cursor()

#-----------GETTING_ALL_USERS------------
database.execute("""SELECT * FROM public.user""")
assign = database.fetchall()

#-----------GETTING_ALL_ASSIGN_PROJECTS--------
database.execute("""SELECT * FROM resource_allocation""")
emp_project_data = database.fetchall()

#----------GETTING_ALL_PROJECTS----------
database.execute("""SELECT * FROM project""")
all_project = database.fetchall()


def project_info(id):
    dictt = {}
    for i in all_project:
        if i[0] == id:
            dictt = {
            'projectID':i[2],
            'projectCode':i[1],
            'projectName' : i[3],
            }
    return dictt


def project_data(id):
    projects = []

    for j in emp_project_data:
        if j[6] == id:
            pro = project_info(j[7])
            projects.append(
                {
                'projectID':pro['projectID'],
                'projectCode':pro['projectCode'],
                'projectName' : pro['projectName'],
                'assignDate' : j[2],
                'startDate': j[8],
                'dueDate' : j[3],
                'priority' : j[4],
                'status' : j[5]}
                )
    return projects


def data(id):
    emp_list = []
    for i in assign:
        if i[7] == str(id):
            data = project_data(i[28])
            if data != []:
                emp_list.append({
                'userID': i[28],
                'name': i[1],
                'email': i[2],
                'project': data,
                })
            else:
                emp_list.append({
                'userID': i[28],
                'name': i[1],
                'email': i[2],
                })

    return emp_list


#-------GETTING_ALL_DATA-------
@csrf_exempt
def all_data(request):
    try:
        if request.method == 'GET':
            manager = request.GET.get('user_id')
            print('-----=-=-=-=-',manager)

            with conn.cursor() as cursor:

                #-------------GETTING_MANAGER_DATA---------------
                cursor.execute("""SELECT * FROM public."user" WHERE "repotingManagerId" = %s""", (manager,))
                manager_name = cursor.fetchall()


                for row in manager_name:
                    print('===========row)row)',row)
                    if row[4] == 'true':

                        emps = data(row[28])

                        if emps != []:
                            data_list.append({
                            'userID': row[28],
                            'name': row[1],
                            'email': row[2],
                            'isRM' : row[4],
                            'role' : row[5],
                            'assignee':emps,
                            })
                        else:
                            data_list.append({
                            'userID': row[28],
                            'name': row[1],
                            'email': row[2],
                            'isRM' : row[4],
                            'role' : row[5], 
                            })

                    else:
                        data_list.append({
                        'userID': row[28],
                        'name': row[1],
                        'email': row[2],
                        'isRM' : row[4],
                        'role' : row[5],

                    })

                # try:
                #     #-------------GETTING_ALL_PROJECTS_OF_USER-----------------
                #     cursor.execute("""SELECT * FROM resource_allocation WHERE user_id = %s""", (row[28],))
                #     emp_projeect_data = cursor.fetchall()

                #     #------STORE_PROJECT_DATA------
                #     projects = []
                #     if emp_projeect_data != []:

                #         for project in emp_projeect_data:

                #             #--------GETTING_PROJECT_NAME-------
                #             cursor.execute("""SELECT * FROM public.project WHERE id = %s""", (project[7],))
                #             project_data = cursor.fetchone()

                #             #--------ADD_DATA_OF_PROJECTS------
                #             projects.append(
                #                 {
                #                 'projectID':project_data[2],
                #                 'projectCode':project_data[1],   
                #                 'projectName' : project_data[3],
                #                 'assignDate' : project[2],
                #                 'startDate': project[8],
                #                 'dueDate' : project[3],
                #                 'priority' : project[4],
                #                 'status' : project[5]}
                #             )

                #         #----------ADD_USER_DATA---------
                #         data_list.append({
                #             'userID': row[28],
                #             'name': row[1],
                #             'email': row[2],
                #             'project' : projects,
                #             "rmID": manager_name[28],
                #             "rmName": manager_name[1],
                #             "isRM": manager_name[4],
                #             "role": manager_name[5]
                #         })
                #     else:
                #         #-----------FOR_NO_PROJECT----------
                #         data_list.append({
                #         'userID': row[28],
                #         'name': row[1],
                #         'email': row[2],
                #         "rmID": manager_name[28],
                #         "rmName": manager_name[1],
                #         "isRM": manager_name[4],
                #         "role": manager_name[5]
                #     })

                # except Exception as e:
                #     pass


                # print("data list ===============>?",data_list)
                return JsonResponse({
                    'status': 200,
                    'message':'Data successfully fetched.',
                    'data':{
                        'users':data_list
                        }
                    },status = 200)

        else:
            return JsonResponse({"Info":"Invalid method"})
        
    except Exception as e:
        return JsonResponse({"Error":e})

#------------GET_USER'S_PROJECT-------------
@csrf_exempt
def get_user_project(request):
    try:
        if request.method == 'GET':
            decoded_token = get_token(request)
            # emp = request.GET.get('user_id')
            # print('-=-=-=',emp)
            with conn.cursor() as cursor:
                cursor.execute("""SELECT * FROM resource_allocation WHERE user_id = %s""", (decoded_token,))
                rows = cursor.fetchall()

                data_list = []
                for row in rows:

                    #--------GETTING_PROJECT_NAME-----------
                    cursor.execute("""SELECT * FROM public.project WHERE id = %s""", (row[7],))
                    project_data = cursor.fetchone()

                    data_list.append({
                    'Project_name': project_data[3],
                    'Assign_by' : row[0],
                    'Assign_to' : row[1],
                    'Assign_date' : row[2],
                    'startDate' : row[8],
                    'Due_date' : row[3],
                    'Task_priority' : row[4],
                    'Task_status' : row[5]
                    })

            return JsonResponse({'status':200,'message':'Data successfully fetched.','data':rows},status = 200)
        else:
            return JsonResponse({"Info":"Invalid method"})
    except Exception as e:
        return JsonResponse({"Error":e})



#--------ADMIN_ASSIGN_PROJECT----------
@csrf_exempt
def assign_project(request):

        if request.POST:

            decoded_token = get_token(request)

            project = request.POST['project_id']
            assign_to = request.POST['assign_to']
            # assign_by = request.POST['assign_by']
            assign_date = request.POST['assign_date']
            start_date = request.POST['start_date']
            due_date = request.POST['due_date']
            task_proirity = request.POST['task_proirity']
            task_status = request.POST['task_status']


            with conn.cursor() as cursor:

            #--------GETTING_USER----------
                cursor.execute("""SELECT * FROM public.user WHERE id = %s""", (assign_to,))
                user_data = cursor.fetchone()

                #--------GETTING_PROJECT-------
                cursor.execute("""SELECT * FROM public.project WHERE id = %s""", (project,))
                project_data = cursor.fetchone()

                #---------GETTING_MANAGER---------
                cursor.execute("""SELECT * FROM public.user WHERE id = %s""", (decoded_token,))
                manager_data = cursor.fetchone()

                # --------INSERT_DATA--------
                # cursor.execute("""
                # INSERT INTO public."resource_allocation" (user_id, project_id,assign_by,assign_to,assign_date,due_date,task_priority,task_status)
                # VALUES (%s, %s, %s, %s, %s, %s, %s ,%s)""", (user_data[28],project_data[0],assign_by,user_data[1],assign_date,due_date,task_proirity,task_status))

                cursor.execute("""
                    INSERT INTO public."resource_allocation" (user_id, project_id, assign_by, assign_to, assign_date, due_date, task_priority, task_status,startdate)
                    SELECT %s, %s, %s, %s, %s, %s, %s, %s ,%s
                    WHERE NOT EXISTS (
                        SELECT 1 FROM public."resource_allocation" WHERE user_id = %s AND project_id = %s
                    )""", (assign_to, project, manager_data[1], user_data[1], assign_date, due_date, task_proirity, task_status,start_date,user_data[28], project_data[0]))

                conn.commit()
                #-----------REPORTING_MANAGER_FILTER-------------
                # cursor.execute("""
                #     INSERT INTO public."resource_allocation" (user_id, project_id, assign_by, assign_to, assign_date, due_date, task_priority, task_status)
                #     SELECT %s, %s, %s, %s, %s, %s, %s, %s
                #     WHERE NOT EXISTS (
                #         SELECT 1 FROM public."resource_allocation" 
                #         WHERE user_id = %s AND project_id = %s
                #     )
                #     AND EXISTS (
                #         SELECT 1 FROM public."user" 
                #         WHERE "repotingManagerId" = %s
                #     )""",
                #     (assign_to, project, assign_by, user_data[1], assign_date, due_date, task_proirity, task_status, user_data[28], project_data[0], assign_by))
                # conn.commit()

            return JsonResponse({'status':200,'message':'Project assigned','Data':''},status = 200)

        else:

            return JsonResponse({"Info":"Invalid Method"})
    


#----------UPDATE_ASSIGN_PROJECT-----------
@csrf_exempt
def update_assign_project(request):
    try:
        if request.POST:
            user = request.POST['user']
            project = request.POST['project']
            assign_date = request.POST['assign_date']
            start_date = request.POST['start_date']
            due_date = request.POST['due_date']
            task_priority = request.POST.get('task_priority')
            task_status = request.POST['task_status']
            with conn.cursor() as cursor:
                cursor.execute("""
                UPDATE public.resource_allocation
                SET assign_date = %s, due_date = %s, task_priority = %s, task_status = %s ,startdate = %s
                WHERE user_id = %s AND project_id = %s""", (assign_date, due_date, task_priority, task_status , start_date,user , project))

                conn.commit()
            return JsonResponse({'status':200,'message':'User info Updated','Data':''},status = 200)
        else:
            return JsonResponse({"Info":"Invalid Method"})
    except Exception as e:
        return JsonResponse({"Error":e})


#------------DELETE_ASSIGN_PROJECT---------
@csrf_exempt
def delete_assign_project(request):

    try:
        if request.method == 'POST':
            user = request.POST.get('user_id')
            project = request.POST.get('project_id')
            print('-----',user,project)
            with conn.cursor() as cursor:
                cursor.execute("DELETE FROM public.resource_allocation WHERE user_id = %s AND project_id = %s", (user,project))
                conn.commit()
            return JsonResponse({'status':200,'message':'User deleted','Data':''},status = 200)
        else:
            return JsonResponse({"Info":"Invalid Method"})
    except Exception as e:
        return JsonResponse({"Error":e})


#------GET_EMPLOYEE_PROJECT_WISE----
@csrf_exempt
def employee_project_wise(request):
    try:
        if request.method == 'GET':
            pro = request.GET.get('project_id')
            with conn.cursor() as cursor:
                cursor.execute("""SELECT * FROM resource_allocation WHERE project_id = %s """, (pro,))
                rows = cursor.fetchall()
                data_list = []
                for row in rows:
                    data_list.append({
                    'employee_name': row[1]
                    })    
            return JsonResponse({'status':200,'message':'Employee fetched successfully.','data':data_list},status = 200)
        else:
            return JsonResponse({"Info":"Invalid method"})
    except Exception as e:
        return JsonResponse({"Error":e})    


#----GET_PROJECT_EMPLOYEE_WISE-----
@csrf_exempt
def get_project_employee_wise(request):
    try:
        if request.method == 'GET':
            # user = request.GET.get('user_id')
            decoded_token = get_token(request)
            with conn.cursor() as cursor:
                cursor.execute("""SELECT * FROM resource_allocation WHERE user_id = %s """, (decoded_token,))
                rows = cursor.fetchall()
                data_list = []
                for row in rows:
                    cursor.execute("""SELECT * FROM project WHERE id = %s """, (row[7],))
                    pro = cursor.fetchone()
                    data_list.append({
                    'P_Code':pro[1],
                    'Id':pro[2],
                    'Name': pro[3]
                    })    
            return JsonResponse({'status':200,'message':'Project fetched successfully .','data':data_list},status = 200)
        else:
            return JsonResponse({"Info":"Invalid method"})
    except Exception as e:
        return JsonResponse({"Error":e})


@csrf_exempt
def manager_data(request):

    try:
        if request.method == 'GET':
            cur = connection.cursor()
            curs = connection.cursor()

            cur.execute("""SELECT * FROM public.resource_allocation;""")

            cursor = connection.cursor()
            cursor.execute("""SELECT id, "projectCode", "projectName" FROM public.project;""")
            project_code = cursor.fetchall()
            project_data = cursor.fetchall()

            project_data = cur.fetchall()

            curs.execute("""SELECT name, email, role, "repotingManagerId", "isActive",id, "isRepotingManager"  FROM public."user" """)
            result = curs.fetchall()

            datalist = []

            def projectcode(self):
                procode = [i for i in project_code if i[0] == self]
                print("================>",procode)
                return procode[0]

            def projectassign(self):
                projct_list = []
                for data in project_data:
                    print('=======project==============',data[6], self)
                    if data[6] == self:
                        project_code = projectcode(data[7])

                        projct_dict = {

                                    'projectID': project_code[0],
                                    'projectCode': project_code[1],
                                    'projectName': project_code[2],
                                    'assignDate' : data[2],
                                    'startDate':data[6],
                                    'duedate' : data[3],
                                    'priority': data[4],
                                    'status' : data[5],

                                }

                        projct_list.append(projct_dict)

                return projct_list

            def Inmanagers(self):
                proid = str(self)
                
                assignmanage = []
                for data in result:     #-- All user's
                    if data[3] == proid:
                        if data[6] == "true":
                            projectdata = projectassign(data[5])

                            prodata = {
                                'userid': data[5],
                                'name' : data[0],
                                'email': data[1],
                                'repotingManagerId':data[3],
                                'isRepotingManager':data[6],
                            }
                            if projectdata:
                                prodata.update({'project': projectdata})
                            assignmanage.append(prodata)
                        else:
                            projectdata = projectassign(data[5])
                            
                            prodatacheck = {
                                'userid': data[5],
                                'name' : data[0],
                                'email': data[1],
                                'repotingManagerId':data[3],
                                'isRepotingManager':data[6],
                            }
                            if projectdata:
                                prodatacheck.update({'project': projectdata})
                            assignmanage.append(prodatacheck)
                return assignmanage

            def reportis(self):
                proid = str(self)
                assign = []
                for data in result:
                    if data[3] == proid:
                        if data[6] == "true":
                            
                            projectdata = projectassign(data[5])
                            inmang = Inmanagers(data[5])
                        
                            prodata = {
                                'userid': data[5],
                                'name' : data[0],
                                'email': data[1],
                                'repotingManagerId':data[3],
                                'isRepotingManager':data[6], 

                            }
                            if projectdata:
                                prodata.update({'project': projectdata})
                            if inmang:
                                prodata.update({"reportee":inmang})    
                            assign.append(prodata)
                        else:
                            inmang = Inmanagers(data[5])
                            projectdata = projectassign(data[5])
                            prodatacheck = {
                                'userid': data[5],
                                'name' : data[0],
                                'email': data[1],
                                'repotingManagerId':data[3],
                                'isRepotingManager':data[6],
                            }
                            if projectdata:
                                prodatacheck.update({'project': projectdata})
                            assign.append(prodatacheck)
                return assign
            repotingManagerId = get_token(request)
            # repotingManagerId = request.POST['projct_man_id']

            for data in result:
                if str(data[5]) == repotingManagerId:
                    if data[6] == 'true':
                        checkreportes = reportis(data[5])
                        projectdata = projectassign(data[5])
                        
                        dict3 = {
                            'userid': data[5],
                            'name' : data[0],
                            'email': data[1],
                            'repotingManagerId':data[3],
                            'isRepotingManager':data[6],
                        }
                        if projectdata:
                            dict3.update({'project': projectdata})
                        if checkreportes:
                            dict3.update({"reportee":checkreportes})
                        datalist.append(dict3)
                        
                    else:
                        projectdata = projectassign(data[5])
                        dict4 = {
                            'userid': data[5],
                            'name' : data[0],
                            'email': data[1],
                            'repotingManagerId':data[3],
                            'isRepotingManager':data[6],

                        }
                        if projectdata:
                                dict4.update({'project': projectdata})
                        datalist.append(dict4)   
            return JsonResponse({"status" : 200,'Messsage':'success','Data':{'User':datalist}}) 
    except Exception as e:
        return JsonResponse({"Error":e})

def get_user(self):
    cur = connection.cursor()
    cur.execute("""SELECT id, name, email FROM public.user  WHERE id = %s """, (self,))

    projct_user = cur.fetchall()

    return projct_user


@csrf_exempt
def get_project_data(request):
    
    try:
        if request.method == 'POST':
        
            if request.POST['projct_date'] :

                cur = connection.cursor()
                cur.execute("""SELECT project_id, user_id, assign_date, startdate, due_date, task_priority, task_status FROM public."resource_allocation"  WHERE startdate = %s """, (request.POST['projct_date'],))  

                cursor = connection.cursor()
                cursor.execute("""SELECT id, "projectCode", "projectName" FROM public.project;""")

                assign_data = cur.fetchall()
                project_data = cursor.fetchall()

                project_list = []
                for data in project_data:
                    for ass_dta in assign_data:

                        if data[0] == ass_dta[0]:
                            
                            prjct_user = get_user(ass_dta[1])

                            pro_dict ={
                                'userid': prjct_user[0][0],
                                'name' : prjct_user[0][1],
                                'email': prjct_user[0][2],

                                'projectID': data[0],
                                'projectCode': data[1],
                                'projectName': data[2],
                                'assignDate': ass_dta[2],
                                'startDate': ass_dta[3],
                                'dueDate': ass_dta[4],
                                'priority': ass_dta[5],
                                'status': ass_dta[6],

                            }
                            project_list.append(pro_dict)
                                    
            return JsonResponse({"status" : 200,'Messsage':'success','Data':{'project':project_list}})
    except Exception as e:
        return JsonResponse({"Error":e})

@csrf_exempt
def get_userdata(request):

    try:
        if request.method == 'GET':
            # manager = request.GET.get('user_id')
            decoded_token = get_token(request)
            with conn.cursor() as cursor:

                #-------------GETTING_MANAGER_DATA---------------
                cursor.execute("""SELECT * FROM public."user" WHERE "id" = %s""", (decoded_token,))
                manager_name = cursor.fetchone()

                if manager_name[4] == 'true':

                    #------------GETTING_EMPLOYEE_OF_MANAGER-----------------
                    cursor.execute("""SELECT * FROM public."user" WHERE "repotingManagerId" = %s""", (decoded_token,))
                    rows = cursor.fetchall()

                    #----STORE_USER_DATA-----
                    data_list = []

                    for row in rows:

                        try:
                            #-------------GETTING_ALL_PROJECTS_OF_USER-----------------
                            cursor.execute("""SELECT * FROM resource_allocation WHERE user_id = %s""", (row[28],))
                            emp_projeect_data = cursor.fetchall()

                            #------STORE_PROJECT_DATA------
                            projects = []
                            if emp_projeect_data != []:

                                for project in emp_projeect_data:

                                    #--------GETTING_PROJECT_NAME-------
                                    cursor.execute("""SELECT * FROM public.project WHERE id = %s""", (project[7],))
                                    project_data = cursor.fetchone()

                                    #--------ADD_DATA_OF_PROJECTS------
                                    projects.append(
                                        {
                                        'projectID': project_data[0],
                                        'projectCode': project_data[1],
                                        'projectName' : project_data[3],
                                        'assignDate' : project[2],
                                        'startDate': project[8],
                                        'dueDate' : project[3],
                                        'priority' : project[4],
                                        'status' : project[5],
                                        'type' : project[9]
                                        }
                                    )

                                #----------ADD_USER_DATA---------
                                data_list.append({
                                    'userID': row[28],
                                    'name': row[1],
                                    'email': row[2],
                                    'project' : projects,
                                    "rmID": manager_name[28],
                                    "rmName": manager_name[1],
                                    "isRM": row[4],
                                    "role": row[5]
                                })
                            else:
                                #-----------FOR_NO_PROJECT----------
                                data_list.append({
                                'userID': row[28],
                                'name': row[1],
                                'email': row[2],
                                "rmID": manager_name[28],
                                "rmName": manager_name[1],
                                "isRM": row[4],
                                "role": row[5]
                            })

                        except Exception as e:
                            pass

                    return JsonResponse({
                        'status': 200,
                        'message':'Data successfully fetched.',
                        'data':{
                            'users':data_list
                            }
                        },status = 200)
            
                else:
                    return JsonResponse({"Info":"You are not eligible for view this data"})

        else:
            return JsonResponse({"Info":"Invalid method"})
    except Exception as e:
        return JsonResponse({"Error":e})


@csrf_exempt
def data_by_date(request):
    try:
        if request.method == 'POST':

            assign_date= request.POST['assign_date']
            due_date = request.POST['due_date']

            if assign_date and due_date:
                cur2 = connection.cursor()
                cursor = connection.cursor()

                cur2.execute("""SELECT project_id, user_id, assign_date, startdate, due_date, task_priority, task_status FROM public.resource_allocation WHERE assign_date >= %s AND due_date <= %s""",(assign_date,due_date,))
                cursor.execute("""SELECT id, "projectCode", "projectName" FROM public.project;""")

                project_data = cursor.fetchall()
                allocation_data = cur2.fetchall()

                task_list = []

                for j in allocation_data:
                    for z in project_data:
                        if z[0] == j[0]:
                            dict1 = {
                            'user_id':j[1],
                            'project_id':j[0],
                            'projectCode':z[1],
                            'projectName':z[2],
                            'from_date':j[2],
                            'start_date':j[3],
                            'to_date':j[4],
                            'task_priority':j[5],
                            'task_status':j[6]
                            }
                            task_list.append(dict1) 
                return JsonResponse({'data':task_list})
    except Exception as e:
        return JsonResponse({"Error":e})