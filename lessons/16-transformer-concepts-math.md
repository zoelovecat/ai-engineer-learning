# Toán — Attention (Q/K/V, scaled dot-product)

Lesson chính: [16-transformer-concepts.md](16-transformer-concepts.md)

## Công thức

Với 1 token có vector Query `q`, và các token trong chuỗi có vector Key `k_i`, Value `v_i`:

1. Điểm khớp: `score_i = q · k_i` (dot product — giống cosine similarity ở bài 1, nhưng không chuẩn hoá độ dài vector ở bước này)
2. Scale (chia cho căn bậc 2 của chiều vector `d_k`, để tránh softmax bão hoà khi vector dài): `score_i / sqrt(d_k)`
3. Softmax để ra trọng số (tổng = 1): `weight_i = softmax(score_i / sqrt(d_k))`
4. Output = trung bình có trọng số của Value: `output = Σ weight_i * v_i`

## Ví dụ số cụ thể (vector 2 chiều, dễ nhẩm)

Câu ví dụ 3 token: "Lan xin nghỉ" — ta tính attention output cho token **"nghỉ"** (đóng vai Query), so với chính 3 token trong câu (Key/Value).

Giả sử (số tự đặt, đã đơn giản hoá để dễ tính tay):

| Token | Key vector | Value vector |
|---|---|---|
| Lan | (1, 0) | (2, 0) |
| xin | (0, 1) | (0, 2) |
| nghỉ | (1, 1) | (4, 4) |

Query của "nghỉ": `q = (1, 1)` (giả sử Q = K cho token này, để đơn giản)

**Bước 1 — dot product `q · k_i`:**
- với "Lan": `(1,1)·(1,0) = 1*1 + 1*0 = 1`
- với "xin": `(1,1)·(0,1) = 1*0 + 1*1 = 1`
- với "nghỉ": `(1,1)·(1,1) = 1*1 + 1*1 = 2`

**Bước 2 — scale** (d_k = 2, sqrt(2) ≈ 1.41):
- Lan: 1 / 1.41 ≈ 0.71
- xin: 1 / 1.41 ≈ 0.71
- nghỉ: 2 / 1.41 ≈ 1.41

**Bước 3 — softmax** (softmax(x_i) = e^x_i / Σ e^x_j):
- e^0.71 ≈ 2.03, e^0.71 ≈ 2.03, e^1.41 ≈ 4.10
- tổng ≈ 2.03 + 2.03 + 4.10 = 8.16
- weight_Lan ≈ 2.03/8.16 ≈ 0.249
- weight_xin ≈ 2.03/8.16 ≈ 0.249
- weight_nghỉ ≈ 4.10/8.16 ≈ 0.502

**Bước 4 — output = Σ weight_i × v_i:**
- x: 0.249×2 + 0.249×0 + 0.502×4 = 0.498 + 0 + 2.008 = 2.506
- y: 0.249×0 + 0.249×2 + 0.502×4 = 0 + 0.498 + 2.008 = 2.506
- `output ≈ (2.51, 2.51)`

## Ý nghĩa kết quả

Token "nghỉ" cuối cùng có vector đại diện là **trung bình có trọng số** của chính nó và 2 token còn lại, với trọng số ~50% dành cho chính nó (vì dot product với chính nó luôn cao nhất khi Q=K) và ~25% mỗi token còn lại. Đây chính là "hoà trộn thông tin" — vector output của "nghỉ" giờ mang theo 1 phần thông tin của "Lan" và "xin", giúp model biết "nghỉ" này gắn với ai, hành động gì trong câu.

**Vì sao O(n²)**: phép tính 4 bước trên phải lặp lại cho **mỗi token trong câu làm Query** (không chỉ "nghỉ") — với câu n token, mỗi token phải tính dot product với n token khác → tổng n × n = n² phép tính dot product. Câu dài gấp đôi → số phép tính tăng gấp 4, không phải gấp 2.

Trong code thực tế (numpy/PyTorch), toàn bộ phép tính trên cho tất cả token được làm 1 lượt bằng phép nhân ma trận `Q @ K.T` (giống `np.dot`/`@` bạn đã dùng ở bài 1 và bài 3 cho embedding) — mỗi hàng của ma trận kết quả `n × n` chính là các `score_i` cho 1 token Query.
