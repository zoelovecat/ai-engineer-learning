# Toán — Quantization: linear quantization (scale/zero-point) và VRAM

Lesson chính: [19-quantization.md](19-quantization.md)

## Công thức

Với 1 nhóm trọng số float có khoảng giá trị `[min, max]`, quantize về `b` bit không dấu:

```
scale = (max - min) / (2^b - 1)
q = round((x - min) / scale)          # số nguyên 0..(2^b - 1)
x' = q * scale + min                  # dequantize — giá trị xấp xỉ x gốc
```

Sai số quantize của 1 giá trị: `|x - x'|` — luôn ≤ `scale/2` (vì `round`).

## Ví dụ số cụ thể

Giả sử 1 block trọng số có giá trị thật: `[-0.8, 0.3, 0.5, -0.2]` → `min = -0.8`, `max = 0.5`. Quantize về INT4 không dấu (`b=4`, giá trị 0..15).

```
scale = (0.5 - (-0.8)) / (2^4 - 1) = 1.3 / 15 ≈ 0.0867
```

Quantize `x = 0.3`:
```
q = round((0.3 - (-0.8)) / 0.0867) = round(1.1 / 0.0867) = round(12.69) = 13
```

Dequantize lại:
```
x' = 13 * 0.0867 + (-0.8) = 1.127 - 0.8 = 0.327
```

Sai số: `|0.3 - 0.327| = 0.027` — nhỏ hơn `scale/2 ≈ 0.043`, đúng như dự kiến.

Thử với `x = -0.2`:
```
q = round((-0.2 - (-0.8)) / 0.0867) = round(0.6 / 0.0867) = round(6.92) = 7
x' = 7 * 0.0867 - 0.8 = 0.6069 - 0.8 = -0.193
```
Sai số `0.007` — nhỏ hơn giá trị trước vì `-0.2` gần điểm chia lưới hơn.

## Ý nghĩa

- Sai số quantize **không cố định cho mọi giá trị** trong block — phụ thuộc khoảng cách tới điểm lưới gần nhất, tối đa `scale/2`.
- `scale` càng lớn (khoảng `[min, max]` càng rộng so với số bit) → sai số càng lớn. Đây là lý do **chia nhỏ theo block/channel** (thay vì 1 scale cho cả layer) quan trọng: block nhỏ hơn → giá trị trong block đồng đều hơn → `max-min` nhỏ hơn → `scale` nhỏ hơn → sai số nhỏ hơn.
- Nếu trong 1 block có 1 giá trị **outlier** cực lớn (vd 8.0 thay vì quanh 0.3-0.5), nó sẽ kéo `max` lên rất cao → `scale` tăng vọt → MỌI giá trị khác trong block (kể cả các giá trị nhỏ, "bình thường") đều bị quantize thô hơn hẳn. Đây chính là cơ chế toán học đứng sau vấn đề "outlier feature" nhắc ở lesson chính — lý do bitsandbytes LLM.int8() phải tách riêng outlier ra khỏi quá trình quantize thay vì gộp chung.

## Liên hệ VRAM (bài thực hành)

Dung lượng = số tham số × bytes/tham số (FP16=2, INT8=1, INT4=0.5). Model 7B tham số:

```
FP16: 7×10⁹ × 2  = 14×10⁹ byte ≈ 14 GB
INT8: 7×10⁹ × 1  = 7×10⁹  byte ≈ 7 GB
INT4: 7×10⁹ × 0.5 = 3.5×10⁹ byte ≈ 3.5 GB
```

Đây là phép nhân đơn giản (không phải linear quantization ở trên) nhưng cùng logic gốc: số bit/tham số càng ít → dung lượng lưu trữ giảm tuyến tính theo đúng tỷ lệ bit.
