# 14 — Kiến trúc bộ nhớ agent (short/episodic/long-term)

**Ngày tạo:** 2026-09-08
**Trạng thái:** Đã học

## Lý thuyết

### 1. Nó là gì — cơ chế thật

Agent ReAct bài 7 chỉ có 1 loại "bộ nhớ": `state.history` — toàn bộ Thought/Action/Observation của **lượt hội thoại hiện tại**, nằm gọn trong context window. Khi phiên kết thúc, mọi thứ biến mất. Kiến trúc bộ nhớ agent phân biệt 3 tầng, mỗi tầng giải quyết 1 giới hạn khác nhau:

- **Short-term memory (working memory)**: chính là context window — input/output của 1 phiên đang diễn ra. Giới hạn cứng: kích thước context window ([[16-transformer-concepts]] — lost-in-the-middle).
- **Episodic memory**: log các phiên đã kết thúc trong quá khứ, **scoped theo 1 danh tính/case cụ thể** (key theo user_id/case_id) — "lần trước user X hỏi gì, kết quả ra sao". Truy xuất lại khi *đúng người/case đó* quay lại.
- **Long-term memory**: kho kiến thức **tổng hợp, khái quát hóa, KHÔNG scoped theo danh tính cụ thể** — ví dụ agent tự rút ra "timeout service X thường do connection pool cạn kiệt" sau khi thấy pattern lặp lại ở nhiều case/user khác nhau. Đây là kiến thức generalize được xuyên user, dùng cho mọi phiên sau.

**Ranh giới cốt lõi giữa episodic và long-term**: episodic scoped theo danh tính (chỉ "của riêng" 1 user/case), long-term không scoped theo danh tính (kiến thức chung của hệ thống) — đây là khác biệt về *bản chất truy xuất*, không chỉ khác "lưu bao lâu".

Cơ chế vận hành: mỗi query mới, ngoài context phiên hiện tại (short-term), agent **truy vấn thêm** vào episodic/long-term memory (giống 1 bước retrieval RAG bài 1-3) để lấy thông tin liên quan từ quá khứ, rồi đưa cả 2 nguồn vào context gửi model.

### 2. Vì sao cần nó

- Chỉ short-term memory → agent "mất trí nhớ" hoàn toàn giữa các phiên.
- Episodic giải quyết **continuity** cho 1 user/case cụ thể qua nhiều phiên.
- Long-term giải quyết **học tích lũy, generalize xuyên user** — khác episodic ở chỗ tổng hợp qua nhiều case, không chỉ nhớ nguyên văn 1 lần tương tác.
- Phần "khó" thật của agent production: tutorial cơ bản chỉ demo agent 1 phiên (giống bài 7) — không đụng vấn đề "agent chạy hàng tháng, hàng nghìn user, làm sao không phình context vô hạn mà vẫn nhớ đúng thứ cần nhớ".

### 3. Trade-off / khi nào cần cẩn thận

- Agent 1 phiên, dùng xong là hết → chỉ cần short-term, thêm episodic/long-term là dư thừa.
- Episodic/long-term = thêm 1 bước retrieval → thêm latency, chi phí lưu trữ, và **rủi ro retrieval sai**: memory bề ngoài giống nhưng không liên quan bị kéo vào context, agent bị "neo" (anchor) vào lời giải cũ sai ngữ cảnh, hoặc context bị loãng (1 dạng lost-in-the-middle mới, xem [[16-transformer-concepts]]).
- **Long-term memory dễ "học sai thành niềm tin cố định"**: agent tự tổng hợp kết luận từ vài case không đại diện (trùng hợp, không phải quy luật) rồi lưu thành niềm tin áp dụng cho mọi user sau — rủi ro tương tự hallucination tích lũy ([[13-hallucination-detection]]) nhưng **khó phát hiện hơn**: nó là trạng thái ẩn tồn tại xuyên nhiều lượt gọi, không lộ ngay trong 1 câu trả lời đơn lẻ.
- **Golden set ([[11-golden-set]]) / LLM-as-judge ([[12-llm-as-judge]]) không tự động bắt được lỗi memory sai** — 2 kỹ thuật đó test input/output của 1 lượt gọi riêng lẻ, không kiểm tra chính nội dung memory store; chỉ phát hiện gián tiếp nếu đúng case trong golden set chạm vùng bị niềm tin sai ảnh hưởng. Cần thêm 1 lớp riêng: audit định kỳ nội dung memory store, tách biệt eval thông thường.
- Cần cơ chế cập nhật/xóa long-term memory khi thông tin cũ sai/outdate (liên hệ "cái neo sai"/data drift đã học ở [[11-golden-set]], nhưng ở đây là memory của agent).

**Chỗ phân biệt junior/middle**: junior nghĩ "thêm bộ nhớ" = "lưu hết lịch sử chat vào 1 file/DB". Middle phân biệt rõ 3 tầng có mục đích khác nhau, biết episodic scoped theo danh tính còn long-term không scoped theo danh tính (khác biệt về bản chất truy xuất, không chỉ thời gian lưu), và biết long-term memory có rủi ro "học sai thành niềm tin cố định" y hệt hallucination nhưng khó phát hiện hơn vì ẩn trong memory store, không lộ ngay trong 1 câu trả lời — cần audit riêng, không phải chỉ dựa vào eval thông thường.

Không có phép toán cốt lõi riêng (kiến trúc hệ thống, retrieval bên trong dùng lại cơ chế bài 1-3) — không tạo file toán riêng.

## Ví dụ áp dụng project

Buổi này đi thẳng checkpoint theo yêu cầu user (không viết code thực hành). Ví dụ dùng trong checkpoint: coding assistant nội bộ hỗ trợ debug lỗi production — dev A hỏi lỗi timeout service X, agent trả lời dựa trên case cũ; dev B (người khác) hỏi y hệt câu đó — minh họa ranh giới episodic (scoped theo dev A) vs long-term (generalize, giúp được cả dev B).

## Bài thực hành

Không có — user chọn đi thẳng checkpoint. Nếu ôn lại và muốn thực hành, có thể triển khai: thêm episodic memory (JSON log theo user_id) + long-term memory (tổng hợp pattern qua nhiều case) vào agent order-tracking bài 7, thử case retrieval sai (nhiễu context) để quan sát trực tiếp.

## Checkpoint

**Câu 1:** Dev A hỏi lỗi timeout service X, agent trả lời dựa trên case cũ. Dev B (người khác) hỏi y hệt — agent nên dùng episodic hay long-term memory để trả lời tốt hơn cho dev B, vì sao 2 tầng cho kết quả khác nhau về bản chất?
→ User trả lời **episodic** — SAI, cần đính chính: phải là **long-term memory**. Lý do: episodic scoped theo danh tính (log của riêng dev A, case của dev A), không tự động surface cho dev B (người khác). Long-term là kiến thức đã tổng hợp/khái quát hóa, không gắn với 1 người cụ thể — dev B hưởng lợi từ kinh nghiệm dev A chính vì nó đã được "nâng cấp" từ chuyện riêng thành kiến thức chung. Đây là **bẫy nhầm lẫn chính** của bài này — user hiểu đúng bản chất "long-term = rút ra sau nhiều phiên" (phần mô tả chung đúng) nhưng áp dụng sai vào tình huống cụ thể (chọn episodic thay vì long-term).

**Câu 2:** Ví dụ cụ thể long-term memory "học sai thành niềm tin cố định", ảnh hưởng bao lâu trước khi phát hiện, vì sao golden set/LLM-as-judge không tự động bắt được.
→ User yêu cầu mình trả lời hộ: agent gặp 2-3 case liên tiếp trùng hợp đều do 1 service, tự tổng hợp thành niềm tin sai, ảnh hưởng âm thầm hàng tuần-hàng tháng cho tới khi 1 case khác nguyên nhân bị chẩn đoán sai nhiều lần đủ để phát hiện. Golden set/LLM-as-judge không bắt được vì chúng test input/output 1 lượt gọi riêng lẻ, không kiểm tra nội dung memory store (trạng thái ẩn xuyên nhiều lượt gọi) — cần audit riêng.

**Câu 3:** Trường hợp cụ thể thêm episodic/long-term memory làm agent tệ đi — cơ chế vì sao.
→ User trả lời đúng hướng: mỗi phiên hỏi chủ đề khác nhau, ép dùng memory dẫn tới nhiễu data. Mình bổ sung cơ chế cụ thể: retrieval kéo nhầm memory bề ngoài giống nhưng không liên quan → agent bị "neo" vào lời giải cũ sai ngữ cảnh, hoặc context bị loãng (lost-in-the-middle).

Kết quả: câu 1 SAI (đã đính chính rõ, đây là bẫy nhầm lẫn chính cần ghi vào file phỏng vấn), câu 2 mình trả lời hộ, câu 3 đúng hướng cần bổ sung cơ chế — độ tin cậy tổng thể thấp hơn các bài trước, ưu tiên hỏi lại câu 1 (ranh giới episodic vs long-term) nếu ôn lại. User xác nhận đánh dấu Đã học.
