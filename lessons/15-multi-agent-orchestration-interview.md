# Phỏng vấn — Multi-agent orchestration

Xem lesson chính: [15-multi-agent-orchestration.md](15-multi-agent-orchestration.md)

## Q&A

**Q: Multi-agent orchestration là gì, khác gì với 1 agent ReAct đơn có nhiều tool?**
A: Là tách bài toán thành nhiều agent chuyên biệt (mỗi agent 1 trách nhiệm/prompt/tool riêng), phối hợp qua 1 kiến trúc (routing, tranh luận, hoặc state chung) — khác với 1 agent đơn có nhiều tool: agent đơn vẫn dùng 1 system prompt/1 "bộ não" duy nhất quyết định mọi tool call.

**Q: Supervisor-worker khác gì code if/else routing tay thông thường?**
A: Về hình thức routing thì giống, nhưng supervisor-worker cho phép: (1) mỗi worker là đơn vị độc lập test/thay thế riêng được, (2) supervisor có thể gọi nhiều worker cùng lúc cho 1 câu hỏi phức hợp rồi tổng hợp — khó làm tự nhiên với if/else tuyến tính, (3) routing chính nó cũng là 1 lần gọi LLM (structured output) chứ không phải rule cứng, nên tổng quát hóa được với query mới không lường trước.

**Q: Debate giải quyết vấn đề gì mà 1 model đơn không giải quyết được?**
A: Giảm rủi ro hallucination/lỗi ngẫu nhiên của 1 model đơn — nhiều agent trả lời độc lập rồi phản biện nhau qua vài vòng, hội tụ về câu trả lời có cơ sở hơn. Đánh đổi: tốn nhiều lần gọi LLM hơn hẳn (cost + latency), chỉ đáng dùng khi accuracy quan trọng hơn tốc độ/chi phí rất nhiều (vd moderation, quyết định y tế/pháp lý).

**Q: Blackboard pattern là gì, rủi ro chính khi dùng là gì?**
A: Nhiều agent cùng đọc/ghi vào 1 state chung, không có supervisor cố định — agent nào thấy đóng góp được thì tự làm. Rủi ro: dễ vòng lặp vô hạn hoặc nhiều agent giẫm chân nhau nếu không có điều kiện dừng/khóa rõ ràng — khó kiểm soát thứ tự hơn supervisor-worker.

**Q: LangGraph là 1 pattern multi-agent hay là gì?**
A: Không phải pattern — là framework để hiện thực các pattern (supervisor-worker, debate, blackboard...) dưới dạng state machine/graph (node = bước hoặc agent, edge = điều kiện chuyển bước), thay thế cho code if/else lồng nhau khi logic điều khiển phức tạp.

**Q: Khi nào KHÔNG nên dùng multi-agent?**
A: Khi task chỉ cần 1-2 tool call, hoặc logic đã deterministic sẵn (vd hàm booking đã check điều kiện/slot có sẵn) — thêm orchestration multi-agent chỉ tăng cost/latency và độ phức tạp debug (lỗi có thể nằm ở tầng routing thay vì ở worker) mà không mang lại lợi ích tương xứng.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Bẫy chính (từ checkpoint thật):** khi hỏi "hậu quả của routing gọi thừa 1 worker không cần thiết", junior thường chỉ nghĩ tới UX (câu trả lời thừa/lệch trọng tâm) mà bỏ quên **cost + latency** — đây là hậu quả nghiêm trọng hơn trong production vì nó âm thầm nhân chi phí ở scale lớn, khó phát hiện bằng mắt (khác bug logic sai luôn lộ rõ). Câu trả lời đầy đủ phải nêu được cả 2 khía cạnh.
- Nhầm lẫn multi-agent với "nhiều tool trong 1 agent" — tool chỉ là hành động agent gọi, còn multi-agent là nhiều "bộ não" (nhiều lần gọi LLM với prompt/vai trò khác nhau) phối hợp.
- Nghĩ multi-agent luôn tốt hơn 1 agent đơn vì "chia nhỏ trách nhiệm nghe hợp lý" — quên mất chi phí thật (số lần gọi LLM tăng tuyến tính hoặc hơn theo số agent tham gia).
- Debate dễ bị hiểu nhầm là luôn cho kết quả tốt hơn — thực ra chỉ tốt hơn khi các agent có góc nhìn/thông tin khác biệt thật sự; nếu cùng 1 model, cùng 1 input, "debate" dễ chỉ là lặp lại thiên kiến giống nhau (không giải quyết được lỗi hệ thống, chỉ giảm lỗi ngẫu nhiên).
- Supervisor tin tưởng tuyệt đối vào output worker (như case Điều 20/36 không liên quan trong ví dụ) — nhiều người thiết kế supervisor-worker mà quên thêm bước kiểm tra chất lượng đầu ra worker trước khi tổng hợp.

## Bảng so sánh nhanh

| Pattern | Cơ chế | Ưu điểm | Nhược điểm | Dùng khi |
|---|---|---|---|---|
| Supervisor-worker | 1 agent routing, worker độc lập xử lý | Rõ trách nhiệm, dễ test/thay worker riêng | Lỗi có thể ở tầng routing | Task có nhiều loại yêu cầu khác nhau, cần rõ ràng ai làm gì |
| Debate | Nhiều agent trả lời độc lập rồi phản biện | Giảm hallucination/lỗi ngẫu nhiên | Tốn nhiều lần gọi LLM nhất | Accuracy quan trọng hơn cost/latency nhiều lần (moderation, y tế, pháp lý) |
| Blackboard | State chung, agent tự nhận việc | Linh hoạt, không cần thứ tự cố định | Khó kiểm soát, dễ vòng lặp/giẫm chân | Nhiều "chuyên gia" cần đóng góp không theo thứ tự cố định |
| LangGraph | Framework hiện thực state machine | Quản lý được logic điều khiển phức tạp một cách tường minh | Overhead học/setup nếu logic đơn giản | Bất kỳ pattern nào ở trên khi logic điều khiển đủ phức tạp để if/else khó quản lý |
