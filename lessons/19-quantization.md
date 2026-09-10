# 19. Quantization (INT8/INT4)

**Ngày học:** 2026-09-10
**Trạng thái:** Đã học

Xem thêm: [Toán](19-quantization-math.md) · [Phỏng vấn](19-quantization-interview.md)

## 1. Lý thuyết

Quantization là giảm độ chính xác số học của trọng số (và đôi khi cả activation) từ FP16/FP32 xuống INT8 hoặc INT4.

Cơ chế cốt lõi — **linear quantization**: chọn 1 khoảng giá trị float `[min, max]` cho 1 nhóm trọng số (thường chia nhỏ theo block/channel để giảm sai số), tính `scale = (max - min) / (2^bits - 1)`, quantize `q = round((x - min) / scale)`, khi tính toán dequantize lại `x' = q*scale + min` (giá trị xấp xỉ — nguồn sai số).

2 loại cần phân biệt:
- **Weight-only quantization**: chỉ nén trọng số lưu trữ, lúc tính toán dequantize về FP16 rồi nhân — tiết kiệm VRAM, tăng tốc vì LLM inference bị nghẽn ở băng thông đọc bộ nhớ (memory-bound) chứ không phải FLOPs.
- **Weight + activation quantization**: cả input lẫn trọng số đều INT8/INT4 khi nhân — tiết kiệm hơn nhưng khó vì activation có **outlier features** (một số ít giá trị cực lớn, quan trọng cho chất lượng output) — đây là chỗ tutorial cơ bản hay bỏ qua. bitsandbytes LLM.int8() giữ riêng outlier ở FP16, chỉ quantize phần còn lại.

**Vì sao cần hiểu sâu:** model 7B ở FP16 cần ~14GB chỉ để load weight — quyết định model có fit GPU 8GB/16GB/24GB hay không. Vì inference bị nghẽn băng thông bộ nhớ, nén nhỏ hơn → đọc nhanh hơn → tăng throughput dù có thêm bước dequantize.

**Trade-off:**
- INT4 rủi ro degrade chất lượng cao hơn INT8, đặc biệt task cần suy luận chính xác (toán, code) hơn sinh text tự do.
- Không phải hardware nào cũng có kernel tối ưu cho INT4 — nếu thiếu, dequantize overhead có thể triệt tiêu lợi ích tốc độ, thậm chí chậm hơn FP16 gốc.
- Quantize xong khó full fine-tune tiếp — đây là lý do QLoRA ra đời (bài 18): đóng băng base đã quantize INT4, chỉ train adapter LoRA (BF16) song song, gradient chỉ chạy qua adapter, không sửa base INT4.
- Cần calibration data đại diện tốt nếu dùng static method (GPTQ/AWQ) — calibration lệch phân phối thật → quantize sai chỗ quan trọng.
- KHÔNG nên dùng khi đủ VRAM chạy FP16 thoải mái và task cần độ chính xác cao chưa test kỹ ở dạng quantize.

## 2. Ví dụ áp dụng

Tự host Qwen2.5-7B làm coding assistant nội bộ, GPU 16GB VRAM, chừa 4GB cho KV cache (context dài):
- FP16 (14GB) → không fit (14+4=18GB > 16GB).
- INT8 (7GB) → fit (7+4=11GB, dư 5GB).
- INT4 (3.5GB) → fit thoải mái nhất, dư nhiều nhất cho context/batch.

→ Buộc phải quantize, lựa chọn thực tế là INT8 vs INT4 tùy mức chấp nhận rủi ro chất lượng.

Không viết code thực hành (bài toán tính toán VRAM, không cần chạy code).

## 3. Bài thực hành

Tính dung lượng weight FP16/INT8/INT4 cho model 7B, kiểm tra ràng buộc VRAM 16GB (chừa 4GB KV cache), và đề xuất cách kiểm chứng chất lượng trước khi đưa quantize vào production.

Kết quả: cả 2 (FP16 không fit, INT8/INT4 đều fit) — xem chi tiết bảng tính trong hội thoại. Cách kiểm chứng: dùng lại **golden set** (bài 11) chạy qua cả FP16 baseline và bản quantize, diff kết quả từng case (đặc biệt case logic phức tạp), kết hợp LLM-as-judge (bài 12) để chấm ở quy mô lớn hơn tay.

## 4. Checkpoint

**Câu 1:** Quantize INT4 xong, có fine-tune trực tiếp trên weight INT4 bằng LoRA được không?
- Trả lời ban đầu: "có, vì bản thân nó là model base đã được nén" — chưa chạm cơ chế.
- Đáp án đúng: KHÔNG train trực tiếp trên INT4 (số nguyên rời rạc, backprop cần đạo hàm liên tục). QLoRA đóng băng hoàn toàn base INT4, gắn thêm LoRA adapter (BF16) chạy song song — chỉ adapter nhận gradient và được cập nhật, base INT4 không bao giờ bị sửa. Fine-tune "gián tiếp" qua adapter, không phải trực tiếp trên INT4.

**Câu 2:** Quantize xong trên A100 (có kernel INT4 tối ưu) nhưng deploy sang GPU cũ không có kernel này thì chạy chậm hơn cả FP16 — vì sao?
- Trả lời ban đầu: "chịu".
- Đáp án đúng: thiếu kernel phần cứng cho phép nhân ma trận trực tiếp trên INT4 → engine phải dequantize từng block INT4→BF16/FP16 ngay trước mỗi phép nhân — đây là compute overhead THÊM VÀO mà FP16 gốc không hề có. Nếu phần cứng không có đường tính nhanh cho INT4, chi phí giải nén liên tục lớn hơn cả phần tiết kiệm từ đọc ít bộ nhớ hơn → tổng thể chậm hơn FP16 thẳng.

**Câu 3:** Tình huống KHÔNG nên quantize dù đủ lý do VRAM?
- Trả lời: "bài toán cần độ chính xác cao (tính toán...), vì quantize đánh đổi độ chính xác lấy VRAM" — đúng hướng, user tự trả lời đúng ngay.

**Follow-up (1b, chưa trả lời — user chọn mark Đã học và chuyển bài trước khi trả lời):** Vì sao QLoRA vẫn chọn quantize base xuống INT4 rồi mới gắn LoRA, thay vì giữ base FP16 và gắn LoRA thường? Lợi ích cụ thể là gì?
- Để ngỏ, ôn lại nếu quay lại bài này: lợi ích là giảm VRAM cần để LOAD base model (từ 14GB xuống 3.5GB cho 7B), cho phép fine-tune model lớn hơn trên GPU nhỏ hơn nhiều — đây chính là mục đích cốt lõi QLoRA ra đời (bài 18), đổi lấy tốc độ train chậm hơn do dequantize liên tục.

**Độ tin cậy:** trung bình-thấp — câu 1 sai lúc đầu (đã đính chính), câu 2 "chịu" (assistant giải thích hết), câu 3 tự trả lời đúng. Follow-up 1b chưa được trả lời/xác nhận khi mark Đã học.
