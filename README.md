# Hệ thống Quản lý Nhân sự (HRM System)

Đây là dự án ứng dụng web quản lý nhân sự nội bộ, được phát triển bằng framework Django (Python). Hệ thống hỗ trợ các tính năng cốt lõi: Quản lý danh sách nhân viên, theo dõi chấm công hằng ngày, quản lý đơn xin nghỉ phép và hệ thống phân quyền (Admin/Nhân viên).

## 1. Yêu cầu hệ thống
- Python 3.8 trở lên.

## 2. Hướng dẫn cài đặt và khởi chạy (Môi trường Local)

**Bước 1: Mở Terminal/Command Prompt tại thư mục gốc của dự án.**

**Bước 2: Thiết lập môi trường ảo (Virtual Environment)**
- Hệ điều hành Windows:
  ```bash
  python -m venv venv
  venv\Scripts\activate
Hệ điều hành macOS/Linux:
python3 -m venv venv
source venv/bin/activate

**Bước 3: Cài đặt các thư viện phụ thuộc
Hệ thống sử dụng các thư viện như Django, django-axes (bảo mật khóa tài khoản),... Chạy lệnh sau để cài đặt toàn bộ:
pip install -r requirements.txt

**Bước 4: Khởi chạy máy chủ ảo
Do dự án đã đi kèm file db.sqlite3 chứa sẵn dữ liệu, bạn không cần phải chạy lệnh migrate. Khởi chạy trực tiếp bằng lệnh:
python manage.py runserver
Sau đó, mở trình duyệt web và truy cập vào địa chỉ: http://127.0.0.1:8000

## 3. Tài khoản Kiểm thử (Đã cấu hình sẵn)
Để tiện cho việc đánh giá, hệ thống đã được tạo sẵn dữ liệu phòng ban (IT, Marketing, Nhân Sự, Kế Toán) và các tài khoản sau:

Tài khoản Quản trị viên (Full Quyền):

Tên đăng nhập: tranvannhu

Mật khẩu: 123456

Tài khoản Nhân viên (Để test chấm công/nghỉ phép):

Tên đăng nhập: tranvannhu21 (Phòng Nhân Sự)

Tên đăng nhập: haminhquang (Phòng Marketing)

Mật khẩu chung: 123456
