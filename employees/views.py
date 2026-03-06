from .models import Employee, Department, Position
from django.shortcuts import render,redirect,get_object_or_404
from .forms import EmployeeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import logout
from .models import Attendance
from datetime import date
from django.contrib.auth.models import User
from .models import LeaveRequest
from django.db.models import Count

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

    department_data = (
        Employee.objects
        .values('department__name')
        .annotate(count=Count('id'))
    )

    labels = []
    data = []

    for d in department_data:
        labels.append(d['department__name'] if d['department__name'] else "Chưa có")
        data.append(d['count'])

    return render(request,'dashboard.html',{
        'total_employee':total_employee,
        'total_department':total_department,
        'labels':labels,
        'data':data
    })
def add_employee(request):

    if request.method == 'POST':

        form = EmployeeForm(request.POST)

        if form.is_valid():

            username = form.cleaned_data['username']
            password = form.cleaned_data['password']

            user = User.objects.create_user(
                username=username,
                password=password
            )

            employee = form.save(commit=False)
            employee.user = user
            employee.save()

            return redirect('/employees')

    else:

        form = EmployeeForm()

    return render(request,'employee_form.html',{
        'form': form
    })

@login_required
def edit_employee(request,id):

    employee = Employee.objects.get(id=id)

    # nếu không phải admin và không phải chính mình
    if not request.user.is_superuser and employee.user != request.user:
        return redirect('/employees')

    departments = Department.objects.all()
    positions = Position.objects.all()

    if request.method == 'POST':

        employee.department_id = request.POST.get('department')
        employee.position_id = request.POST.get('position')

        employee.phone = request.POST.get('phone')
        employee.address = request.POST.get('address')

        if request.FILES.get('photo'):
            employee.photo = request.FILES.get('photo')

        employee.save()

        return redirect('/employees')

    return render(request,'employee_edit.html',{
        'employee':employee,
        'departments':departments,
        'positions':positions
    })



def is_admin(user):
    return user.is_superuser

@login_required
def delete_employee(request,id):

    if not request.user.is_superuser:
        return redirect('/employees')

    employee = Employee.objects.get(id=id)

    employee.delete()

    return redirect('/employees')


def logout_view(request):
    logout(request)
    return redirect('/')

@login_required
def leave_request(request):

    if request.method == "POST":

        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        reason = request.POST.get("reason")

        employee = Employee.objects.get(user=request.user)

        LeaveRequest.objects.create(
            employee=employee,
            start_date=start,
            end_date=end,
            reason=reason,
            status="Pending"
        )

        return redirect('/')

    return render(request,'leave_request.html')

@login_required
def my_leave(request):

    employee = Employee.objects.get(user=request.user)

    leaves = LeaveRequest.objects.filter(employee=employee)

    return render(request,'leave_list.html',{'leaves':leaves})

@login_required
def checkin(request):

    employee = Employee.objects.filter(user=request.user).first()

    if not employee:
        return redirect('/')

    if request.method == 'POST':

        today = date.today()

        already = Attendance.objects.filter(employee=employee,date=today).exists()

        if not already:
            Attendance.objects.create(employee=employee)

    records = Attendance.objects.filter(employee=employee).order_by('-date')

    return render(request,'attendance.html',{
        'records':records
    })