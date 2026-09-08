# 11 — Eval dataset / golden set: ghi chú phỏng vấn

Xem lý thuyết đầy đủ: [11-golden-set.md](11-golden-set.md)

## Q&A

**Q: Golden set là gì, vì sao cần cho hệ thống LLM?**
A: Tập cố định gồm input + expected output (hoặc rubric) dùng để test toàn bộ pipeline mỗi khi đổi prompt/model/logic. Đóng vai trò "unit test" cho hệ thống non-deterministic — không khẳng định luôn đúng, chỉ khẳng định không tệ đi so với trước (regression detection).

**Q: Vì sao exact string match thường không dùng được để eval output LLM?**
A: LLM/agent diễn đạt câu trả lời khác nhau mỗi lần dù cùng đúng ý — exact match sẽ báo FAIL oan cho câu trả lời đúng nhưng khác chữ. Cần match theo key fact/keyphrase bắt buộc, hoặc để 1 model khác chấm theo rubric (LLM-as-judge).

**Q: Chọn keyphrase quá chặt hoặc quá lỏng gây hậu quả gì?**
A: Quá chặt → false fail (báo sai dù hệ thống đúng, gây alert fatigue, dần bị bỏ qua). Quá lỏng → false pass (báo đúng dù hệ thống sai/hallucinate, tạo an toàn giả). Nên chỉ bắt buộc key fact không có cách diễn đạt khác (số liệu, tên riêng), phần còn lại cần LLM-as-judge.

**Q: Vì sao bug không crash (silent bug) nguy hiểm hơn bug gây crash?**
A: Bug crash lộ ra ngay lập tức, ai cũng thấy. Bug im lặng vẫn chạy bình thường, chỉ sai 1 phần kết quả — không ai phát hiện nếu không có cơ chế tự động re-verify toàn bộ hành vi cũ. Review thủ công thường chỉ nhìn đúng chỗ vừa sửa, không tự nhiên kiểm tra lại các luồng khác dùng chung dữ liệu/logic đó.

**Q: Khi nào 1 golden set FAIL không phải là regression thật?**
A: Hai trường hợp chính: (1) hành vi mong muốn đã thay đổi theo chủ đích (đổi chính sách) mà quên cập nhật expected; (2) data drift — dữ liệu nền (SLA, giá, trạng thái...) thay đổi hợp lệ, không phải do code/logic đổi. Cần phân biệt "code có đổi không" trước khi kết luận regression thật.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Nhầm golden set = viết vài test case rồi để mãi**: bẫy phổ biến — golden set cần bảo trì, bổ sung dần từ case lỗi thật, và review định kỳ để tránh trở thành "cái neo" trói hành vi cũ hoặc dữ liệu cũ.
- **Không phân biệt được 2 loại "cái neo sai"**: policy/hành vi mong muốn đổi vs. data drift — đây là câu hỏi hay bị hỏi xoáy vì junior thường chỉ nghĩ tới 1 loại (policy đổi) mà quên data nền cũng có thể trôi dạt, khiến chẩn đoán sai "có regression" khi thực ra chỉ là dữ liệu cập nhật hợp lệ.
- **Tin rằng review thủ công kỹ hơn là đủ thay cho golden set/CI**: câu trả lời đúng là quy mô — con người review giỏi mấy cũng chỉ nhìn đúng phần vừa đổi, không có động lực tự nhiên để verify lại toàn bộ hệ thống mỗi lần; đây chính là lý do CI + golden set tồn tại như 1 cơ chế *bắt buộc*, không phụ thuộc ý thức cá nhân.
- **Coi mọi FAIL trong golden set là bug thật**: cần luôn hỏi "code/logic thay đổi hay chỉ data thay đổi" trước khi kết luận, tránh tốn công fix nhầm chỗ hoặc bỏ qua nhầm 1 regression thật.

## Bảng so sánh nhanh: cách so khớp trong golden set

| Cách so khớp | Khi nào dùng | Rủi ro |
|---|---|---|
| Exact match | Output hoàn toàn deterministic (rule-based, không LLM) | Hầu như không dùng được với LLM thật |
| Key-fact/keyphrase match | Cần fact số liệu/tên riêng bắt buộc chính xác | Chọn keyphrase sai → false pass/false fail |
| LLM-as-judge (rubric) | Đánh giá "đúng ý, đầy đủ, không hallucinate" | Tốn chi phí gọi API, cần tự eval độ tin cậy của judge |
