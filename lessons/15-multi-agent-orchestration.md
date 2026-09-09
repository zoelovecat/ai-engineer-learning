# 15. Multi-agent orchestration (supervisor-worker, debate, blackboard, LangGraph)

**Ngày học:** 2026-09-09
**Trạng thái:** Đã học

Xem thêm: [Phỏng vấn](15-multi-agent-orchestration-interview.md)

## 1. Lý thuyết

Đến bài 7, agent là 1 vòng lặp ReAct đơn: reason → act → observe → lặp. Multi-agent orchestration là khi **tách bài toán thành nhiều agent chuyên biệt**, mỗi agent 1 trách nhiệm hẹp, phối hợp với nhau thay vì nhồi hết logic vào 1 prompt khổng lồ.

Các pattern chính:
- **Supervisor-worker**: 1 agent "supervisor" nhận task, routing tới worker phù hợp, tổng hợp kết quả. Worker không biết về nhau.
- **Debate**: nhiều agent trả lời độc lập, sau đó thấy câu trả lời của nhau và phản biện qua vài vòng — mục tiêu hội tụ về câu trả lời đúng hơn, giảm hallucination/lệch của 1 model đơn.
- **Blackboard**: không có supervisor cố định — có 1 state chung nhiều agent cùng đọc/ghi, agent nào thấy đóng góp được thì tự làm bước tiếp theo. Linh hoạt hơn nhưng khó kiểm soát thứ tự.
- **LangGraph**: không phải 1 pattern riêng — là framework hiện thực các pattern trên dưới dạng state machine (graph: node = bước/agent, edge = điều kiện chuyển bước), thay vì if/else lồng nhau.

**Vì sao cần:** task phức tạp (nhiều loại yêu cầu khác nhau trong 1 hệ thống) nếu nhồi vào 1 system prompt sẽ khiến prompt quá dài (liên quan lost-in-the-middle — bài 16), không tách được trách nhiệm để test/debug riêng, không tận dụng được model khác nhau cho việc khác nhau.

**Trade-off / khi nào KHÔNG dùng:**
- Chi phí + latency tăng: mỗi lần chuyển giao giữa agent thường là thêm 1 lần gọi LLM. Task đơn giản (1-2 tool call, hoặc logic deterministic có sẵn) dùng multi-agent là over-engineering.
- Debug khó hơn: lỗi có thể nằm ở routing (supervisor giao sai) chứ không phải ở worker.
- Debate tốn nhất — chỉ đáng dùng khi độ chính xác quan trọng hơn cost/latency nhiều lần (vd moderation nội dung), không dùng cho chatbot trả lời nhanh.
- Blackboard khó kiểm soát nhất — dễ vòng lặp vô hạn hoặc nhiều agent giẫm chân nhau nếu thiếu điều kiện dừng rõ ràng.
- Junior vs middle: junior thấy multi-agent hay là áp dụng bừa; middle mặc định thử supervisor-worker đơn giản trước, chỉ leo thang lên debate/blackboard khi có bằng chứng qua eval (bài 11/12) rằng 1 agent đơn không đủ.

## 2. Ví dụ áp dụng

Use case: **Trợ lý nhân sự nội bộ** — nhân viên hỏi 1 câu, có thể là:
- Hỏi chính sách/luật lao động → cần tra văn bản chính xác → `PolicyWorker` (tái sử dụng THẬT `HybridSearchIndex` từ bài 3/9).
- Yêu cầu xử lý thật trên hệ thống HR (check phép còn lại, xin nghỉ) → `LeaveWorker` (mock database).
- Có thể cần cả 2 cùng lúc.

`Supervisor` chỉ routing (quyết định worker nào xử lý) + tổng hợp kết quả — không tự đọc/hiểu nội dung. Với model thật, bước routing chính là 1 lần gọi LLM với structured output (bài 8) trả về JSON `{"needs_policy": bool, "needs_leave": bool, ...}`.

Code đầy đủ, đã chạy thật: [practice/15-multi-agent-supervisor.py](../practice/15-multi-agent-supervisor.py).

Kết quả chạy thật đáng chú ý: Query 3 (câu hỏi ghép cả policy + leave) → `PolicyWorker` trả về Điều 20/36 — không thực sự liên quan tới "nghỉ liên tục bao nhiêu ngày" vì văn bản mẫu không có điều khoản đó. Đây là giới hạn thật của hybrid search (bài 3) lộ ra trong kiến trúc multi-agent: supervisor tin tưởng tuyệt đối vào output worker, không có cơ chế kiểm tra chất lượng.

## 3. Bài thực hành đã giao

Chọn 1 trong 2 (chưa hoàn thành trong buổi này, để làm sau):
1. Thêm confidence check trong `PolicyWorker.handle()`: nếu điểm RRF top-1 quá thấp, trả về "Không tìm thấy quy định phù hợp" thay vì trả bừa.
2. Viết test nhỏ kiểm tra routing đúng chi phí: câu hỏi chỉ về leave thì `PolicyWorker` không được gọi (đếm số lần gọi).

## 4. Checkpoint

**Câu 1:** Nếu supervisor gặp câu hỏi chỉ liên quan leave nhưng bug routing gọi thừa `PolicyWorker`, hậu quả thực tế là gì?
- Trả lời ban đầu: câu trả lời thừa nội dung, gây khó chịu UX (đúng 1 phần).
- Bổ sung: hậu quả nghiêm trọng hơn trong production là **chi phí + latency** — mỗi lần gọi thừa tốn 1 lần encode embedding + hybrid search, âm thầm nhân chi phí lên ở scale lớn mà khó nhận ra bằng mắt (khác bug logic sai — dễ phát hiện vì câu trả lời sai rõ).

**Câu 2:** Agent moderation nội dung (accuracy > speed/cost) nên dùng pattern nào?
- Trả lời: **debate** — đúng. Giảm hallucination/lệch của 1 model đơn qua nhiều model phản biện nhau, phù hợp khi độ chính xác quan trọng hơn cost/latency.

**Câu 3:** Tình huống KHÔNG cần multi-agent, chỉ cần 1 agent đơn (hoặc không cần agent).
- Trả lời: bài toán booking đơn giản — logic check điều khoản/phòng/slot đã deterministic, nằm sẵn trong hàm booking, không cần orchestration nhiều agent. Đúng hướng.

**Câu hỏi follow-up (giám sát production):** Dùng công cụ nào để phát hiện sớm bug "routing gọi thừa worker"?
- Trả lời: **Langfuse** (bài 10) — đúng. Dùng tracing/span để đo số lần gọi mỗi worker, latency/cost mỗi span.

Checkpoint đạt 3/3 (câu 1 cần bổ sung ý cost/latency, sau đó xác nhận hiểu qua câu follow-up). User xác nhận đánh dấu Đã học.
