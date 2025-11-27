Lưu ý quan trọng
Giới hạn Bot API vs Client API: Cách trên dùng Telethon (Client API) nên tải được file lớn (lên tới 2GB/4GB), phù hợp với file IPA game/app. Nếu dùng Bot API thông thường (python-telegram-bot), bạn chỉ tải được file < 20MB.​

Private Channel: Nếu file nằm trong channel Private, user (tương ứng với Session String) phải là thành viên của channel đó. Link tin nhắn private thường có dạng t.me/c/1234567890/100. Script trên cần tinh chỉnh ID (thêm -100 vào trước ID channel) để hoạt động chính xác với private channel.

Bảo mật: Session String cho phép truy cập toàn quyền vào tài khoản Telegram của bạn. Hãy giữ bí mật tuyệt đối trong GitHub Secrets.
