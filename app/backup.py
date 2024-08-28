from django.shortcuts import render
import psycopg2
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse


#------DATABASE_CONNECTION--------
conn = psycopg2.connect(
    dbname="dwr_staging",
    user="root",
    password="password",
    host="localhost",
    port="5432"
)


#-------GETTING_ALL_DATA---------
@csrf_exempt
def all_data(request):
    if request.method == 'GET':
        manager = request.GET.get('user_id')

        with conn.cursor() as cursor:

            #-------------GETTING_MANAGER_DATA---------------
            cursor.execute("""SELECT * FROM public."user" WHERE "id" = %s""", (manager,))
            manager_name = cursor.fetchone()

            if manager_name[4] == 'true':

                #------------GETTING_EMPLOYEE_OF_MANAGER-----------------
                cursor.execute("""SELECT * FROM public."user" WHERE "repotingManagerId" = %s""", (manager,))
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
                                    'projectID':project_data[2],
                                    'projectCode':project_data[1],   
                                    'projectName' : project_data[3],
                                    'assignDate' : project[2],
                                    'startDate': project[8],
                                    'dueDate' : project[3],
                                    'priority' : project[4],
                                    'status' : project[5]}
                                )

                            #----------ADD_USER_DATA---------
                            data_list.append({
                                'userID': row[28],
                                'name': row[1],
                                'email': row[2],
                                'project' : projects,
                                "rmID": manager_name[28],
                                "rmName": manager_name[1],
                                "isRM": manager_name[4],
                                "role": manager_name[5]
                            })
                        else:
                            #-----------FOR_NO_PROJECT----------
                            data_list.append({
                            'userID': row[28],
                            'name': row[1],
                            'email': row[2],
                            "rmID": manager_name[28],
                            "rmName": manager_name[1],
                            "isRM": manager_name[4],
                            "role": manager_name[5]
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


#------------GET_USER'S_PROJECT-------------
@csrf_exempt
def get_user_project(request):
    if request.method == 'GET':
        emp = request.GET.get('user_id')
        print('-=-=-=',emp)
        with conn.cursor() as cursor:
            cursor.execute("""SELECT * FROM resource_allocation WHERE user_id = %s""", (emp,))
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


#--------ADMIN_ASSIGN_PROJECT----------
@csrf_exempt
def assign_project(request):

    if request.POST:

        project = request.POST['project_id']
        assign_to = request.POST['assign_to']
        assign_by = request.POST['assign_by']
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
            cursor.execute("""SELECT * FROM public.user WHERE id = %s""", (assign_by,))
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


#------------DELETE_ASSIGN_PROJECT---------
@csrf_exempt
def delete_assign_project(request):

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
