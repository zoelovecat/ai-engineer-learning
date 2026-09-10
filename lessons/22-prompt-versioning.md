# 22. Prompt versioning (version control, A/B test)

**Ngày học:** 2026-09-10
**Trạng thái:** Đã học

Xem thêm: [Phỏng vấn](22-prompt-versioning-interview.md)

## 1. Lý thuyết

Quản lý prompt (system prompt, few-shot examples, instructions) như quản lý code — mỗi thay đổi có version ID riêng, có thể diff giữa các version, rollback về version cũ, và tách khỏi code (không hardcode string literal) để thay đổi prompt không cần deploy lại app.

3 phần cơ chế:
- **Version control cho prompt**: lưu ở nơi riêng (file YAML/JSON trong git, hoặc registry chuyên dụng như Langfuse Prompt Management, PromptLayer, LangSmith Hub), mỗi version có ID/tag, có lịch sử thay đổi.
- **A/B test**: route % traffic thật tới 2 version song song (vd 90% version ổn định, 10% version mới), đo metric qua eval offline (golden set — bài 11) và/hoặc feedback production thật, so sánh có ý nghĩa thống kê trước khi rollout 100%.
- **Rollback**: version mới gây regression (phát hiện qua golden set hoặc production metrics giảm) → quay lại version cũ ngay, không cần code change/deploy.

**Vì sao cần hiểu sâu:** tutorial cơ bản hardcode prompt trong code — thay đổi nhỏ phải qua PR+deploy, không biết chắc version nào đang chạy ở production khi debug, và không đo được định lượng "prompt mới có thực sự tốt hơn không" — chỉ cảm tính. Golden set + A/B test lấp lỗ hổng này bằng số liệu thật.

**Trade-off:**
- Thêm hạ tầng quản lý (registry, cần tích hợp gateway/serving để route theo version) — over-engineering nếu team nhỏ, ít đổi prompt.
- A/B test cần đủ traffic/mẫu để có ý nghĩa thống kê — mẫu nhỏ (vd 20 request) dễ nhiễu, kết luận vội sai.
- Offline eval (golden set) nhanh, an toàn nhưng có thể không phản ánh hết đa dạng hành vi user thật; A/B test thật đo đúng outcome nhưng chậm và có rủi ro ảnh hưởng user thật nếu version mới tệ. Cách đúng: dùng offline eval LỌC TRƯỚC (loại version rõ tệ hơn), rồi mới đưa vào A/B test thật với traffic nhỏ.
- Không cần dùng nếu prompt gần như không đổi hoặc hệ thống đủ nhỏ để rollback thủ công đã đủ nhanh.

## 2. Ví dụ áp dụng

PolicyWorker (bài 15) dùng system prompt v1, muốn thử v2 (thêm hướng dẫn "luôn trích dẫn đúng số điều luật") để giảm lỗi trích dẫn sai đã phát hiện ở bài 3/15.

- Trước A/B test thật: tạo v2 như version mới trong Langfuse Prompt Management (gắn label `staging`), chạy qua golden set (bài 11, gồm case đã từng lỗi trích dẫn), so kết quả với v1 (label `production`) trên cùng bộ câu hỏi — không tốn traffic thật ở bước này.
- A/B test: 90% v1 / 10% v2, chạy tới khi đủ cỡ mẫu (không cố định theo ngày mà theo số request tối thiểu), quyết định dựa trên tỷ lệ trích dẫn đúng có ý nghĩa thống kê (không phải chênh 1-2% ngẫu nhiên) — v2 tốt hơn rõ ràng thì tăng dần traffic (10%→50%→100%); rollback ngay lập tức nếu phát hiện lỗi nghiêm trọng mới trong lúc test.
- Langfuse liên kết trace (bài 10) với version prompt cụ thể — biết đúng request nào chạy version nào khi debug.

## 3. Bài thực hành

Thiết kế (không code): bước cần làm trước khi A/B test v2 với user thật, kế hoạch A/B test cụ thể (% traffic, tiêu chí rollout/rollback), và đánh giá tình huống mẫu quá nhỏ (20 request).

## 4. Checkpoint

**Câu 1:** Trước khi A/B test v2 với user thật, nên làm gì, bằng công cụ nào?
- Trả lời: "Langfuse. dùng như nào" — đúng công cụ nhưng chưa tự nêu được bước cụ thể (chạy qua golden set offline trước khi tốn traffic thật) — assistant giải thích thêm cách dùng Langfuse Prompt Management (version/label, liên kết golden set, liên kết trace).

**Câu 2:** Thiết kế kế hoạch A/B test cụ thể?
- User yêu cầu assistant trả lời hộ: 90/10 traffic split, chạy tới đủ cỡ mẫu, quyết định dựa trên metric có ý nghĩa thống kê, rollback ngay nếu lỗi nghiêm trọng mới xuất hiện trong lúc test.

**Câu 3:** A/B test 20 request cho kết quả v2 tốt hơn — có nên rollout ngay không?
- User yêu cầu assistant trả lời hộ: KHÔNG — mẫu quá nhỏ, chênh lệch dễ là nhiễu ngẫu nhiên, cần thêm mẫu (và lý tưởng đã lọc qua golden set trước) mới quyết định.

**Độ tin cậy:** thấp — câu 1 chỉ nêu đúng tên công cụ, chưa tự nêu bước quy trình; câu 2-3 assistant trả lời hộ hoàn toàn. Ưu tiên hỏi lại cả 3 câu nếu ôn lại.
