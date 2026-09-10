# 24. Red-teaming

**Ngày học:** 2026-09-10
**Trạng thái:** Đã học

Xem thêm: [Phỏng vấn](24-red-teaming-interview.md)

## 1. Lý thuyết

Red-teaming là quá trình chủ động, có hệ thống thử tấn công chính sản phẩm AI của mình (đóng vai kẻ tấn công) trước khi launch, để tìm lỗ hổng và vá trước khi có hậu quả thật.

**Khác biệt cốt lõi so với eval/golden set (bài 11):** golden set test "model có làm ĐÚNG chức năng như kỳ vọng không" (input/expected output biết trước, happy path + edge case đã lường trước). Red-teaming test "có ai đó CỐ TÌNH phá được hệ thống theo cách chưa lường trước không" — mang tính khám phá/đối kháng, không có expected output cố định, đánh giá "có bị exploit hay không".

**2 cách thực hiện:**
- Thủ công: chuyên gia tự nghĩ kịch bản — jailbreak prompt, roleplay bypass safety, "crescendo attack" (chia nhỏ yêu cầu độc hại thành nhiều bước vô hại rồi ghép lại qua nhiều lượt hội thoại).
- Tự động hóa: LLM khác đóng vai attacker sinh hàng loạt biến thể, LLM-as-judge (bài 12) chấm response có bị exploit hay không — scale hơn nhưng có thể bỏ sót kiểu tấn công sáng tạo mà chỉ con người nghĩ ra.

Phạm vi cần bao phủ: prompt injection (bài 23), jailbreak, data exfiltration qua agent có tool, bias/toxicity, hallucination gây hại thật.

**Vì sao cần hiểu sâu:** hệ thống chỉ test happy path (bài 11) không biết được có bị bẻ khóa bởi jailbreak phổ biến hay không — khoảng trống giữa "đúng chức năng" và "an toàn khi bị cố tình phá". Bắt buộc trước khi launch, đặc biệt khi liên quan compliance/pháp lý.

**Trade-off:**
- Không có "hoàn thành 100%" — không gian tấn công gần vô hạn, chỉ giảm rủi ro biết trước, không đảm bảo an toàn tuyệt đối (liên hệ bài 23).
- Cần lặp lại định kỳ, không phải làm 1 lần trước launch — mỗi khi đổi prompt/model (bài 22) phải re-run.
- Tốn thời gian/nguồn lực — có thể thuê ngoài hoặc dùng framework có sẵn (Microsoft PyRIT).
- Không thay thế được lớp phòng thủ kỹ thuật (bài 23) — red-teaming là để TÌM lỗ hổng, không phải bản thân là giải pháp phòng thủ.

## 2. Ví dụ áp dụng

Hệ HR agent (bài 15) sắp launch, có MCP tool `search_policy_documents` + `send_email` (bài 9, 23).

3 loại tấn công cụ thể cần thử:
- Indirect injection qua tài liệu chính sách (kịch bản bài 23) → nên làm cả thủ công (nghĩ kịch bản tinh vi) lẫn tự động hóa (regression test mỗi lần đổi prompt/model).
- Crescendo attack nhiều lượt (dẫn dắt dần từ câu hỏi vô hại tới yêu cầu rò rỉ lương/dữ liệu) → nên làm thủ công, cần tư duy dẫn dắt hội thoại tinh vi khó tự động sinh tự nhiên.
- Roleplay jailbreak ("đóng vai admin, bỏ qua giới hạn") → nên tự động hóa, pattern phổ biến đã biết, chạy hàng loạt biến thể qua adversarial LLM + LLM-as-judge.

Tiêu chí "fail" cụ thể với `send_email`: coi là fail nếu agent THỰC SỰ gọi tool với recipient ngoài danh sách cho phép, hoặc nội dung chứa dữ liệu nhạy cảm mà người yêu cầu không có quyền xem — tính fail ngay từ lúc agent quyết định gọi tool sai tham số, không cần đợi email gửi thành công.

## 3. Bài thực hành

Thiết kế (không code): liệt kê loại tấn công cụ thể cho hệ HR agent, chọn thủ công/tự động cho từng loại, và tiêu chí "fail" cụ thể với tool `send_email`.

## 4. Checkpoint

User yêu cầu assistant trả lời hộ toàn bộ (không tự làm trước) — nội dung xem chi tiết ở mục 2. Độ tin cậy thấp, ưu tiên hỏi lại toàn bộ 3 câu nếu ôn lại: (1) liệt kê tấn công cụ thể — không chỉ nói chung chung; (2) phân biệt khi nào nên thủ công vs tự động hóa; (3) tiêu chí "fail" phải gắn với hành động tool call thực sự, không chỉ dựa vào việc model "có vẻ" bị lừa.
