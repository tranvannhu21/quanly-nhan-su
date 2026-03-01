from django.urls import path
from . import views

urlpatterns = [

path('',views.home),

path('employees',views.employee_list),

path('dashboard',views.dashboard),

path('employees/add',views.add_employee),

path('employees/edit/<int:id>',views.edit_employee),

path('employees/delete/<int:id>',views.delete_employee),

path('logout/',views.logout_view),

]