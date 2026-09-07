# Interview notes: Vector DB internals (HNSW)

Lesson chính: [06-vector-db-hnsw.md](06-vector-db-hnsw.md)

## Q&A có thể gặp

**Q: HNSW là gì, giải quyết vấn đề gì?**
A: Approximate Nearest Neighbor search bằng đồ thị nhiều tầng (giống skip-list) — giải quyết vấn đề brute-force O(N) không scale khi corpus lớn, đổi lại độ chính xác tuyệt đối lấy tốc độ gần O(log N).

**Q: M và ef_search khác nhau ở đâu?**
A: M là tham số **build-time** — số cạnh tối đa mỗi node giữ ở mỗi tầng, quyết định độ dày đồ thị. ef_search là tham số **query-time** — độ rộng tập ứng viên xét trong lúc greedy search, có thể chỉnh mà không cần build lại index. ef_construction giống ef_search nhưng áp dụng lúc build.

**Q: HNSW có luôn trả về đúng k neighbor gần nhất không?**
A: Không — nó là approximate, có thể bỏ sót do đi theo đường greedy (không quay lui/backtrack đầy đủ). Recall@k đo được sẽ luôn ≤ 1.0 (không phải luôn = 1.0 như brute-force).

**Q: Khi nào KHÔNG cần dùng HNSW/vector DB chuyên dụng?**
A: Corpus nhỏ (vài nghìn vector) — brute-force (numpy dot product toàn bộ) vẫn đủ nhanh và chính xác tuyệt đối, không cần đánh đổi gì. Chỉ cần ANN khi N đủ lớn để brute-force thực sự thành bottleneck.

**Q: Nếu recall@k đo được (concept #5) thấp hơn kỳ vọng, nguyên nhân có thể ở đâu?**
A: Không chỉ do embedding model/chunking — có thể do tầng index: ef_search đặt quá thấp khiến HNSW bỏ sót neighbor thật gần nhất. Cần tách riêng: đo recall của HNSW so với brute-force (đúng tuyệt đối) trên cùng embedding, để biết lỗi nằm ở tầng nào.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Nhầm vector DB luôn trả về "đúng nhất".** HNSW là approximate — đây là điểm junior hay bỏ qua, nghĩ index nào cũng cho kết quả chính xác tuyệt đối như brute-force.
- **Tune ef_search cao "cho chắc"** mà không đo trade-off — ef_search quá cao có thể làm mất hết lợi thế tốc độ của HNSW so với brute-force (khi ef gần bằng N thì gần như duyệt hết, không còn nhanh hơn brute-force bao nhiêu).
- **Coi nhẹ RAM**: HNSW giữ toàn bộ graph + vector trong RAM ở hầu hết implementation — với corpus rất lớn, đây là giới hạn hạ tầng thật cần tính trước, không chỉ là vấn đề tốc độ.
- **Không phân biệt build-time param (M, ef_construction) với query-time param (ef_search)** — build-time cần build lại index mới đổi được, query-time đổi được ngay lúc query mà không cần rebuild.

## Ghi chú từ checkpoint thật (2026-09-07)

- **Cơ chế chính xác khiến HNSW bỏ sót neighbor** (điểm user quên, cần nhớ kỹ): tìm kiếm dùng **greedy search không quay lui (no backtracking)** — tại mỗi bước chỉ đi tới hàng xóm trực tiếp gần query nhất, không bao giờ quay lại thử nhánh đã bỏ qua. Nếu tất cả hàng xóm trực tiếp của node hiện tại đều xa hơn (local optimum trong cấu trúc đồ thị), thuật toán dừng ở đó dù có thể tồn tại node gần hơn ở nhánh chưa từng đi qua. Ví dụ dễ nhớ: leo núi trong sương mù, luôn bước lên cao hơn xung quanh, có thể dừng ở đỉnh đồi nhỏ mà không biết có núi cao hơn ở xa (phải đi xuống trước mới tới được). `ef_search` là van an toàn: giữ song song nhiều ứng viên mỗi bước thay vì chỉ 1, giảm xác suất kẹt local optimum.
- **Bẫy hay gặp**: trả lời được phần trade-off (tham số cao/thấp đổi lấy gì) nhưng không giải thích được *vì sao* — phỏng vấn viên thường hỏi xoáy đúng chỗ "cơ chế nào gây ra việc đó", không chỉ dừng ở "đánh đổi tốc độ/độ chính xác".
- **Cách tách lỗi recall@k thấp: tầng index hay tầng embedding/chunking?** Giữ nguyên embedding (cùng model, cùng vector), so recall giữa HNSW và brute-force trên **cùng 1 tập vector**: nếu 2 cái lệch nhiều → lỗi ở tầng index (ef quá thấp). Nếu HNSW ≈ brute-force (recall gần 1.0) nhưng recall so với ground truth thật (concept #5) vẫn thấp → lỗi ở embedding/chunking, không phải index. Đây là câu hỏi phỏng vấn thực tế kiểu "debug ở đâu" — cần biết tách từng tầng ra để cô lập nguyên nhân, không đoán mò.

## Bảng so sánh nhanh

| | Brute-force (exact) | HNSW (approximate) |
|---|---|---|
| Độ chính xác | tuyệt đối (100%) | gần đúng, phụ thuộc M/ef |
| Độ phức tạp mỗi query | O(N) | ~O(log N) |
| Phù hợp corpus | nhỏ (vài nghìn) | lớn (hàng trăm nghìn - hàng triệu+) |
| Tham số cần tune | không có | M, ef_construction (build), ef_search (query) |
| Bộ nhớ | chỉ cần lưu vector | vector + đồ thị nhiều tầng (tốn hơn) |
