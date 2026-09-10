# Phỏng vấn — Prompt versioning (version control, A/B test)

Lesson chính: [22-prompt-versioning.md](22-prompt-versioning.md)

## Q&A

**Q: Prompt versioning là gì, vì sao không hardcode prompt trong code?**
A: Quản lý prompt như code — version ID, diff, rollback, tách khỏi code để đổi prompt không cần deploy lại app. Hardcode trong code khiến mọi thay đổi nhỏ phải qua PR+deploy, chậm, và khó biết chắc version nào đang chạy production khi debug.

**Q: Trước khi đưa 1 prompt mới vào A/B test với user thật, bước nào nên làm trước?**
A: Chạy qua golden set offline (bài 11) trước — so kết quả version mới với version cũ trên tập câu hỏi đã biết đáp án đúng, không tốn traffic thật. Chỉ khi không regression mới chuyển sang A/B test thật.

**Q: A/B test prompt cần thiết kế gì để kết luận đáng tin cậy?**
A: Traffic split hợp lý (bắt đầu nhỏ, vd 90/10), chạy tới đủ cỡ mẫu (không cố định theo thời gian mà theo số request tối thiểu để giảm nhiễu), quyết định dựa trên chênh lệch có ý nghĩa thống kê chứ không phải chênh lệch nhỏ ngẫu nhiên, và có khả năng rollback ngay nếu phát hiện lỗi nghiêm trọng trong lúc test.

**Q: Vì sao 20 request A/B test không đủ để quyết định rollout?**
A: Mẫu quá nhỏ, chênh lệch quan sát được rất dễ chỉ là nhiễu ngẫu nhiên (may mắn gặp case dễ ở 1 nhánh) chứ không phải khác biệt thật giữa 2 version — cần cỡ mẫu đủ lớn mới kết luận đáng tin.

**Q: Offline eval (golden set) và A/B test online khác nhau thế nào, dùng cả 2 khi nào?**
A: Offline eval nhanh, an toàn (không ảnh hưởng user thật) nhưng có thể không phản ánh hết đa dạng hành vi thật; A/B test online đo đúng outcome thực nhưng chậm và có rủi ro nếu version mới tệ. Cách đúng: dùng offline eval lọc trước (loại bỏ version rõ tệ hơn), rồi mới đưa version đã qua lọc vào A/B test thật với traffic nhỏ.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Bẫy chính (từ checkpoint thật):** nêu đúng tên công cụ (Langfuse) nhưng không tự nêu được QUY TRÌNH — cụ thể là bước "chạy qua golden set trước khi A/B test thật". Biết tên tool không thay thế được hiểu quy trình.
- Nhầm A/B test chỉ cần "chạy 1 thời gian rồi so sánh" mà không quan tâm cỡ mẫu — dễ kết luận vội với mẫu nhỏ (20 request), dẫn tới rollout dựa trên nhiễu ngẫu nhiên thay vì khác biệt thật.
- Quên rollback phải làm được NGAY khi phát hiện lỗi nghiêm trọng trong lúc A/B test đang chạy, không phải đợi hết chu kỳ test theo kế hoạch.
- Nhầm offline eval và A/B test online là 2 lựa chọn thay thế nhau (chọn 1 trong 2) — thực ra nên dùng tuần tự: offline lọc trước, online xác nhận sau, không bỏ qua bước nào.

## Bảng so sánh nhanh

| | Git-based (tự quản, file YAML/JSON trong repo) | Registry chuyên dụng (Langfuse Prompt Management, PromptLayer, LangSmith Hub) |
|---|---|---|
| Version/diff | Có, qua git history | Có, thường có UI diff trực quan |
| Đổi prompt không cần deploy code | Không hẳn — vẫn cần app đọc file mới hoặc redeploy | Có — app fetch theo version ID từ registry tại runtime |
| A/B test theo % traffic | Phải tự code routing | Thường có sẵn cơ chế routing/label (production/staging) |
| Phù hợp khi | Team nhỏ, ít thay đổi, ưu tiên đơn giản | Đổi prompt thường xuyên, cần A/B test/rollback nhanh không qua deploy |
