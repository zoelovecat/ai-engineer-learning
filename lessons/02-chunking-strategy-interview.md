# Phỏng vấn — Chunking strategy

Lesson chính: [02-chunking-strategy.md](02-chunking-strategy.md)

## Q&A

**Q: Chunking là gì và vì sao nó quan trọng hơn cả chọn embedding model?**
A: Chia document dài thành đoạn nhỏ để embed. Quan trọng hơn chọn model vì nếu ranh giới chunk sai (cắt ngang ý, gộp 2 chủ đề khác nhau), dù embedding model tốt cỡ nào, vector của chunk vẫn mang nội dung "nửa vời" — retrieval sẽ kém bất kể model.

**Q: Có mấy cách chunking chính, khi nào dùng cách nào?**
A: Fixed-size/sliding window (dữ liệu không có cấu trúc, đơn giản, có overlap để không cắt đứt câu ở ranh giới); heading-aware (dữ liệu có cấu trúc rõ — luật, hợp đồng, docs kỹ thuật; ranh giới ngữ nghĩa do chính tài liệu định nghĩa sẵn); semantic chunking (dữ liệu tự do, không có cấu trúc, nhưng cần ranh giới ý nghĩa động — dùng similarity giữa câu liên tiếp để tìm chỗ cắt, tốn thêm chi phí embed).

**Q: Overlap trong sliding window giải quyết vấn đề gì và KHÔNG giải quyết được vấn đề gì?**
A: Giải quyết: câu bị cắt ở ranh giới chunk này vẫn còn nguyên vẹn ở chunk kế (nhờ phần lặp lại). KHÔNG giải quyết: việc 2 chủ đề/2 Điều khác nhau bị gộp chung vào 1 chunk — vì overlap chỉ dịch chuyển ranh giới cắt, không mang thông tin "ở đây chủ đề đổi", nó vẫn coi text là 1 chuỗi liên tục đồng nhất.

**Q: Semantic chunking hoạt động thế nào?**
A: Embed từng câu, tính similarity giữa các câu liên tiếp, chỗ nào similarity giảm mạnh (topic shift) thì cắt chunk ở đó. Ưu điểm: thích nghi theo nội dung thực. Nhược điểm: tốn chi phí embed thêm (mỗi câu 1 lần gọi), ngưỡng cắt (threshold) là hyperparameter phải tune, kết quả có thể không ổn định giữa các lần chạy.

**Q: Nếu 1 đơn vị heading (VD 1 Điều luật) quá dài, bạn xử lý thế nào?**
A: Không dùng heading-aware thuần — kết hợp hybrid: chia thô theo heading trước, nếu vượt ngưỡng kích thước thì chia tiếp bên trong (theo khoản, hoặc fixed-size), và bắt buộc prepend lại tiêu đề heading cha (VD "Điều 20.") vào đầu mỗi sub-chunk để không mất ngữ cảnh "đây là khoản của Điều nào".

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Bẫy "overlap càng lớn càng tốt"**: nhiều người nghĩ tăng overlap sẽ giảm mất mát thông tin ở mọi trường hợp. Thực tế overlap chỉ giúp với vấn đề "cắt đứt câu/ý ở ranh giới", hoàn toàn không giúp với vấn đề "2 chủ đề khác nhau bị gộp chung 1 chunk" — vì fixed-size chunking không có khái niệm "chủ đề" để mà tránh.
- **Bẫy "code không lỗi = đúng"**: case biên dễ bị bỏ sót nhất trong heading-aware chunking là **phần nội dung trước heading đầu tiên (preamble)** — nếu vòng lặp chỉ bắt đầu từ vị trí heading đầu tiên tìm được, đoạn preamble sẽ bị bỏ hoàn toàn khỏi mọi chunk, không có lỗi/exception nào báo hiệu, chỉ âm thầm mất dữ liệu. Đây là câu hỏi thực tế rất hay gặp khi review code chunking: "code này còn case biên nào chưa xử lý?"
- **Bẫy "semantic chunking luôn tốt nhất vì nó thông minh nhất"**: sai với dữ liệu đã có cấu trúc rõ ràng (luật, docs kỹ thuật) — dùng semantic chunking ở đây là phức tạp hóa không cần thiết, tốn thêm chi phí embed để "đoán" ra ranh giới mà tài liệu đã tự cho biết sẵn qua heading.
- **Bẫy chọn chunk_size cố định cho mọi loại document**: middle sẽ hỏi "document này có cấu trúc gì" trước khi chọn chiến lược, thay vì mặc định `chunk_size=500` cho mọi thứ.

## Bảng so sánh nhanh

| Chiến lược | Khi dùng | Ưu điểm | Nhược điểm |
|---|---|---|---|
| Fixed-size/sliding window | Dữ liệu không cấu trúc (chat, transcript, bài viết tự do) | Đơn giản, nhanh, dễ implement | Cắt ngang ý, overlap không cứu được việc gộp chủ đề khác nhau |
| Heading-aware | Dữ liệu có cấu trúc rõ (luật, hợp đồng, docs kỹ thuật) | Ranh giới ngữ nghĩa chính xác, không cần đoán | Cần cấu trúc rõ để parse; heading quá dài/quá ngắn cần xử lý thêm (hybrid) |
| Semantic chunking | Dữ liệu tự do nhưng cần ranh giới ý nghĩa động | Thích nghi theo nội dung thực, không cần cấu trúc sẵn | Tốn chi phí embed từng câu, ngưỡng cắt phải tune, có thể bất ổn định |
