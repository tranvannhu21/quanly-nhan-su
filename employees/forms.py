from django import forms
from .models import Employee

class EmployeeForm(forms.ModelForm):

    class Meta:
        model = Employee
        fields = ['department','position','phone','address']

        labels = {
            'department': 'Phòng ban',
            'position': 'Chức vụ',
            'phone': 'Số điện thoại',
            'address': 'Địa chỉ',
        }