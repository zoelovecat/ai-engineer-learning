# Concept #6: Vector DB internals (HNSW) (Giai đoạn 2 - RAG)

Ngày tạo: 2026-09-07

Trạng thái: Đang học

🎯 Điểm hay bị hỏi khi phỏng vấn: [06-vector-db-hnsw-interview.md](06-vector-db-hnsw-interview.md)

## 1. Nó là gì

Vấn đề gốc: so query với **toàn bộ** N vector trong corpus (brute-force/exact search) là O(N) mỗi query — chậm, không scale với N lớn (hàng triệu vector). HNSW (Hierarchical Navigable Small World) là thuật toán **Approximate Nearest Neighbor (ANN)** — đánh đổi 1 chút độ chính xác để lấy tốc độ gần O(log N).

Cơ chế:

- Mỗi vector là 1 node trong 1 đồ thị, nối cạnh tới các node "gần" nó.
- Đồ thị có **nhiều tầng (layer)** kiểu skip-list: tầng trên thưa (ít node, cạnh dài, đi xa nhanh), càng xuống tầng dưới càng dày (tầng 0 = toàn bộ node, cạnh ngắn, chi tiết).
- **Tìm kiếm**: bắt đầu ở tầng cao nhất → greedy search tới hàng xóm gần query nhất trong tầng đó → hết đường đi gần hơn thì rơi xuống tầng dưới tại đúng node đó → lặp lại tới tầng 0 → kết quả gần đúng cuối cùng.
- Trực giác: giống tra bản đồ tỉnh (tầng cao, đi nhanh tới đúng khu vực) → bản đồ quận → bản đồ đường (tầng 0, chi tiết), thay vì dò từng nhà trong cả thành phố.
- 2 tham số quan trọng:
  - **M**: số cạnh tối đa mỗi node giữ mỗi tầng — lớn hơn = đồ thị dày hơn = chính xác hơn nhưng tốn RAM + build chậm hơn.
  - **ef (ef_search / ef_construction)**: độ rộng tập ứng viên giữ lại mỗi bước greedy search — lớn hơn = chính xác hơn (gần brute-force) nhưng chậm hơn.

Đây là thuật toán index đứng sau Pinecone, Weaviate, Qdrant, pgvector (`hnsw` index type), Milvus.

## 2. Vì sao cần hiểu sâu

Tutorial cơ bản coi vector DB là hộp đen "insert vector, query top-k, luôn đúng". Thực tế HNSW là **approximate** — có thể bỏ sót neighbor thật gần nhất nếu M/ef đặt thấp để ưu tiên tốc độ. Recall@k (concept #5) đo được thấp có thể do tầng index (ef quá thấp), không phải do embedding hay retrieval logic — đây là chỗ dễ debug sai hướng nếu không hiểu cơ chế.

Build index (insert hàng loạt) chậm hơn nhiều so với query, vì mỗi lần insert phải tìm đúng vị trí gắn cạnh trong graph nhiều tầng.

## 3. Trade-off / khi nào cần tune / khi nào KHÔNG cần

- ef_search thấp: query nhanh nhưng recall thấp, nhất là vùng dữ liệu dày đặc.
- M lớn/ef_construction lớn: build chậm, tốn RAM hơn, đổi lấy recall cao hơn khi query.
- HNSW giữ toàn bộ graph + vector trong RAM (hầu hết implementation) — giới hạn thực tế với corpus rất lớn.
- Dùng managed DB (Pinecone) với corpus vừa/nhỏ — default M/ef thường đã ổn, chỉ tune tay khi tự host và đã đo recall@k không đạt.
- **Không phải lúc nào cũng cần ANN**: corpus nhỏ (vài nghìn vector) → brute-force vẫn đủ nhanh và **chính xác tuyệt đối** — junior thấy "vector search" là nghĩ ngay Pinecone/Qdrant, middle biết đánh giá quy mô trước khi chọn.

## Ví dụ áp dụng project

`sample-luat-lao-dong.txt` chỉ 4 chunk — quá nhỏ để cần HNSW (ví dụ thực tế cho "khi nào KHÔNG cần", brute-force `np.dot` đã dùng từ bài 1 là lựa chọn đúng). Để cảm nhận trade-off M/ef thật, bài thực hành dùng corpus tổng hợp lớn hơn (5000 vector ngẫu nhiên).

## Bài thực hành

File: [practice/06-hnsw-vs-bruteforce.py](../practice/06-hnsw-vs-bruteforce.py)

1. Sinh 5000 vector ngẫu nhiên 128 chiều làm corpus giả lập, normalize.
2. `brute_force_search` làm đáp án đúng tuyệt đối + đo thời gian.
3. Build `hnswlib.Index(space='cosine', dim=128)` với `M=16, ef_construction=200`.
4. Query 20 vector ngẫu nhiên với `ef_search` = 10, 50, 200 — đo recall@10 (so với brute-force) và thời gian trung bình mỗi query cho từng giá trị.
5. Quan sát: ef_search tăng → recall tăng, latency tăng theo đúng lý thuyết không?

Trạng thái: đã viết xong code đầy đủ, **chưa chạy thật** (môi trường agent không có Python) — cần user tự chạy và báo kết quả.

## Checkpoint (chưa đạt — cần ôn lại, 2026-09-07)

3 câu hỏi đã hỏi (xem đầy đủ Q&A trong [06-vector-db-hnsw-interview.md](06-vector-db-hnsw-interview.md)):

1. Vì sao HNSW "approximate", cơ chế cụ thể nào khiến nó bỏ sót neighbor gần nhất? → User nắm đúng phần trade-off (M/ef cao ↔ chậm hơn nhưng chính xác hơn) nhưng đó là **hệ quả**, chưa nêu được **cơ chế gốc**: greedy search không quay lui (no backtracking) có thể kẹt ở local optimum trong đồ thị. Đã giải thích lại.
2. Thiết kế thử nghiệm để xác nhận lỗi recall@k thấp nằm ở tầng index (HNSW) hay ở embedding/chunking? → User trả lời "không biết". Đã giải thích: giữ nguyên embedding, so recall giữa HNSW và brute-force trên **cùng 1 tập vector** (chính là bài thực hành `practice/06-hnsw-vs-bruteforce.py`) — nếu 2 cái lệch nhau nhiều thì lỗi ở tầng index; nếu HNSW ≈ brute-force nhưng recall so với ground truth thật vẫn thấp thì lỗi ở embedding/chunking.
3. Corpus 3000 document, nên dùng HNSW ngay cho "chuyên nghiệp" không? → User trả lời đúng: cần đánh giá theo quy mô dữ liệu và mức chấp nhận sai lệch, không phải cứ "chuyên nghiệp" là hợp lý.

Trạng thái: **Đang học** (chưa đủ điều kiện Đã học) — cần ôn lại cơ chế local optimum/no-backtracking và cách thiết kế thử nghiệm tách tầng index trước khi mark hoàn thành. Vẫn còn nợ chạy `practice/06-hnsw-vs-bruteforce.py` thật để có số liệu kiểm chứng.
