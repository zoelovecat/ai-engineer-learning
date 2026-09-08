# 13 — Phát hiện hallucination (self-consistency, citation-based)

**Ngày tạo:** 2026-09-08
**Trạng thái:** Đã học

## Lý thuyết

### 1. Nó là gì — cơ chế thật

2 kỹ thuật độc lập, giải quyết theo 2 hướng khác nhau — đây chính là câu trả lời cho lỗ hổng [[12-llm-as-judge]] để lại (judge không có ground truth thì không phát hiện được bịa đặt).

**Self-consistency**: hỏi cùng 1 câu hỏi nhiều lần (thường `temperature > 0`), so sánh các câu trả lời với nhau. Nếu model thực sự biết câu trả lời, các lần trả lời hội tụ về cùng nội dung dù diễn đạt khác. Nếu model đang bịa, các lần trả lời có xu hướng mâu thuẫn nhau. Đo độ nhất quán → nhất quán thấp = tín hiệu cảnh báo hallucination cao.

**Citation-based verification**: bắt model, khi trả lời, phải trích dẫn nguồn cụ thể (ví dụ "theo Điều 36") — output tự nhiên của hệ thống RAG ([[01-embedding-models]], [[02-chunking-strategy]]). Hệ thống kiểm chứng độc lập lấy đúng chunk được trích dẫn, so sánh nội dung claim với nội dung thật trong chunk — claim không khớp hoặc chunk không tồn tại = hallucination bị bắt trực tiếp.

Khác biệt cốt lõi: self-consistency là kỹ thuật **gián tiếp, thống kê** (dùng được cho mọi loại LLM output, kể cả không RAG). Citation-based là kỹ thuật **trực tiếp, có căn cứ** (chỉ dùng được khi hệ thống có nguồn để trích dẫn).

### 2. Vì sao cần nó

- Giải quyết đúng lỗ hổng bài 12: LLM-as-judge không có ground truth thì không phát hiện được hallucination bằng cách "hỏi 1 lần rồi chấm điểm". 2 kỹ thuật này tự tạo tín hiệu kiểm chứng (nhiều lần trả lời, hoặc nguồn trích dẫn) thay vì cần ground truth có sẵn.
- Hallucination là rủi ro production nghiêm trọng nhất của LLM — tutorial cơ bản bỏ qua vì demo ít khi lộ ra, nhưng ở domain pháp lý/y tế/tài chính là rủi ro compliance thật.

### 3. Trade-off / khi nào cần cẩn thận

- Self-consistency tốn tiền + latency (gọi model N lần/câu hỏi) — chỉ nên dùng cho case rủi ro cao, không phải mọi request.
- **Self-consistency có giới hạn quan trọng**: chỉ bắt được hallucination xuất phát từ *sự không chắc chắn* (model đang đoán/sáng tác ngẫu nhiên) — KHÔNG bắt được hallucination xuất phát từ *niềm tin sai nhưng nhất quán* (model tự tin nhưng sai). Ví dụ cụ thể: model học 1 fact đã outdate hoặc 1 thông tin sai lặp lại nhiều trong training data — model "tin" vào nó với độ tin cậy cao y hệt fact đúng, nên không có gì dao động giữa các lần hỏi lại; temperature/sampling chỉ tạo ngẫu nhiên ở cách diễn đạt bề mặt, không ảnh hưởng tới fact model đã học chắc chắn.
- Citation-based cần hệ thống có nguồn thật để trích dẫn — không dùng được cho câu hỏi mở không có RAG/tool trả nguồn.
- **Citation-based verification không phải "có trích dẫn là đủ"** — có thể thất bại theo 2 cách:
  1. Verification chỉ check "trích dẫn có tồn tại" (existence check) mà không so sánh nội dung claim với text thật trong chunk (content check) — model trích đúng nguồn thật nhưng bóp méo nội dung của nó sẽ lọt qua.
  2. Bản thân bước "so khớp nội dung" cũng có thể sai — nếu dùng LLM khác để so khớp, nó thừa hưởng đúng giới hạn của LLM-as-judge (bài 12); nếu bước retrieval upstream trả sai chunk (bug chunking/off-by-one như từng gặp ở bài 7), verification so với "ground truth" sai ngay từ đầu, cho pass giả.
- Cả 2 kỹ thuật đều không loại bỏ hoàn toàn hallucination — cần kết hợp nhiều lớp phòng thủ (golden set + LLM-as-judge + 1 trong 2 kỹ thuật này), không có kỹ thuật nào đủ một mình.

**Chỗ phân biệt junior/middle**: junior nghĩ "hallucination detection = hỏi LLM xem nó có bịa không" (giới hạn cấu trúc đã học ở bài 12). Middle hiểu phải tạo **tín hiệu kiểm chứng độc lập với chính câu trả lời đang xét** (qua tính nhất quán thống kê hoặc đối chiếu nguồn cụ thể), biết chọn đúng kỹ thuật theo việc hệ thống có nguồn để trích dẫn hay không, và biết rõ giới hạn của từng kỹ thuật (self-consistency không bắt được niềm tin sai nhất quán; citation-based cần verification đủ sâu, không chỉ check tồn tại).

Không có phép toán cốt lõi bắt buộc — không tạo file toán riêng.

## Ví dụ áp dụng project

Buổi này đi thẳng vào checkpoint theo yêu cầu của user (không làm ví dụ project cụ thể/bài thực hành code lần này) — lý thuyết đã đủ sâu qua phần trade-off ở trên với ví dụ cụ thể minh họa (chatbot chính sách công ty không có RAG; hệ thống RAG luật lao động bài 1-3 cho citation-based).

## Bài thực hành

Không có — user chọn bỏ qua phần ví dụ/thực hành, đi thẳng checkpoint lý thuyết. Nếu ôn lại và muốn thực hành, có thể triển khai:
- Self-consistency: gọi mock LLM N lần với biến thể ngẫu nhiên nhỏ, đo tỷ lệ đồng thuận.
- Citation-based: tái dùng hybrid search bài 3 — model trả lời kèm số Điều, viết hàm verify so khớp claim với text thật trong chunk được trích.

## Checkpoint

**Câu 1:** Chatbot nội bộ không dùng RAG (trả lời từ kiến thức train sẵn) — chọn self-consistency hay citation-based, vì sao kỹ thuật còn lại không áp dụng được?
→ User trả lời đúng: self-consistency, vì citation-based cần tài liệu để trích dẫn mà hệ thống này không có.

**Câu 2:** Cho 1 tình huống cụ thể self-consistency thất bại (model bịa nhưng vẫn nhất quán).
→ User trả lời đúng và tinh: data/fact đã outdate nhưng model học tin chắc vào nó — bịa nhất quán vì đó là niềm tin có độ tin cậy cao, không phải đoán mò ngẫu nhiên. Mình bổ sung: temperature/sampling chỉ tạo ngẫu nhiên ở diễn đạt bề mặt, không ảnh hưởng fact model đã học chắc chắn — đây là giới hạn cốt lõi: self-consistency chỉ bắt hallucination do "không chắc chắn", không bắt hallucination do "niềm tin sai nhưng nhất quán".

**Câu 3:** Hệ thống RAG luật lao động với citation-based verification — 2 cách cụ thể verification có thể thất bại dù model đã trích dẫn.
→ User không biết, mình trả lời hộ: (1) verification chỉ check trích dẫn tồn tại, không check nội dung claim khớp text thật trong chunk — model trích đúng nguồn nhưng bóp méo nội dung sẽ lọt; (2) bước so khớp nội dung tự nó có thể sai (nếu dùng LLM khác, thừa hưởng giới hạn bài 12; nếu retrieval upstream trả sai chunk do bug, verification so với ground truth sai ngay từ đầu).

Kết quả: câu 1-2 user tự trả lời đúng (câu 2 khá tinh, chỉ cần bổ sung nhỏ), câu 3 mình trả lời hộ — độ tin cậy tổng thể khá, ưu tiên hỏi lại câu 3 nếu ôn lại. User xác nhận đánh dấu Đã học.
