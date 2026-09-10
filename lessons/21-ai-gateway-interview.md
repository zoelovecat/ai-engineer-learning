# Phỏng vấn — AI Gateway (LiteLLM: routing, cost tracking, fallback)

Lesson chính: [21-ai-gateway.md](21-ai-gateway.md)

## Q&A

**Q: AI Gateway là gì, giải quyết vấn đề gì?**
A: Lớp proxy đứng giữa app và nhiều LLM provider, expose 1 API thống nhất (thường OpenAI-compatible). Giải quyết việc phải hardcode SDK riêng từng provider rải khắp code — đổi provider/model chỉ cần đổi config, không sửa code ở mọi nơi gọi.

**Q: 3 chức năng cốt lõi của gateway là gì?**
A: Routing (chuyển request theo rule: task, cost, load balancing giữa nhiều key/provider), cost tracking (đếm token + gắn metadata để group theo user/agent/project), fallback (tự động chuyển sang provider dự phòng khi lỗi, không lộ ra ngoài).

**Q: Cost tracking cần thêm gì ngoài đếm token để trả lời "ai/phần nào tốn tiền nhất"?**
A: Cần gắn metadata (agent_id/user/project) vào mỗi request khi đi qua gateway, rồi group by nhãn đó khi tổng hợp — đếm token chỉ là bước tính ra số tiền, không tự tách được theo chiều muốn xem nếu thiếu nhãn.

**Q: Fallback tiềm ẩn rủi ro gì, làm sao phát hiện?**
A: Có thể âm thầm đổi sang model chất lượng thấp hơn mà không ai nhận ra ngay (khi provider chính lỗi, fallback về model yếu hơn). Cần theo dõi bằng golden set/eval (bài 11-12) để phát hiện regression do gateway gây ra, không chỉ tin "vẫn trả lời được là ổn".

**Q: AI Gateway khác Model serving (vLLM/TGI, bài 20) ở điểm nào?**
A: Serving là lớp chạy CHÍNH model (batching, KV cache — bên trong 1 backend). Gateway là lớp ROUTING/quản lý phía TRÊN nhiều backend khác nhau (có thể gồm cả model tự host qua vLLM lẫn managed API như OpenAI/Anthropic) — 2 khái niệm bổ sung nhau, không thay thế.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Bẫy chính (từ checkpoint thật):** nghĩ "cost tracking" = "đếm token" là đủ để biết agent/user nào tốn tiền nhất — SAI, đếm token chỉ ra tổng chi phí, cần thêm bước gắn NHÃN (agent_id/user/project) vào từng request và group by nhãn đó mới tách được theo chiều cần xem.
- Nhầm fallback tự động = hỏi người dùng chọn model thay thế — với hệ agent tự động (không người dùng ngồi chờ), fallback phải chạy im lặng theo thứ tự ưu tiên đã cấu hình sẵn, không dừng lại hỏi giữa chừng.
- Nhầm gateway và model serving là 1 khái niệm hoặc thay thế nhau — gateway routing đa provider, serving là engine chạy model bên trong 1 backend cụ thể.
- Quên rủi ro fallback âm thầm hạ chất lượng — cần gắn liền với eval/golden set để giám sát, không phải "cấu hình 1 lần là xong".

## Bảng so sánh nhanh

| | Gọi thẳng SDK từng provider | Tự dựng gateway (LiteLLM proxy) | Managed gateway (Portkey, Cloudflare AI Gateway...) |
|---|---|---|---|
| Độ phức tạp code | Thấp ban đầu, tăng dần khi nhiều provider | Cần vận hành thêm 1 service | Không cần tự vận hành |
| Đổi provider | Sửa code ở mọi nơi gọi | Chỉ đổi config routing | Chỉ đổi config trên dashboard |
| Cost tracking | Tự viết logic riêng | Có sẵn, theo user/project | Có sẵn, thường có dashboard đẹp hơn |
| Fallback | Tự code try/catch thủ công | Cấu hình khai báo | Cấu hình khai báo |
| Phù hợp khi | 1 provider, quy mô nhỏ | Cần tự chủ hạ tầng, nhiều provider/model tự host | Không muốn tự vận hành, chấp nhận phụ thuộc bên thứ 3 |
