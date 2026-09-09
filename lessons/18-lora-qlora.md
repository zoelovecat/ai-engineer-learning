# 18. LoRA/QLoRA (PEFT)

**Ngày học:** 2026-09-09
**Trạng thái:** Đã học

Xem thêm: [Toán](18-lora-qlora-math.md) · [Phỏng vấn](18-lora-qlora-interview.md)

## 1. Lý thuyết

Full fine-tuning cập nhật toàn bộ tham số model — cực tốn GPU/RAM. **PEFT (Parameter-Efficient Fine-Tuning)** chỉ train 1 phần rất nhỏ tham số, giữ nguyên phần còn lại. **LoRA (Low-Rank Adaptation)** là kỹ thuật PEFT phổ biến nhất.

Cơ chế: đóng băng ma trận trọng số gốc `W` (không train), thêm 2 ma trận nhỏ `A` (d×r) và `B` (r×d) với rank `r` rất nhỏ (8-64) so với chiều gốc d (vd 4096). Output = `W·x + B·A·x`. Khi train chỉ `A`, `B` được cập nhật.

Ý tưởng toán học: "độ thay đổi cần thiết" để model thích nghi task mới không cần đủ hạng đầy đủ như ma trận gốc — xấp xỉ tốt bằng tích 2 ma trận hạng thấp (low-rank), giống nén thông tin.

`r` = số chiều (rank) của "không gian thay đổi" LoRA biểu diễn được. `r` nhỏ → ít bậc tự do → chỉ biểu diễn được thay đổi theo ít "hướng" độc lập → dễ underfit với task cần điều chỉnh nhiều khía cạnh độc lập cùng lúc.

**QLoRA** = LoRA + Quantization (bài 19): model gốc nén xuống 4-bit trước khi gắn LoRA adapter → giảm bộ nhớ cần load model → fine-tune model lớn (7B, 13B) trên GPU tiêu dùng.

**Vì sao cần hiểu sâu:** hiểu `W + B·A` giải thích vì sao adapter train xong chỉ vài chục MB (chỉ chứa A, B) → đổi adapter tức thì cho nhiều task mà không cần load lại model gốc. Hiểu rank giúp biết cách tune: r nhỏ cho task đơn giản (đổi format/giọng văn), r lớn hơn cho task phức tạp hơn.

**Trade-off:**
- LoRA vẫn cần load được base model vào GPU (forward pass chạy qua toàn bộ model) — không giải quyết "không có GPU nào cả".
- Capacity hạn chế bởi rank — không phù hợp để học 1 khối kiến thức/kỹ năng hoàn toàn mới phức tạp (lúc đó cần full fine-tuning).
- QLoRA đổi **thời gian train lấy bộ nhớ** (chậm hơn do dequantize liên tục), không phải "tốn tài nguyên nói chung" — không nên dùng nếu VRAM đã đủ cho LoRA thường.
- Vẫn tuân nguyên tắc bài 17: chỉ đáng làm khi đã xác định đúng đây là vấn đề hành vi cần fine-tune, không phải kiến thức (RAG) hay chỉ cần prompt tốt hơn.

## 2. Ví dụ áp dụng

Use case HR (bài 15): model 7B, áp LoRA vào ma trận Query attention (4096×4096) ở 1 layer. Full fine-tune ma trận này = 16,777,216 tham số. LoRA rank r=8 = 65,536 tham số (~0.39% so với full). Toàn model LoRA thường chiếm 0.1%-1% tổng tham số — lý do adapter chỉ nặng vài chục MB.

Liên hệ: 3 phòng ban (HR, IT, Kế toán) cần agent văn phong khác nhau nhưng chung kiến thức nền → train 3 LoRA adapter riêng trên 1 base model, đổi adapter khi phục vụ phòng ban tương ứng, thay vì giữ 3 bản copy đầy đủ model.

Không viết code thực hành riêng (đi thẳng checkpoint theo yêu cầu user).

## 3. Checkpoint

**Câu 1:** Vì sao rank càng nhỏ càng ít tham số, nhưng không thể giảm quá thấp (r=1) cho mọi task?
- Trả lời ban đầu: "vì tham số train quá nhỏ" — vòng vo, chưa chạm cơ chế.
- Đáp án đúng: r=1 → ma trận B·A chỉ có hạng 1 → mọi thay đổi LoRA tạo ra chỉ là 1 "hướng" duy nhất trong không gian trọng số, không đủ bậc tự do cho task cần điều chỉnh nhiều khía cạnh độc lập → underfit.

**Câu 2:** LoRA rank nhỏ có phù hợp khi cần học thêm kiến thức chuyên môn hoàn toàn mới không?
- Trả lời: Không, vì không gian rank nhỏ không đủ biểu diễn khối kiến thức mới. Đúng — user tự trả lời đúng ngay.

**Câu 3:** QLoRA đánh đổi gì để giảm bộ nhớ?
- Trả lời ban đầu: "lâu hơn, tính toán nhiều hơn, tốn tài nguyên" — có điểm mâu thuẫn (QLoRA sinh ra để TIẾT KIỆM bộ nhớ).
- Đáp án đúng: đổi thời gian train (chậm hơn do dequantize liên tục) lấy bộ nhớ (VRAM ít hơn) — không phải "tốn tài nguyên nói chung".

**Follow-up:** Đủ VRAM cho LoRA thường thì có nên vẫn dùng QLoRA "cho chắc" không?
- User yêu cầu assistant trả lời hộ: Không nên — chịu chi phí chậm hơn để đổi lợi ích (tiết kiệm bộ nhớ) không cần thiết. Chỉ dùng QLoRA khi bộ nhớ là ràng buộc thực sự.

**Độ tin cậy:** trung bình — câu 2 tự trả lời đúng, câu 1/3 cần bổ sung cơ chế sau khi giải thích lại (không hỏi lại xác nhận riêng), follow-up assistant trả lời hộ hoàn toàn theo yêu cầu user.
