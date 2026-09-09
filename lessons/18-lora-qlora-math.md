# Toán — LoRA: số tham số tiết kiệm được

Lesson chính: [18-lora-qlora.md](18-lora-qlora.md)

## Công thức

Ma trận trọng số gốc `W` kích thước `d × d` (ví dụ 1 ma trận Query trong attention — bài 16). LoRA thêm:
- `A`: kích thước `d × r`
- `B`: kích thước `r × d`

Output: `h = W·x + B·A·x` (hoặc thường nhân thêm hệ số scale `α/r`, bỏ qua ở đây cho đơn giản).

Số tham số cần train:
- Full fine-tuning: `d × d`
- LoRA: `(d × r) + (r × d) = 2 × d × r`

## Ví dụ số cụ thể

`d = 4096`, `r = 8` (số thật dùng ở ví dụ HR trong lesson chính):

- Full fine-tuning: `4096 × 4096 = 16,777,216` tham số
- LoRA: `2 × 4096 × 8 = 65,536` tham số
- Tỷ lệ: `65,536 / 16,777,216 = 0.00390625 ≈ 0.39%`

Thử với `r = 64` (rank lớn hơn, cho task phức tạp hơn):
- LoRA: `2 × 4096 × 64 = 524,288` tham số
- Tỷ lệ: `524,288 / 16,777,216 = 0.03125 = 3.125%`

## Ý nghĩa

Tăng `r` từ 8 lên 64 (gấp 8 lần) thì số tham số train cũng tăng đúng 8 lần (quan hệ tuyến tính với `r`, vì công thức là `2×d×r`) — nhưng vẫn chỉ chiếm ~3% so với full fine-tuning. Đây là lý do LoRA "rẻ" ngay cả khi tăng rank để tăng capacity — chi phí tăng theo `r` chứ không theo `d²` như full fine-tuning.

Trong code (`peft` library), `LoraConfig(r=8, target_modules=["q_proj", "v_proj"], ...)` chính là khai báo `r` và áp LoRA vào đúng các ma trận Query/Value trong attention (bài 16) — không phải toàn bộ model, càng giảm thêm số tham số cần train so với nếu áp LoRA cho mọi ma trận.
