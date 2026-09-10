# Phỏng vấn — Quantization (INT8/INT4)

Lesson chính: [19-quantization.md](19-quantization.md) · [Toán](19-quantization-math.md)

## Q&A

**Q: Quantization là gì, cơ chế cốt lõi?**
A: Giảm độ chính xác số học của trọng số (và đôi khi activation) từ FP16/FP32 xuống INT8/INT4. Cơ chế linear quantization: tính `scale` từ khoảng giá trị `[min,max]` của 1 block, `q = round((x-min)/scale)` để nén, `x' = q*scale+min` để dùng lại (giá trị xấp xỉ, có sai số).

**Q: Vì sao quantization giúp tăng tốc, không chỉ tiết kiệm bộ nhớ?**
A: LLM inference (đặc biệt decode) bị nghẽn ở băng thông đọc bộ nhớ (memory-bound), không phải số phép tính (FLOPs). Trọng số nhỏ hơn → đọc nhanh hơn → tăng throughput, dù có thêm bước dequantize.

**Q: Weight-only quantization khác gì weight+activation quantization?**
A: Weight-only chỉ nén trọng số lưu trữ, lúc tính dequantize về FP16 rồi nhân bình thường — an toàn, dễ làm. Weight+activation quantize cả input khi nhân ma trận — tiết kiệm hơn nhưng khó vì activation có outlier features (số ít giá trị cực lớn, quan trọng cho chất lượng) dễ bị hỏng nếu quantize thô.

**Q: Quantize INT4 xong có fine-tune tiếp trực tiếp trên đó được không?**
A: Không trực tiếp — trọng số INT4 là số nguyên rời rạc, backprop cần đạo hàm liên tục. QLoRA giải quyết bằng cách đóng băng hoàn toàn base INT4, gắn thêm LoRA adapter (BF16) song song, chỉ adapter nhận gradient.

**Q: Vì sao quantize trên GPU không có kernel tối ưu có thể CHẬM HƠN cả FP16 gốc?**
A: Thiếu kernel tính toán trực tiếp trên INT4 → engine phải dequantize từng block về FP16/BF16 ngay trước mỗi phép nhân — đây là overhead THÊM VÀO so với FP16 gốc (không cần bước giải nén nào). Nếu phần cứng không có đường tính nhanh cho INT4, overhead này có thể lớn hơn phần tiết kiệm từ đọc ít bộ nhớ hơn.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Bẫy chính (từ checkpoint thật):** trả lời "quantize xong vẫn fine-tune trực tiếp được vì nó là model đã nén" — SAI, không chạm cơ chế backprop. Câu trả lời đúng phải nói rõ: base bị ĐÓNG BĂNG, chỉ adapter LoRA (độ chính xác cao hơn) nhận gradient, không phải quantize "cho phép" train trực tiếp trên số nguyên.
- **Bẫy về hiệu năng (từ checkpoint thật):** mặc định "quantize luôn nhanh hơn vì nhẹ hơn" — sai nếu hardware thiếu kernel tối ưu cho bit-width đó; lúc đó dequantize overhead có thể làm CHẬM HƠN bản gốc. Luôn phải kiểm tra hardware có hỗ trợ kernel INT4/INT8 hay không trước khi kỳ vọng tăng tốc.
- Nhầm quantization là "chỉ làm tròn số", bỏ qua khái niệm `scale`/`zero-point` theo từng block — dẫn tới không giải thích được vì sao chia block nhỏ hơn giúp giảm sai số.
- Quên vấn đề outlier features: nghĩ mọi giá trị trong 1 layer quantize đều như nhau, không biết một vài outlier hiếm có thể kéo `scale` cả block lên khiến toàn bộ giá trị khác bị quantize thô hơn (xem file Toán).
- Nhầm INT4 luôn tệ hơn INT8 ở mọi trường hợp — thực ra AWQ/GPTQ tối ưu tốt có thể giữ chất lượng khá gần INT8 ở nhiều task, cần đo bằng golden set thay vì suy đoán.

## Bảng so sánh nhanh

| Phương pháp | Bit | Cơ chế | Điểm mạnh | Điểm yếu |
|---|---|---|---|---|
| bitsandbytes LLM.int8() | INT8 | Giữ outlier ở FP16, phần còn lại INT8 | Không cần calibration data, dùng được cả lúc training (nền tảng QLoRA) | Không nén mạnh bằng GPTQ/AWQ |
| GPTQ | INT4 (thường) | Tối ưu layer-wise giảm sai số tái tạo, cần calibration data | Nén mạnh, nhanh khi inference | Cần calibration tốt, khó fine-tune tiếp |
| AWQ | INT4 | Bảo vệ trọng số quan trọng dựa trên magnitude activation | Chất lượng thường tốt hơn GPTQ cùng bit-width | Vẫn cần calibration |
| GGUF (llama.cpp) | INT4/INT5/INT8 nhiều mức | Tối ưu CPU/edge, trộn bit-width theo layer | Chạy tốt trên CPU/máy cá nhân, hệ sinh thái lớn | Không tương thích trực tiếp `transformers` |

## Follow-up chưa trả lời (ôn lại nếu quay lại bài này)

**Q: Vì sao QLoRA vẫn chọn quantize base xuống INT4 rồi mới gắn LoRA, thay vì giữ base FP16 và gắn LoRA thường?**
A (gợi ý, chưa được user xác nhận trực tiếp): lợi ích cốt lõi là giảm VRAM cần để LOAD base model khi fine-tune (7B: 14GB FP16 → 3.5GB INT4), cho phép fine-tune model lớn hơn nhiều trên GPU tiêu dùng — đổi lấy tốc độ train chậm hơn do dequantize liên tục (đã học ở bài 18).
