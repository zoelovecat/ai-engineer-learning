# 16. Transformer khái niệm (attention, context window, lost-in-the-middle)

**Ngày học:** 2026-09-09
**Trạng thái:** Đã học

Xem thêm: [Toán](16-transformer-concepts-math.md) · [Phỏng vấn](16-transformer-concepts-interview.md)

## 1. Lý thuyết

**Attention**: cơ chế cho phép model, khi xử lý 1 token, "nhìn" vào tất cả token khác trong chuỗi để quyết định token nào liên quan nhất — thay vì xử lý tuần tự như RNN cũ.

Cơ chế: mỗi token có 3 vector — Query (Q), Key (K), Value (V). Với mỗi token, tính dot product giữa Query của nó với Key của mọi token khác → điểm khớp → qua softmax thành trọng số (tổng = 1) → dùng trọng số đó lấy trung bình có trọng số của các Value → vector đại diện đã "hoà trộn" thông tin từ token liên quan nhất.

Việc này làm đồng thời cho **mọi cặp token** (self-attention) → độ phức tạp **O(n²)** theo độ dài chuỗi n, vì mỗi trong n token đều phải so với n token khác (n × n phép so sánh) — đây là gốc rễ giới hạn context window.

**Context window**: số token tối đa xử lý được trong 1 lần gọi. Giới hạn vì: (1) chi phí attention tăng bình phương theo độ dài, (2) model train với độ dài cố định, ngoài phạm vi đó vị trí token "lạ" với model.

**Lost-in-the-middle**: model tận dụng thông tin ở đầu/cuối context tốt hơn hẳn thông tin ở giữa — do phân bổ trọng số attention không đều, thiên vị 2 đầu. Không phải "quên" theo nghĩa kỹ thuật (dữ liệu vẫn nằm trong context), mà là model ít chú ý tới nó khi tổng hợp câu trả lời.

**Vì sao cần hiểu sâu**: liên kết trực tiếp tới reranking (bài 4) — 1 lý do thật cần rerank không chỉ lọc chunk không liên quan mà còn sắp xếp lại vị trí để chunk quan trọng nằm ở đầu/cuối prompt. Cũng giải thích vì sao agent nhiều bước (bài 7, bài 14) cần chiến lược tóm tắt/nén lịch sử.

**Trade-off / lưu ý**: context window lớn hơn KHÔNG giải quyết lost-in-the-middle (bẫy phổ biến: nghĩ context dài hơn thì nhét bao nhiêu cũng được). Chi phí tính toán tăng theo cấp số nhân, không tuyến tính. Junior thấy RAG sai thì tăng top_k; middle hỏi trước "chunk đúng có bị chôn giữa context không" và ưu tiên rerank/sắp xếp lại thay vì nhồi thêm.

## 2. Ví dụ áp dụng

Dùng lại use case HR (bài 15): nếu `PolicyWorker` tăng `top_k` từ 2 lên 15 "cho chắc", và câu trả lời đúng nằm ở đoạn thứ 8/15 (giữa) — dù retrieval đúng (chunk có mặt trong context), LLM vẫn có xác suất cao bỏ qua nó khi tổng hợp câu trả lời. Dễ nhầm là bug ở embedding/hybrid search (bài 1/3), nhưng bug thực chất nằm ở cách sắp xếp/số lượng chunk đưa vào prompt.

Không viết code thực hành riêng cho bài này (đi thẳng checkpoint theo yêu cầu).

## 3. Checkpoint

**Câu 1:** Đồng nghiệp nói "context 1 triệu token rồi, nhét hết tài liệu vào luôn khỏi cần retrieval/rerank". Đồng ý không?
- Trả lời: Không, vì lost-in-the-middle — context dài không đảm bảo model chú ý đều; rerank giúp đẩy context quan trọng lên đầu để attention chú ý hơn. Đúng.

**Câu 2:** Vì sao attention là O(n²)?
- Trả lời ban đầu: "1 token tự tính trọng số với các token còn lại" — đúng 1 phần, thiếu ý mấu chốt.
- Bổ sung: điều này lặp lại cho TẤT CẢ n token (không chỉ 1 token) → n × n = n² phép tính. Thiếu ý "lặp cho mọi token" thì dễ nhầm sang O(n).

**Câu 3:** Tình huống lost-in-the-middle gây trả lời sai dù retrieval đúng, và 1 cách khắc phục không phải "giảm top_k".
- Trả lời: hội thoại quá dài khiến agent quên thông tin quan trọng rút ra ở giữa. Cách khắc phục: **đưa các phần quan trọng đã rút ra vào episodic memory** (liên hệ bài 14) thay vì để nguyên trong short-term context thô — né lost-in-the-middle bằng cách chủ động trích xuất/lưu có cấu trúc thay vì cậy vào attention tự tìm.

Checkpoint đạt (câu 1 đúng ngay, câu 2 bổ sung ý n×n, câu 3 hoàn thiện sau gợi ý liên hệ bài 14). User xác nhận đánh dấu Đã học.
