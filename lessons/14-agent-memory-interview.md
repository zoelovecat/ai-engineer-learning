# 14 — Kiến trúc bộ nhớ agent: ghi chú phỏng vấn

Xem lý thuyết đầy đủ: [14-agent-memory.md](14-agent-memory.md)

## Q&A

**Q: 3 tầng bộ nhớ agent khác nhau thế nào?**
A: Short-term = context window của phiên hiện tại (mất khi phiên kết thúc). Episodic = log các phiên quá khứ, scoped theo 1 danh tính/case cụ thể (user_id/case_id), truy xuất lại khi đúng người/case đó quay lại. Long-term = kiến thức tổng hợp/khái quát hóa, KHÔNG scoped theo danh tính — generalize được xuyên user.

**Q: Ranh giới thật giữa episodic và long-term memory là gì?**
A: Không phải "lưu bao lâu" — mà là **có scoped theo danh tính hay không**. Episodic là "chuyện riêng" của 1 user/case cụ thể, không tự động chia sẻ cho user khác. Long-term là kiến thức đã được nâng cấp thành "chung của hệ thống", dùng được cho mọi user sau, kể cả người chưa từng tương tác trước đó.

**Q: Vì sao thêm memory cho agent không phải lúc nào cũng tốt hơn?**
A: Mỗi lần truy vấn memory là 1 bước retrieval (như RAG) — có rủi ro kéo nhầm memory bề ngoài giống nhưng không liên quan, khiến agent bị "neo" vào lời giải cũ sai ngữ cảnh, hoặc làm loãng context (lost-in-the-middle). Thêm memory luôn kèm rủi ro nhiễu, không miễn phí.

**Q: Long-term memory có rủi ro gì giống hallucination, và vì sao khó phát hiện hơn?**
A: Agent có thể tự tổng hợp 1 "niềm tin" sai từ vài case không đại diện (trùng hợp, không phải quy luật) rồi lưu thành kiến thức dùng lâu dài — giống hallucination bị "đóng băng". Khó phát hiện hơn vì nó là trạng thái ẩn tồn tại xuyên nhiều lượt gọi, không lộ ra ngay trong 1 câu trả lời đơn lẻ như hallucination thông thường.

**Q: Golden set và LLM-as-judge có tự động bắt được lỗi long-term memory sai không?**
A: Không tự động. Cả 2 kỹ thuật test input/output của 1 lượt gọi riêng lẻ, không kiểm tra nội dung của chính memory store. Chỉ phát hiện gián tiếp nếu case trong golden set vô tình chạm đúng vùng bị niềm tin sai ảnh hưởng — cần thêm 1 lớp riêng: audit định kỳ nội dung memory store.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **NHẦM episodic và long-term khi áp dụng vào tình huống cụ thể** (bẫy đã xảy ra thật ở checkpoint bài này): hiểu đúng định nghĩa chung ("long-term là tổng hợp sau nhiều phiên") nhưng khi cho 1 tình huống cụ thể (user khác hỏi lại câu tương tự), lại chọn nhầm episodic. Quy tắc để tránh nhầm: luôn tự hỏi "thông tin này có SCOPED theo đúng 1 danh tính không, hay đã được KHÁI QUÁT HÓA xuyên nhiều danh tính" — nếu câu hỏi liên quan tới 1 user/case KHÁC với người tạo ra memory đó, chỉ long-term mới giúp được.
- **Coi thêm memory luôn là cải thiện**: bẫy phổ biến — quên rằng mỗi lần thêm nguồn thông tin vào context là thêm 1 kênh có thể đưa nhiễu vào, không phải chỉ có lợi.
- **Không nghĩ tới việc long-term memory cần audit riêng**: nhiều người nghĩ "cứ eval agent bình thường (golden set/LLM-as-judge) là đủ" — quên rằng các kỹ thuật đó không soi được vào chính nội dung của memory store, nơi lỗi có thể âm ỉ tồn tại lâu trước khi lộ ra ở 1 output cụ thể.
- **Quên cơ chế cập nhật/xóa memory cũ**: long-term memory cũng cần cơ chế "hết hạn"/cập nhật khi thông tin outdate, giống vấn đề "cái neo sai"/data drift ở golden set (bài 11), nhưng áp dụng cho memory của chính agent chứ không phải eval set của người dạy agent.

## Bảng so sánh nhanh

| Khía cạnh | Short-term | Episodic | Long-term |
|---|---|---|---|
| Phạm vi | 1 phiên đang diễn ra | 1 danh tính/case cụ thể, nhiều phiên | Toàn hệ thống, xuyên mọi danh tính |
| Cách lưu | Context window (tạm) | Log có cấu trúc (DB/vector store theo user_id) | Kho kiến thức tổng hợp (thường vector store riêng) |
| Mất khi nào | Kết thúc phiên | Không mất, nhưng chỉ dùng lại cho đúng danh tính đó | Không mất, dùng chung mãi tới khi cập nhật/xóa |
| Rủi ro chính | Giới hạn kích thước (lost-in-the-middle) | Retrieval sai kéo nhầm case không liên quan | Học sai thành niềm tin cố định, khó audit |
