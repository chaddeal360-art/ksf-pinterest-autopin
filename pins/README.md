# Ảnh pin theo lịch

Đặt ảnh pin dọc vào thư mục này, **tên file = cột `id`** trong `schedule/pins.csv`, ví dụ:

```
pins/2026-11-25-a.jpg
pins/2026-11-25-b.png
```

- Kích thước nên dùng: **1000 × 1500 px** (tỷ lệ 2:3), JPG/PNG/WebP, dưới 10 MB.
- Có thể upload thẳng trên GitHub (điện thoại cũng được): mở thư mục `pins` → **Add file → Upload files**.
- Hoặc dán URL ảnh (ví dụ ảnh đã tải lên WordPress) vào cột `image` của dòng đó trong `schedule/pins.csv`.

Pin nào đến ngày mà chưa có ảnh sẽ chờ, có ảnh là lần chạy kế tiếp đăng luôn.
