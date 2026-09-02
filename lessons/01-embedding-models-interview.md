# Điểm nên nhớ khi phỏng vấn — Concept #1: Embedding models

Lesson chính: [01-embedding-models.md](01-embedding-models.md) · Toán: [01-embedding-models-math.md](01-embedding-models-math.md)

## Câu hỏi có thể gặp

**Q: Embedding là gì, cơ chế hoạt động ra sao?**
A: Là 1 vector số (VD 768/1536 chiều) đại diện cho ý nghĩa ngữ nghĩa của 1 đoạn text, tạo bởi model encoder (thường train bằng contrastive learning) sao cho câu có nghĩa gần nhau → vector gần nhau (đo bằng cosine similarity).

**Q: Sự khác biệt chính giữa dùng API (OpenAI/Cohere) và model mã nguồn mở (BGE/E5) để tạo embedding?**
A: API dễ dùng, chất lượng ổn định, nhưng tốn phí theo token và dữ liệu phải gửi ra ngoài (vấn đề với dữ liệu nhạy cảm). Model mã nguồn mở tự host được, miễn phí vận hành, kiểm soát dữ liệu hoàn toàn, nhưng cần tự lo hạ tầng (CPU/GPU) và một số model cần xử lý riêng (VD prefix của E5).

**Q: Dimension size của embedding ảnh hưởng gì?**
A: Dimension lớn → biểu diễn ngữ nghĩa chi tiết hơn nhưng tốn RAM/disk hơn, so sánh (cosine similarity) và build index (HNSW) chậm hơn. Một số model hỗ trợ Matryoshka embeddings — cắt ngắn dimension (VD 1536→256) mà mất rất ít độ chính xác, dùng để tối ưu chi phí lưu trữ/tốc độ.

**Q: Cosine similarity khác dot product ở điểm nào? Vì sao dùng cosine similarity mà không dùng thẳng dot product?**
A: Cosine similarity = dot product chia cho tích độ dài 2 vector → chuẩn hóa loại bỏ ảnh hưởng độ dài, chỉ so sánh "hướng". Dot product thô bị lệch bởi độ dài vector, không phản ánh đúng độ tương đồng ngữ nghĩa nếu vector chưa được chuẩn hóa (normalize).

**Q: Vậy tại sao trong code chỉ thấy tính dot product mà không thấy chia cho magnitude?**
A: Vì vector đã được encode với `normalize_embeddings=True`, tức đã có độ dài = 1 (unit vector) từ trước. Khi |A|=|B|=1, cosine similarity toán học rút gọn thành đúng bằng dot product — nên không cần chia lại.

**Q: Vì sao E5 cần prefix "query: "/"passage: " mà BGE/OpenAI thì không?**
A: E5 được train với 2 loại input khác nhau (câu hỏi ngắn vs đoạn văn bản dài) gắn kèm prefix để model phân biệt vai trò — quên prefix là lỗi phổ biến khiến retrieval kém mà không rõ nguyên nhân vì không có lỗi runtime, chỉ có chất lượng thấp hơn.

**Q: Nếu dữ liệu chứa nhiều mã số/tên riêng/số điều luật, chỉ dùng embedding (vector search) có đủ không?**
A: Không — embedding thuần yếu ở khớp chính xác chuỗi ký tự/tên riêng/mã số vì nó tối ưu cho ngữ nghĩa, không phải khớp từ khóa chính xác. Cần kết hợp thêm BM25 (hybrid search — concept tiếp theo).

**Q: Có thể trộn vector từ 2 embedding model khác nhau trong cùng 1 vector index không?**
A: Không — mỗi model tạo ra không gian vector riêng, khoảng cách/góc giữa các vector không so sánh được chéo giữa 2 không gian khác nhau. Đổi model bắt buộc phải re-embed lại toàn bộ dữ liệu.

**Q: Khi nào KHÔNG nên chọn dimension lớn nhất dù có ngân sách?**
A: Khi dữ liệu ít (VD vài nghìn chunk) — lợi ích về độ chính xác không đáng so với chi phí lưu trữ/tốc độ tăng thêm; dimension lớn chỉ đáng khi dữ liệu đủ lớn/phức tạp để tận dụng được độ chi tiết đó.

**Q: Nếu cần tìm đúng đoạn văn bản chứa "Điều 36 Bộ luật Lao động" trong kho luật, bạn thiết kế retrieval thế nào?**
A: Kết hợp hybrid search — vector search bắt các câu hỏi diễn giải không nêu số điều (VD "công ty sa thải tôi không báo trước có đúng luật không"), còn BM25 khớp chính xác keyword/số điều luật ("Điều 36"). Lý do bắt buộc cần BM25: với embedding, "Điều 36" và "Điều 63" gần như không có khác biệt ngữ nghĩa đáng kể — model chỉ thấy "một điều luật nào đó", không tự nhiên phân biệt được số cụ thể, nên vector search một mình có thể trả về sai điều luật dù nội dung câu hỏi rất rõ ràng.

**Q: Vì sao không nên đặt ngưỡng cosine similarity cố định (VD "> 0.75 là liên quan") để quyết định kết quả có trả cho user hay không?**
A: Vì hiện tượng anisotropy — nhiều embedding model (đặc biệt multilingual size nhỏ) nén toàn bộ câu cùng ngôn ngữ/miền vào một dải similarity hẹp và cao sẵn (thực nghiệm: câu hoàn toàn không liên quan vẫn ra ~0.77-0.80), nên giá trị tuyệt đối không phản ánh đúng "có liên quan hay không", kể cả trong cùng 1 model chứ không chỉ khác nhau giữa các model. Cách đúng: dùng top-k (thứ hạng tương đối) thay vì ngưỡng tuyệt đối, và calibrate/đánh giá bằng tập câu hỏi có nhãn đúng/sai (liên hệ recall@k, MRR — concept #5) thay vì đoán một con số.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Nhầm cosine similarity với Euclidean distance** — 2 metric khác nhau (1 đo góc, 1 đo khoảng cách thẳng); nhiều vector DB cho chọn metric, chọn sai sẽ ảnh hưởng chất lượng retrieval dù cùng 1 embedding model.
- **Tưởng "normalize" là xử lý văn bản** (lowercase, bỏ dấu câu...) — thực ra ở đây `normalize_embeddings=True` là chuẩn hóa ĐỘ DÀI VECTOR (chia cho magnitude), không liên quan gì đến tiền xử lý text.
- **Quên mất domain mismatch**: model embedding train chủ yếu tiếng Anh sẽ cho kết quả kém với văn bản tiếng Việt nhiều thuật ngữ hành chính — cần chọn model multilingual (BGE-M3) cho use case luật lao động Việt Nam.
- **Tưởng embed nhiều câu cùng lúc (batching) không khác gì encode từng câu một** — thực ra batching tận dụng tốt hơn CPU/GPU (đặc biệt GPU), là kỹ thuật tối ưu throughput thật ở production, không chỉ là "gọi hàm nhiều lần".
- **Không phân biệt được embedding có train "on-the-fly" theo dữ liệu mới hay không** — model embedding thường là frozen (không tự học thêm khi bạn dùng), muốn nó "học" domain mới phải fine-tune riêng (liên hệ concept #26 - contrastive learning, và Giai đoạn 4 - fine-tuning).

## Bảng so sánh nhanh (ôn trước phỏng vấn)

| Model | Nhà cung cấp | Dimension | Điểm mạnh | Điểm cần lưu ý |
|---|---|---|---|---|
| text-embedding-3-small/large | OpenAI (API) | 1536 / 3072 (cắt ngắn được) | Dễ dùng, chất lượng tốt | Tốn phí, dữ liệu đi qua API ngoài |
| embed-v3 | Cohere (API) | 1024 | Multilingual mạnh, tách mode query/document | Tốn phí, phụ thuộc API |
| BGE (BGE-M3) | Mã nguồn mở | 384–1024 | Tự host, multilingual tốt (kể cả tiếng Việt) | Cần tự lo hạ tầng serving |
| E5 | Mã nguồn mở | 384–1024 | Tương tự BGE | Bắt buộc đúng prefix "query:"/"passage:" |

## Hiệu năng — điểm hay bị hỏi thêm

- `model.encode()` (forward pass qua Transformer) là bước NẶNG, tỉ lệ với số câu × kích thước model — chạy GPU nếu có, tự rơi về CPU nếu không mà **không báo lỗi**, dễ khiến người mới nhầm là "chậm do bug".
- Tính cosine similarity sau khi đã có vector (`vectors @ vectors.T`) là bước RẤT NHẸ ở quy mô nhỏ — chỉ thành vấn đề khi so sánh brute-force hàng triệu vector, lúc đó mới cần cấu trúc index như HNSW (concept #6) thay vì tính trực tiếp.
