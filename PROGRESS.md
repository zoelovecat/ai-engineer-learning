# 📍 Tiến độ học AI Engineer — mở file này để biết đang học đến đâu

> File này tự động cập nhật bởi skill `ai-engineer-track` sau mỗi buổi học đã được xác nhận. Không tự sửa tay trừ khi cần chỉnh lại thứ tự.

**Cập nhật lần cuối:** 2026-09-07
**Đang học:** Model Context Protocol (MCP)
**Tiến độ:** 6/26 concept đã học xong

---

## Bảng theo dõi

Trạng thái: `Chưa học` / `Đang học` / `Đã học` / `Cần ôn lại`

| # | Giai đoạn | Concept | Trạng thái | Ngày hoàn thành | Ghi chú |
|---|-----------|---------|-----------|------------------|---------|
| 1 | 2 - RAG | Embedding models (OpenAI/Cohere/BGE/E5, dimension trade-off) | Đã học | 2026-09-02 | Lý thuyết + toán (dot product, cosine similarity) + thực hành (so sánh similarity đồng nghĩa/không liên quan, test prefix query/passage) + checkpoint đạt (hybrid search cho số điều luật, vấn đề anisotropy/ngưỡng cứng). [Bài học](lessons/01-embedding-models.md) · [Toán](lessons/01-embedding-models-math.md) · [Phỏng vấn](lessons/01-embedding-models-interview.md) |
| 2 | 2 - RAG | Chunking strategy (semantic, sliding window, heading-aware) | Đã học | 2026-09-02 | Lý thuyết + thực hành (chunk_fixed vs chunk_heading_aware trên văn bản luật mẫu) + checkpoint đạt (chia nhỏ Điều quá dài kèm prepend heading, overlap không cứu được gộp chủ đề, phát hiện bug mất preamble). [Bài học](lessons/02-chunking-strategy.md) · [Phỏng vấn](lessons/02-chunking-strategy-interview.md) |
| 3 | 2 - RAG | Hybrid search (vector + BM25) | Đã học | 2026-09-02 | Lý thuyết + toán (BM25, RRF) + thực hành (rank_bm25 + rrf_fusion trên sample-luat-lao-dong.txt) + checkpoint: hybrid không sửa được lỗi khi cả BM25 và vector cùng đồng thuận sai (shared blind spot phát hiện thật ở query "công ty cho tôi nghỉ việc"), cần reranking cross-encoder để sửa (giải thích lại, user xác nhận hiểu qua trao đổi, không tự trả lời). [Bài học](lessons/03-hybrid-search.md) · [Toán](lessons/03-hybrid-search-math.md) · [Phỏng vấn](lessons/03-hybrid-search-interview.md) |
| 4 | 2 - RAG | Reranking (Cohere Rerank, cross-encoder) | Cần ôn lại | | Đã dạy lý thuyết + viết code thực hành (practice/04-reranking.py), nhưng CHƯA chạy thật (env agent không có Python) và checkpoint user báo còn mơ hồ chung, chưa rõ điểm cụ thể — nên chạy thử code thật trước khi ôn lại lý thuyết. [Bài học](lessons/04-reranking.md) · [Phỏng vấn](lessons/04-reranking-interview.md) |
| 5 | 2 - RAG | Đánh giá retrieval (recall@k, MRR) | Đã học | 2026-09-04 | User chủ động yêu cầu đánh dấu Đã học dù CHƯA chạy practice/05-retrieval-eval.py và CHƯA làm checkpoint — cần lưu ý khi ôn lại: recall@k/MRR mới dừng ở lý thuyết, chưa được kiểm chứng bằng số liệu thật trên eval-luat-lao-dong.json. [Bài học](lessons/05-retrieval-eval.md) · [Phỏng vấn](lessons/05-retrieval-eval-interview.md) |
| 6 | 2 - RAG | Vector DB internals (HNSW) | Cần ôn lại | | Đã dạy lý thuyết + viết code thực hành (practice/06-hnsw-vs-bruteforce.py, CHƯA chạy thật). Checkpoint 3 câu: câu 3 đúng, câu 1 (cơ chế local optimum/no-backtracking) và câu 2 (thiết kế thử nghiệm tách tầng index) chưa nắm — đã giải thích lại, cần ôn khi quay lại. [Bài học](lessons/06-vector-db-hnsw.md) · [Phỏng vấn](lessons/06-vector-db-hnsw-interview.md) |
| 7 | 3 - Agent | Pattern suy luận: ReAct / Plan-and-Execute / Reflexion | Đã học | 2026-09-07 | Code thực hành đầy đủ (practice/07-agent-patterns.py). Checkpoint: user yêu cầu mình trả lời hộ cả 3 câu (chưa tự diễn giải), sau khi đọc xác nhận Đã học — độ tin cậy thấp hơn các bài có tự trả lời, nên ưu tiên hỏi lại đúng 3 câu này nếu ôn lại. [Bài học](lessons/07-agent-patterns.md) · [Phỏng vấn](lessons/07-agent-patterns-interview.md) |
| 8 | 3 - Agent | Tool-calling ở tầng model (structured output/JSON schema) | Đã học | 2026-09-07 | Code thực hành (practice/08-tool-calling.py, hỗ trợ cả model thật lẫn offline), CHƯA chạy thật. Checkpoint 3 câu: câu 3 user tự trả lời đúng hướng, câu 1-2 mình trả lời hộ — độ tin cậy thấp hơn ở câu 1-2, ưu tiên hỏi lại nếu ôn. [Bài học](lessons/08-tool-calling.md) · [Phỏng vấn](lessons/08-tool-calling-interview.md) |
| 9 | 3 - Agent | Model Context Protocol (MCP) | Đang học | | |
| 10 | 6 - MLOps | Observability (Langfuse/LangSmith) | Chưa học | | |
| 11 | 5 - Eval | Eval dataset / golden set, tránh regression | Chưa học | | |
| 12 | 5 - Eval | LLM-as-judge | Chưa học | | |
| 13 | 5 - Eval | Phát hiện hallucination (self-consistency, citation-based) | Chưa học | | |
| 14 | 3 - Agent | Kiến trúc bộ nhớ agent (short/episodic/long-term) | Chưa học | | |
| 15 | 3 - Agent | Multi-agent orchestration (supervisor-worker, debate, blackboard, LangGraph) | Chưa học | | |
| 16 | 4 - Fine-tuning | Transformer khái niệm (attention, context window, lost-in-the-middle) | Chưa học | | |
| 17 | 4 - Fine-tuning | Khi nào fine-tune vs prompt/RAG | Chưa học | | |
| 18 | 4 - Fine-tuning | LoRA/QLoRA (PEFT, transformers + peft) | Chưa học | | |
| 19 | 4 - Fine-tuning | Quantization (INT8/INT4) | Chưa học | | |
| 20 | 6 - MLOps | Model serving (vLLM/TGI, batching) | Chưa học | | |
| 21 | 6 - MLOps | AI Gateway (LiteLLM: routing, cost tracking, fallback) | Chưa học | | |
| 22 | 6 - MLOps | Prompt versioning (version control, A/B test) | Chưa học | | |
| 23 | 7 - Security | Prompt injection (tấn công + phòng thủ) | Chưa học | | |
| 24 | 7 - Security | Red-teaming | Chưa học | | |
| 25 | 8 - ML nền tảng | Classification/regression, train/test split, overfitting, precision/recall/F1 | Chưa học | | |
| 26 | 8 - ML nền tảng | Embedding training (contrastive learning) | Chưa học | | |

## Log buổi học

<!-- Mỗi buổi thêm 1 dòng sau khi user XÁC NHẬN hoàn thành: ngày — concept — kết quả checkpoint — ghi chú follow-up -->
- 2026-09-02 — Embedding models — checkpoint đạt (4/4 câu, 2 câu cần bổ sung ở lượt đầu về khớp số điều luật và anisotropy đã hiểu đúng ở lượt 2) — tiếp theo: Chunking strategy.
- 2026-09-02 — Chunking strategy — checkpoint đạt (3/3 câu, câu về preamble bị mất dữ liệu trả lời sai ở lượt đầu, hiểu đúng sau khi trace code) — tiếp theo: Hybrid search (vector + BM25).
- 2026-09-02 — Hybrid search (vector + BM25) — thực hành thật phát hiện case hybrid không sửa được lỗi shared blind spot giữa BM25/vector; checkpoint cuối user không tự trả lời ("không biết"), được giải thích lại và xác nhận đánh dấu hoàn thành — tiếp theo: Reranking (Cohere Rerank, cross-encoder).
- 2026-09-04 — Reranking (Cohere Rerank, cross-encoder) — dạy lý thuyết + viết practice/04-reranking.py (chưa chạy thật, thiếu Python trong môi trường agent); checkpoint 3 câu user không tự trả lời, sau khi giải thích lại vẫn báo "mơ hồ" chung — KHÔNG đánh dấu Đã học, giữ "Cần ôn lại", chuyển tạm sang Đánh giá retrieval (recall@k, MRR), sẽ quay lại ôn reranking sau khi user chạy thử code thật.
- 2026-09-04 — Đánh giá retrieval (recall@k, MRR) — dạy lý thuyết + viết practice/05-retrieval-eval.py và eval set, nhưng user yêu cầu đánh dấu Đã học ngay dù CHƯA chạy code và CHƯA làm checkpoint — ghi nhận theo yêu cầu, nhưng đây là concept có độ tin cậy thấp hơn các bài trước (chưa kiểm chứng bằng số liệu thật) — tiếp theo: Vector DB internals (HNSW).
- 2026-09-07 — Vector DB internals (HNSW) — dạy lý thuyết + viết practice/06-hnsw-vs-bruteforce.py (chưa chạy thật); checkpoint 3 câu: câu 3 (khi nào không cần HNSW) đúng, câu 1 (cơ chế local optimum/no-backtracking khiến HNSW approximate) trả lời được trade-off nhưng thiếu cơ chế gốc, câu 2 (thiết kế thử nghiệm tách lỗi tầng index vs embedding) "không biết" — đã giải thích lại cả 2, KHÔNG đánh dấu Đã học, giữ "Cần ôn lại" — tiếp theo: Pattern suy luận ReAct/Plan-and-Execute/Reflexion.
- 2026-09-07 — Pattern suy luận agent (ReAct/Plan-and-Execute/Reflexion) — dạy lý thuyết + viết practice/07-agent-patterns.py (mock LLM, chạy được ngay); checkpoint 3 câu, user yêu cầu mình trả lời hộ hoàn toàn, sau khi đọc xác nhận đánh dấu Đã học — tiếp theo: Tool-calling ở tầng model (structured output/JSON schema).
- 2026-09-07 — Tool-calling ở tầng model (structured output/JSON schema) — dạy lý thuyết + viết practice/08-tool-calling.py (hỗ trợ model thật qua ANTHROPIC_API_KEY hoặc chế độ offline); checkpoint 3 câu, user tự trả lời câu 3 (đúng hướng, đã làm rõ thêm), câu 1-2 mình trả lời hộ, xác nhận đánh dấu Đã học — tiếp theo: Model Context Protocol (MCP).
