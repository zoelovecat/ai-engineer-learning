# Concept #2: Chunking strategy (Giai đoạn 2 - RAG)

Trạng thái: Đã học (2026-09-02)

🎯 Điểm hay bị hỏi khi phỏng vấn: [02-chunking-strategy-interview.md](02-chunking-strategy-interview.md)

## 1. Nó là gì

Chunking là chia một document dài thành các đoạn nhỏ hơn để embed và lưu vào vector DB. Mỗi chunk cần mang **một đơn vị ngữ nghĩa trọn vẹn**: không quá to (loãng, chứa nhiều ý → embedding "trung bình hóa" mất focus), không quá nhỏ (mất ngữ cảnh, câu bị cắt giữa chừng).

Ba cách chia:

- **Fixed-size / sliding window**: chia đều theo số ký tự/token, có `overlap` giữa các chunk liên tiếp để câu bị cắt ở ranh giới chunk này vẫn còn trọn vẹn ở chunk kế. Không quan tâm cấu trúc nội dung — đây là cách tutorial cơ bản hầu như luôn dùng.
- **Heading-aware / structure-aware chunking**: dựa vào cấu trúc document thật (heading, Điều/Khoản, section) để chia. Chunk luôn là 1 đơn vị ngữ nghĩa hoàn chỉnh mà tác giả gốc đã định nghĩa sẵn.
- **Semantic chunking**: dùng embedding của từng câu, đo similarity giữa các câu liên tiếp, cắt chunk ở chỗ similarity giảm mạnh (chủ đề đổi). Thích nghi động, không cần cấu trúc rõ ràng, nhưng đắt hơn (phải embed từng câu) và ngưỡng cắt là hyperparameter phải tune.

## 2. Vì sao cần hiểu sâu (chỗ tutorial hay bỏ qua)

Chunking quyết định chất lượng RAG **nhiều hơn cả chọn embedding model**. Nếu chunk sai ranh giới, dù embedding model tốt cỡ nào, chunk đó vẫn mang nội dung "nửa vời" — không match đúng khi user hỏi trúng nội dung nằm giữa 2 chunk bị cắt lệch.

Với luật lao động: chia đều 500 ký tự rất dễ cắt ngang giữa các điểm (a, b, c...) của 1 khoản, hoặc tệ hơn — gộp phần cuối của Điều này với phần đầu Điều khác hoàn toàn không liên quan vào cùng 1 chunk, làm loãng embedding.

**Case biên dễ bị bỏ sót khi code heading-aware chunking (rút ra từ bài thực hành thật)**: nếu vòng lặp chỉ duyệt từ vị trí heading đầu tiên tìm được, **phần nội dung trước heading đầu tiên (preamble — ví dụ tên chương, lời mở đầu) sẽ bị bỏ hoàn toàn**, không nằm trong bất kỳ chunk nào — không lỗi, không exception, chỉ âm thầm mất dữ liệu. Đây là loại bug nguy hiểm nhất vì code chạy "sạch". Luôn tự hỏi: "còn case biên nào ở đầu/cuối/rỗng chưa xử lý?"

## 3. Trade-off / khi nào KHÔNG dùng

- **Sliding window**: dùng khi document không có cấu trúc rõ (transcript, chat log, bài viết tự do). Không dùng khi document có cấu trúc chuẩn hóa mạnh (luật, hợp đồng) — bỏ phí thông tin cấu trúc sẵn có.
- **Heading-aware**: lựa chọn mặc định cho luật lao động (có Điều/Khoản/Chương rõ ràng). Nhược điểm: 1 Điều quá dài (nhiều khoản) vẫn tạo ra chunk quá to, mất focus — cần chia tiếp bên trong (xem "Kỹ thuật hybrid" bên dưới); 1 Điều quá ngắn thì chunk quá bé.
- **Semantic chunking**: tốt cho nội dung không có cấu trúc và ranh giới ý nghĩa không cố định. Không đáng dùng cho luật — heading-aware đã cho ranh giới "đúng" do chính văn bản định nghĩa sẵn, dùng semantic chunking ở đây phức tạp hóa không cần thiết.
- **Tăng `overlap` không giải quyết được việc chunk fixed-size gộp 2 chủ đề khác nhau** — overlap chỉ tránh cắt đứt giữa câu ở ranh giới, nó không "biết" ranh giới chủ đề nằm ở đâu (đây là giới hạn cốt lõi của fixed-size chunking, dù tune overlap thế nào cũng không né được).

### Kỹ thuật hybrid (khi 1 Điều quá dài)

Không phải chọn 1 trong 3 cách — với Điều luật rất dài (nhiều khoản), kết hợp: heading-aware chia thô theo Điều trước, nếu 1 Điều vượt ngưỡng kích thước thì chia tiếp bên trong theo khoản (fixed/structure nhỏ hơn), và **luôn prepend tiêu đề "Điều X" vào đầu mỗi sub-chunk** — nếu không, sub-chunk chứa khoản 2 sẽ mất thông tin "đây là khoản 2 của Điều nào", embedding kém chính xác khi user hỏi có nhắc số điều.

## Ví dụ áp dụng project

Dùng heading-aware chunking (chia theo "Điều X.") cho văn bản Bộ luật Lao động trước khi embed — đảm bảo mỗi chunk là 1 Điều trọn vẹn, giữ nguyên số điều + tiêu đề, để khi user hỏi về 1 điều cụ thể, chunk trả về luôn đầy đủ ngữ cảnh.

## Bài thực hành

Dữ liệu mẫu: [data/sample-luat-lao-dong.txt](data/sample-luat-lao-dong.txt) (Điều 13, 20, 35, 36 — có cấu trúc Điều/Khoản/điểm a,b,c).
Code: `practice/02-chunking-strategy.py`

Viết `chunk_fixed(text, size=500, overlap=50)` và `chunk_heading_aware(text)` (regex `Điều \d+\.`), chạy trên file mẫu, so sánh kết quả.

**Kết quả quan sát được:**
- `chunk_fixed` cắt ngang giữa từ (vd "phải g|iao kết"), và tệ hơn: gộp phần cuối Điều 20 với phần đầu Điều 35 (2 chủ đề khác nhau) vào cùng 1 chunk; điểm (c) của 1 khoản bị tách sang chunk khác với (a), (b) — mất ngữ cảnh khi retrieve.
- `chunk_heading_aware` giữ mỗi Điều trọn vẹn, tiêu đề luôn đi kèm nội dung.
- Bug case biên: code gốc bỏ sót đoạn text trước "Điều" đầu tiên (preamble) — sửa bằng cách kiểm tra `positions[0] > 0` và thêm `text[:positions[0]]` làm chunk riêng nếu có nội dung.

## Checkpoint (đã đạt — 2026-09-02)

- Điều quá dài → chunk mất focus, gộp nhiều khoản không liên quan → cần chia nhỏ thêm bên trong kèm prepend tiêu đề Điều. **Đạt.**
- Tăng `overlap` không giải quyết việc 2 Điều khác nhau bị gộp vào 1 chunk, vì overlap không mang thông tin ranh giới chủ đề. **Đạt.**
- Preamble trước heading đầu tiên: lúc đầu trả lời sai ("không mất dữ liệu, chỉ lẫn vào Điều đầu") — thực tế bị bỏ hoàn toàn khỏi mọi chunk. Sau khi giải thích + xem code sửa, đã hiểu đúng.
