# Phỏng vấn — Transformer khái niệm (attention, context window, lost-in-the-middle)

Lesson chính: [16-transformer-concepts.md](16-transformer-concepts.md) · [Toán](16-transformer-concepts-math.md)

## Q&A

**Q: Attention là gì, giải thích cơ chế Q/K/V ngắn gọn?**
A: Cơ chế cho mỗi token "nhìn" tất cả token khác để quyết định token nào liên quan. Mỗi token có Query (đại diện "tôi đang tìm gì"), Key (đại diện "tôi là gì" để được tìm), Value (nội dung thực sự mang theo). Tính dot product Q·K ra điểm khớp, softmax thành trọng số, rồi lấy trung bình có trọng số của Value.

**Q: Vì sao attention là O(n²)?**
A: Vì mỗi token trong chuỗi n token đều phải tính điểm khớp với n token khác (kể cả chính nó) → n × n = n² phép so sánh. Không phải 1 token so với các token khác 1 lần — mà TẤT CẢ n token đều làm vậy.

**Q: Context window là gì, vì sao có giới hạn?**
A: Số token tối đa (input + output) model xử lý 1 lần. Giới hạn vì chi phí attention tăng bình phương theo độ dài (dài gấp đôi thì tính toán gấp 4), và model chỉ được train ổn định trong 1 khoảng độ dài nhất định — vượt quá đó, vị trí token trở nên "lạ".

**Q: Lost-in-the-middle là gì? Model có thực sự "quên" thông tin ở giữa không?**
A: Hiện tượng model dùng thông tin ở đầu/cuối context tốt hơn hẳn ở giữa. Không phải "quên" theo nghĩa kỹ thuật — dữ liệu vẫn nằm nguyên trong context, chỉ là trọng số attention phân bổ không đều, thiên vị 2 đầu, nên model ít dùng tới phần giữa khi tổng hợp câu trả lời.

**Q: Context window dài hơn (vd 1M token) có giải quyết được lost-in-the-middle không?**
A: Không. Đây là 2 vấn đề độc lập — context dài hơn chỉ tăng SỐ LƯỢNG token chứa được, không thay đổi việc attention phân bổ trọng số không đều. Thực nghiệm cho thấy model context rất dài vẫn giảm hiệu suất truy xuất thông tin ở giữa.

**Q: Liên hệ giữa lost-in-the-middle và reranking (bài 4)?**
A: Rerank không chỉ lọc bớt chunk không liên quan — còn có vai trò SẮP XẾP LẠI vị trí để chunk quan trọng nhất nằm ở đầu/cuối prompt, tránh rơi vào vùng giữa context mà attention ít chú ý.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Bẫy chính (từ checkpoint thật):** giải thích O(n²) mà chỉ nói "1 token tính trọng số với các token khác" — đúng nhưng KHÔNG ĐỦ, dễ bị hiểu nhầm thành O(n). Phải nói rõ điều này lặp lại cho MỌI token trong chuỗi (n lần), nên tổng là n².
- Nhầm lost-in-the-middle với giới hạn context window — đây là 2 khái niệm khác nhau: context window là "chứa được bao nhiêu", lost-in-the-middle là "trong phần đã chứa, model chú ý không đều".
- Nghĩ tăng context window (dùng model hỗ trợ context dài hơn) là giải pháp cho RAG trả lời sai khi có nhiều chunk — sai, vì vấn đề là VỊ TRÍ thông tin trong context, không phải có đủ chỗ chứa hay không.
- Quên rằng lost-in-the-middle áp dụng cả cho lịch sử hội thoại dài (agent nhiều bước), không chỉ RAG chunk — liên hệ với agent memory (bài 14): giải pháp không phải giảm context mà là chủ động trích xuất thông tin quan trọng vào episodic memory có cấu trúc.

## Bảng so sánh nhanh

| Khái niệm | Vấn đề giải quyết | Không giải quyết được gì |
|---|---|---|
| Context window lớn hơn | Chứa được nhiều token hơn trong 1 lần gọi | Không cải thiện việc model có "chú ý" đều tới mọi phần trong context hay không |
| Reranking | Sắp xếp lại vị trí chunk quan trọng lên đầu/cuối | Không thể tạo ra thông tin nếu retrieval ban đầu không lấy được chunk đúng |
| Episodic memory (trích xuất thông tin quan trọng) | Tránh mất thông tin quan trọng khi hội thoại/context quá dài | Không thay thế được short-term context cho những gì cần ngữ cảnh tức thời |
