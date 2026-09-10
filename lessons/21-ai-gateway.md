# 21. AI Gateway (LiteLLM: routing, cost tracking, fallback)

**Ngày học:** 2026-09-10
**Trạng thái:** Đã học

Xem thêm: [Phỏng vấn](21-ai-gateway-interview.md)

## 1. Lý thuyết

AI Gateway là 1 lớp proxy đứng giữa ứng dụng và nhiều LLM provider (OpenAI, Anthropic, Azure, model tự host qua vLLM — bài 20), expose ra 1 API thống nhất (thường OpenAI-compatible) — code gọi model nào cũng qua cùng interface, không cần biết SDK riêng từng provider.

3 chức năng cốt lõi:
- **Routing**: chuyển request tới provider/model theo rule — theo task (model mạnh cho reasoning, model rẻ cho task đơn giản), load balancing giữa nhiều API key/provider cùng model (tránh dính rate limit 1 key), hoặc theo chi phí/latency ưu tiên.
- **Cost tracking**: đếm token input/output thực tế mỗi request, map sang đơn giá theo provider/model, cộng dồn theo user/team/project — cần request được gắn metadata (agent_id/user/project) để group được theo đúng chiều muốn xem, không chỉ đếm token thô.
- **Fallback**: provider chính lỗi (rate limit, timeout, 5xx) → tự động retry sang provider/model dự phòng tương đương, app không cần biết — giữ uptime, không phải code try/catch thủ công khắp nơi.

**Vì sao cần hiểu sâu:** tutorial cơ bản hardcode thẳng SDK provider (OpenAI/Anthropic) rải khắp code — đổi provider phải sửa từng chỗ. Hệ multi-agent (bài 15) mỗi agent cần model khác nhau — quản lý qua nhiều SDK riêng lẻ rất rối, khó thấy tổng chi phí. Điểm hay bị bỏ qua: cost tracking cần TÁCH THEO NHÃN (agent/user/project), không chỉ đếm token; và fallback phải tự động, không lộ ra ngoài cho người dùng cuối.

**Trade-off:**
- Thêm 1 network hop/điểm lỗi tiềm năng — gateway sập (nếu tự host không HA) thì mọi thứ phía sau cũng sập dù provider gốc vẫn ổn.
- Cấu hình routing/fallback sai có thể ÂM THẦM đổi sang model chất lượng thấp hơn mà không ai nhận ra — cần eval/golden set (bài 11-12) để phát hiện regression do gateway gây ra.
- Không đáng dùng khi chỉ 1 provider, quy mô nhỏ — tự dựng gateway lúc đó là over-engineering.
- Khác **model serving** (bài 20): serving chạy chính model (batching, KV cache), gateway là lớp routing/quản lý phía trên nhiều backend — bổ sung nhau, không thay thế.

## 2. Ví dụ áp dụng

Hệ multi-agent HR (bài 15): Supervisor (routing đơn giản) + PolicyWorker (đọc hiểu chính sách, cần model mạnh) + LeaveWorker (tra DB, logic đơn giản). Tình huống: API key OpenAI chính bị rate limit giờ cao điểm, lãnh đạo muốn biết agent nào tốn tiền nhất mỗi tháng.

- Routing: PolicyWorker → model mạnh (cần suy luận chính xác); LeaveWorker và Supervisor → model rẻ/nhẹ (task đơn giản, chỉ routing/tra DB).
- Fallback: rate limit giờ cao điểm → tự động chuyển sang model/provider cùng tier (độ thông minh tương đương) theo thứ tự ưu tiên đã cấu hình sẵn, không hỏi giữa chừng (khác với hệ có người dùng trực tiếp chờ chọn). Rủi ro: model fallback không theo kịp task cũ — cần theo dõi bằng golden set (bài 11).
- Cost tracking: gắn `agent_id` (PolicyWorker/LeaveWorker/Supervisor) vào mỗi request khi đi qua gateway, group by nhãn đó khi tổng hợp báo cáo tháng — đếm token chỉ là bước tính ra số tiền, tách theo agent mới trả lời được "ai tốn tiền nhất".

## 3. Bài thực hành

Thiết kế (không code): rule routing cho 3 agent, chiến lược fallback khi rate limit giờ cao điểm, và cách tách cost tracking theo agent.

## 4. Checkpoint

**Câu 1:** Rule routing cho 3 agent?
- Trả lời: task cần độ chính xác cao dùng model xịn/đắt, task đơn giản dùng model rẻ — đúng nguyên tắc, đã áp cụ thể: PolicyWorker → model mạnh, LeaveWorker/Supervisor → model rẻ.

**Câu 2:** Chiến lược fallback khi rate limit + rủi ro cần theo dõi?
- Trả lời: fallback sang model độ thông minh tương đương, rủi ro model mới không theo kịp task cũ, cần eval golden set — đúng phần cốt lõi. Ý "để người dùng tự chọn" chỉ hợp với hệ có người dùng trực tiếp; với hệ agent tự động, gateway tự fallback theo thứ tự ưu tiên cấu hình sẵn, không hỏi giữa chừng — đã bổ sung.

**Câu 3:** Cost tracking cần tách theo chiều nào để biết agent nào tốn tiền nhất?
- Trả lời ban đầu: "tracking token" — chưa đủ, chỉ là bước TÍNH ra số tiền.
- Đáp án đúng (assistant trả lời hộ): cần gắn metadata (`agent_id`/user/project) vào mỗi request, group by nhãn đó khi tổng hợp — đếm token không tự tách được theo agent nếu không gắn nhãn.

**Độ tin cậy:** trung bình — câu 1-2 tự trả lời đúng (câu 2 cần bổ sung nhỏ), câu 3 assistant trả lời hộ hoàn toàn.
