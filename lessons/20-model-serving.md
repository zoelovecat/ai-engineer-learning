# 20. Model serving (vLLM/TGI, batching)

**Ngày học:** 2026-09-10
**Trạng thái:** Đã học

Xem thêm: [Phỏng vấn](20-model-serving-interview.md)

## 1. Lý thuyết

Model serving là lớp hạ tầng chuyên serve LLM ở production — khác hẳn tự viết code gọi `model.generate()` trực tiếp trong 1 API endpoint (chỉ ổn 1 user, sụp throughput khi có concurrent request thật).

**Continuous batching (in-flight batching):** batching kiểu cũ (static) gom N request thành 1 batch cố định, đợi CẢ batch xong mới trả kết quả — request ngắn phải chờ request dài trong cùng batch. Continuous batching: ở mỗi bước decode, scheduler loại request đã xong khỏi batch ngay, chèn request mới từ hàng đợi vào slot vừa trống — GPU luôn được lấp đầy, không có khoảng trống chờ request chậm nhất.

**PagedAttention (đóng góp chính của vLLM):** KV cache (bài 16) thường cấp phát liên tục và phải dự trù trước độ dài tối đa → lãng phí lớn (fragmentation). PagedAttention áp dụng ý tưởng virtual memory paging của OS: chia KV cache thành block cố định kích thước nhỏ, ánh xạ logical block → physical block qua page table — không cần liên tục, không cần dự trù trước. Cho phép nhồi nhiều sequence hơn trong cùng VRAM, và **share block** giữa các sequence có chung prefix (system prompt chung, beam search) — không lưu trùng.

**Vì sao cần hiểu sâu:** tutorial cơ bản dừng ở "load model, gọi `.generate()` trong route" — đúng chức năng nhưng throughput sụp khi có concurrent request thật (mỗi request 1 forward pass riêng, hoặc batch tĩnh lãng phí). vLLM/TGI giải quyết đúng câu hỏi "phục vụ nhiều user cùng lúc trên số GPU cố định, tối đa hoá throughput" — khác hẳn khi gọi managed API (họ đã lo phần này).

**Trade-off:**
- Thêm độ phức tạp vận hành (service riêng, quản lý version, thêm network hop, overhead khởi động).
- Tối ưu **throughput** tổng thể, không nhất thiết tối ưu **latency** của 1 request đơn lẻ — batch đông thì request mới có thể chờ lâu hơn chạy riêng lẻ. Đánh đổi throughput vs latency-per-request theo SLA thật.
- Không đáng dùng nếu traffic rất thấp (1-2 user) hoặc đang dùng managed API (OpenAI/Anthropic) — họ đã tự vận hành lớp này.
- Quantization (bài 19) và batching cạnh tranh cùng nguồn VRAM (model nhẹ hơn nhưng batching nhiều request vẫn cần VRAM cho KV cache từng request) — phải cân đối.

## 2. Ví dụ áp dụng

Agent HR (bài 15), production, ~50 nhân viên hỏi cùng giờ cao điểm, mỗi câu cần model 7B (INT8, bài 19) sinh ~150 token, tự host trên 1 GPU 24GB.

- Serve tuần tự (tự viết FastAPI gọi `.generate()` trực tiếp): GPU chạy ở chế độ memory-bandwidth-bound khi decode 1 sequence (không tận dụng hết compute song song), xử lý tuần tự nên độ trễ tăng tuyến tính theo số người xếp hàng — vừa lãng phí compute vừa tệ trải nghiệm.
- Chuyển sang vLLM (continuous batching): GPU lấp đầy liên tục, request mới chèn ngay khi có slot trống thay vì chờ cả batch/lượt trước xong.
- Nhiều nhân viên dùng chung 1 đoạn system prompt dài (chính sách công ty): PagedAttention share block KV cache của phần prompt chung, tránh lưu trùng và tính lại cho mỗi request có cùng prefix.

## 3. Bài thực hành

Thiết kế tình huống (không code): so sánh trải nghiệm/throughput giữa serve tuần tự vs vLLM continuous batching cho 50 request đồng thời, và giải thích lợi ích PagedAttention khi nhiều request chia sẻ system prompt chung.

## 4. Checkpoint

**Câu 1:** Điều gì xảy ra nếu giữ serve tuần tự (không dùng vLLM/TGI) với 50 request đồng thời?
- Trả lời: phải đợi người trước xong mới tới lượt, nghẽn, GPU không dùng hết công suất mỗi lần gen, phí tài nguyên, giảm trải nghiệm — đúng, nắm được cả khía cạnh compute lẫn latency.

**Câu 2:** Chuyển sang vLLM continuous batching thay đổi gì?
- Trả lời: tài nguyên luôn có việc để làm, người dùng không cần đợi hết các lượt trước mà được ưu tiên khi tài nguyên trống — đúng.

**Câu 3:** PagedAttention giúp ích gì khi nhiều nhân viên dùng chung system prompt?
- Trả lời: các block có common prompt được dùng lại, tránh tính toán lại không cần thiết — đúng (liên hệ đúng khái niệm "share block").

**Độ tin cậy:** cao — cả 3 câu tự trả lời đúng ngay, không cần bổ sung.
