# Interview notes: Đánh giá retrieval (recall@k, MRR)

Lesson chính: [05-retrieval-eval.md](05-retrieval-eval.md)

## Q&A có thể gặp

**Q: Recall@k và MRR khác nhau ở đâu, vì sao cần cả 2?**
A: Recall@k chỉ hỏi "document đúng có mặt trong top-k không" (nhị phân, không quan tâm vị trí). MRR quan tâm document đúng đứng **hạng mấy**. Một pipeline có thể recall@10 cao (đúng có mặt) nhưng MRR thấp (đúng đứng hạng 8-9, gần cuối) — nghĩa là retrieval "tìm thấy" nhưng "xếp hạng dở", đây là dấu hiệu nên thêm rerank thay vì sửa retrieval.

**Q: Vì sao không dùng luôn "accuracy" (top-1 đúng hay không) mà cần cả recall@k?**
A: Top-1 accuracy quá khắt khe và không phản ánh đúng cách hệ thống dùng — pipeline RAG thường lấy top-3/top-5 đưa vào context LLM chứ không chỉ top-1, nên recall@k (khớp đúng k đó) đo sát thực tế sử dụng hơn.

**Q: Eval set tự viết có đáng tin không?**
A: Có rủi ro thiên vị (confirmation bias) nếu người viết câu hỏi biết trước đáp án và vô tình viết câu hỏi "dễ" cho hệ thống. Production nên bổ sung eval set từ log câu hỏi thật của user (khó/tự nhiên hơn) + có người review độc lập gán đáp án đúng.

**Q: Đo recall@k trước hay sau khi thêm rerank?**
A: Recall@k thường đo ở tầng retrieval thô (trước rerank) để biết "kho ứng viên có đủ tốt không" trước khi quyết định đầu tư rerank. MRR có thể đo cả trước và sau rerank để so sánh rerank có thực sự cải thiện thứ hạng không.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Nhầm recall cao = hệ thống tốt.** Recall@10 cao dù đúng đứng hạng 10 vẫn tính là "có" — nhưng nếu pipeline chỉ dùng top-3 thực tế thì con số đó vô nghĩa. Luôn hỏi ngược: "recall@k với k bằng bao nhiêu, có khớp với k thực tế dùng trong context LLM không?"
- **Chỉ nhìn 1 con số trung bình.** Trung bình toàn eval set có thể che giấu 1 nhóm câu hỏi (vd nhóm semantic không có số điều) yếu hẳn so với nhóm còn lại — luôn tách nhóm khi báo cáo số liệu, đừng chỉ đưa 1 con số tổng.
- **MRR=0 vs Recall=0 là cùng 1 việc** khi document đúng hoàn toàn không xuất hiện trong danh sách xét — nhưng khi có mặt thì recall không phân biệt hạng 1 hay hạng k, còn MRR phân biệt rất rõ (1 vs 1/k).

## Bảng so sánh nhanh

| | Recall@k | MRR | NDCG (mở rộng, không học sâu ở đây) |
|---|---|---|---|
| Đo gì | có mặt trong top-k hay không | vị trí chính xác của đáp án đúng đầu tiên | vị trí + độ liên quan của NHIỀU đáp án đúng |
| Nhạy với vị trí trong top-k? | không | có | có |
| Phù hợp khi nào | ước lượng "kho ứng viên" có đủ tốt trước rerank | so sánh chất lượng xếp hạng cuối (có thể sau rerank) | có nhiều mức độ liên quan / nhiều đáp án đúng |
