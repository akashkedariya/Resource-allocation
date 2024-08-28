from django.urls import path,include
from .views import*

urlpatterns = [
    path("get_manager/",all_data),
    path("assign_project/",assign_project),
    path("update_assign_project/",update_assign_project),
    path("delete_assign_project/",delete_assign_project),
    path("get_user_project/",get_user_project),
    path("employee_project_wise/" ,employee_project_wise),
    path("get_project_employee_wise/",get_project_employee_wise),
    path("manager_data/" ,manager_data),
    path("get_project_data/",get_project_data),
    path("get_userdata/",get_userdata),
    path("data_by_date/",data_by_date), 
    path("get_project_data_by_filter/",get_project_data_by_filter),

]