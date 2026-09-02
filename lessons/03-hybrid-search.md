# Concept #3: Hybrid search (vector + BM25) (Giai đoạn 2 - RAG)

Ngày tạo: 2026-09-02

Trạng thái: Đã học (2026-09-02)

📐 Phần toán (BM25 + RRF — tính tay từng bước): [03-hybrid-search-math.md](03-hybrid-search-math.md)
🎯 Điểm hay bị hỏi khi phỏng vấn: [03-hybrid-search-interview.md](03-hybrid-search-interview.md)

## 1. Nó là gì

Hybrid search = chạy song song 2 kiểu retrieval trên cùng câu hỏi rồi gộp kết quả:

- **Vector search (dense/semantic)**: encode câu hỏi + chunk thành vector (concept #1), tính cosine similarity, lấy top-k gần nhất. Hiểu nghĩa, không hiểu chuỗi ký tự chính xác.
- **BM25 (sparse/lexical)**: chấm điểm dựa trên inverted index, không có "nghĩa", chỉ đếm từ khớp:

```
BM25(D,Q) = Σ IDF(qi) × f(qi,D)·(k1+1) / [f(qi,D) + k1·(1 - b + b·|D|/avgdl)]
```

- `f(qi,D)`: số lần từ qi xuất hiện trong document D.
- `IDF(qi)`: từ càng hiếm trong toàn corpus càng weight cao.
- `|D|/avgdl`: phạt document quá dài so với độ dài trung bình.
- `k1` (≈1.2–2), `b` (≈0.75): hằng số tune được.

- **Fusion**: 2 hệ thống ra 2 danh sách rank với score không cùng thang đo (cosine 0–1, BM25 0→∞ tùy corpus) → không cộng thẳng được. Kỹ thuật chuẩn production: **Reciprocal Rank Fusion (RRF)**:

```
score_RRF(d) = Σ over mỗi hệ thống r: 1 / (k + rank_r(d))     (k thường = 60)
```

RRF bỏ qua giá trị score thô, chỉ dùng thứ hạng — document đứng top ở cả 2 kênh được cộng dồn điểm cao nhất. Đây là cách Elasticsearch, Qdrant, Weaviate làm hybrid search mặc định.

## 2. Vì sao cần hiểu sâu (chỗ tutorial hay bỏ qua)

Nối với anisotropy đã học ở bài 1: embedding model nén nghĩa vào không gian vector chung, nên token hiếm/out-of-distribution (mã số điều luật, tên riêng, SKU, số điện thoại) bị nén gần nhau mất phân biệt — cosine similarity giữa "Điều 36" và "Điều 38" có thể gần y hệt "Điều 36" và "Điều 90", vì model không train để phân biệt các con số này về ngữ nghĩa.

BM25 giải quyết đúng lỗ hổng đó: khớp chính xác chuỗi ký tự bất kể model có hiểu ngữ nghĩa hay không. Query thực tế luôn là hỗn hợp — vừa cần semantic vừa cần exact match — nên production RAG gần như luôn hybrid, còn tutorial cơ bản chỉ demo vector thuần vì dễ code.

## 3. Trade-off / khi nào KHÔNG dùng

- Chi phí kỹ thuật kép: maintain 2 index, 2 query song song, thêm bước fusion → tăng latency và độ phức tạp hạ tầng.
- Corpus nhỏ, query luôn là câu hỏi tự nhiên thuần túy, không có mã số/tên riêng/thuật ngữ chính xác → vector thuần đã đủ, hybrid là over-engineering.
- Tham số k1, b (BM25) và k (RRF), hoặc alpha (weighted-sum) không nên đoán mò — cần eval set (recall@k, MRR — concept #5) để biết tune đúng hướng.
- Weighted-sum (`score = α·vector_score + (1-α)·bm25_score`) bắt buộc phải normalize 2 score về cùng thang (min-max/z-score) trước khi cộng, nếu không 1 kênh sẽ áp đảo kênh kia.

## Ví dụ áp dụng project

Dữ liệu Bộ luật Lao động (`lessons/data/sample-luat-lao-dong.txt`): user hỏi "Điều 36 nói gì về đơn phương chấm dứt hợp đồng lao động?" — vector search có thể trả về đúng Điều 35, 37 (gần nghĩa) thay vì đúng Điều 36 (đúng số). Hybrid search với BM25 kéo đúng chunk chứa "Điều 36" lên top nhờ exact match, trong khi vector vẫn giúp xếp hạng nội dung liên quan.

## Bài thực hành

1. Cài (nếu chưa có): `pip install rank_bm25 sentence-transformers`
2. Dùng lại các chunk đã tạo ở bài 2 (`chunk_heading_aware` trên `sample-luat-lao-dong.txt`).
3. Viết script:
   - Xây BM25 index bằng `rank_bm25.BM25Okapi` trên danh sách chunk.
   - Encode chunk bằng embedding model (như bài 1) để làm vector search.
   - Query: `"Điều 36 quy định gì"` — lấy top-5 riêng từ BM25 và riêng từ vector search, in ra so sánh.
   - Viết hàm `rrf_fusion(bm25_ranked_list, vector_ranked_list, k=60)` gộp 2 danh sách rank thành 1, sắp theo score_RRF.
4. So sánh: top-1 vector-only có đúng Điều 36 không? Top-1 sau hybrid có đúng không? Thử thêm query thuần semantic không có số điều (VD "công ty tự ý cho tôi nghỉ việc thì sao") — hybrid có làm kết quả tệ hơn vector-only không, vì sao?

## Checkpoint (đã đạt — 2026-09-02, có giải thích lại)

Chạy thực hành thật trên `sample-luat-lao-dong.txt` phát hiện 1 case thú vị hơn cả dự kiến: query "công ty tự ý cho tôi nghỉ việc thì sao" bị **cả BM25 lẫn vector search** xếp nhầm Điều 35 (quyền NLĐ tự nghỉ) lên trên Điều 36 (quyền NSDLĐ cho nghỉ) — đúng ra câu hỏi phải khớp Điều 36 hơn.

- Câu hỏi: Hybrid (RRF) có sửa được lỗi này không, vì sao? → User trả lời "không biết" ở lượt đầu, được giải thích lại: RRF chỉ gộp thứ hạng, cứu được document khi 2 kênh **bất đồng ý kiến**; khi cả 2 kênh cùng đồng thuận sai (shared blind spot), RRF không có cơ chế phát hiện sai, chỉ tổng hợp phiếu bầu chung sai.
- Câu hỏi: Hướng nào sửa được lỗi chung này? → Reranking bằng cross-encoder (concept #4) — model đọc query + document **cùng lúc** (không encode riêng biệt rồi so khớp như BM25/vector), nên phân biệt được sắc thái tinh vi (ai là chủ thể hành động) mà 2 kênh retrieval kia bỏ lỡ.

Chi tiết đầy đủ đã lưu trong [03-hybrid-search-interview.md](03-hybrid-search-interview.md).
