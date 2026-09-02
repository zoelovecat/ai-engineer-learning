# Toán cho Concept #3: BM25 + Reciprocal Rank Fusion (RRF)

← Quay lại bài chính: [03-hybrid-search.md](03-hybrid-search.md)

## Phần A — Tính tay BM25

Công thức:

```
BM25(D,Q) = Σ IDF(qi) × f(qi,D)·(k1+1) / [f(qi,D) + k1·(1 - b + b·|D|/avgdl)]
IDF(qi)   = ln( (N - n(qi) + 0.5) / (n(qi) + 0.5) + 1 )
```

- N: tổng số document trong corpus.
- n(qi): số document chứa từ qi.
- f(qi,D): số lần qi xuất hiện trong D.
- |D|: độ dài document (số từ). avgdl: độ dài trung bình toàn corpus.
- k1=1.5, b=0.75 (giá trị mặc định phổ biến).

### Dữ liệu ví dụ (3 chunk luật lao động, rút gọn)

- D1 (10 từ): "Điều 36 người lao động đơn phương chấm dứt hợp đồng phải báo trước"
- D2 (9 từ): "Điều 38 người sử dụng lao động đơn phương chấm dứt hợp đồng"
- D3 (8 từ): "Tiền lương làm thêm giờ được tính theo quy định"

N = 3, avgdl = (10+9+8)/3 = 9

Query: **"Điều 36"** → 2 term: "Điều", "36"

### Bước 1 — Tính IDF từng term

- "Điều" xuất hiện trong D1, D2 → n=2
  `IDF = ln((3-2+0.5)/(2+0.5)+1) = ln(1.5/2.5 + 1) = ln(1.6) ≈ 0.470`
- "36" chỉ xuất hiện trong D1 → n=1
  `IDF = ln((3-1+0.5)/(1+0.5)+1) = ln(2.5/1.5 + 1) = ln(2.667) ≈ 0.981`

→ Từ càng hiếm (n nhỏ) IDF càng cao. "36" hiếm hơn "Điều" nên được weight gần gấp đôi.

### Bước 2 — Tính BM25(D1, Q)

|D1|/avgdl = 10/9 = 1.111
Mẫu số dùng chung cho mọi term của D1:
`k1·(1-b+b·|D|/avgdl) = 1.5·(0.25 + 0.75·1.111) = 1.5·1.083 = 1.625`

- Term "Điều" (f=1): `0.470 × 1×2.5 / (1+1.625) = 1.175 / 2.625 ≈ 0.448`
- Term "36" (f=1): `0.981 × 1×2.5 / (1+1.625) = 2.453 / 2.625 ≈ 0.935`

**BM25(D1,Q) = 0.448 + 0.935 = 1.382**

### Bước 3 — Tính BM25(D2, Q)

|D2|/avgdl = 9/9 = 1.0 → mẫu số chung: `1.5·(0.25+0.75) = 1.5`

- Term "Điều" (f=1): `0.470 × 2.5 / (1+1.5) = 1.175/2.5 ≈ 0.470`
- Term "36" (f=0): D2 không chứa "36" → đóng góp = 0

**BM25(D2,Q) = 0.470 + 0 = 0.470**

### Bước 4 — BM25(D3, Q)

D3 không chứa "Điều" lẫn "36" → **BM25(D3,Q) = 0**

### Kết quả & ý nghĩa

Xếp hạng BM25: **D1 (1.382) > D2 (0.470) > D3 (0)**

D1 thắng áp đảo vì chứa đúng số "36" — đúng cái vector search có thể bỏ lỡ (D1 và D2 rất giống nhau về ngữ nghĩa: cùng nói "đơn phương chấm dứt hợp đồng", nên vector similarity giữa D1, D2 có thể gần bằng nhau, không phân biệt được số điều). Đây chính là lý do BM25 cứu được lỗi anisotropy đã thấy ở bài 1.

## Phần B — Tính tay Reciprocal Rank Fusion (RRF)

Công thức: `score_RRF(d) = Σ 1/(k + rank_r(d))`, k=60.

Giả sử với cùng query "Điều 36 quy định gì", 2 hệ thống trả về rank sau (1=tốt nhất):

| Document | Rank vector search | Rank BM25 |
|---|---|---|
| D1 | 3 (embedding không phân biệt tốt D1 vs D2) | 1 |
| D2 | 1 (ngữ nghĩa gần nhất) | 2 |
| D3 | 2 | 3 |

Tính từng document:

- `score_RRF(D1) = 1/(60+3) + 1/(60+1) = 1/63 + 1/61 = 0.01587 + 0.01639 = 0.03226`
- `score_RRF(D2) = 1/(60+1) + 1/(60+2) = 1/61 + 1/62 = 0.01639 + 0.01613 = 0.03252`
- `score_RRF(D3) = 1/(60+2) + 1/(60+3) = 1/62 + 1/63 = 0.01613 + 0.01587 = 0.03200`

Xếp hạng RRF: **D2 (0.03252) > D1 (0.03226) > D3 (0.03200)**

### Ý nghĩa quan trọng (điểm dễ bị hiểu sai)

Dù D1 mới là chunk **đúng** (chứa chính xác "Điều 36"), RRF ở đây vẫn xếp D2 lên đầu vì D2 hạng 1 ở vector còn D1 chỉ hạng 1 ở BM25 — với k=60, chênh lệch rank nhỏ (1 vs 3) tạo ra chênh lệch score cực nhỏ, không đủ để một tín hiệu "exact match mạnh" áp đảo. Đây là trade-off thật của RRF: nó **ổn định, khó bị 1 kênh lỗi phá hỏng toàn bộ**, nhưng cũng **không tự động ưu tiên exact-match** như người ta hay tưởng. Nếu muốn ưu tiên exact match mạnh hơn, cần giảm k (VD k=10) hoặc chuyển sang weighted-sum có normalize và tăng trọng số BM25 — quyết định này phải dựa trên eval set (recall@k/MRR — concept #5), không đoán cảm tính.

Liên hệ code: `rank_bm25.BM25Okapi(...).get_scores(query_tokens)` trả về mảng số chính là công thức Phần A; hàm `rrf_fusion()` bạn viết trong bài thực hành chính là công thức Phần B — thử in ra rank thô của cả 2 kênh trước khi fusion để đối chiếu với bảng trên.
