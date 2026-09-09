# Phỏng vấn — LoRA/QLoRA (PEFT)

Lesson chính: [18-lora-qlora.md](18-lora-qlora.md) · [Toán](18-lora-qlora-math.md)

## Q&A

**Q: LoRA là gì, cơ chế cốt lõi?**
A: PEFT (Parameter-Efficient Fine-Tuning) — đóng băng trọng số gốc `W`, thêm 2 ma trận nhỏ `A`, `B` với rank `r` nhỏ, output = `W·x + B·A·x`, chỉ train `A`, `B`. Dựa trên giả định "độ thay đổi cần thiết" có thể xấp xỉ bằng ma trận hạng thấp.

**Q: Vì sao LoRA tiết kiệm bộ nhớ/tham số hơn hẳn full fine-tuning?**
A: Full fine-tuning train `d×d` tham số cho 1 ma trận; LoRA chỉ train `2×d×r` với `r << d` (vd r=8 so với d=4096) → chỉ ~0.4% số tham số cho ví dụ đó, và tăng theo `r` tuyến tính chứ không theo `d²`.

**Q: Rank `r` ảnh hưởng gì tới kết quả?**
A: `r` là số chiều (bậc tự do) của không gian thay đổi LoRA có thể biểu diễn. `r` nhỏ → ít tham số, train nhanh, nhưng dễ underfit với task cần điều chỉnh nhiều khía cạnh độc lập. `r` lớn → capacity cao hơn nhưng tốn nhiều tham số hơn (dù vẫn rẻ hơn full fine-tuning nhiều).

**Q: QLoRA khác LoRA ở điểm nào, đánh đổi gì?**
A: QLoRA = LoRA + quantize base model xuống 4-bit trước khi train adapter → giảm mạnh VRAM cần thiết, cho phép fine-tune model lớn trên GPU tiêu dùng. Đánh đổi: train chậm hơn do phải dequantize liên tục trong tính toán — đổi thời gian lấy bộ nhớ, không phải "tốn tài nguyên nói chung".

**Q: LoRA có phù hợp để dạy model 1 mảng kiến thức chuyên môn hoàn toàn mới không?**
A: Không phù hợp — không gian rank nhỏ không đủ biểu diễn 1 khối kiến thức lớn. LoRA hợp với tinh chỉnh nhẹ hành vi/phong cách/domain hẹp; kiến thức mới nên qua RAG (bài 17) hoặc full fine-tuning nếu thực sự cần thay đổi sâu.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Bẫy chính (từ checkpoint thật):** giải thích "vì sao không thể giảm rank quá thấp" mà chỉ nói "vì tham số quá nhỏ" — đó là mô tả lại triệu chứng (số liệu nhỏ), KHÔNG phải cơ chế. Câu trả lời đúng phải nói tới **hạng (rank) của ma trận B·A giới hạn số "hướng" độc lập** mà LoRA có thể điều chỉnh — đây là bản chất toán học, không phải chỉ là "số lượng".
- **Bẫy về QLoRA:** dễ nói QLoRA "tốn tài nguyên hơn" chung chung — sai bản chất, vì mục đích chính của QLoRA là TIẾT KIỆM bộ nhớ. Đánh đổi chính xác là tốc độ (chậm hơn), không phải tài nguyên nói chung. Cũng cần biết: nếu đã đủ VRAM, dùng QLoRA "cho chắc" là không cần thiết — chỉ nên dùng khi bộ nhớ thực sự là ràng buộc.
- Nhầm LoRA là "phiên bản rẻ hơn của full fine-tuning nhưng làm được y hệt" — sai, LoRA có giới hạn capacity thật sự do rank thấp, không thay thế hoàn toàn full fine-tuning cho mọi task.
- Quên rằng LoRA thường chỉ áp vào MỘT SỐ ma trận cụ thể (thường là Q/K/V trong attention — bài 16), không phải toàn bộ model — việc chọn `target_modules` ảnh hưởng trực tiếp tới hiệu quả và số tham số train.

## Bảng so sánh nhanh

| Kỹ thuật | Tham số train | Bộ nhớ cần | Tốc độ train | Phù hợp khi |
|---|---|---|---|---|
| Full fine-tuning | 100% | Rất cao | Nhanh nhất (không overhead) | Cần thay đổi sâu, có đủ compute lớn |
| LoRA | ~0.1%-1% | Trung bình (vẫn cần load full model) | Nhanh | Tinh chỉnh hành vi/phong cách, đủ VRAM cho base model |
| QLoRA | ~0.1%-1% (như LoRA) | Thấp (base model 4-bit) | Chậm hơn LoRA (dequantize overhead) | VRAM hạn chế, cần fine-tune model lớn trên GPU tiêu dùng |
