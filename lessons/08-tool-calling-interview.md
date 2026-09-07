# Interview notes: Tool-calling ở tầng model (structured output/JSON schema)

Lesson chính: [08-tool-calling.md](08-tool-calling.md)

## Q&A có thể gặp

**Q: Model "gọi tool" bằng cơ chế gì, có phải nó thực sự chạy code không?**
A: Không. Model chỉ sinh ra 1 object có cấu trúc (tên tool + tham số) dựa trên tool schema được cấp trong request — vẫn là next-token prediction, chỉ được hướng để sinh đúng định dạng JSON. Client (code của bạn) mới là bên thực sự chạy hàm tương ứng.

**Q: Vì sao 2 tool có tên/mô tả giống nhau dễ khiến model chọn nhầm?**
A: Vì với model, tool name và description chỉ là text trong prompt để nó suy luận chọn — không có cơ chế logic cứng nào đảm bảo chọn đúng, giống hệt cách model có thể hiểu nhầm 2 câu văn gần nghĩa nhau.

**Q: Nếu agent gọi sai tool hoặc sai tham số, nên sửa ở đâu?**
A: Thường không phải bug code parse JSON — mà là model dự đoán sai token lúc sinh structured output. Sửa bằng cách viết `description` tool rõ ràng hơn, đặt tên tham số tường minh hơn (kèm ví dụ định dạng), giảm số tool cấp cùng lúc, hoặc dùng model có tool-calling tốt hơn.

**Q: Constrained decoding là gì, giải quyết vấn đề gì?**
A: Kỹ thuật ở tầng serving ép logits chỉ được chọn token tạo ra JSON hợp lệ theo đúng schema đã khai báo — đảm bảo output luôn parse được về mặt cú pháp, dù không đảm bảo giá trị bên trong luôn đúng ngữ nghĩa (vd vẫn có thể chọn sai tool hoặc sai giá trị tham số).

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Nhầm tool-calling là 1 tính năng "chắc chắn đúng" của model.** Không phải mọi model đều tool-calling tốt như nhau; model nhỏ/rẻ dễ sinh sai schema — luôn cần validate + retry ở client.
- **Debug sai hướng khi agent gọi nhầm tool** — junior hay đi soát lại code parse JSON, trong khi vấn đề thật nằm ở description/tên tool mơ hồ khiến model chọn sai ngay từ bước sinh output.
- **Nhồi quá nhiều tool "cho chắc"** — càng nhiều tool cùng lúc, model càng dễ nhầm lẫn; nên nhóm/tinh giản theo ngữ cảnh thay vì cấp hết mọi tool có sẵn trong mọi request.
- **Không phân biệt được lỗi cú pháp JSON (constrained decoding có thể giải quyết) với lỗi ngữ nghĩa (chọn sai tool/sai giá trị tham số — decoding không giải quyết được, cần description/schema tốt hơn).**

## Bảng so sánh nhanh

| | Text tự do (không tool-calling) | Tool-calling (structured output) |
|---|---|---|
| Output | text bất kỳ | object JSON khớp schema đã khai báo |
| Cần train riêng? | không | có (model được fine-tune cho khả năng này) |
| Đảm bảo đúng cú pháp | không áp dụng | có thể ép bằng constrained decoding |
| Đảm bảo đúng ngữ nghĩa (chọn đúng tool/tham số) | không áp dụng | không — vẫn phụ thuộc description/schema rõ ràng |
