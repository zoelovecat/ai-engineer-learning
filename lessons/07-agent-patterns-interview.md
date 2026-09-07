# Interview notes: Pattern suy luận agent (ReAct / Plan-and-Execute / Reflexion)

Lesson chính: [07-agent-patterns.md](07-agent-patterns.md)

## Q&A có thể gặp

**Q: ReAct và Plan-and-Execute khác nhau ở đâu về mặt kiến trúc?**
A: ReAct quyết định từng bước MỘT dựa trên observation của bước trước — không biết trước số bước hay nội dung bước sau. Plan-and-Execute sinh TOÀN BỘ kế hoạch một lần trước khi thực thi bất kỳ hành động nào — có thể audit/review kế hoạch trước khi agent làm gì.

**Q: Vì sao Plan-and-Execute lại quan trọng cho các hành động có ảnh hưởng thật (vd giao dịch tiền)?**
A: Vì kế hoạch được sinh ra và có thể hiển thị/review TRƯỚC khi bất kỳ tool nào chạy — cho phép con người hoặc hệ thống kiểm soát chấp thuận trước khi agent hành động. ReAct không cho phép điều này vì bước 2 chỉ được quyết định SAU khi có observation của bước 1 (đã lỡ chạy rồi).

**Q: Reflexion khác gì so với việc chỉ đơn giản thêm "few-shot example lỗi trước" vào prompt?**
A: Về bản chất là tương tự (đều là đưa feedback bằng ngôn ngữ vào context), khác biệt là Reflexion tạo self-reflection MỘT CÁCH TỰ ĐỘNG dựa trên kết quả/thất bại thật của chính agent trong task hiện tại (không phải ví dụ soạn sẵn trước), và có thể lặp qua nhiều vòng thử trong cùng 1 session.

**Q: Reflexion có luôn cải thiện chất lượng agent không?**
A: Không — cần tín hiệu thất bại khách quan (tool báo lỗi, test case fail, evaluator độc lập) để self-reflection có căn cứ. Nếu không có tín hiệu rõ ràng, model tự đánh giá có thể sai (nghĩ đã đúng trong khi vẫn sai), khiến self-reflection vô nghĩa hoặc phản tác dụng.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Nhầm "agent" là 1 khái niệm chung, không phân biệt pattern.** Junior hay coi mọi agent framework (LangChain AgentExecutor...) là như nhau; middle phải chỉ ra được control-flow khác biệt cụ thể (biết trước số bước hay không, audit được trước khi chạy hay không).
- **Đánh giá thấp chi phí latency của ReAct** — mỗi Thought-Action là 1 lần gọi LLM riêng, task càng nhiều bước thì latency cộng dồn càng lớn, khác hẳn 1 lần gọi LLM đơn giản.
- **Coi Reflexion là "luôn tốt hơn"** — quên rằng nó tốn thêm nhiều lần gọi model (thử - fail - reflect - thử lại), chỉ đáng dùng khi task cho phép nhiều lần thử và có tín hiệu thất bại khách quan.
- **Không phân biệt được khi nào task đơn giản không cần pattern nào cả** — 1-2 bước rõ ràng, biết trước hoàn toàn, chỉ cần gọi function-calling trực tiếp, không cần ReAct/Plan-and-Execute.

## Bảng so sánh nhanh

| | ReAct | Plan-and-Execute | Reflexion |
|---|---|---|---|
| Số bước biết trước? | không | có (toàn bộ plan trước khi chạy) | tùy pattern nền (thường kết hợp ReAct/Plan) |
| Audit được trước khi hành động? | không | có | không trực tiếp — audit sau vòng thử |
| Chi phí/latency | cộng dồn theo số bước, khó đoán trước | có thể ước lượng trước (số bước cố định) | cao nhất — thêm hẳn vòng lặp thử lại |
| Hợp task nào | cần "khám phá", chưa biết trước cấu trúc | cấu trúc rõ, cần kiểm soát trước khi thực thi | cho phép thử nhiều lần, có tín hiệu thất bại rõ |
