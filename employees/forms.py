from django import forms
from django.contrib.auth.models import User
from .models import Employee

class EmployeeForm(forms.ModelForm):

    username = forms.CharField(label="Tên đăng nhập")
    password = forms.CharField(widget=forms.PasswordInput,label="Mật khẩu")

    class Meta:
        model = Employee
        fields = ['department','position','phone','address']

        labels = {
            'department': 'Phòng ban',
            'position': 'Chức vụ',
            'phone': 'Số điện thoại',
            'address': 'Địa chỉ',
        }