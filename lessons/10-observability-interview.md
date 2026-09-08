# 10 — Observability: ghi chú phỏng vấn

Xem lý thuyết đầy đủ: [10-observability.md](10-observability.md)

## Q&A

**Q: Trace và span khác nhau thế nào?**
A: Trace = toàn bộ 1 lượt xử lý từ đầu tới cuối (1 trace_id). Span = 1 đơn vị công việc bên trong trace (1 lần gọi LLM, 1 lần gọi tool), có start/end time, parent span, tạo thành cây (span tree) bên trong 1 trace.

**Q: Vì sao agent nhiều bước cần tracing thay vì chỉ print/log?**
A: Log tuần tự không thể hiện quan hệ cha-con giữa các bước và không tổng hợp được latency/cost tích lũy theo cây. Tracing trả lời trực tiếp câu hỏi "bước nào trong chuỗi N bước gây chậm/sai", log thường phải tự suy luận thủ công.

**Q: Inclusive duration và self (exclusive) duration khác nhau thế nào? Vì sao quan trọng?**
A: Inclusive duration = tổng thời gian span đó tồn tại, bao gồm cả thời gian mọi span con chạy bên trong. Self duration = thời gian span đó *tự làm việc*, trừ đi tổng thời gian các span con trực tiếp. Chỉ leaf span (không có con) mới có self = inclusive. Nếu chỉ nhìn inclusive duration, span gốc/span cha luôn "trông chậm nhất" dù nó không tự làm gì — dẫn tới tối ưu sai chỗ.

**Q: Vì sao đóng span phải dùng try/finally (hoặc __exit__ tương đương), không đặt code sau logic bình thường?**
A: Nếu code bên trong span ném exception, phần code "sau" logic bình thường (không nằm trong finally) sẽ không được chạy — span sẽ treo ở trạng thái chưa đóng (end=None), làm hỏng cả stack cha-con của các span tiếp theo, và mất đúng dữ liệu debug cần nhất (lúc có lỗi thật).

**Q: Tracing có làm agent chạy nhanh/tốt hơn không?**
A: Không trực tiếp. Tracing chỉ giúp *quan sát* để biết chỗ nào cần sửa — bản thân nó không cải thiện logic agent, và còn thêm 1 chút latency + 1 dependency ngoài (server tracing).

**Q: Khi nào KHÔNG cần observability/tracing?**
A: Khi hệ thống chỉ có 1 lần gọi LLM duy nhất, không có loop/tool nhiều bước — log request/response đơn giản là đủ, thêm tracing là overhead không cần thiết.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Nhầm "span chậm nhất theo tổng thời gian" với "bước cần tối ưu"**: đây là bẫy thực tế gặp trong bài tập — root span luôn có duration lớn nhất (vì bao trùm mọi con), nhưng đó không phải nơi cần tối ưu. Câu hỏi phỏng vấn dạng "làm sao biết bước nào cần tối ưu" phải trả lời bằng self-time, không phải duration thô.
- **Nghĩ observability = thêm logging**: thiếu ý quan trọng là quan hệ **cha-con có cấu trúc (span tree)** + gắn liền cost/latency per-step — đây mới là khác biệt so với print/log rời rạc.
- **Quên rằng dữ liệu trace có thể chứa thông tin nhạy cảm**: input/output LLM gửi lên service tracing cloud (nếu không self-host) có thể chứa PII/secret — cần mask/redact, đặc biệt quan trọng khi nói tới compliance/bảo mật.
- **Bỏ qua chi phí đóng span an toàn khi có lỗi**: nhiều người viết tracer tự chế quên dùng try/finally, dẫn tới trace bị hỏng đúng lúc cần nhất (khi có exception) — điểm này lộ rõ trong bài thực hành (Câu 3 checkpoint).

## Bảng so sánh nhanh

| Khía cạnh | Log/print thường | Tracing (span tree) |
|---|---|---|
| Quan hệ giữa các bước | Không có (chỉ tuần tự theo thời gian in ra) | Cha-con rõ ràng (parent_id), dựng lại cây |
| Latency/cost | Phải tự cộng dồn thủ công | Tự động theo từng span + tổng theo trace |
| Trả lời "bước nào là thủ phạm" | Khó, phải đọc từng dòng log | Trực tiếp qua self-time của từng span |
| Chi phí thêm | Gần như 0 | Latency nhỏ + dependency service tracing |
| Khi nào dùng | Agent 1 bước, demo đơn giản | Agent nhiều bước, nhiều tool, production thật |
