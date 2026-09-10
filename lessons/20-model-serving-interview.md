# Phỏng vấn — Model serving (vLLM/TGI, batching)

Lesson chính: [20-model-serving.md](20-model-serving.md)

## Q&A

**Q: Vì sao không thể chỉ gọi `model.generate()` trực tiếp trong 1 API route cho production?**
A: Hoạt động đúng chức năng với 1 user, nhưng throughput sụp khi có concurrent request thật — mỗi request 1 forward pass riêng lẻ (hoặc static batching lãng phí), GPU không được chia sẻ hiệu quả giữa nhiều request.

**Q: Continuous batching là gì, khác static batching thế nào?**
A: Static batching gom N request cố định, đợi CẢ batch xong mới trả — request ngắn bị "kẹt" chờ request dài. Continuous batching: ở mỗi bước decode, loại request đã xong khỏi batch ngay, chèn request mới từ hàng đợi vào slot trống — GPU luôn bận, không có khoảng trống chờ.

**Q: PagedAttention là gì, giải quyết vấn đề gì?**
A: Áp dụng ý tưởng virtual memory paging của OS cho KV cache: chia thành block cố định nhỏ, ánh xạ logical→physical qua page table, không cần cấp phát liên tục hay dự trù trước độ dài tối đa → giảm fragmentation, nhồi được nhiều sequence hơn trong cùng VRAM, và cho phép share block giữa sequence có chung prefix.

**Q: vLLM/TGI tối ưu throughput hay latency?**
A: Chủ yếu tối ưu throughput tổng thể (tổng token/giây phục vụ toàn hệ thống). Không nhất thiết tối ưu latency của 1 request đơn lẻ — nếu batch đông, request mới có thể chờ lâu hơn so với chạy một mình. Đây là đánh đổi cần cân nhắc theo SLA.

**Q: Khi nào KHÔNG cần vLLM/TGI?**
A: Traffic rất thấp (1-2 user), hoặc đang dùng managed API (OpenAI/Anthropic/Claude API) — họ đã tự vận hành lớp serving tối ưu này, tự dựng lại tốn công không cần thiết.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- Nhầm continuous batching chỉ là "tăng batch size" — thực ra điểm khác biệt là tính **động** (chèn/loại request giữa chừng ở mỗi step), không phải kích thước batch cố định lớn hơn.
- Nhầm PagedAttention chỉ là "kỹ thuật nén bộ nhớ" giống quantization (bài 19) — đây là 2 kỹ thuật khác nhau và **cạnh tranh cùng nguồn VRAM**: quantization giảm size model, PagedAttention tối ưu cách cấp phát KV cache. Dùng cả 2 cùng lúc vẫn phải cân đối tổng VRAM.
- Bỏ qua đánh đổi throughput vs latency — nghĩ vLLM luôn "nhanh hơn" mọi mặt; thực ra dưới tải cao, latency per-request có thể tăng dù throughput tổng thể tăng.
- Nhầm "share block" của PagedAttention tự động xảy ra cho MỌI request giống nhau về nội dung — thực ra cần cùng prefix token-for-token (và cơ chế prefix caching liên quan) mới share được, không phải cứ "tương tự" là share.

## Bảng so sánh nhanh

| | vLLM | TGI (Text Generation Inference) |
|---|---|---|
| Điểm mạnh nổi bật | PagedAttention (KV cache hiệu quả nhất hiện nay) | Tích hợp sẵn nhiều kỹ thuật quantization, ổn định trong hệ sinh thái Hugging Face |
| Batching | Continuous batching | Continuous batching |
| API | OpenAI-compatible endpoint sẵn có | REST API riêng + OpenAI-compatible |
| Phù hợp khi | Cần throughput cao nhất, tự host model lớn | Đã dùng nhiều trong hệ sinh thái HF, cần quantization đi kèm dễ dàng |
