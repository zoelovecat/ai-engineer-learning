# Phỏng vấn cho Concept #3: Hybrid search (vector + BM25)

← Quay lại bài chính: [03-hybrid-search.md](03-hybrid-search.md) · Toán: [03-hybrid-search-math.md](03-hybrid-search-math.md)

## Q&A thường gặp

**Q: Hybrid search là gì, khác vector search thuần ở đâu?**
A: Chạy song song vector search (semantic, dựa trên embedding + cosine similarity) và BM25 (lexical, dựa trên inverted index + term frequency/IDF), rồi gộp 2 danh sách kết quả bằng 1 thuật toán fusion (thường là RRF). Vector search hiểu nghĩa nhưng yếu với exact match; BM25 ngược lại.

**Q: Vì sao không cộng thẳng score của vector search và BM25?**
A: Vì 2 loại score không cùng thang đo — cosine similarity nằm trong [0,1] hoặc [-1,1], còn BM25 score không có chặn trên, phụ thuộc vào corpus (IDF, độ dài trung bình). Cộng thẳng sẽ để 1 kênh áp đảo kênh kia một cách vô nghĩa. Phải normalize (min-max/z-score) nếu dùng weighted-sum, hoặc dùng RRF để bỏ qua giá trị score, chỉ dùng rank.

**Q: RRF hoạt động thế nào, vì sao dùng rank thay vì score?**
A: `score_RRF(d) = Σ 1/(k + rank_r(d))`, k thường=60. Dùng rank vì rank luôn nằm trong thang đo giống nhau (1, 2, 3...) bất kể hệ thống retrieval nào, nên fusion không cần lo normalize hay canh chỉnh trọng số giữa các kênh có phân phối score khác nhau.

**Q: Vì sao cần BM25 nếu đã có vector search "hiểu ngữ nghĩa"?**
A: Vì embedding model nén nghĩa vào không gian vector chung, các token hiếm/out-of-distribution (mã số, tên riêng, thuật ngữ chính xác) bị nén gần nhau mất phân biệt (anisotropy). BM25 khớp chính xác chuỗi ký tự, không quan tâm ngữ nghĩa, nên cứu được đúng những case vector yếu.

**Q: Khi nào KHÔNG cần hybrid search?**
A: Khi corpus nhỏ và query luôn là câu hỏi tự nhiên thuần túy, không có mã số/tên riêng/thuật ngữ cần khớp chính xác — lúc đó vector thuần đã đủ, thêm BM25 chỉ tăng độ phức tạp/latency mà không tăng chất lượng đáng kể.

**Q: k1, b trong BM25 dùng để làm gì?**
A: k1 kiểm soát mức độ "bão hòa" của term frequency (từ xuất hiện càng nhiều điểm càng tăng nhưng tăng chậm dần — tránh document spam từ khóa thắng tuyệt đối). b kiểm soát mức độ phạt document dài hơn trung bình (b=0 nghĩa là không phạt độ dài, b=1 phạt tối đa).

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Bẫy: "RRF tự động ưu tiên exact match"** — SAI. Xem ví dụ tính tay trong file toán: document đúng (BM25 rank 1) vẫn có thể thua document khác nếu document kia rank 1 ở vector search — vì chênh lệch rank nhỏ tạo chênh lệch score RRF rất nhỏ với k=60. RRF ổn định/khó bị 1 kênh lỗi phá hỏng, nhưng KHÔNG tự động thiên vị kênh nào — muốn ưu tiên exact match phải giảm k hoặc dùng weighted-sum có tune trọng số.
- **Bẫy: nhầm hybrid search với "dùng 2 model embedding rồi trung bình vector"** — hybrid search luôn là 2 *loại* retrieval khác cơ chế (dense vs sparse), không phải trộn nhiều dense model.
- **Bẫy: nghĩ BM25 "cũ", không cần học vì đã có LLM/embedding hiện đại** — thực tế BM25 vẫn là baseline mạnh, gần như luôn có mặt trong production RAG thật (Elasticsearch, Azure AI Search, Weaviate đều default hybrid), vì nó rẻ, nhanh, và giải quyết đúng lỗ hổng của vector search.
- **Bẫy: quên rằng BM25 cần tokenization tốt** — tiếng Việt không có khoảng trắng phân từ rõ ràng như tiếng Anh (VD "đơn phương" là 1 cụm 2 từ), tokenize sai (`.split()` theo khoảng trắng) làm giảm chất lượng BM25 đáng kể so với dùng tokenizer tiếng Việt (underthesea, pyvi).
- **Bẫy: tưởng phải chọn 1 trong 2 (vector HOẶC BM25)** — thực ra production luôn muốn cả 2 vì chúng bù trừ điểm yếu cho nhau, không phải cạnh tranh loại trừ.

**Q: Hybrid search (RRF) có sửa được lỗi khi cả BM25 lẫn vector search cùng retrieve sai (đồng ý sai) không?**
A: Không. RRF chỉ gộp thứ hạng — nó "cứu" document khi 2 kênh **bất đồng ý kiến** (kênh này xếp thấp, kênh kia xếp cao). Khi cả 2 kênh cùng đồng thuận sai (shared blind spot), RRF không có cơ chế kiểm tra đúng/sai, chỉ tổng hợp phiếu bầu — phiếu bầu chung sai thì kết quả gộp vẫn sai. Hybrid search sửa được lỗi lệch pha giữa 2 kênh, không sửa được lỗi chung của cả 2 kênh.

**Q: Khi hybrid vẫn sai vì lỗi chung giữa BM25 và vector search, hướng nào có thể sửa được?**
A: Reranking bằng cross-encoder (concept #4). BM25 và vector search đều encode query và document **riêng biệt** rồi so khớp (BM25: đếm từ; vector: so cosine 2 vector độc lập) — không bên nào thực sự "đọc" query và document cùng lúc để suy luận quan hệ ngữ nghĩa tinh (VD ai là chủ thể hành động trong câu). Cross-encoder nhận **cả query lẫn document làm 1 input chung**, cho attention chạy xuyên suốt cả 2, nên phân biệt được sắc thái tinh vi mà retrieval encode-riêng-biệt bỏ lỡ. Vì đắt hơn (chạy per pair, không cache được như vector), cross-encoder chỉ áp dụng sau khi hybrid đã lọc thô còn ít candidate.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp (bổ sung — thực hành thật)

- **Bẫy: nghĩ hybrid search luôn cải thiện kết quả so với 1 kênh đơn lẻ** — thực hành thật cho thấy hybrid **không tự cải thiện gì** nếu cả BM25 và vector search cùng mắc lỗi giống nhau; hybrid chỉ hoạt động tốt khi điểm yếu 2 kênh **bù trừ** lẫn nhau (1 kênh đúng, 1 kênh sai), không phải khi cả 2 cùng sai theo cùng 1 hướng.
- **Bẫy: minh họa lý thuyết bằng corpus quá nhỏ** — với corpus chỉ 4 chunk, vector search có thể phân biệt đúng số Điều dễ dàng (không lộ ra vấn đề anisotropy), khiến người học tưởng vector search "không có vấn đề gì" — vấn đề chỉ lộ rõ với corpus lớn hơn, nhiều candidate ngữ nghĩa gần nhau hơn.
- **Case thật gặp phải**: query "công ty tự ý cho tôi nghỉ việc thì sao" bị cả BM25 và vector search xếp nhầm Điều 35 (quyền của người lao động tự nghỉ) lên trên Điều 36 (quyền của người sử dụng lao động cho nghỉ) — vì cụm từ "nghỉ việc" về mặt bề mặt/ngữ nghĩa gần Điều 35 hơn, dù về logic câu hỏi đang hỏi đúng Điều 36. Đây là ví dụ thật cho "shared blind spot" — lý do cần reranking chứ không chỉ dừng ở hybrid search.

## Bảng so sánh nhanh

| | Vector search | BM25 | Hybrid (RRF) |
|---|---|---|---|
| Cơ chế | Embedding + cosine similarity | Inverted index + TF-IDF | Cả 2 + fusion theo rank |
| Mạnh ở | Đồng nghĩa, diễn đạt khác, ngữ nghĩa | Exact match: mã số, tên riêng, từ hiếm | Bù trừ điểm yếu 2 bên |
| Yếu ở | Tên riêng, mã số, thuật ngữ hiếm (anisotropy) | Không hiểu đồng nghĩa/diễn đạt khác | Thêm latency, cần tune k/k1/b |
| Chi phí hạ tầng | 1 vector index | 1 inverted index | Cả 2 index + bước fusion |
| Khi dùng | Corpus nhỏ, query tự nhiên thuần | Ít khi dùng riêng trong RAG hiện đại | Mặc định cho production RAG thật |
