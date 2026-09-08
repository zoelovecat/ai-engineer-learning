# 12 — LLM-as-judge: ghi chú phỏng vấn

Xem lý thuyết đầy đủ: [12-llm-as-judge.md](12-llm-as-judge.md)

## Q&A

**Q: LLM-as-judge là gì, khác gì với golden set key-fact match?**
A: Dùng 1 LLM (thường khác/mạnh hơn model sinh câu trả lời) để chấm điểm output theo rubric, thay cho rule cứng (string/keyphrase match ở golden set). Golden set: rule-based, deterministic, chỉ check được fact cụ thể. LLM-as-judge: đánh giá được tiêu chí tinh vi rule không code nổi (mạch lạc, giọng điệu, đầy đủ ý) nhưng bản thân judge cũng có thể sai.

**Q: Vì sao phải tự eval độ tin cậy của judge trước khi tin nó?**
A: Judge là 1 LLM, cũng hallucinate/thiên vị. Cần lấy 1 tập nhỏ đã human-label, so khớp với điểm judge, đo agreement rate (exact match, within-tolerance) — nếu lệch nhiều, đặc biệt lệch nhiều ở đúng loại lỗi nguy hiểm (hallucination, bias), không nên tin dùng standalone.

**Q: Self-preference bias là gì, khắc phục thế nào?**
A: Khi model vừa sinh câu trả lời vừa làm judge, nó có xu hướng chấm cao hơn cho output giống văn phong/phong cách chính nó, bất kể nội dung tốt hay không. Khắc phục: dùng model khác (thường mạnh hơn) làm judge, tách biệt khỏi model sinh output.

**Q: Vì sao LLM-as-judge (không có ground truth) khó phát hiện hallucination, và đây có phải lỗi sửa được bằng rubric tốt hơn không?**
A: Đây là giới hạn CẤU TRÚC, không phải lỗi rubric: nếu judge chỉ nhận query + answer, nó không có căn cứ nào để biết 1 fact cụ thể (tên riêng, số liệu) là thật hay bịa — nó chỉ đánh giá được độ trôi chảy/hợp lý về văn phong. Rubric chặt hơn hay model tốt hơn chỉ giảm lỗi phán đoán trong phạm vi thông tin nó có, không giải quyết việc nó thiếu thông tin để kiểm chứng ngay từ đầu. Cách đúng: đổi INPUT cho judge — citation-based verification hoặc self-consistency (bài 13).

**Q: Khi nào không nên dùng LLM-as-judge, dùng gì thay thế?**
A: Khi tiêu chí check được bằng rule/keyphrase (bài 11) — rule rẻ hơn, nhanh hơn, deterministic, không rủi ro bias. Chỉ dùng LLM-as-judge cho phần rule không code nổi.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Nhầm "giới hạn cấu trúc" với "lỗi rubric có thể sửa"**: đây là bẫy chính của bài này — junior thường nghĩ "judge sai thì viết rubric chặt hơn/dùng model tốt hơn là xong". Nhưng nếu vấn đề là *thiếu ground truth để đối chiếu*, không rubric nào cứu được — phải đổi kiến trúc pipeline (thêm citation, thêm bước verify riêng), không phải tinh chỉnh prompt.
- **Dùng cùng 1 model cho cả sinh và chấm mà không nhận ra bias**: nhiều pipeline thực tế mắc lỗi này vì tiện (chỉ cần 1 API key, 1 model) — hậu quả là echo chamber, đặc biệt nguy hiểm khi đổi model/prompt sau này làm eval báo sai lệch giả.
- **Tin tưởng con số agreement trung bình mà bỏ qua PHÂN BỐ lỗi**: agreement 60-70% nghe có vẻ ổn, nhưng nếu phần lệch tập trung đúng vào loại lỗi nguy hiểm nhất (hallucination, bias) thay vì rải rác ngẫu nhiên, con số trung bình đó đánh lừa — cần xem judge sai ở ĐÂU, không chỉ sai BAO NHIÊU.
- **Coi LLM-as-judge là giải pháp thay thế hoàn toàn cho rule-based check**: sai — 2 kỹ thuật bổ sung nhau, không cạnh tranh nhau; rule cho phần check được rẻ và chắc chắn, judge cho phần rule không làm được.

## Bảng so sánh nhanh

| Khía cạnh | Golden set (key-fact match) | LLM-as-judge |
|---|---|---|
| Cơ chế | Rule cứng, string/keyphrase match | 1 LLM chấm theo rubric |
| Đánh giá được | Fact cụ thể (số liệu, tên riêng) | Mạch lạc, đầy đủ ý, giọng điệu, tiêu chí tinh vi |
| Có tự sai không | Không (deterministic) | Có (judge cũng là LLM) |
| Rủi ro chính | Chọn keyphrase sai (quá chặt/lỏng) | Self-preference bias, không phát hiện hallucination nếu thiếu ground truth |
| Chi phí | Gần như 0 | Tốn gọi API mỗi lần eval |
| Khi nào dùng | Tiêu chí check được bằng rule | Tiêu chí rule không code nổi |
