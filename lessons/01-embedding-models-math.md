# Toán nền cho Concept #1: Dot product & Cosine similarity

Lesson chính: [01-embedding-models.md](01-embedding-models.md)

## 1. Vector ở đây là gì

Sau khi encode, mỗi câu trở thành 1 mảng số, ví dụ 4 chiều:
`A = [0.8, 0.1, -0.3, 0.5]`

Mỗi số là 1 "tọa độ". Câu có nghĩa gần nhau → 2 mảng số này "gần nhau" trong không gian nhiều chiều. Câu hỏi tiếp theo là: "gần nhau" đo bằng cách nào?

## 2. Dot product (tích vô hướng) — tính như thế nào

**Công thức:** nhân từng cặp tọa độ tương ứng của 2 vector, rồi cộng tất cả lại.

```
A · B = a1*b1 + a2*b2 + ... + an*bn
```

**Ví dụ tính tay:** A = [1, 2, 3], B = [4, 5, 6]

```
A · B = (1*4) + (2*5) + (3*6) = 4 + 10 + 18 = 32
```

**Ý nghĩa:**
- Dot product càng lớn (dương) → 2 vector càng "cùng hướng" — *và/hoặc* càng dài.
- Dot product = 0 → 2 vector vuông góc (không liên quan theo hướng này).
- Dot product âm → 2 vector ngược hướng nhau.

**Vấn đề:** dot product bị ảnh hưởng bởi cả ĐỘ DÀI lẫn HƯỚNG của vector. Một vector rất dài sẽ luôn cho dot product lớn hơn dù hướng của nó không "giống" câu kia hơn. Vì vậy dot product thô **chưa dùng được ngay** để so sánh độ tương đồng ngữ nghĩa một cách công bằng — cần bước tiếp theo.

## 3. Magnitude / L2 norm (độ dài vector) — tính như thế nào

**Công thức:** căn bậc hai của tổng bình phương từng tọa độ.

```
|A| = sqrt(a1^2 + a2^2 + ... + an^2)
```

**Ví dụ tính tay:** A = [3, 4]

```
|A| = sqrt(3^2 + 4^2) = sqrt(9 + 16) = sqrt(25) = 5
```

(Đây chính là định lý Pythagoras — độ dài vector = cạnh huyền của tam giác vuông tạo bởi các tọa độ.)

## 4. Cosine similarity — tính như thế nào

**Công thức:** lấy dot product rồi CHIA cho tích độ dài 2 vector, để loại bỏ ảnh hưởng của độ dài, chỉ giữ lại "góc" giữa 2 vector.

```
cosine_similarity(A, B) = (A · B) / (|A| * |B|)
```

Kết quả luôn nằm trong khoảng **[-1, 1]**:
- `1` → 2 vector cùng hướng tuyệt đối (nghĩa giống nhau nhất có thể)
- `0` → không liên quan (vuông góc)
- `-1` → ngược nghĩa hoàn toàn

**Ví dụ tính tay:** A = [1, 2, 3], B = [4, 5, 6]

```
A · B = 32                       (đã tính ở mục 2)
|A|   = sqrt(1+4+9)   = sqrt(14) ≈ 3.742
|B|   = sqrt(16+25+36) = sqrt(77) ≈ 8.775

cosine_similarity(A, B) = 32 / (3.742 * 8.775) ≈ 32 / 32.84 ≈ 0.974
```

→ 0.974 rất gần 1, nghĩa là 2 vector này gần như cùng hướng — nếu đây là 2 câu, chúng có nghĩa rất gần nhau.

## 5. Vì sao code trong bài thực hành chỉ cần "dot product" (không thấy chia lại cho magnitude)?

Trong `practice/01-embedding-models.py`, bạn gọi `model.encode(..., normalize_embeddings=True)`. "Normalize" nghĩa là chia từng vector cho chính độ dài của nó, để nó có độ dài đúng bằng 1 (gọi là **unit vector**):

```
A_norm = A / |A|
```

Khi `|A| = |B| = 1`, công thức cosine similarity ở mục 4 rút gọn thành:

```
cosine_similarity(A, B) = (A · B) / (1 * 1) = A · B
```

**Đó là lý do:** khi vector đã normalize sẵn, cosine similarity CHÍNH LÀ dot product — không cần chia lại nữa. Trong `cosine_sim_matrix()`, cách nhanh nhất để tính toàn bộ ma trận NxN bằng numpy là:

```python
sim_matrix = vectors @ vectors.T
```

`@` là phép nhân ma trận. `vectors` có shape `(N, dim)`, `vectors.T` (chuyển vị) có shape `(dim, N)`. Kết quả `(N, N)` — phần tử ở hàng `i`, cột `j` chính là dot product giữa vector câu `i` và vector câu `j`, tức là cosine similarity giữa chúng (vì đã normalize).

## 6. CPU vs GPU & hiệu năng trong bài thực hành

Bài thực hành có 2 loại phép tính, tính chất khác hẳn nhau:

| Bước | Phép tính | Nặng hay nhẹ | Chạy ở đâu |
|---|---|---|---|
| `model.encode(...)` | Forward pass qua cả mạng Transformer | Nặng, tỉ lệ với số câu × kích thước model | GPU nếu máy có + PyTorch bản CUDA; tự rơi về CPU nếu không (không báo lỗi — dễ nhầm) |
| `cosine_sim_matrix()` / `vectors @ vectors.T` | Dot product / nhân ma trận trên vector đã encode sẵn | Rất nhẹ khi N nhỏ (numpy dùng BLAS tối ưu) | Luôn CPU, chỉ đáng lo khi N cực lớn (hàng triệu vector) → lúc đó dùng HNSW (concept #6) thay vì so brute-force |

- Với 5 câu và model nhỏ (bge-small, multilingual-e5-small, ~30-120M tham số): CPU đã đủ nhanh (<1s), không cần GPU.
- Ở production embed hàng nghìn/triệu chunk luật lao động: CPU là bottleneck rõ rệt → cần GPU hoặc dùng API (OpenAI/Cohere chạy GPU phía họ). Batching (encode nhiều câu/lần thay vì từng câu) tăng throughput rõ trên cả CPU lẫn GPU.

**Lưu ý bug nhỏ trong `practice/01-embedding-models.py`:** dòng `return np.dot(vectors, vectors.T)` dùng `np.dot` nhưng file chưa có `import numpy as np` ở đầu — cần thêm import này, nếu không sẽ lỗi `NameError` khi chạy.

## 7. Tự kiểm chứng (không bắt buộc nộp)

Cho 2 vector đã normalize sẵn: `A = [0.6, 0.8]`, `B = [0.8, 0.6]`
(kiểm tra: `|A| = sqrt(0.36+0.64) = sqrt(1) = 1`, `|B|` tương tự = 1 → đúng là đã normalize)

- Tự tính tay `A · B`.
- So sánh với kết quả `numpy.dot(A, B)` khi chạy thử trong Python.
- Thử đổi `B = [-0.8, -0.6]` (ngược hướng hoàn toàn với A) — dot product ra âm hay dương? Có khớp với phần "ý nghĩa" ở mục 2 không?
