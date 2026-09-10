# Phỏng vấn — Prompt injection (tấn công + phòng thủ)

Lesson chính: [23-prompt-injection.md](23-prompt-injection.md)

## Q&A

**Q: Prompt injection là gì, vì sao LLM dễ bị tấn công kiểu này?**
A: Khai thác việc LLM không có ranh giới cứng giữa "instruction" (system prompt) và "data" (user input, tài liệu, kết quả tool) — cả 2 chỉ là chuỗi token nằm chung context window, không có cấu trúc phần cứng nào ngăn model nghe theo 1 câu lệnh giả mạo nằm lẫn trong data.

**Q: Direct injection khác Indirect injection thế nào? Loại nào nguy hiểm hơn, vì sao?**
A: Direct: user tự nhập để bypass system prompt, dễ phát hiện qua log. Indirect: nội dung độc hại nằm trong dữ liệu bên thứ 3 mà agent tự động đọc (web, RAG, email, kết quả tool) — nguy hiểm hơn vì user thật không biết, agent "tự ăn phải" khi làm đúng chức năng, khó phát hiện hơn vì phải giám sát nội dung agent đọc chứ không chỉ input user.

**Q: Vì sao injection nguy hiểm hơn hẳn khi agent có quyền gọi tool?**
A: Không dừng ở "trả lời sai" mà biến thành hành động thực có side-effect — rò rỉ dữ liệu, gửi email giả mạo, xóa dữ liệu, thanh toán sai — mức độ nguy hiểm tỷ lệ thuận với quyền hạn (privilege) agent đang nắm giữ.

**Q: Kể các lớp phòng thủ và lớp nào hiệu quả nhất khi model đã bị injection "qua mặt"?**
A: Input sanitization, tách vai trò trong prompt, output validation/guardrail, least privilege, giám sát/observability. Khi model đã bị lừa thành công, chỉ có **output validation** (chặn hành động trước khi thực thi) và **least privilege** (giới hạn phạm vi tool) còn hiệu quả — vì chúng chặn ở tầng HÀNH ĐỘNG THỰC THI, không phụ thuộc việc model có hiểu đúng hay không.

**Q: Có thể làm cho hệ thống "an toàn tuyệt đối" trước prompt injection không?**
A: Không — đây là hạn chế kiến trúc của LLM hiện tại (không có ranh giới cứng instruction/data ở tầng model), chưa có giải pháp giải quyết triệt để. Mọi lớp phòng thủ chỉ giảm xác suất/tác hại (defense in depth), không loại bỏ hoàn toàn rủi ro.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Bẫy chính (từ checkpoint thật):** khi được yêu cầu thiết kế 1 kịch bản injection cụ thể, dễ trả lời chung chung ("chèn vào agent trước khi gọi tool") mà không chỉ rõ được: chèn vào ĐÂU (loại dữ liệu cụ thể — tài liệu RAG, trang web, email), NỘI DUNG giả dạng gì, và MỤC TIÊU cuối là dụ agent gọi tool nguy hiểm nào. Trả lời đúng phải cụ thể tới mức đó mới cho thấy hiểu injection thật xảy ra qua đường nào.
- **Bẫy thứ 2:** không phân biệt được lớp phòng thủ nào "ngăn model hiểu sai" (sanitization, tách vai trò — không đáng tin 100%, dễ bypass) với lớp nào "chặn ở tầng hành động dù model đã bị lừa" (output validation, least privilege — vẫn hiệu quả kể cả khi injection đã thành công về mặt hiểu). Câu hỏi phỏng vấn dạng "lớp nào quan trọng nhất" luôn cần chỉ ra đúng phân biệt này.
- Trả lời "không an toàn tuyệt đối" nhưng chỉ vì "định nghĩa nói vậy" — thiếu lý do gốc rễ (không có ranh giới kiến trúc cứng giữa instruction/data trong LLM hiện tại).
- Nhầm system prompt là 1 lớp bảo mật đáng tin cậy — thực ra system prompt cũng chỉ là text trong context, không có cơ chế enforcement cứng, dễ bị injection ghi đè nếu không có guardrail ở tầng hành động.

## Bảng so sánh nhanh

| | Direct injection | Indirect injection |
|---|---|---|
| Nguồn | User tự nhập trực tiếp | Dữ liệu bên thứ 3 agent tự đọc (web, tài liệu, email, tool result) |
| Người dùng thật có biết không | Có (chính họ làm) | Không — agent "tự ăn phải" khi làm đúng việc |
| Dễ phát hiện qua log user không | Dễ hơn | Khó hơn — cần giám sát nội dung agent đọc, không chỉ input user |
| Ví dụ | User gõ "ignore your instructions..." | Tài liệu RAG bị chèn sẵn câu lệnh độc hại, agent đọc qua tool `search_policy_documents` |
