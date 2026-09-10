# Phỏng vấn — Red-teaming

Lesson chính: [24-red-teaming.md](24-red-teaming.md)

## Q&A

**Q: Red-teaming là gì, khác gì với eval/golden set (bài 11)?**
A: Red-teaming là chủ động thử tấn công chính hệ thống của mình trước khi launch để tìm lỗ hổng. Golden set test "có làm đúng chức năng kỳ vọng không" (expected output biết trước); red-teaming test "có ai cố tình phá được không" (đối kháng, không có expected output cố định, đánh giá bị exploit hay không).

**Q: Kể 1 vài kỹ thuật tấn công cụ thể dùng trong red-teaming?**
A: Jailbreak prompt (bypass safety alignment), roleplay để bypass giới hạn ("đóng vai admin có toàn quyền"), crescendo attack (chia nhỏ yêu cầu độc hại thành nhiều bước vô hại qua nhiều lượt hội thoại rồi ghép lại), indirect injection qua dữ liệu agent đọc (bài 23).

**Q: Thủ công và tự động hóa red-teaming khác nhau thế nào, khi nào dùng loại nào?**
A: Thủ công: chuyên gia tự nghĩ kịch bản, sáng tạo hơn, phát hiện tấn công tinh vi mới nhưng chậm, tốn nhân lực — hợp cho tìm lỗ hổng lần đầu/launch lớn. Tự động: LLM đóng vai attacker sinh hàng loạt biến thể + LLM-as-judge chấm — scale nhanh nhưng giới hạn trong pattern đã biết — hợp cho regression test định kỳ sau mỗi lần đổi prompt/model.

**Q: Vì sao red-teaming không bao giờ "hoàn thành 100%"?**
A: Không gian kiểu tấn công gần như vô hạn, chỉ giảm rủi ro biết trước chứ không đảm bảo an toàn tuyệt đối — cùng bản chất với việc không có phòng thủ tuyệt đối trước prompt injection (bài 23). Cần lặp lại định kỳ, không phải làm 1 lần rồi thôi.

**Q: Tiêu chí đánh giá 1 lần thử tấn công là "fail" nên dựa vào đâu?**
A: Dựa vào HÀNH ĐỘNG THỰC SỰ xảy ra (agent có gọi tool nguy hiểm với tham số sai hay không — vd gửi email cho recipient ngoài danh sách cho phép, hoặc chứa dữ liệu nhạy cảm vượt quyền người hỏi), không chỉ dựa vào việc câu trả lời text "nghe có vẻ" đã bị lừa hay chưa.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- Nhầm red-teaming và eval/golden set là cùng 1 việc ("cũng là test mà") — khác nhau ở bản chất: 1 bên đo correctness theo kỳ vọng đã biết, 1 bên đo khả năng chống chịu trước tấn công chưa lường trước.
- Liệt kê tấn công quá chung chung ("thử jailbreak") mà không nêu được kịch bản cụ thể (chèn gì, ở đâu, dẫn tới hành động nào) — phỏng vấn thường yêu cầu ví dụ cụ thể để phân biệt hiểu thật với thuộc lòng khái niệm.
- Nghĩ tự động hóa red-teaming (adversarial LLM) là đủ, bỏ qua red-team thủ công — tự động hóa giỏi ở việc lặp lại pattern đã biết, nhưng dễ bỏ sót kiểu tấn công sáng tạo mới mà chỉ con người mới nghĩ ra.
- Đặt tiêu chí "fail" dựa trên cảm nhận văn bản trả lời (model "có vẻ" bị lừa) thay vì dựa trên hành động/tool call thực sự xảy ra với tham số nguy hiểm — dễ đánh giá sai mức độ nghiêm trọng thật.
- Coi red-teaming là 1 lần làm trước launch là xong — quên rằng mỗi lần đổi prompt/model (bài 22) cần re-run, vì thay đổi nhỏ có thể mở lại lỗ hổng đã vá.

## Bảng so sánh nhanh

| | Thủ công (chuyên gia) | Tự động hóa (adversarial LLM + judge) |
|---|---|---|
| Độ sáng tạo | Cao — phát hiện kiểu tấn công mới, tinh vi (crescendo, social engineering) | Thấp hơn — giới hạn trong pattern đã biết/model tự sinh |
| Scale | Chậm, tốn nhân lực | Nhanh, chạy hàng loạt biến thể |
| Chi phí | Cao (chuyên gia/thuê ngoài) | Thấp hơn sau khi dựng pipeline |
| Phù hợp khi | Trước launch lớn, cần tìm lỗ hổng tinh vi | Regression test định kỳ sau mỗi lần đổi prompt/model |
