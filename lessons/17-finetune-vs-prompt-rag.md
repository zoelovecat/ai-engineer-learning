# 17. Khi nào fine-tune vs chỉ dùng prompt/RAG

**Ngày học:** 2026-09-09
**Trạng thái:** Đã học

Xem thêm: [Phỏng vấn](17-finetune-vs-prompt-rag-interview.md)

## 1. Lý thuyết

Đây là 1 quyết định kiến trúc, không phải kỹ thuật đơn lẻ. 3 hướng khắc phục khi model trả lời chưa tốt, theo thứ tự chi phí tăng dần:

1. **Prompt engineering**: sửa system prompt, few-shot — không đổi model, không cần data train.
2. **RAG**: cấp kiến thức/thông tin model không có sẵn, tại thời điểm inference, qua context.
3. **Fine-tuning** (LoRA/QLoRA — bài 18): huấn luyện lại 1 phần trọng số bằng data input-output, để thay đổi hành vi/phong cách/kỹ năng cố định.

Phân biệt mấu chốt: **RAG thay đổi model BIẾT GÌ** (kiến thức, update được liên tục, audit được vì có nguồn) — **fine-tune thay đổi model LÀM GÌ/NÓI NHƯ THẾ NÀO** (hành vi, "ngấm" vào trọng số, khó biết chính xác vì sao model trả lời vậy).

**Vì sao cần hiểu sâu:** đa số vấn đề không cần fine-tune. Vấn đề "thiếu kiến thức" → RAG giải quyết đúng gốc, rẻ hơn, dễ update. Vấn đề "hành vi lặp lại sai dù đã ghi rõ trong prompt" → mới là dấu hiệu gần với fine-tune, nhưng vẫn nên thử few-shot trước. Chi phí ẩn của fine-tune: cần data chất lượng (vài trăm-vài nghìn example), compute, và maintenance khi base model có bản mới.

**Trade-off / khi nào KHÔNG fine-tune:**
- Vấn đề là thiếu kiến thức → luôn thử RAG trước.
- Chưa thử hết prompt engineering + RAG (fine-tune là phương án cuối, không phải bước đầu).
- Data ví dụ ít/chất lượng thấp → dễ làm model tệ đi (overfit, mất khả năng tổng quát — bài 25).
- Bài toán thay đổi thường xuyên → sửa prompt nhanh hơn train lại nhiều.
- Junior thấy "chưa đủ tốt" → nghĩ ngay fine-tune; middle theo thứ tự prompt → RAG → fine-tune, và hỏi "đây là THIẾU KIẾN THỨC hay THIẾU HÀNH VI/KỸ NĂNG" trước.

## 2. Ví dụ áp dụng

Use case HR (bài 15): "Trợ lý HR trả lời đúng nội dung nhưng văn phong quá cứng nhắc" → vấn đề hành vi (không phải thiếu kiến thức, vì `PolicyWorker` vẫn tìm đúng Điều luật) → thử sửa prompt + few-shot trước; chỉ cân nhắc fine-tune nếu đã thử prompt kỹ mà vẫn không nhất quán.

Ngược lại "trợ lý trả lời sai vì không biết chính sách mới ban hành tuần trước" → thiếu kiến thức → update tài liệu RAG, không cần fine-tune.

Ví dụ 2 (checkpoint câu 2): agent code-assistant dùng API deprecated 2 năm (model học từ data train cũ) → RAG trước (thiếu kiến thức); nếu đã RAG + few-shot mà model vẫn cố dùng API cũ → dấu hiệu prior của model quá mạnh, context không đủ sức ghi đè → lúc đó fine-tune mới hợp lý.

Không viết code thực hành riêng cho bài này (đi thẳng checkpoint).

## 3. Checkpoint

**Câu 1:** Rủi ro cụ thể của việc fine-tune ngay mà chưa thử prompt trước?
- Trả lời ban đầu: cần cẩn thận chọn data training — đúng nhưng lạc trọng tâm câu hỏi.
- Đáp án đúng: tốn công sức/tiền/thời gian chuẩn bị data + train cho vấn đề có thể chỉ cần sửa 1 dòng prompt; nếu sau khi fine-tune vẫn sai (vì gốc rễ chỉ thiếu hướng dẫn rõ), phải quay lại sửa trên cả model đã fine-tune — khó điều chỉnh hơn nhiều so với sửa prompt tức thì.

**Câu 2:** Agent dùng API deprecated do data train cũ — RAG hay fine-tune?
- Trả lời: RAG (đúng, vì thiếu/sai kiến thức). Bổ sung hay: nếu đã RAG+few-shot mà model vẫn dùng API cũ → dấu hiệu cần fine-tune (prior quá mạnh). Đúng, ý này trả lời trước cho câu 3.

**Câu 3:** Dấu hiệu cụ thể cho thấy RAG+prompt đã tối ưu hết mà vẫn không đủ, cần fine-tune?
- User không tự trả lời, assistant giải thích: golden set (bài 11) + recall@k (bài 5) cho thấy retrieval đúng gần như tuyệt đối, đã thử NHIỀU phiên bản prompt/few-shot qua nhiều vòng eval — nhưng accuracy vẫn dừng ở mức thấp, lặp lại cùng kiểu lỗi dù context đúng và đầy đủ.

**Follow-up:** Nếu golden set chỉ dừng ở 70% sau ĐÚNG 1 lần thử sửa prompt, đã đủ điều kiện kết luận cần fine-tune chưa?
- User không tự trả lời, assistant giải thích: Chưa đủ — cần thử nhiều phiên bản prompt có hệ thống (đổi cách diễn đạt, few-shot, thứ tự thông tin) qua nhiều vòng đo bằng golden set trước khi kết luận, vì hiệu quả prompt engineering phụ thuộc nhiều vào cách viết cụ thể, 1 lần thất bại chưa đủ bằng chứng.

**Độ tin cậy:** thấp hơn các bài trước — câu 1 sau khi giải thích không được hỏi lại để xác nhận hiểu, câu 3 và follow-up đều do assistant trả lời hộ hoàn toàn (user chủ động yêu cầu). Chỉ câu 2 là user tự trả lời đúng. Nên ưu tiên hỏi lại câu 1, 3 và follow-up nếu ôn lại concept này.
