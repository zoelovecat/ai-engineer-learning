# Interview notes: Reranking (Cohere Rerank, cross-encoder)

Lesson chính: [04-reranking.md](04-reranking.md)

## Q&A có thể gặp

**Q: Bi-encoder và cross-encoder khác nhau ở đâu?**
A: Bi-encoder encode query và document riêng biệt thành vector rồi so cosine — nhanh, precompute/index được (dùng cho retrieval quy mô lớn). Cross-encoder đưa cả 2 vào cùng 1 forward pass, cho attention xuyên suốt giữa chúng, ra 1 score liên quan trực tiếp — chính xác hơn nhưng không precompute được, chỉ dùng cho rerank tập nhỏ.

**Q: Vì sao không dùng cross-encoder làm retrieval chính luôn, bỏ bi-encoder đi?**
A: Vì cross-encoder phải chạy 1 forward pass cho mỗi cặp (query, document) tại thời điểm query — không index/precompute trước được. Với corpus lớn (hàng triệu document) sẽ quá chậm để dùng trực tiếp. Đó là lý do có kiến trúc 2 tầng: bi-encoder/BM25 thu hẹp về top-k rẻ, cross-encoder rerank tập nhỏ đó.

**Q: RRF (Reciprocal Rank Fusion) có sửa được lỗi khi cả BM25 và vector cùng xếp sai không?**
A: Không. RRF chỉ gộp thứ hạng có sẵn từ các hệ thống, không tự đánh giá lại nội dung. Nó cứu được khi các kênh bất đồng ý kiến (bù trừ lẫn nhau), nhưng khi tất cả kênh cùng sai giống nhau (shared blind spot), RRF chỉ cộng dồn phiếu bầu sai đó.

**Q: Rerank có luôn cải thiện chất lượng RAG không?**
A: Không — rerank chỉ sắp xếp lại trong tập đã retrieve. Nếu recall@k của bước retrieve thô thấp (document đúng còn không nằm trong candidate ban đầu), rerank không giúp được gì. Phải đo recall@k trước khi đầu tư vào rerank.

**Q: Khi nào KHÔNG nên dùng rerank?**
A: Corpus nhỏ/retrieval thô đã đủ chính xác, latency là ưu tiên hàng đầu, hoặc recall@k của retrieval thô còn thấp (nên sửa retrieval trước).

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Nhầm rerank = retrieval tốt hơn nói chung.** Rerank không tìm thêm tài liệu — nó chỉ sắp xếp lại candidate đã có. Nếu top-k ban đầu (trước rerank) sai/thiếu, rerank vô dụng. Đây là bẫy phổ biến: junior nghĩ "cứ thêm rerank là chất lượng tăng" mà không kiểm tra recall trước.
- **Nhầm cross-encoder có thể thay hoàn toàn bi-encoder vì "chính xác hơn".** Đúng là chính xác hơn nhưng không scale — không index/cache trước được vì cần cả query lẫn document cùng lúc mới tính được score. Đây là câu hỏi phỏng vấn kinh điển về kiến trúc 2 tầng retrieval.
- **Case thực tế đã gặp (ghi lại vì đáng nhớ):** shared blind spot giữa BM25 và vector (cả 2 cùng xếp nhầm Điều 35 lên trên Điều 36 cho câu hỏi liên quan tới ai là chủ thể chấm dứt hợp đồng) — RRF không sửa được vì RRF không có cơ chế "đọc lại nội dung", chỉ cross-encoder mới có khả năng phân biệt sắc thái chủ thể hành động này nhờ đọc query+document cùng lúc.
- **Ghi chú tự đánh giá (2026-09-04):** sau khi giải thích lại 3 câu checkpoint, user báo còn "mơ hồ" chung, chưa xác định rõ điểm cụ thể sai ở đâu — có thể là dấu hiệu cần thấy kết quả thực hành thật (chạy `practice/04-reranking.py`) trước khi khái niệm "thấm", giống pattern đã xảy ra ở bài chunking và hybrid search trước đó. Khi ôn lại, ưu tiên hỏi lại xem đã chạy code thật chưa trước khi giảng lại lý thuyết.

## Bảng so sánh nhanh

| | BM25 | Bi-encoder (vector) | Cross-encoder (rerank) |
|---|---|---|---|
| Encode query+doc | riêng biệt (không encode, đếm từ) | riêng biệt | cùng lúc (1 forward pass) |
| Bắt được tương tác token-level | không | không | có |
| Scale cho toàn corpus | có (inverted index) | có (ANN index) | không (phải chạy per-pair) |
| Dùng ở tầng nào | retrieve thô | retrieve thô | rerank tập nhỏ đã retrieve |
| Sửa được shared blind spot (2 kênh cùng sai)? | — | — | có khả năng (đọc lại quan hệ ngữ nghĩa) |
