# ksf-pinterest-autopin

Tự động tạo pin Pinterest cho bài mới trên **kindredspacefinds.com** bằng GitHub Actions.

Cứ 4 giờ một lần, workflow đọc các bài đã đăng qua WordPress REST API, lấy ảnh pin dọc trong
`<figure class="ksf-pinsave">` (ảnh, alt text, `data-pin-description`) rồi tạo pin bằng Pinterest API v5,
có link về bài viết. Bài đã pin được ghi vào `state/posted.json`. Trước khi đăng, script còn kiểm tra board: nếu bài đã có pin (do tài khoản khác hoặc đăng tay) thì bỏ qua, nên không bị pin trùng.
Mỗi lần chạy pin tối đa 2 bài (bài cũ trước), vì vậy các bài cũ cũng sẽ được pin dần dần.

## Trạng thái (23/11/2026)

- App Pinterest **Kindred Space Finds Publisher** (ID 1635267) đã có sẵn, đang Trial, yêu cầu Standard đang chờ duyệt.
- Lịch đăng pin theo kế hoạch (`schedule/pins.csv`, 56 pin từ 25/11 đến 22/12) đã bật trong
  `.github/workflows/scheduled-pins.yml`; nó tự bắt đầu đăng khi có secrets (xem mục *Đăng pin theo lịch*).
- Lịch chạy tự động đang **tạm tắt** trong `.github/workflows/autopin.yml`. Khi Standard được duyệt: lấy refresh token qua OAuth
  (redirect URI đã đăng ký: `https://kindredspacefinds.com/`), nhập secrets, rồi bỏ comment phần `schedule`.
- Trong lúc chờ: Pinterest Auto-publish RSS đã bật cho feed `https://kindredspacefinds.com/category/meal-prep-recipes/feed/`
  → board "Easy Meal Prep & Freezer Recipes". Script này kiểm tra board trước khi đăng nên sẽ bỏ qua bài đã có pin.

## Cài đặt (một lần)

1. **Pinterest business + app**: vào https://developers.pinterest.com/apps/ → *Connect app*.
   Ghi lại **App ID** và **App secret key**. App mới được cấp *Trial access*: pin tạo ra chỉ mình bạn thấy
   (sandbox). Muốn pin công khai phải xin **Standard access** (gửi video demo: đăng nhập OAuth và tạo pin).
2. **Token**: trong trang app, tạo access token có quyền `boards:read`, `boards:write`, `pins:read`, `pins:write`.
   Lưu lại **refresh token** (dùng được khoảng 1 năm; script tự đổi lấy access token mới mỗi lần chạy).
3. **Board ID**: `curl -H "Authorization: Bearer <access token>" https://api.pinterest.com/v5/boards`
   rồi lấy `id` của board muốn đăng.
4. Trong repo GitHub: **Settings → Secrets and variables → Actions**
   - *Secrets*: `PINTEREST_APP_ID`, `PINTEREST_APP_SECRET`, `PINTEREST_REFRESH_TOKEN`
   - *Variables*: `PINTEREST_BOARD_ID`
   - Tuỳ chọn: `BOARD_MAP` = `{"18":"<board công thức>","7":"<board bếp>"}` (key là category ID trên WordPress),
     `ONLY_AFTER` = `2026-11-20` (bỏ qua bài cũ hơn ngày này), `MAX_PINS_PER_RUN`,
     `PINTEREST_API_BASE` = `https://api-sandbox.pinterest.com/v5` để thử khi app còn Trial
     (khi đó dùng secret `PINTEREST_ACCESS_TOKEN` là sandbox token).

## Chạy thử

**Actions → Auto-pin new posts to Pinterest → Run workflow**, để `dry_run = 1`: log sẽ in ra pin sẽ được tạo
mà không đăng gì. Đổi thành `0` để đăng thật. Sau đó lịch 4 giờ/lần tự chạy.

## Đăng pin theo lịch (`schedule/pins.csv`)

Ngoài pin tự động cho bài mới, workflow **Post scheduled pins** đăng các pin đã lên lịch sẵn, mỗi bài
có thể có nhiều pin với tiêu đề/mô tả khác nhau.

- Mỗi dòng trong `schedule/pins.csv` là một pin: `id`, `date` (UTC), `board` (tên board), `title`,
  `description`, `link`, `image`, `alt`.
- Chạy 2 lần/ngày (13:17 và 01:17 UTC, tức 8:17 sáng và 8:17 tối giờ miền Đông Mỹ), mỗi lần 1 pin.
  Pin quá hạn chưa đăng sẽ được đăng dần ở các lần sau.
- Một pin chỉ được đăng khi **đã có ảnh** (file `pins/<id>.jpg|.png|.webp`, xem `pins/README.md`,
  hoặc URL trong cột `image`) **và bài đã lên site** (bài hẹn giờ trả về 404 nên sẽ được chờ).
- Pin đã đăng ghi vào `state/scheduled.json`, không bao giờ đăng lại.
- Board được tìm theo **tên** trong tài khoản Pinterest. Tạo sẵn các board có tên đúng như cột `board`,
  hoặc đặt Variable `BOARD_IDS` = `{"Gifts in a Jar":"<id>","Freezer Meals & Meal Prep":"<id>"}`.
- Khi chưa nhập secrets Pinterest, workflow chỉ ghi log pin nào đến hạn rồi dừng, không báo lỗi.
- Thêm/sửa lịch: sửa `schedule/pins.csv` (id không được trùng). Chạy thử: **Actions → Post scheduled pins →
  Run workflow**, `dry_run = 1`, có thể nhập `today` để giả lập ngày.

## Category ID trên site

Kitchen & Pantry 7 · Bathroom Storage 8 · Closet Systems 9 · Workspace & Garage 10 · Save on Bills 12 ·
Laundry & Cleaning 13 · Living Room & Bedroom 14 · Kids & Pets 15 · Home Maintenance 16 ·
Moving & Decluttering 17 · Meal Prep & Recipes 18
