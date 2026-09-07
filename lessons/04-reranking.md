# Concept #4: Reranking (Cohere Rerank, cross-encoder) (Giai đoạn 2 - RAG)

Ngày tạo: 2026-09-03

Trạng thái: Cần ôn lại (user báo còn mơ hồ sau checkpoint — 2026-09-04)

🎯 Điểm hay bị hỏi khi phỏng vấn: [04-reranking-interview.md](04-reranking-interview.md)

## 1. Nó là gì

Phân biệt 2 kiến trúc:

- **Bi-encoder** (embedding model, concept #1): encode query và document **riêng biệt, độc lập** thành 2 vector cố định, so sánh bằng cosine sau đó. Model không bao giờ "thấy" query và document cùng lúc — phải nén nghĩa document vào 1 vector *trước khi* biết câu hỏi là gì.
- **Cross-encoder** (dùng để rerank): nhét cả query và document vào **cùng một lần forward pass** — `[CLS] query [SEP] document [SEP]` — qua transformer. Self-attention cho phép từng token của query attend trực tiếp vào từng token của document ngay lúc encode. Output là 1 relevance score duy nhất (qua classification head + sigmoid), không phải 1 vector.

Vì cross-encoder "đọc cùng lúc" nên nó bắt được tương tác token-level (ví dụ: ai là chủ thể hành động trong câu) mà BM25 (đếm từ, không hiểu quan hệ) và bi-encoder (đã nén nghĩa rồi mới so sánh) đều bỏ lỡ.

Quy trình production chuẩn (kiến trúc 2 tầng):

```
retrieve thô (BM25 + vector, top 50-100, ưu tiên RECALL — rẻ, scale tốt)
        ↓
cross-encoder rerank (chấm lại từng cặp query-doc, ưu tiên PRECISION — đắt, chỉ chạy trên tập nhỏ)
        ↓
top 3-10 đưa vào context LLM
```

Công cụ thật: **Cohere Rerank** (API managed) hoặc cross-encoder mã nguồn mở qua `sentence-transformers.CrossEncoder` (ví dụ `BAAI/bge-reranker-base` — đa ngôn ngữ, dùng được tiếng Việt).

## 2. Vì sao cần hiểu sâu (chỗ tutorial hay bỏ qua)

Retrieval thô phải tối ưu tốc độ ở quy mô toàn corpus → chấp nhận representation nén sẵn, thô. Rerank chỉ chạy trên tập nhỏ đã lọc nên "afford" được tính toán đắt hơn (cross-attention full, không parallelize/precompute được như so sánh vector) mà vẫn đủ nhanh. Tutorial cơ bản gần như luôn dừng ở "vector top-k → đưa thẳng LLM", bỏ qua bước rerank vì cần thêm 1 model/API call — nhưng production thật gần như luôn có bước này.

## 3. Trade-off / khi nào KHÔNG dùng

- **Chi phí & latency**: mỗi candidate trong top-k phải chạy riêng 1 forward pass qua cross-encoder (không parallelize/cache được như bi-encoder) → rerank 50 candidate tốn nhiều hơn hẳn 1 lần so sánh vector.
- **Không sửa được recall thấp**: rerank chỉ sắp xếp lại trong tập đã retrieve — nếu retrieve thô ban đầu không hề chứa đúng document, rerank vô dụng. Phải đo recall@k (concept #5) trước khi quyết định đầu tư vào rerank.
- **Không cần nếu** corpus nhỏ, retrieval thô đã đủ chính xác, hoặc latency là ưu tiên số 1.
- **Không nên rerank toàn bộ corpus** (bỏ tầng retrieve thô) — cross-encoder không scale được vì phải chạy 1 forward pass cho mỗi cặp (query, document) tại thời điểm query, không index/precompute trước được như vector search.

## Ví dụ áp dụng project

Dùng lại đúng case thật đã phát hiện ở bài 3 (hybrid search): query `"công ty tự ý cho tôi nghỉ việc thì sao"` trên `sample-luat-lao-dong.txt` bị cả BM25, vector, và cả RRF fusion cùng xếp nhầm Điều 35 (NLĐ tự nghỉ) lên trên Điều 36 (NSDLĐ cho nghỉ) — shared blind spot. Cross-encoder rerank là kỹ thuật được kỳ vọng sửa đúng lỗi này vì nó đọc quan hệ chủ thể hành động mà BM25/vector không capture được.

## Bài thực hành

File: [practice/04-reranking.py](../practice/04-reranking.py)

1. Cài `sentence-transformers`, load `CrossEncoder("BAAI/bge-reranker-base")`.
2. Lấy lại top-10 candidate từ hybrid RRF (bài 3) cho query "công ty tự ý cho tôi nghỉ việc thì sao".
3. Chấm lại từng cặp (query, candidate) bằng cross-encoder, sắp xếp lại theo score.
4. So sánh top-1 trước/sau rerank, và chênh lệch score cụ thể giữa chunk Điều 35 vs Điều 36.

Trạng thái thực hành: đã viết xong code, **chưa chạy thực tế** (môi trường agent không có Python cài sẵn) — cần user tự chạy trên máy và báo lại kết quả khi ôn lại.

## Checkpoint (chưa đạt — còn mơ hồ, 2026-09-04)

3 câu hỏi đã hỏi (xem đầy đủ Q&A trong [04-reranking-interview.md](04-reranking-interview.md)):
1. Vì sao cross-encoder sửa được shared blind spot mà RRF không?
2. Recall@10 thấp (~40%) thì có nên ưu tiên đầu tư rerank không?
3. Vấn đề của việc rerank toàn bộ corpus thay vì chỉ top-k đã retrieve thô?

User không tự trả lời, yêu cầu giải thích, và sau khi nghe giải thích lại vẫn báo **"mơ hồ"** chung (không chỉ rõ điểm cụ thể) — cần quay lại ôn kỹ hơn, có thể ưu tiên chạy thử code thật (practice/04-reranking.py) để thấy kết quả cụ thể trước khi ôn lý thuyết lại, vì 2 bài trước (chunking, hybrid search) đều chỉ thực sự "thấm" sau khi chạy thực hành thật và thấy lỗi cụ thể.
