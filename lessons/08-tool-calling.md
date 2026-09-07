# Concept #8: Tool-calling ở tầng model (structured output/JSON schema) (Giai đoạn 3 - Agent)

Ngày tạo: 2026-09-07

Trạng thái: Đã học (2026-09-07)

🎯 Điểm hay bị hỏi khi phỏng vấn: [08-tool-calling-interview.md](08-tool-calling-interview.md)

## 1. Nó là gì

Ở bài #7, tool call được giả lập bằng if/else. Thực tế, model thật (GPT-4, Claude...) được **fine-tune riêng** để, khi được cấp 1 danh sách "tool schema" (tên tool, mô tả, tham số + kiểu dữ liệu, thường viết bằng JSON Schema) trong request, model sinh ra **structured output** đúng định dạng đó thay vì text tự do.

Về bản chất vẫn là next-token prediction — nhưng model đã học để:
1. Quyết định có nên gọi tool hay trả lời trực tiếp bằng text.
2. Nếu gọi tool: chọn đúng tên tool, sinh object tham số khớp đúng JSON schema đã khai báo.

Request thực tế: system prompt + tool definitions (JSON schema) + conversation history. Response trả về có field riêng (`tool_use` ở Anthropic, `tool_calls` ở OpenAI) chứa tên tool + arguments đã parse được — client tự thực thi tool, gửi `tool_result` ngược lại cho model ở lượt sau.

Một số provider hỗ trợ **constrained decoding**: ép logits chỉ chọn token tạo JSON hợp lệ theo schema, đảm bảo output luôn parse được thay vì chỉ dựa vào model "học tốt".

## 2. Vì sao cần hiểu sâu

Tutorial cơ bản viết "model tự biết gọi tool" như phép màu — bỏ qua việc đây là khả năng **được train riêng**, không phải model nào cũng tốt như nhau. Hiểu cơ chế giúp debug đúng khi agent gọi sai tool/sai tham số: đây là model dự đoán sai token lúc sinh JSON, cách sửa là viết `description` rõ hơn, đặt tên tham số tường minh hơn, hoặc đổi model — không phải sửa code parse JSON.

2 tool có tên/mô tả gần giống dễ khiến model chọn nhầm — vì tên và description tool cũng chỉ là *text trong prompt* để model "suy luận" chọn, không có logic cứng đảm bảo đúng.

## 3. Trade-off / khi nào cần cẩn thận

- Model nhỏ/rẻ dễ sinh sai schema (thiếu field, sai kiểu, "ảo giác" tham số không có) — cần lớp validate + retry ở client, không tin tuyệt đối output.
- Không nên nhồi quá nhiều tool cùng lúc — model dễ chọn nhầm khi danh sách dài; nên nhóm tool theo ngữ cảnh.
- JSON schema quá phức tạp (nested sâu, nhiều optional field) tăng khả năng model sinh sai cấu trúc — nên thiết kế phẳng, rõ ràng.
- Không cần tool-calling nếu task chỉ cần trả lời text thuần — thêm tool tốn token context và có thể khiến model "thừa hành động".

## Ví dụ áp dụng project

Tool `get_order_status(order_id: str)` trong agent e-commerce — description mơ hồ ("lấy thông tin đơn") dễ khiến model nhầm lẫn khi có thêm `get_customer_info(customer_id)` cùng lúc, hoặc sinh `order_id` sai định dạng nếu description không nêu rõ format ví dụ.

## Bài thực hành

File: [practice/08-tool-calling.py](../practice/08-tool-calling.py)

- Định nghĩa 2 tool bằng JSON Schema thật (`get_order_status`, `get_customer_info`).
- Nếu có `ANTHROPIC_API_KEY` trong môi trường: gọi model Claude thật, in ra request/response thật, thấy model tự sinh `tool_use` block, thực thi tool, gửi `tool_result` lượt 2 để lấy câu trả lời cuối.
- Nếu không có key: chạy chế độ offline — dùng 1 ví dụ tự viết tay đúng định dạng thật (không phải output đã gọi API thật) để phân tích cấu trúc request/response mà không cần mạng.

Trạng thái: đã viết code đầy đủ, **chưa chạy** (môi trường agent không có API key lẫn Python cài sẵn) — cần user tự chạy (có hoặc không có API key) và báo lại quan sát.

## Checkpoint (đã đạt — 2026-09-07)

3 câu hỏi đã hỏi (xem đầy đủ Q&A trong [08-tool-calling-interview.md](08-tool-calling-interview.md)):
1. Object tham số tool sinh ra về bản chất là gì (đối chiếu next-token prediction)?
2. Tool description mơ hồ + tool tên gần giống → điều gì xảy ra, vì sao không phải lỗi code Python?
3. Agent gọi sai tham số dù logic Python đúng — nguyên nhân và hướng sửa đầu tiên?

User tự trả lời câu 3 (đúng hướng: do model yếu, cần cải thiện description/instruction — đã làm rõ thêm là "viết lại description/schema", không phải "huấn luyện lại model" như cách diễn đạt ban đầu). Câu 1 và câu 2 user yêu cầu mình trả lời hộ, đã giải thích chi tiết. User xác nhận đánh dấu Đã học. Độ tin cậy: câu 3 verified qua tự trả lời, câu 1-2 chưa — nếu ôn lại nên hỏi lại đúng 2 câu đó trước.
