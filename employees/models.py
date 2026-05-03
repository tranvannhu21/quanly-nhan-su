from django.db import models
from django.contrib.auth.models import User


class Department(models.Model):

    name = models.CharField("Tên phòng ban", max_length=100)

    def __str__(self):
        return self.name

    class Meta:
        verbose_name = "Phòng ban"
        verbose_name_plural = "Phòng ban"


class Position(models.Model):

    title = models.CharField("Chức vụ", max_length=100)

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Chức vụ"
        verbose_name_plural = "Chức vụ"


class Employee(models.Model):

    user = models.OneToOneField(User, on_delete=models.CASCADE, verbose_name="Tài khoản")

    department = models.ForeignKey(
        Department,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Phòng ban"
    )

    position = models.ForeignKey(
        Position,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name="Chức vụ"
    )

    phone = models.CharField("Số điện thoại", max_length=20)

    address = models.TextField("Địa chỉ")

    photo = models.ImageField("Ảnh nhân viên", upload_to='employees/', null=True, blank=True)

    def __str__(self):
        return self.user.username

    class Meta:
        verbose_name = "Nhân viên"
        verbose_name_plural = "Nhân viên"


class LeaveRequest(models.Model):

    STATUS = (
        ('pending', 'Chờ duyệt'),
        ('approved', 'Đã duyệt'),
        ('rejected', 'Từ chối')
    )

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name="Nhân viên")

    start_date = models.DateField("Ngày bắt đầu")

    end_date = models.DateField("Ngày kết thúc")

    reason = models.TextField("Lý do")

    status = models.CharField(
        "Trạng thái",
        max_length=20,
        choices=STATUS,
        default='pending'
    )

    def __str__(self):
        return f"{self.employee} - {self.start_date}"

    class Meta:
        verbose_name = "Đơn nghỉ phép"
        verbose_name_plural = "Đơn nghỉ phép"


class Attendance(models.Model):

    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Nhân viên")

    ngay = models.DateField("Ngày", auto_now_add=True)

    gio_vao = models.TimeField("Giờ vào", null=True, blank=True)

    gio_ra = models.TimeField("Giờ ra", null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.ngay}"

    class Meta:
        verbose_name = "Chấm công"
        verbose_name_plural = "Chấm công"