# Phỏng vấn — Khi nào fine-tune vs prompt/RAG

Lesson chính: [17-finetune-vs-prompt-rag.md](17-finetune-vs-prompt-rag.md)

## Q&A

**Q: Phân biệt RAG và fine-tune bằng 1 câu?**
A: RAG thay đổi model BIẾT GÌ (kiến thức, cấp lúc inference, audit được vì có nguồn); fine-tune thay đổi model LÀM GÌ/NÓI NHƯ THẾ NÀO (hành vi, ngấm vào trọng số, khó audit).

**Q: Thứ tự ưu tiên nên thử khi model trả lời chưa tốt?**
A: Prompt engineering → RAG → fine-tune, theo thứ tự chi phí/độ phức tạp tăng dần. Fine-tune là phương án cuối, chỉ dùng khi 2 cái kia đã tối ưu mà vẫn thiếu.

**Q: Rủi ro của việc fine-tune ngay mà chưa thử prompt trước?**
A: Tốn công/tiền/thời gian chuẩn bị data + train cho vấn đề có thể chỉ cần sửa prompt trong vài phút; nếu vẫn sai sau khi fine-tune (do gốc rễ thực ra chỉ thiếu hướng dẫn rõ trong prompt), phải sửa lại trên model đã fine-tune — khó và chậm hơn nhiều so với sửa prompt trực tiếp.

**Q: Dấu hiệu THẬT cho thấy cần cân nhắc fine-tune?**
A: Đã có golden set/eval (bài 11, bài 5) cho thấy retrieval/context đúng gần tuyệt đối, đã thử NHIỀU phiên bản prompt/few-shot có hệ thống qua nhiều vòng — nhưng accuracy vẫn dừng ở mức thấp, lặp lại cùng kiểu lỗi. Đây là dấu hiệu model có đủ thông tin nhưng "không biết cách dùng" theo ý muốn.

**Q: Vì sao fine-tune trên ít data/data chất lượng thấp lại nguy hiểm?**
A: Dễ gây overfit — model học thuộc lòng pattern hẹp trong tập nhỏ, mất khả năng tổng quát hoá cho case mới ngoài tập train (liên hệ overfitting — bài 25).

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Bẫy chính (từ checkpoint thật):** hỏi "rủi ro của bỏ qua prompt engineering trước khi fine-tune" mà chỉ trả lời chung chung "cẩn thận chọn data training" — đó là rủi ro CỦA BẢN THÂN fine-tune, không phải rủi ro của việc BỎ QUA bước trước đó. Cần phân biệt 2 loại rủi ro này khi trả lời.
- **Bẫy về "đủ bằng chứng":** thấy accuracy thấp sau ĐÚNG 1 LẦN thử sửa prompt rồi vội kết luận "cần fine-tune" — sai, vì hiệu quả prompt engineering phụ thuộc nhiều vào cách viết cụ thể, cần thử có hệ thống (nhiều phiên bản) trước khi kết luận.
- Nhầm lẫn agent "dùng kiến thức cũ do data train" là lỗi cần fine-tune ngay — thực ra đây thường là vấn đề RAG (cấp kiến thức mới) trước; chỉ khi RAG+few-shot không đủ sức ghi đè prior mạnh của model mới cần fine-tune.
- Quên rằng fine-tune có chi phí MAINTENANCE ẩn: mỗi lần base model ra bản mới, phải cân nhắc fine-tune lại — chi phí này ít tutorial nhắc tới nhưng ảnh hưởng lớn tới quyết định dài hạn.

## Bảng so sánh nhanh

| Hướng | Thay đổi gì | Chi phí | Update kiến thức mới | Khi nào dùng |
|---|---|---|---|---|
| Prompt engineering | Cách hỏi/hướng dẫn | Rất thấp (vài phút) | Không áp dụng | Luôn thử đầu tiên |
| RAG | Kiến thức cấp lúc inference | Thấp-trung bình | Dễ (đổi tài liệu/index) | Vấn đề thiếu/sai kiến thức |
| Fine-tune (LoRA/QLoRA) | Hành vi/phong cách/kỹ năng cố định | Cao (data + compute + maintenance) | Khó (phải train lại) | Hành vi lặp lại sai dù đã tối ưu prompt+RAG, có bằng chứng từ eval |
