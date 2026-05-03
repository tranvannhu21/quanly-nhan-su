from .models import Employee, Department, Position
from django.shortcuts import render, redirect
from .forms import EmployeeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from .models import Attendance, LeaveRequest
from datetime import date, datetime
from django.contrib.auth.models import User
from django.db.models import Count
from django.contrib import messages
import calendar
from django.db.models import Q
import openpyxl
from django.http import HttpResponse
from datetime import time

def home(request):
    return render(request,'home.html')

def employee_list(request):

    keyword = request.GET.get('q')

    employees = Employee.objects.select_related(
        'department','position','user'
    )

    if keyword:
        employees = employees.filter(
            Q(user__username__icontains=keyword) |
            Q(department__name__icontains=keyword) |
            Q(position__title__icontains=keyword)
        )

    return render(request,'employee_list.html',{
        'employees': employees,
        'keyword': keyword
    })


from datetime import date, time

@login_required
def dashboard(request):

    today = date.today()

    # tổng nhân viên
    total_employee = Employee.objects.count()

    # tổng phòng ban
    total_department = Department.objects.count()

    # ====== biểu đồ phòng ban ======

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

    # ====== thống kê chấm công hôm nay ======

    today_attendance = Attendance.objects.filter(ngay=today)

    present = today_attendance.values('user').distinct().count()

    absent = total_employee - present

    late = Attendance.objects.filter(
        ngay=today,
        gio_vao__gt=time(8,0)
    ).count()

    context = {
        'total_employee': total_employee,
        'total_department': total_department,
        'labels': labels,
        'data': data,

        # thêm dashboard chấm công
        'present': present,
        'absent': absent,
        'late': late
    }

    return render(request,'dashboard.html',context)


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
    # 1. Thử tìm hồ sơ nhân viên
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        # Thay vì redirect, ta báo lỗi trực tiếp trên trang để biết đường mà sửa
        messages.error(request, f"Lỗi: Tài khoản {request.user.username} chưa có hồ sơ trong bảng Employee!")
        # Nếu không có hồ sơ thì không cho làm gì tiếp, hiện trang trắng kèm lỗi
        return render(request, 'leave_request.html', {'error_critical': True})

    # 2. Xử lý POST (Gửi đơn)
    if request.method == "POST":
        start = request.POST.get("start_date")
        end = request.POST.get("end_date")
        reason = request.POST.get("reason")

        LeaveRequest.objects.create(
            employee=employee,
            start_date=start,
            end_date=end,
            reason=reason,
            status="pending"
        )
        messages.success(request, "Gửi đơn thành công!")
        return redirect('/leave/')

    # 3. Lấy lịch sử (Chỉ lấy của mình hoặc lấy tất cả nếu là Admin)
    if request.user.is_superuser:
        leaves = LeaveRequest.objects.all().order_by('-start_date')
    else:
        leaves = LeaveRequest.objects.filter(employee=employee).order_by('-start_date')

    return render(request, 'leave_request.html', {
        'leaves': leaves,
        'employee': employee
        'is_admin': request.user.is_superuser
    })

@login_required
def update_leave_status(request, leave_id, status):
    # Chỉ cho phép tài khoản Admin/Staff thao tác
    if not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền thực hiện thao tác này!")
        return redirect('/leave/')

    try:
        leave = LeaveRequest.objects.get(id=leave_id)
        # Cập nhật trạng thái dựa trên tham số truyền vào (approved/rejected)
        if status in ['approved', 'rejected']:
            leave.status = status
            leave.save()
            messages.success(request, f"Đã cập nhật trạng thái đơn thành: {status}")
    except LeaveRequest.DoesNotExist:
        messages.error(request, "Đơn nghỉ phép không tồn tại!")

    return redirect('/leave/')

import openpyxl
from django.http import HttpResponse

@login_required
def export_leave(request):

    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Nghi Phep"

    ws.append([
        "Nhân viên",
        "Ngày bắt đầu",
        "Ngày kết thúc",
        "Lý do",
        "Trạng thái"
    ])

    leaves = LeaveRequest.objects.select_related('employee','employee__user')

    for l in leaves:

        ws.append([
            l.employee.user.username,
            l.start_date,
            l.end_date,
            l.reason,
            l.status
        ])

    response = HttpResponse(
        content_type="application/ms-excel"
    )

    response["Content-Disposition"] = "attachment; filename=nghi_phep.xlsx"

    wb.save(response)

    return response

@login_required
def my_leave(request):

    employee = Employee.objects.get(user=request.user)

    leaves = LeaveRequest.objects.filter(employee=employee)

    return render(request,'leave_list.html',{'leaves':leaves})


# ===============================
# CHẤM CÔNG
# ===============================

@login_required
def attendance_view(request):

    today = date.today()

    records = Attendance.objects.filter(
        user=request.user
    ).order_by('-ngay','-gio_vao')

    # ===== TÍNH SỐ GIỜ LÀM =====
    for r in records:

        if r.gio_vao and r.gio_ra:

            start = datetime.combine(r.ngay, r.gio_vao)
            end = datetime.combine(r.ngay, r.gio_ra)

            diff = end - start

            hours = diff.total_seconds() / 3600

            r.work_hours = f"{hours:.2f}h"

        else:
            r.work_hours = "--"

    if request.method == 'POST':

        action = request.POST.get('action')

        # ===== CHECK IN =====
        if action == 'checkin':

            already_checked = Attendance.objects.filter(
                user=request.user,
                ngay=today
            ).exists()

            if already_checked:
                messages.warning(request,"Bạn đã check-in hôm nay rồi")
            else:
                Attendance.objects.create(
                    user=request.user,
                    ngay=today,
                    gio_vao=datetime.now().time()
                )
                messages.success(request,"Check-in thành công")

        # ===== CHECK OUT =====
        elif action == 'checkout':

            record = Attendance.objects.filter(
                user=request.user,
                ngay=today,
                gio_ra__isnull=True
            ).first()

            if record:
                record.gio_ra = datetime.now().time()
                record.save()
                messages.success(request,"Check-out thành công")
            else:
                messages.error(request,"Bạn chưa check-in hôm nay")

        return redirect('attendance')

    return render(request,'attendance.html',{
        'records':records
    })

@login_required
def attendance_table(request):

    # ===== LẤY THÁNG =====
    month = request.GET.get('month')

    if not month:
        month = datetime.now().month
    else:
        month = int(month)

    # ===== LẤY NĂM =====
    year = request.GET.get('year')

    if not year:
        year = datetime.now().year
    else:
        year = int(year)

    # ===== SỐ NGÀY TRONG THÁNG =====
    days_in_month = calendar.monthrange(year, month)[1]

    employees = Employee.objects.all()

    table = []

    for emp in employees:

        row = {
            "name": emp.user.username,
            "days": [],
            "total": 0
        }

        for day in range(1, days_in_month + 1):

            try:

                record = Attendance.objects.get(
                    user=emp.user,
                    ngay=date(year, month, day)
                )

                # kiểm tra đi muộn
                if record.gio_vao and record.gio_vao > time(8,0):
                    row["days"].append("late")
                else:
                    row["days"].append("present")

                row["total"] += 1

            except Attendance.DoesNotExist:

                row["days"].append("absent")

        table.append(row)

    # ===== DANH SÁCH NĂM =====
    years = range(2023, 2031)

    context = {
        "table": table,
        "days": range(1, days_in_month + 1),
        "month": month,
        "months": range(1,13),
        "year": year,
        "years": years
    }

    return render(request,"attendance_table.html",context)

@login_required
def export_attendance(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Cham Cong"

    # Thêm tiêu đề cột
    ws.append(["Nhân viên", "Ngày", "Giờ vào", "Giờ ra", "Tổng giờ làm"])

    records = Attendance.objects.select_related('user').all()

    for r in records:
        tong_gio_str = "0.00h"
        
        # Kiểm tra xem có đủ dữ liệu giờ vào và giờ ra không
        if r.gio_vao and r.gio_ra:
            # Sử dụng datetime.combine thông qua class datetime
            # Chúng ta dùng một ngày mặc định vì chỉ cần tính độ lệch thời gian
            dummy_date = date(2000, 1, 1)
            start_dt = datetime.combine(dummy_date, r.gio_vao)
            end_dt = datetime.combine(dummy_date, r.gio_ra)
            
            # Tính toán hiệu số
            diff = end_dt - start_dt
            hours = diff.total_seconds() / 3600
            
            if hours > 0:
                tong_gio_str = f"{hours:.2f}h"
            else:
                tong_gio_str = "0.00h"

        ws.append([
            r.user.username,
            r.ngay,
            r.gio_vao,
            r.gio_ra,
            tong_gio_str
        ])

    # Tạo response trả về file Excel
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = 'attachment; filename="cham_cong.xlsx"'
    wb.save(response)

    return response


@login_required
def leave_list_admin(request):

    leaves = LeaveRequest.objects.select_related('employee','employee__user')\
        .order_by('-start_date')

    return render(request,'leave_admin_list.html',{
        'leaves': leaves
    })