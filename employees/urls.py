from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [

path('',views.home),

path('employees',views.employee_list),

path('dashboard',views.dashboard),

path('employees/add',views.add_employee),

path('employees/edit/<int:id>',views.edit_employee),

path('employees/delete/<int:id>',views.delete_employee),

path('logout/',views.logout_view),

path('leave/',views.leave_request,name='leave'),

path('leave-list/', views.leave_list_admin, name='leave_list_admin'),

path('my-leave/',views.my_leave,name='my_leave'),

path('leave/update/<int:leave_id>/<str:status>/', views.update_leave_status, name='update_leave_status'),

path('attendance/', views.attendance_view, name='attendance'),

path('attendance-table/', views.attendance_table, name='attendance_table'),

path('export-attendance/', views.export_attendance),

path('export-leave/', views.export_leave, name='export_leave'),

# 4 đường dẫn chức năng Quên mật khẩu
path('password_reset/', auth_views.PasswordResetView.as_view(template_name='password_reset.html'), name='password_reset'),

path('password_reset/done/', auth_views.PasswordResetDoneView.as_view(template_name='password_reset_done.html'), name='password_reset_done'),

path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='password_reset_confirm.html'), name='password_reset_confirm'),

path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='password_reset_complete.html'), name='password_reset_complete'),

# 2 đường dẫn cho chức năng Đổi mật khẩu (dành cho người đang đăng nhập)
path('password_change/', auth_views.PasswordChangeView.as_view(template_name='password_change.html'), name='password_change'),

path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='password_change_done.html'), name='password_change_done'),

]