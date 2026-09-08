# 13 — Phát hiện hallucination: ghi chú phỏng vấn

Xem lý thuyết đầy đủ: [13-hallucination-detection.md](13-hallucination-detection.md)

## Q&A

**Q: Self-consistency là gì, cơ chế phát hiện hallucination ra sao?**
A: Hỏi cùng câu hỏi nhiều lần (temperature > 0), so sánh các câu trả lời. Model biết thật sẽ hội tụ về cùng nội dung; model bịa có xu hướng mâu thuẫn giữa các lần. Đo độ nhất quán làm tín hiệu cảnh báo hallucination.

**Q: Citation-based verification hoạt động thế nào?**
A: Bắt model trích dẫn nguồn cụ thể (điều luật, đoạn tài liệu) khi trả lời — tự nhiên có trong hệ thống RAG. Hệ thống verify độc lập lấy đúng chunk được trích, so sánh nội dung claim với nội dung thật — không khớp hoặc nguồn không tồn tại = hallucination.

**Q: Khi nào dùng self-consistency, khi nào dùng citation-based?**
A: Self-consistency dùng được cho mọi loại output kể cả không có RAG (gián tiếp, thống kê). Citation-based chỉ dùng được khi hệ thống có nguồn thật để trích dẫn (RAG, tool trả dữ liệu có cấu trúc) — trực tiếp, có căn cứ.

**Q: Giới hạn cốt lõi của self-consistency là gì?**
A: Chỉ bắt được hallucination do model "không chắc chắn" (đoán/sáng tác ngẫu nhiên). Không bắt được hallucination do "niềm tin sai nhưng nhất quán" — ví dụ model học 1 fact đã outdate hoặc sai lặp lại nhiều trong training data, tin vào nó với độ tin cậy cao như fact đúng, nên các lần trả lời vẫn nhất quán dù nội dung sai. Temperature chỉ tạo ngẫu nhiên ở diễn đạt bề mặt, không ảnh hưởng tới fact đã học chắc chắn.

**Q: Vì sao "có trích dẫn" không đồng nghĩa với "không hallucinate"?**
A: 2 lý do: (1) verification có thể chỉ check trích dẫn có tồn tại (existence check) mà không so sánh nội dung claim với text thật trong nguồn (content check) — model trích đúng nguồn nhưng bóp méo nội dung vẫn lọt qua; (2) bước so khớp nội dung tự nó có thể sai — nếu dùng LLM khác để so khớp thì thừa hưởng giới hạn của LLM-as-judge (bài 12), hoặc nếu retrieval upstream trả sai chunk (bug chunking) thì verification so với ground truth sai ngay từ đầu.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Coi self-consistency là "chứng minh đúng"**: sai — nó chỉ là tín hiệu xác suất về sự KHÔNG CHẮC CHẮN của model, không phải bằng chứng về tính đúng đắn. Model có thể nhất quán sai (niềm tin sai bám chắc trong weights).
- **Coi "có trích dẫn" = "không hallucinate"**: bẫy phổ biến nhất của citation-based — cần luôn phân biệt existence-check (nguồn có tồn tại) với content-check (nội dung claim có khớp nguồn thật) — 2 mức độ sâu khác nhau.
- **Quên rằng verification cũng có thể sai theo chuỗi (upstream)**: nếu retrieval trả sai chunk (lỗi ở tầng RAG bài 1-3), toàn bộ bước verify citation phía sau dựa trên nền sai — không phải chỉ bước cuối mới có rủi ro, mọi tầng trước đó đều ảnh hưởng.
- **Nghĩ đây là giải pháp toàn diện, dùng 1 kỹ thuật là đủ**: cả 2 kỹ thuật đều không loại bỏ hoàn toàn hallucination, cần kết hợp nhiều lớp (golden set + LLM-as-judge + 1 trong 2 kỹ thuật này).

## Bảng so sánh nhanh

| Khía cạnh | Self-consistency | Citation-based verification |
|---|---|---|
| Cơ chế | So sánh nhiều lần trả lời cùng 1 câu hỏi | So khớp claim với nguồn được trích dẫn |
| Cần RAG/nguồn không | Không | Có (bắt buộc) |
| Loại hallucination bắt được | Do model không chắc chắn (đoán ngẫu nhiên) | Do model bịa claim không khớp nguồn thật |
| Loại hallucination BỎ SÓT | Niềm tin sai nhưng nhất quán (fact outdate, bias huấn luyện) | Nguồn tồn tại nhưng verification chỉ check tồn tại, không check nội dung |
| Chi phí | Tốn N lần gọi model | Tốn bước verify độc lập (có thể là 1 LLM khác) |
