from django.contrib import admin
from .models import Department, Position, Employee, LeaveRequest, Attendance


admin.site.register(Department)
admin.site.register(Position)
admin.site.register(Employee)
admin.site.register(LeaveRequest)
admin.site.register(Attendance)