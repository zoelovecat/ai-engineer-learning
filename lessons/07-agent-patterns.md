# Concept #7: Pattern suy luận agent — ReAct / Plan-and-Execute / Reflexion (Giai đoạn 3 - Agent)

Ngày tạo: 2026-09-07

Trạng thái: Đã học (2026-09-07)

🎯 Điểm hay bị hỏi khi phỏng vấn: [07-agent-patterns-interview.md](07-agent-patterns-interview.md)

## 1. Nó là gì

3 kiến trúc điều khiển vòng lặp agent:

- **ReAct (Reason + Act)**: vòng lặp `Thought → Action → Observation → Thought → ...`. Model tự sinh suy nghĩ, quyết định action dựa trên observation của bước trước, lặp lại — không có kế hoạch cố định trước, "vừa đi vừa dò đường".
- **Plan-and-Execute**: tách 2 pha — **Planner** sinh toàn bộ danh sách bước *trước khi* thực thi bất kỳ hành động nào; **Executor** chạy tuần tự từng bước (có thể model con riêng). Có thể replan nếu 1 bước thất bại.
- **Reflexion**: sau khi hoàn thành/thất bại task, agent tự sinh "self-reflection" (tự phê bình bằng text), lưu vào memory, thử lại có tham chiếu bài học đó. Cơ chế "verbal reinforcement learning" — không update trọng số, chỉ đưa feedback ngôn ngữ vào context cho lần sau.

## 2. Vì sao cần hiểu sâu

Tutorial cơ bản chỉ demo ReAct (dễ code bằng 1 vòng `while`), bỏ qua việc mỗi pattern hợp 1 dạng task khác nhau: ReAct hợp task "khám phá" (chưa biết trước số bước, observation quyết định bước sau); Plan-and-Execute hợp task có cấu trúc rõ, cần **audit kế hoạch trước khi chạy** (quan trọng khi hành động có ảnh hưởng thật — vd tạo hoàn tiền); Reflexion hợp khi cho phép thử nhiều lần và có tín hiệu thất bại rõ ràng.

## 3. Trade-off / khi nào KHÔNG dùng

- **ReAct**: latency cộng dồn theo số bước (mỗi vòng là 1 lần gọi LLM riêng); dễ lạc đường nếu task dài (error compounding); không audit được trước khi chạy.
- **Plan-and-Execute**: kế hoạch có thể sai ngay từ đầu do thiếu observation thực tế; cần thêm cơ chế replanning; không hợp task cần phản ứng tức thời theo quan sát nhỏ.
- **Reflexion**: thêm hẳn 1 vòng lặp thử-fail-reflect-thử lại → tốn nhiều lần gọi LLM hơn; không có tín hiệu thất bại khách quan thì model có thể "ảo tưởng" đã đúng.
- Chọn pattern theo đặc điểm task: số bước biết trước không, cần audit trước khi chạy không, có chấp nhận thử nhiều lần không — đây là điểm phân biệt middle (chọn đúng kiến trúc) với junior (dùng 1 khối `AgentExecutor` chung chung).

## Ví dụ áp dụng project

Agent hỗ trợ khách hàng e-commerce, tool: `get_order_status`, `get_shipping_estimate`, `create_refund`.

- "Đơn #A1023 bao giờ tới?" → **ReAct** — chưa biết trước cần tra estimate hay không, tùy status trả về.
- "Đổi trả đơn #A1023 vì hàng lỗi, xử lý hoàn tiền" → **Plan-and-Execute** — cần audit kế hoạch trước khi thực thi vì ảnh hưởng tiền thật.
- Agent lặp lại lỗi hiểu sai policy đổi trả → thêm **Reflexion** để tự sửa qua các lần thử.

## Bài thực hành

File: [practice/07-agent-patterns.py](../practice/07-agent-patterns.py) — không cần API key thật, dùng "LLM giả" (mock, rule-based) để tập trung vào **kiến trúc điều khiển**, không phụ thuộc chất lượng suy luận model thật.

1. `MockTools`: `get_order_status`, `get_shipping_estimate` trả dữ liệu cứng.
2. `run_react`: vòng `while` gọi `fake_llm_react_step(state)` — số bước **không cố định**, phụ thuộc observation (đơn "đang giao" → thêm 1 bước tra SLA; đơn "đã giao"/"chưa gửi" → trả lời ngay).
3. `run_plan_and_execute`: `fake_llm_planner(query)` sinh **toàn bộ plan 1 lần**, in ra để audit trước khi thực thi, rồi vòng `for` chạy tuần tự.
4. So sánh 3 query mẫu: 2 query ReAct chạy số bước khác nhau (tùy trạng thái đơn), 1 query Plan-and-Execute in được kế hoạch đầy đủ trước khi tool nào chạy.

Code đã implement đầy đủ (không phải khung TODO) — các comment `TODO (học: ...)` trong file đánh dấu đúng điểm kiến trúc cần chú ý khi đọc code, không phải chỗ cần tự viết thêm.

Trạng thái: đã viết xong code đầy đủ, **chưa chạy thật** (môi trường agent không có Python cài sẵn, dù bài này chỉ dùng standard library nên chạy được ngay không cần cài gì) — cần user tự chạy và báo kết quả.

## Checkpoint (đã đạt — 2026-09-07)

3 câu hỏi đã hỏi (xem đầy đủ Q&A trong [07-agent-patterns-interview.md](07-agent-patterns-interview.md)):
1. Số bước ReAct của Query 1 vs Query 2 và vì sao khác nhau.
2. Vì sao Plan-and-Execute in được toàn bộ kế hoạch trước khi thực thi, còn ReAct thì không.
3. Chọn pattern nào khi cần con người duyệt trước khi hoàn tiền, vì sao.

User yêu cầu mình trả lời hộ cả 3 câu (không tự giải thích trước) — mình đã trả lời và giải thích chi tiết dựa trên code thật trong `practice/07-agent-patterns.py`. Sau khi đọc, user xác nhận đánh dấu **Đã học**. Lưu ý: hiểu biết concept này chưa được verify bằng cách user tự diễn giải lại — nếu sau này ôn lại thấy còn mơ hồ, nên ưu tiên hỏi lại đúng 3 câu này trước.
