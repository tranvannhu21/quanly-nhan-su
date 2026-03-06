from django.db import models
from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name


class Position(models.Model):

    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title


class Employee(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE)

    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True)

    position = models.ForeignKey(Position, on_delete=models.SET_NULL, null=True)

    phone = models.CharField(max_length=20)

    address = models.TextField()

    photo = models.ImageField(upload_to='employees/', null=True, blank=True)

    def __str__(self):
        return self.user.username


class LeaveRequest(models.Model):

    STATUS = (
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối')
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)

    start_date = models.DateField()
    end_date = models.DateField()

    reason = models.TextField()

    status = models.CharField(max_length=20, choices=STATUS, default='pending')

class Attendance(models.Model):

    employee = models.ForeignKey(Employee,on_delete=models.CASCADE)

    date = models.DateField(auto_now_add=True)

    check_in = models.TimeField(auto_now_add=True)

    def __str__(self):
        return str(self.employee)