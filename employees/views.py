from .models import Employee, Department, Position, Attendance, LeaveRequest
from django.shortcuts import render, redirect
from .forms import EmployeeForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout
from django.contrib.auth.models import User
from django.db.models import Count, Q
from django.contrib import messages
from django.http import HttpResponse
from datetime import date, datetime, time
import calendar
import openpyxl

# ===============================
# TRANG CHỦ & DANH SÁCH
# ===============================
def home(request):
    return render(request,'home.html')

def employee_list(request):
    keyword = request.GET.get('q')
    employees = Employee.objects.select_related('department','position','user')
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

@login_required
def dashboard(request):
    today = date.today()
    total_employee = Employee.objects.count()
    total_department = Department.objects.count()

    # Biểu đồ phòng ban
    department_data = Employee.objects.values('department__name').annotate(count=Count('id'))
    labels = [d['department__name'] if d['department__name'] else "Chưa có" for d in department_data]
    data = [d['count'] for d in department_data]

    # Thống kê chấm công
    today_attendance = Attendance.objects.filter(ngay=today)
    present = today_attendance.values('user').distinct().count()
    absent = total_employee - present
    late = Attendance.objects.filter(ngay=today, gio_vao__gt=time(8,0)).count()

    context = {
        'total_employee': total_employee,
        'total_department': total_department,
        'labels': labels,
        'data': data,
        'present': present,
        'absent': absent,
        'late': late
    }
    return render(request,'dashboard.html',context)

# ===============================
# QUẢN LÝ NHÂN VIÊN (CRUD)
# ===============================
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = User.objects.create_user(username=username, password=password)
            employee = form.save(commit=False)
            employee.user = user
            employee.save()
            return redirect('/employees')
    else:
        form = EmployeeForm()
    return render(request,'employee_form.html',{'form': form})

@login_required
def edit_employee(request, id):
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
def delete_employee(request, id):
    if not request.user.is_superuser:
        return redirect('/employees')
    Employee.objects.get(id=id).delete()
    return redirect('/employees')

def logout_view(request):
    logout(request)
    return redirect('/')

# ===============================
# NGHIỆP VỤ NGHỈ PHÉP
# ===============================
@login_required
def leave_request(request):
    try:
        employee = Employee.objects.get(user=request.user)
    except Employee.DoesNotExist:
        if request.user.is_superuser:
            employee = None
        else:
            messages.error(request, f"Lỗi: Tài khoản {request.user.username} chưa có hồ sơ nhân viên!")
            return render(request, 'leave_request.html', {'error_critical': True})

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

    if request.user.is_superuser:
        leaves = LeaveRequest.objects.all().order_by('-start_date')
    else:
        leaves = LeaveRequest.objects.filter(employee=employee).order_by('-start_date')

    return render(request, 'leave_request.html', {
        'leaves': leaves,
        'employee': employee, # Đã thêm dấu phẩy ở đây
        'is_admin': request.user.is_superuser
    })

@login_required
def update_leave_status(request, leave_id, status):
    if not request.user.is_superuser:
        messages.error(request, "Bạn không có quyền thực hiện thao tác này!")
        return redirect('/leave/')

    try:
        leave = LeaveRequest.objects.get(id=leave_id)
        if status in ['approved', 'rejected']:
            leave.status = status
            leave.save()
            messages.success(request, f"Đã cập nhật trạng thái đơn thành: {status}")
    except LeaveRequest.DoesNotExist:
        messages.error(request, "Đơn nghỉ phép không tồn tại!")
    return redirect('/leave/')

@login_required
def export_leave(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Nghi Phep"
    ws.append(["Nhân viên", "Ngày bắt đầu", "Ngày kết thúc", "Lý do", "Trạng thái"])
    leaves = LeaveRequest.objects.select_related('employee','employee__user')
    for l in leaves:
        ws.append([l.employee.user.username, l.start_date, l.end_date, l.reason, l.status])
    response = HttpResponse(content_type="application/ms-excel")
    response["Content-Disposition"] = "attachment; filename=nghi_phep.xlsx"
    wb.save(response)
    return response

@login_required
def my_leave(request):
    employee = Employee.objects.get(user=request.user)
    leaves = LeaveRequest.objects.filter(employee=employee)
    return render(request,'leave_list.html',{'leaves':leaves})

@login_required
def leave_list_admin(request):
    leaves = LeaveRequest.objects.select_related('employee','employee__user').order_by('-start_date')
    return render(request,'leave_admin_list.html',{'leaves': leaves})

# ===============================
# CHẤM CÔNG
# ===============================
@login_required
def attendance_view(request):
    today = date.today()
    records = Attendance.objects.filter(user=request.user).order_by('-ngay','-gio_vao')

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
        if action == 'checkin':
            if Attendance.objects.filter(user=request.user, ngay=today).exists():
                messages.warning(request,"Bạn đã check-in hôm nay rồi")
            else:
                Attendance.objects.create(user=request.user, ngay=today, gio_vao=datetime.now().time())
                messages.success(request,"Check-in thành công")
        elif action == 'checkout':
            record = Attendance.objects.filter(user=request.user, ngay=today, gio_ra__isnull=True).first()
            if record:
                record.gio_ra = datetime.now().time()
                record.save()
                messages.success(request,"Check-out thành công")
            else:
                messages.error(request,"Bạn chưa check-in hôm nay")
        return redirect('attendance')

    return render(request,'attendance.html',{'records':records})

@login_required
def attendance_table(request):
    month = int(request.GET.get('month', datetime.now().month))
    year = int(request.GET.get('year', datetime.now().year))
    days_in_month = calendar.monthrange(year, month)[1]
    employees = Employee.objects.all()
    table = []

    for emp in employees:
        row = {"name": emp.user.username, "days": [], "total": 0}
        for day in range(1, days_in_month + 1):
            try:
                record = Attendance.objects.get(user=emp.user, ngay=date(year, month, day))
                status = "late" if record.gio_vao and record.gio_vao > time(8,0) else "present"
                row["days"].append(status)
                row["total"] += 1
            except Attendance.DoesNotExist:
                row["days"].append("absent")
        table.append(row)

    context = {
        "table": table,
        "days": range(1, days_in_month + 1),
        "month": month,
        "months": range(1,13),
        "year": year,
        "years": range(2023, 2031)
    }
    return render(request,"attendance_table.html",context)

@login_required
def export_attendance(request):
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Cham Cong"
    ws.append(["Nhân viên", "Ngày", "Giờ vào", "Giờ ra", "Tổng giờ làm"])
    records = Attendance.objects.select_related('user').all()

    for r in records:
        tong_gio_str = "0.00h"
        if r.gio_vao and r.gio_ra:
            dummy_date = date(2000, 1, 1)
            start_dt = datetime.combine(dummy_date, r.gio_vao)
            end_dt = datetime.combine(dummy_date, r.gio_ra)
            diff = end_dt - start_dt
            hours = diff.total_seconds() / 3600
            tong_gio_str = f"{max(hours, 0):.2f}h"
        ws.append([r.user.username, r.ngay, r.gio_vao, r.gio_ra, tong_gio_str])

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename="cham_cong.xlsx"'
    wb.save(response)
    return response

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
import google.generativeai as genai
import os
import json

# Lấy API Key từ file .env (Bảo mật)
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

model = genai.GenerativeModel(
    model_name='gemini-1.5-flash',
    system_instruction="Bạn là trợ lý Nhân sự (HR) của công ty. Hãy trả lời ngắn gọn về quy định công ty."
)

@csrf_exempt # Tạm thời bỏ qua CSRF để test dễ hơn
def chatbot_api(request):
    if request.method == "POST":
        data = json.loads(request.body)
        user_message = data.get("message", "")
        
        try:
            response = model.generate_content(user_message)
            return JsonResponse({"reply": response.text})
        except Exception as e:
            return JsonResponse({"reply": "Xin lỗi, hệ thống AI đang bận!"}, status=500)