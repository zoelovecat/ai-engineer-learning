# Concept #1: Embedding models (Giai đoạn 2 - RAG)

Trạng thái: Đang học (đã học lý thuyết, đang làm bài thực hành)

📐 Phần toán (dot product, cosine similarity — tính tay từng bước): [01-embedding-models-math.md](01-embedding-models-math.md)
🎯 Điểm hay bị hỏi khi phỏng vấn: [01-embedding-models-interview.md](01-embedding-models-interview.md)

## 1. Nó là gì

Embedding model biến một đoạn text thành một vector số (ví dụ 768 hoặc 1536 chiều). Cơ chế: model (thường là biến thể encoder của Transformer, đã train bằng contrastive learning — concept #26) học cách "nén" ý nghĩa ngữ nghĩa của câu vào không gian vector sao cho **câu có nghĩa gần nhau thì vector gần nhau** (đo bằng cosine similarity hoặc dot product).

Ví dụ: "Người lao động bị sa thải trái pháp luật" và "Chấm dứt hợp đồng lao động không đúng quy định" — dù không chung từ nào nhiều, vector của chúng vẫn gần nhau vì embedding model học được ngữ nghĩa, không phải khớp từ khóa.

So sánh các lựa chọn phổ biến:

| Model | Nhà cung cấp | Dimension | Đặc điểm |
|---|---|---|---|
| text-embedding-3-small/large | OpenAI (API) | 1536 / 3072 (có thể cắt ngắn) | Dễ dùng, chất lượng tốt, tốn phí theo token, dữ liệu đi qua API bên ngoài |
| embed-v3 | Cohere (API) | 1024 | Mạnh về multilingual, có mode riêng cho search query vs document |
| BGE (BAAI) | Mã nguồn mở | 384–1024 tùy bản | Tự host, miễn phí, có bản tiếng Việt/multilingual tốt (BGE-M3) |
| E5 | Mã nguồn mở (Microsoft) | 384–1024 | Tương tự BGE, cần prefix "query: "/"passage: " đúng cách khi encode |

Vì project scam-detection xử lý luật lao động Việt Nam + dữ liệu case có thể nhạy cảm, việc chọn model tự host (BGE-M3, E5) so với gọi API (OpenAI/Cohere) là một quyết định thật.

## 2. Vì sao cần hiểu sâu (chỗ tutorial hay bỏ qua)

- **Dimension trade-off**: dimension càng lớn → biểu diễn ngữ nghĩa chi tiết hơn, nhưng tốn RAM/disk hơn, cosine similarity chậm hơn, HNSW build lâu hơn. Một số model (OpenAI v3, Matryoshka embeddings) cho phép cắt ngắn dimension (1536 → 256) mà mất rất ít độ chính xác — kỹ thuật tối ưu chi phí thật.
- **Query vs document asymmetry**: E5/BGE cần prefix khác nhau cho câu hỏi ("query: ...") và đoạn văn bản lưu trữ ("passage: ..."). Quên bước này là lỗi phổ biến khiến retrieval kém mà không rõ nguyên nhân.
- **Domain mismatch**: model train chủ yếu tiếng Anh sẽ kém với văn bản luật tiếng Việt đầy thuật ngữ hành chính → lý do chọn BGE-M3 (multilingual mạnh) cho tiếng Việt.
- Không thể trộn vector từ 2 model khác nhau trong cùng 1 index — đổi model nghĩa là phải re-embed toàn bộ dữ liệu.

## 3. Trade-off / khi nào KHÔNG dùng

- Đừng chọn dimension lớn nhất "cho chắc" nếu dữ liệu ít (vài nghìn chunk) — độ lợi chất lượng không đáng chi phí lưu trữ/tốc độ.
- Dữ liệu có nhiều mã số văn bản, số điều luật, tên riêng chính xác (VD "Điều 36 Bộ luật Lao động 2019") → embedding thuần **yếu** ở khớp chính xác chuỗi ký tự → cần **hybrid search** (concept #3) sau này.
- Nếu cần production nhanh, ít nhạy cảm dữ liệu, không quan tâm chi phí dài hạn → dùng OpenAI/Cohere API là hợp lý, không cần tự host.

## Ví dụ áp dụng project

Dùng để encode các đoạn (chunk) văn bản Bộ luật Lao động thành vector lưu vào vector DB, và encode câu hỏi user ("Công ty sa thải tôi không báo trước có đúng luật không?") thành vector để tìm chunk liên quan nhất.

## Bài thực hành

1. Cài `sentence-transformers`: `pip install sentence-transformers`
2. Viết script Python:
   - 5 câu: 2 cặp đồng nghĩa khác từ (chủ đề luật lao động: sa thải, nghỉ việc, lương, hợp đồng) + 1 câu không liên quan (VD thời tiết).
   - Encode bằng `BAAI/bge-small-en-v1.5` hoặc `intfloat/multilingual-e5-small`.
   - Tính ma trận cosine similarity giữa tất cả các cặp câu.
3. Quan sát: câu đồng nghĩa có similarity cao hơn hẳn câu không liên quan không? Nếu dùng E5, thử prefix "query: " vs không prefix, similarity có đổi không.

## Checkpoint (chưa thực hiện)

- Nếu dữ liệu có nhiều mã số/tên riêng, chọn hybrid search hay vector thuần? Vì sao?
- Cho ví dụ 1 trường hợp KHÔNG nên tăng dimension embedding dù có ngân sách.
- Vì sao không thể trộn vector từ 2 model embedding khác nhau trong cùng 1 index?
