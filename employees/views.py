from .models import Employee, Department
from django.shortcuts import render,redirect,get_object_or_404
from .forms import EmployeeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout

def home(request):

    return render(request,'home.html')


def employee_list(request):

    keyword = request.GET.get('q')

    employees = Employee.objects.all()

    if keyword:
        employees = employees.filter(user__username__icontains=keyword)

    return render(request,'employee_list.html',{
        'employees':employees
    })


@login_required
def dashboard(request):

    total_employee = Employee.objects.count()

    total_department = Department.objects.count()

    return render(request,'dashboard.html',{
        'total_employee':total_employee,
        'total_department':total_department
    })

def add_employee(request):

    if request.method == 'POST':

        form = EmployeeForm(request.POST)

        if form.is_valid():
            form.save()
            return redirect('/employees')

    else:
        form = EmployeeForm()

    return render(request,'employee_add.html',{'form':form})


def edit_employee(request,id):

    employee = get_object_or_404(Employee,id=id)

    form = EmployeeForm(request.POST or None,instance=employee)

    if form.is_valid():
        form.save()
        return redirect('/employees')

    return render(request,'employee_edit.html',{
        'form':form
    })



def is_admin(user):
    return user.is_superuser

@user_passes_test(is_admin)
def delete_employee(request,id):
    employee = get_object_or_404(Employee,id=id)
    employee.delete()
    return redirect('/employees')


def logout_view(request):
    logout(request)
    return redirect('/')