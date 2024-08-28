from django.shortcuts import render
import psycopg2
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from django.db import connection
import jwt
from resource_allocation.auth_middelware import *
import datetime


#------DATABASE_CONNECTION--------
conn = psycopg2.connect(
    dbname="dwr_staging",
    user="root",
    password="password",
    host="localhost",
    port="5432"
)


#----------CHECK_DATE_FORMATE------------
def validate(date_text):

        try:
            datetime.date.fromisoformat(date_text)

        except ValueError:
            raise ValueError("Incorrect data format, should be YYYY-MM-DD")


#----------FETCH_TOKEN_FROM_HEADERS----------
def get_token(request):

    try:
        token_Get=request.headers['Authorization'].split("Bearer ")[1]
        secret_key =  'dSUNYPjdhqSqRrowcRuR30uSiHNw'

        decoded_token = jwt.decode(token_Get, secret_key, algorithms='HS256')
        decoded_token = str(decoded_token['id'])

        # cur = connection.cursor()
        # cur.execute("""SELECT id, name, "isRepotingManager" FROM public.user  WHERE id = %s """, [decoded_token['id']])
        # user = cur.fetchall()

        # if user[0][2] == 'false':
        #     raise Exception("You are not authorize to view this data!")

        return decoded_token

    except Exception as e:
            return JsonResponse({"Error":e})


#----------CHECK_USER_EXIST_OR_NOT_AND_ADMIN_OR NOT------------
def checkuser(id):
    
    cur_allocation = connection.cursor()
    cur_allocation.execute("""SELECT * FROM public.user WHERE "id" = %s;""",[id])
    allocation = cur_allocation.fetchone()

    if not allocation:
        return True
    # else:
    #     if allocation[4] == 'false':
    #         raise Exception("You are not authorize to view this data!")


#----------CHECK_USER_COLLABORATE_IN_PROJECT--------
def checkproject(id):

    pro_allocation = connection.cursor()
    pro_allocation.execute("""SELECT "projectId" FROM public.project_collaborater WHERE "projectId" = %s ;""",[id])
    pro_coll = pro_allocation.fetchall()
    if not pro_coll :
        return True
    else:
        return False


def checkassignproject(id):

    print('--------',id)

    pro_allocation = connection.cursor()
    pro_allocation.execute("""SELECT * FROM public."resource_allocation" WHERE id = %s;""",[id])
    pro_coll = pro_allocation.fetchall()
    if not pro_coll :
        return True
    else:
        return False



#-----------GETTING_PROJECT_INFo---------
def project_samedate(assign_to,project,date):
    with conn.cursor() as cursor:
        cursor.execute("""SELECT * FROM public."resource_allocation" WHERE user_id = %s AND project_id = %s""", (assign_to,project))
        same_data = cursor.fetchall()

        try:
            for i in same_data:
                from datetime import datetime

                date1 = datetime.strptime(i[3], "%Y-%m-%d")
                date2 = datetime.strptime(date, "%Y-%m-%d")
                date3 = datetime.strptime(i[2], "%Y-%m-%d")
                
                print('-------------date1,date2',date1,date2)
                difference = date2 - date1
                # print('----------------differencedifference',difference)
                data = str(difference).split('day')        

                # print('=======================================>>>',i)

                print("========88888888888888888888888888========",date3,date2)

                if date3 != date2:

                    print("========99999999999999999999999999999========",date1,date2)    
                    if date1 == date2 or str(data[0]) == '1 ':
                        print('======================>ifff')
                        # print('==============i[11]====',i[11])
                        return {'data':i[11]}
                    else:
                        print('====================>else')
                        continue
                        # return None
                else:
                    print('==================>')
                    return {'same':i[11]}

        except Exception as e:
            print('-------------eee',e)

data_list = []
database = conn.cursor()

#-----------GETTING_ALL_USERS------------
database.execute("""SELECT * FROM public.user""")
assign = database.fetchall()

#-----------GETTING_ALL_ASSIGN_PROJECTS--------
typee = 'false'
database.execute("""SELECT * FROM resource_allocation WHERE "isdeleted" = %s;""",[typee])
emp_project_data = database.fetchall()
# print('--------------emp_project_data',emp_project_data)

#----------GETTING_ALL_PROJECTS----------
database.execute("""SELECT * FROM project""")
all_project = database.fetchall()


#----------GETTING_PROJECT_INFO---------
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


#---------GETTING_ASSIGN_PROJECT_INFO---------
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


#---------CREATING_EMPLOYEE_HIRE----------
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

            with conn.cursor() as cursor:

                #-------------GETTING_MANAGER_DATA---------------
                cursor.execute("""SELECT * FROM public."user" WHERE "repotingManagerId" = %s""", (manager,))
                manager_name = cursor.fetchall()

                for row in manager_name:
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
            a = checkuser(decoded_token)
            if a == True:
                return JsonResponse({'status': 401,'message':'User does not exist'},status=401)
            else:

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

    try:
        if request.POST:

            decoded_token = get_token(request)
            project = request.POST['project_id']
            assign_to = request.POST['assign_to']
            typee =  request.POST['type']
            assign_date = request.POST['assign_date']
            start_date = request.POST['start_date']
            due_date = request.POST['due_date']

            #----------CHECH_DATE_FORMATE---------
            validate(assign_date)
            validate(start_date)
            validate(due_date)

            # if assign_date > due_date :
            #     return JsonResponse({'status': 401,"message":"due date must be greater than assign date"},status=401)

            ty = ['allocated','holiday','leave']
            if typee not in ty:
                return JsonResponse({'status': 400,'message':'type field should be allocated or holiday or leave'},status=400)

            task_proirity = request.POST['task_proirity']
            task_status = request.POST['task_status']

            a = checkuser(assign_to)
            b = checkproject(project)

            if a == True:
                return JsonResponse({'status': 401,'message':'User does not exist'},status=401)
            else:
                if b == True:
                    return JsonResponse({'status': 404,'message':'Project does not exist'},status=404)
                else:
                    cursor = connection.cursor()
                    cursor.execute("""SELECT "userId", "projectId" FROM public.project_collaborater WHERE "userId" = %s AND "projectId" = %s ;""",[assign_to, project])

                    pro_coll = cursor.fetchall()

                    if pro_coll:

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

                            
                            same_data = project_samedate(assign_to,project,assign_date)
                            print('--------------same_data',same_data)

                            if same_data != None:
                                print('------')
                            

                            # if same_data:
                            #     from datetime import datetime, timedelta
                            #     date1 = datetime.strptime(same_data[3], "%Y-%m-%d")
                            #     date2 = datetime.strptime(assign_date, "%Y-%m-%d")

                            #     # Calculate the difference between the two dates
                            #     difference = date2 - date1
                            #     print('----------------differencedifference',difference)
                            #     data = str(difference).split('day')
                            #     print(data[0])
                            if same_data != None:
                            
                                if same_data.get('data'):
                                    print('---------------same id')
                                    
                                    with conn.cursor() as cursor:
                                        cursor.execute("""
                                        UPDATE public.resource_allocation
                                        SET due_date = %s
                                        WHERE id = %s""", (due_date,str(same_data.get('data'))))

                                        u_data = {
                                        'id':same_data.get('data'),
                                        'assignTo':int(assign_to),
                                        'assignBy':manager_data[1],
                                        'project':int(project),
                                        'assignDate':assign_date,
                                        'dueDate':due_date,
                                        'priority':task_proirity,
                                        'status':task_status,
                                        'startDate':start_date,
                                        'type':typee,
                                    }

                                    conn.commit()   

                                    return JsonResponse({'status':200,'message':'Updated','Data':u_data},status = 200)

                                elif same_data.get('same'):
                                    return JsonResponse({'status':401,'message':'this project is already assign for this date'},status = 401)

                            elif same_data == None:
                                
                                print('-------------------NONE-------')
                                Isdeleted = 'false'
                                cursor.execute("""
                                    INSERT INTO public."resource_allocation" (user_id, project_id, assign_by, assign_to, assign_date, due_date, task_priority, task_status,startdate,type,isdeleted)
                                    SELECT %s, %s, %s, %s, %s, %s, %s, %s ,%s,%s,%s""", (assign_to, project, manager_data[1], user_data[1], assign_date, due_date, task_proirity, task_status,start_date, typee, Isdeleted))
                                conn.commit()

                                cursor.execute("""SELECT id FROM public."resource_allocation" WHERE user_id = %s AND project_id = %s AND assign_date = %s AND due_date = %s""", (assign_to,project,assign_date,due_date))
                                data = cursor.fetchone()

                                u_data = {
                                    'id' : data[0],
                                    'assignTo':int(assign_to),
                                    'assignBy':manager_data[1],
                                    'project':int(project),
                                    'assignDate':assign_date,
                                    'dueDate':due_date,
                                    'priority':task_proirity,
                                    'status':task_status,
                                    'startDate':start_date,
                                    'type':typee,
                                }                                

                            else:
                                print('---------------same else')
                                Isdeleted = 'false'
                                cursor.execute("""
                                    INSERT INTO public."resource_allocation" (user_id, project_id, assign_by, assign_to, assign_date, due_date, task_priority, task_status,startdate,isdeleted)
                                    SELECT %s, %s, %s, %s, %s, %s, %s, %s ,%s,%s""", (assign_to, project, manager_data[1], user_data[1], assign_date, due_date, task_proirity, task_status,start_date, Isdeleted))
                                u_data = {
                                    'assignTo':assign_to,
                                    'assignBy':manager_data[1],
                                    'project':project,
                                    'assignDate':assign_date,
                                    'dueDate':due_date,
                                    'priority':task_proirity,
                                    'status':task_status,
                                    'startDate':start_date,
                                    'type':typee,
                                }
                                conn.commit()
                            
                            # elif same_data == None:

                            #     Isdeleted = 'false'
                            #     cursor.execute("""
                            #         INSERT INTO public."resource_allocation" (user_id, project_id, assign_by, assign_to, assign_date, due_date, task_priority, task_status,startdate,type,isdeleted)
                            #         SELECT %s, %s, %s, %s, %s, %s, %s, %s ,%s,%s,%s""", (assign_to, project, manager_data[1], user_data[1], assign_date, due_date, task_proirity, task_status,start_date, typee, Isdeleted))
                            #     conn.commit()

                            #     cursor.execute("""SELECT id FROM public."resource_allocation" WHERE user_id = %s AND project_id = %s AND assign_date = %s AND due_date = %s""", (assign_to,project,assign_date,due_date))
                            #     data = cursor.fetchone()

                            #     u_data = {
                            #         'id' : data[0],
                            #         'assignTo':assign_to,
                            #         'assignBy':manager_data[1],
                            #         'project':project,
                            #         'assignDate':assign_date,
                            #         'dueDate':due_date,
                            #         'priority':task_proirity,
                            #         'status':task_status,
                            #         'startDate':start_date,
                            #         'type':typee,
                            #     }
                                

                            return JsonResponse({'status':200,'message':'Project assigned','Data':u_data},status = 200)

                    else: 
                        return JsonResponse({'status':404,'data':[],"message":"This employee is not collaborator of this project!"})

        else:
            return JsonResponse({'status':405 ,"Info":"Invalid Method"})
        
    except Exception as e:
        return JsonResponse({'status':400,'Error':str(e)},status=400)
      

#----------UPDATE_ASSIGN_PROJECT-----------
from rest_framework.decorators import api_view
@api_view(['GET', 'PUT', 'DELETE'])
def update_assign_project(request):
    try:
        if request.POST:
            # user_id = get_token(request)
            # user_id = request.POST['user_id']
            ids = request.POST['id']
            # project = request.POST['project']
            assign_date = request.POST['assign_date']
            start_date = request.POST['start_date']
            due_date = request.POST['due_date']
            task_priority = request.POST.get('task_priority')
            task_status = request.POST['task_status']
            typee = request.POST['typee']

            validate(assign_date)
            validate(start_date)
            validate(due_date)

            with conn.cursor() as cursor:
                cursor.execute("""
                UPDATE public.resource_allocation
                SET assign_date = %s, due_date = %s, task_priority = %s, task_status = %s ,startdate = %s ,type = %s
                WHERE id = %s """, (assign_date, due_date, task_priority, task_status , start_date, typee, ids))

                conn.commit()

                cursor.execute("""SELECT * FROM public."resource_allocation" WHERE id = %s """,[ids])
                u_data = cursor.fetchone()
                u_dict = {
                    "id" : u_data[11],
                    "assignBy" : u_data[0],
                    "assignTo" : u_data[1],
                    "assignDate" : u_data[2],
                    "dueDate" : u_data[3],
                    "priority" : u_data[4],
                    "status" : u_data[5],
                    "userId" : u_data[6],
                    "projectId" : u_data[7],
                    "startDate" : u_data[8],
                    "type" : u_data[9],
                    "isdeleted" : u_data[10],                    
                }

            return JsonResponse({'status':200,'message':'User info Updated','Data':u_dict})
        else:
            return JsonResponse({"Info":"Invalid Method"})
    except Exception as e:
        return JsonResponse({'status':400,'Error':str(e)},status=400)    


#------------DELETE_ASSIGN_PROJECT---------
# @csrf_exempt
@api_view(['GET', 'PUT', 'DELETE'])    
def delete_assign_project(request):

    try:
        if request.method == 'DELETE':
            user = request.POST.get('assignment_id')

            delete = checkassignproject(user)
            if delete == True:
                return JsonResponse({'status':402,'message':'project not found','Data':''},status = 402)
            else:
                with conn.cursor() as cursor:
                    cursor = connection.cursor()
                    isdel = 'true'
                    cursor.execute("UPDATE public.resource_allocation SET isdeleted = %s WHERE id = %s", (isdel, user))            
                    conn.commit()
                return JsonResponse({'status':200,'message':'assign project deleted','Data':''},status = 200)
        else:
            return JsonResponse({"Info":"Invalid Method"})
    except Exception as e:
        return JsonResponse({'status':422,'Error':'missing required parameter'},status=422)


#--------GET_EMPLOYEE_PROJECT_WISE-------
@csrf_exempt
def employee_project_wise(request):

    try:
        if request.method == 'GET':
            pro = request.GET['project_id']
            checkproject(pro)

            with conn.cursor() as cursor:
                cursor.execute("""SELECT * FROM resource_allocation WHERE project_id = %s """, (pro,))
                rows = cursor.fetchall()

                data_list = []
                for row in rows:
                    data_list.append({
                    'employee_name': row[1]
                    })    
            return JsonResponse({'status':200,'message':'Employee fetched successfully.','data':data_list})
        else:
            return JsonResponse({"Info":"Invalid method"})
    except Exception as e:
        return JsonResponse({'status':400,'Error':str(e)},status=400)


#----GET_PROJECT_EMPLOYEE_WISE-----
@csrf_exempt
def get_project_employee_wise(request):

    try:
        if request.method == 'GET':
            decoded_token = get_token(request)
            a = checkuser(decoded_token)
            if a == True:
                return JsonResponse({'status': 401,'message':'User does not exist'},status=401)
            else:
                with conn.cursor() as cursor:
                    cursor.execute("""SELECT * FROM resource_allocation WHERE user_id = %s """, (decoded_token,))
                    rows = cursor.fetchall()

                    data_list = []
                    for row in rows:
                        cursor.execute("""SELECT * FROM project WHERE id = %s """, (row[7],))
                        pro = cursor.fetchone()
                        data_list.append({
                        'P_Code':pro[1],
                        'Id':pro[0],
                        'Name': pro[3]
                        })    
                return JsonResponse({'status':200,'message':'Project fetched successfully .','data':data_list})
        else:
            return JsonResponse({"Info":"Invalid method"})
        
    except Exception as e:
        return JsonResponse({'status':400,'Error':str(e)},status=400)


@csrf_exempt
def manager_data(request):

    try:
        if request.method == 'GET':
            cur = connection.cursor()
            curs = connection.cursor()

            cur.execute("""SELECT * FROM public.resource_allocation WHERE "type" = 'allocated';""")

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
                return procode[0]

            def projectassign(self):
                projct_list = []
                for data in project_data:
                    if data[6] == self:
                        project_code = projectcode(data[7])

                        # if data[9] == 'leave' or data[9] == 'holiday':
                        #     pass
                        # else:
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
                                'project':[]

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
                                'project':[]
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
                                'project':[]


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
                                'project':[]

                            }
                            if projectdata:
                                prodatacheck.update({'project': projectdata})
                            assign.append(prodatacheck)
                return assign

            repotingManagerId = get_token(request)
            a = checkuser(repotingManagerId)
            if a == True:
                return JsonResponse({'status': 401,'message':'User does not exist'},status=401)
            else:

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
                                'project':[]

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
                                'project':[]


                            }
                            if projectdata:
                                    dict4.update({'project': projectdata})
                            datalist.append(dict4)   
                return JsonResponse({"status" : 200,'Messsage':'success','Data':{'User':datalist}})
        
    except Exception as e:
        return JsonResponse({'status':400,'Error':str(e)},status=400)


#---------GETTING_USER_DATA-----------
def get_user(self):
    cur = connection.cursor()
    cur.execute("""SELECT id, name, email FROM public.user  WHERE id = %s """, (self,))

    projct_user = cur.fetchall()

    return projct_user


#---------GETTING_PROJECT_DATA_BY_DATE----------
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


#----------GETTING_ALL_EMPLOYEE_OF_MANAGER-----------
@csrf_exempt
def get_userdata(request):

    try:
        if request.method == 'GET':
            # manager = request.GET.get('user_id')
            decoded_token = get_token(request)
            a = checkuser(decoded_token)

            if a == True:
                return JsonResponse({'status': 401,'message':'User does not exist'},status=401)
            else:
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
                                isdel = 'false'
                                #-------------GETTING_ALL_PROJECTS_OF_USER-----------------
                                cursor.execute("""SELECT * FROM resource_allocation WHERE user_id = %s AND isdeleted = %s""", (row[28],isdel,))
                                emp_projeect_data = cursor.fetchall()

                                #------STORE_PROJECT_DATA------
                                projects = []
                                if emp_projeect_data != []:

                                    for project in emp_projeect_data:

                                        #--------GETTING_PROJECT_NAME-------
                                        cursor.execute("""SELECT * FROM public.project WHERE id = %s""", (project[7],))
                                        project_data = cursor.fetchone()

                                        #--------ADD_DATA_OF_PROJECTS------

                                        # if project[9] == 'holiday' or project[9] == 'leave':
                                        #     pass
                                        # else:
                                        projects.append(
                                            {
                                            'id' : project[11],
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
                                    rm_value = ""
                                    if row[4] == "true":
                                        rm_value = True
                                    else:
                                        rm_value = False
                                    data_list.append({
                                        'userID': row[28],
                                        'name': row[1],
                                        'email': row[2],
                                        'project' : projects,
                                        "rmID": manager_name[28],
                                        "rmName": manager_name[1],
                                        "isRM": rm_value,
                                        "role": row[5]
                                    })
                                else:
                                    rm_value = ""
                                    if row[4] == "true":
                                        rm_value = True
                                    else:
                                        rm_value = False
                                    #-----------FOR_NO_PROJECT----------
                                    data_list.append({
                                    'userID': row[28],
                                    'name': row[1],
                                    'email': row[2],
                                    'project':[],
                                    "rmID": manager_name[28],
                                    "rmName": manager_name[1],
                                    "isRM": rm_value,
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
                            })
                
                    else:
                        return JsonResponse({"Info":"You are not eligible for view this data"})
            

        else:
            return JsonResponse({"Info":"Invalid method"})
    except Exception as e:
        return JsonResponse({'status':400,'Error':str(e)},status=400)


#-----------GETTING_PROJECT_BY_DATE--------------
@csrf_exempt
def data_by_date(request):
    try:
        if request.method == 'POST':

            assign_date= request.POST['assign_date']
            due_date = request.POST['due_date']

            validate(assign_date)
            validate(due_date)

            if assign_date and due_date:
                cur2 = connection.cursor()
                cursor = connection.cursor()

                cur2.execute("""SELECT project_id, user_id, assign_date, startdate, due_date, task_priority, task_status,type FROM public.resource_allocation WHERE assign_date >= %s AND due_date <= %s""",(assign_date,due_date,))
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
                            'task_status':j[6],
                            'type' :j[7]
                            }
                            task_list.append(dict1) 
                return JsonResponse({'data':task_list})
    except Exception as e:
        return JsonResponse({'status':400,'Error':str(e)},status=400)
    

def get_user(self):
    cur = connection.cursor()
    cur.execute("""SELECT id, name, email FROM public.user  WHERE id = %s """, [self])
    projct_user = cur.fetchall()

    return projct_user


def get_project_data_by_filter(request):

    if request.method == 'GET':

        assign_data = ''
        if request.GET['project_id'] and request.GET['user_id'] and request.GET['startdate']:
        
            cur = connection.cursor()
            cur.execute("""SELECT project_id, user_id, assign_date, startdate, due_date, task_priority, task_status, type  FROM public.resource_allocation WHERE project_id = %s AND user_id = %s AND startdate = %s ;""",[request.GET['project_id'] , request.GET['user_id'], request.GET['startdate']])    
            assign_data = cur.fetchall()

        elif request.GET['project_id'] and request.GET['user_id']:
        
            cur = connection.cursor()
            cur.execute("""SELECT project_id, user_id, assign_date, startdate, due_date, task_priority, task_status, type  FROM public.resource_allocation WHERE project_id = %s AND user_id = %s ;""",[request.GET['project_id'] , request.GET['user_id']])    
            assign_data = cur.fetchall()


        elif request.GET['user_id'] and request.GET['startdate']:
            
            cur = connection.cursor()
            cur.execute("""SELECT project_id, user_id, assign_date, startdate, due_date, task_priority, task_status, type  FROM public.resource_allocation WHERE user_id = %s AND startdate = %s ;""",[request.GET['user_id'] , request.GET['startdate']])    
            assign_data = cur.fetchall()


        elif request.GET['project_id'] and request.GET['startdate']:
        
            cur = connection.cursor()
            cur.execute("""SELECT project_id, user_id, assign_date, startdate, due_date, task_priority, task_status, type  FROM public.resource_allocation WHERE project_id = %s AND startdate = %s ;""",[request.GET['project_id'] , request.GET['startdate']])    
            assign_data = cur.fetchall()


        elif request.GET['user_id']:

            cur = connection.cursor()
            cur.execute("""SELECT project_id, user_id, assign_date, startdate, due_date, task_priority, task_status, type  FROM public.resource_allocation WHERE user_id = %s;""",(str(request.GET['user_id']),))    
            assign_data = cur.fetchall()

        elif request.GET['project_id'] :
            cur = connection.cursor()
            cur.execute("""SELECT project_id, user_id, assign_date, startdate, due_date, task_priority, task_status, type FROM public.resource_allocation  WHERE project_id = %s """, [request.GET['project_id']])
            assign_data = cur.fetchall()

        elif request.GET['startdate']:
            cur = connection.cursor()
            cur.execute("""SELECT project_id, user_id, assign_date, startdate, due_date, task_priority, task_status, type  FROM public.resource_allocation WHERE startdate = %s;""",[str(request.GET['startdate'])])    
            assign_data = cur.fetchall()
        cursor = connection.cursor()
        cursor.execute("""SELECT id, "projectCode", "projectName" FROM public.project;""")

        # assign_data = cur.fetchall()
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
        user = request.GET['user_id']
        if user != '':
            a = checkuser(user)
            if a == True:
                return JsonResponse({"status" : 401,'Messsage':'User does not exist'},status = 401)

        if project_list :
            return JsonResponse({"status" : 200,'Messsage':'success','Data':{'project':project_list}})

        else:
            return JsonResponse({"status" : 404,'Messsage':'Project does not exist'},status = 404)