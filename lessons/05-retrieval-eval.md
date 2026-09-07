# Concept #5: Đánh giá retrieval (recall@k, MRR) (Giai đoạn 2 - RAG)

Ngày tạo: 2026-09-04

Trạng thái: Đã học (2026-09-04) — **lưu ý: user chủ động yêu cầu đánh dấu xong dù chưa chạy practice/05-retrieval-eval.py và chưa làm checkpoint**, nên khi ôn lại nên ưu tiên chạy code thật trước để kiểm chứng bằng số liệu.

🎯 Điểm hay bị hỏi khi phỏng vấn: [05-retrieval-eval-interview.md](05-retrieval-eval-interview.md)

## 1. Nó là gì

2 metric định lượng để đo "retrieval tốt tới đâu" thay vì cảm tính đọc top-1 bằng mắt:

- **Recall@k**: tỷ lệ % câu hỏi mà document đúng **có mặt** trong top-k kết quả (không quan tâm đứng thứ mấy trong top-k).
  ```
  Recall@k = (số câu hỏi có doc đúng trong top-k) / (tổng số câu hỏi)
  ```
- **MRR (Mean Reciprocal Rank)**: quan tâm **thứ hạng chính xác** của document đúng.
  ```
  RR (1 câu hỏi) = 1 / rank(doc đúng đầu tiên)   — 0 nếu không có trong danh sách xét
  MRR = trung bình RR trên toàn eval set
  ```

Cần một **eval set** trước: tập câu hỏi kèm đáp án đúng (ground truth) đã biết trước, tự xây thủ công hoặc lấy từ log thực tế.

## 2. Vì sao cần hiểu sâu

4 bài trước đánh giá "đúng/sai" bằng đọc top-1 vài ví dụ — không scale, không phát hiện được regression khi đổi embedding model/chunking/thêm rerank. Recall@k/MRR biến đánh giá thành số đo lặp lại được trên hàng chục câu hỏi cùng lúc — bắt buộc phải có trước khi tune bất kỳ tham số nào (k1/b BM25, k của RRF, ngưỡng top-k trước rerank) có căn cứ thay vì đoán mò.

Đây cũng là câu trả lời cho câu hỏi đã treo ở bài Reranking: "recall@10 thấp có nên đầu tư rerank không" — không trả lời được nếu không đo recall trước. Recall@k đo chất lượng retrieval thô (trước rerank); MRR quan tâm vị trí chính xác nên thường đo ở tầng cuối pipeline (có thể sau rerank).

## 3. Trade-off / khi nào cần cẩn thận

- Chi phí xây eval set: cần label thủ công, dễ thiên vị nếu tự viết câu hỏi + tự biết đáp án — production nên lấy từ log câu hỏi thật + review tay.
- Recall@k không phạt vị trí: recall@10=100% dù đúng hạng 1 hay hạng 10 — phải chọn k khớp với k thực tế dùng trong pipeline (nếu chỉ đưa top-3 vào LLM thì đo recall@3, không phải recall@10).
- MRR chỉ tính document đúng **đầu tiên** — không hợp nếu câu hỏi có nhiều đáp án đúng (lúc đó cần NDCG).
- Không nên chỉ nhìn 1 con số trung bình toàn eval set — nên tách theo loại câu hỏi (explicit số điều / thuần semantic) vì trung bình có thể che giấu 1 nhóm yếu hẳn.

## Ví dụ áp dụng project

Eval set 12 câu trên `sample-luat-lao-dong.txt` (`lessons/data/eval-luat-lao-dong.json`), trộn loại `explicit` (có "Điều X") và `semantic` (không có số), đo riêng recall@5/MRR cho từng loại và cho 3 pipeline (BM25-only, vector-only, hybrid RRF) — để thấy rõ hybrid có thực sự cải thiện nhóm nào mà không hại nhóm kia, thay vì chỉ nhìn vài ví dụ đơn lẻ như các bài trước.

## Bài thực hành

File: [practice/05-retrieval-eval.py](../practice/05-retrieval-eval.py), eval set: [lessons/data/eval-luat-lao-dong.json](data/eval-luat-lao-dong.json)

1. `recall_at_k(ranked_indices, chunks, expected_dieu, k)` — 1 nếu chunk đúng số Điều nằm trong top-k, ngược lại 0.
2. `reciprocal_rank(ranked_indices, chunks, expected_dieu)` — 1/rank của chunk đúng đầu tiên, 0.0 nếu không thấy.
3. Chạy 3 pipeline (BM25-only, vector-only, hybrid RRF) trên toàn eval set, in bảng recall@5/MRR tách theo `explicit`/`semantic`, in ra câu nào bị MISS (recall=0).

Trạng thái: đã viết xong code đầy đủ, **chưa chạy thật** (môi trường agent không có Python) — cần user tự chạy và báo kết quả.

## Checkpoint

Chưa thực hiện — chờ user chạy `practice/05-retrieval-eval.py` và báo kết quả thật.
