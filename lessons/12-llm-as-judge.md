# 12 — LLM-as-judge

**Ngày tạo:** 2026-09-08
**Trạng thái:** Đã học

## Lý thuyết

### 1. Nó là gì — cơ chế thật

Ở [[11-golden-set]], keyphrase match chỉ verify được fact cụ thể. Câu hỏi lớn hơn — "câu trả lời này có đúng ý, đầy đủ, không hallucinate, giọng điệu phù hợp không" — không check được bằng string match. LLM-as-judge dùng chính 1 LLM (thường mạnh hơn, hoặc khác model sinh câu trả lời) để **chấm điểm output của 1 LLM/agent khác**, dựa trên 1 **rubric** viết rõ trong prompt.

Cơ chế: (1) Judge nhận query, câu trả lời cần chấm, (tùy chọn) ground truth/rubric; (2) Judge trả về điểm + lý do chấm (để verify judge có đang chấm đúng logic); (3) Chạy hàng loạt qua golden set/log thật → tổng hợp % pass hoặc điểm trung bình.

Khác với golden set (rule cứng, không cần LLM): LLM-as-judge dùng sức mạnh LLM để đánh giá thứ rule cứng không check được (mạch lạc, đầy đủ ý, giọng điệu, hallucinate tinh vi).

### 2. Vì sao cần nó

- Chấm tay mọi case không scale — hàng nghìn câu hỏi/ngày không thể người đọc từng câu.
- Giải quyết đúng khoảng trống bài 11 để lại: keyphrase match không đánh giá được "chất lượng tổng thể".
- Judge chấm được tiêu chí tinh vi mà rule không code nổi: né tránh câu hỏi, mâu thuẫn nội bộ, đúng tông giọng brand.

### 3. Trade-off / khi nào cần cẩn thận

- **Judge cũng có thể sai** — phải tự eval độ tin cậy của judge trước khi tin: lấy tập nhỏ đã human-label, so khớp với judge, đo agreement rate.
- **Self-preference bias**: dùng cùng 1 model vừa sinh vừa chấm → model chấm cao hơn cho output *giống văn phong chính nó*, tạo "buồng vọng" (echo chamber) — nếu đổi model/prompt làm văn phong đổi, eval sẽ báo "giảm chất lượng" giả dù nội dung không tệ hơn. Nên dùng model khác (thường mạnh hơn) làm judge.
- **Giới hạn CẤU TRÚC (không phải chỉ lỗi thiết kế rubric)**: nếu judge không được cấp ground truth/nguồn để đối chiếu, nó **về nguyên tắc không có cách nào biết** 1 fact cụ thể (tên carrier, số liệu) đúng hay bịa — dù model tốt đến đâu, rubric chặt đến đâu, nó chỉ đánh giá được *độ trôi chảy/hợp lý về văn phong*, không đánh giá được *đúng sự thật* khi thiếu căn cứ kiểm chứng. Đây là lý do "phát hiện hallucination" (bài 13) tồn tại như 1 concept riêng — cách khắc phục đúng là **đổi input cho judge** (citation-based verification, self-consistency), không phải "judge giỏi hơn".
- Chi phí: mỗi lần eval tốn thêm gọi API — với eval set lớn, chi phí cộng dồn đáng kể.
- Không thay rule-based check khi rule đủ dùng ([[11-golden-set]]) — chỉ dùng LLM-as-judge cho phần rule không code nổi.

**Chỗ phân biệt junior/middle**: junior nghĩ "LLM-as-judge = hỏi LLM xem câu trả lời ổn không". Middle hiểu đây là hệ thống cần tự kiểm chứng (đo agreement với human label), biết phân biệt **giới hạn cấu trúc** (thiếu ground truth → không có cách nào phát hiện hallucination bằng judge đơn thuần) với **lỗi thiết kế rubric** (sửa được bằng rubric/model tốt hơn), và biết ranh giới rõ ràng: chỉ dùng khi rule-based không đủ.

Không có phép toán cốt lõi — không tạo file toán riêng.

## Ví dụ áp dụng project

Domain: coding assistant tự động review PR. Golden set chỉ check được "có đề cập file X không". LLM-as-judge với rubric 3 tiêu chí (chỉ đúng vấn đề thật, đề xuất fix cụ thể, giọng điệu xây dựng) — chấm hàng trăm PR tự động, lọc case điểm thấp để review tay.

## Bài thực hành

File: `practice/12-llm-as-judge.py` — mock judge (rule-based, không gọi API thật) **cố ý KHÔNG được cấp ground truth** (chỉ có query + answer), giống nhiều pipeline LLM-as-judge thật khi thiếu dữ liệu tham chiếu.

5 case, mỗi case có `human_score` (điểm người chấm, có đối chiếu ORDERS_DB thật) vs điểm judge mock tính theo rubric (độ dài, từ khóa vận chuyển, + 1 tín hiệu bias cố ý: cụm mở đầu "Chắc chắn rằng").

**Đã chạy thật thành công**: agreement 40% exact match, 60% trong sai số 1 điểm. 2 case lệch nặng (≥2 điểm) đúng như thiết kế:
- `hallucinated_fluent`: bịa hoàn toàn sai carrier/ETA (human=1) nhưng judge cho 5/5 vì viết trôi chảy, đủ từ khóa — minh chứng giới hạn cấu trúc (không ground truth → không phát hiện hallucination).
- `biased_style_mediocre`: nội dung nghèo nàn (human=2) nhưng judge cho 5/5 vì mở đầu bằng cụm quen thuộc — minh chứng self-preference/style bias.

## Checkpoint

**Câu 1:** Case `hallucinated_fluent` cho thấy judge không phát hiện được bịa đặt — đây là giới hạn thiết kế của riêng mock này hay giới hạn cấu trúc chung? Áp dụng thế nào để giảm rủi ro?
→ User trả lời đúng 1 phần (rubric chặt hơn/model tốt hơn giúp giảm lỗi) nhưng chưa chạm trọng tâm — mình bổ sung: đây là **giới hạn cấu trúc**, không phải lỗi rubric — judge không có cách nào biết fact đúng/sai nếu không được cấp ground truth/nguồn đối chiếu, bất kể model tốt tới đâu. Cách khắc phục đúng: đổi input cho judge (citation-based verification, self-consistency — bài 13), không phải "judge giỏi hơn".

**Câu 2:** Case `biased_style_mediocre` minh họa hiện tượng gì, rủi ro nếu dùng cùng 1 model vừa sinh vừa chấm?
→ User trả lời đúng: self-preference bias, judge đánh giá cao giọng văn giống bản thân. Mình bổ sung: tạo "buồng vọng" — đổi model/prompt sau này làm văn phong đổi sẽ khiến eval báo giảm chất lượng giả dù nội dung không tệ hơn; nên dùng model khác (mạnh hơn) làm judge.

**Câu 3:** Với agreement 40%/60%, có nên dùng judge này standalone trong production không?
→ User yêu cầu mình trả lời hộ: KHÔNG — vì 2/5 case lệch nặng đúng là 2 loại lỗi nguy hiểm nhất (hallucination lọt qua, bias làm nội dung tệ trông ổn), không phải lỗi ngẫu nhiên rải rác. Nên kết hợp: rule-based key-fact match ([[11-golden-set]]) làm lớp lọc đầu cho phần check được bằng rule; LLM-as-judge chỉ cho phần rule không code nổi; thêm citation-based check (bài 13) cho phần hallucination; định kỳ đo lại agreement với batch human-label mới.

Kết quả: câu 2 user tự trả lời đúng, câu 1 cần bổ sung ý cấu trúc quan trọng, câu 3 mình trả lời hộ — độ tin cậy hỗn hợp, ưu tiên hỏi lại câu 1 và 3 nếu ôn lại. User xác nhận hiểu → đánh dấu Đã học.
