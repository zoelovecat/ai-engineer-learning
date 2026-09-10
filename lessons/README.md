# Bài học đã lưu

Mỗi file trong thư mục này là nội dung đầy đủ của một concept đã học (lý thuyết + ví dụ áp dụng project + bài thực hành + checkpoint), do skill `ai-engineer-track` tạo và lưu lại để đọc lại/cập nhật sau này.

Tên file theo mẫu: `<số thứ tự trong PROGRESS.md>-<slug-concept>.md`.

## Danh sách

<!-- Skill tự thêm dòng vào đây mỗi khi lưu bài học mới -->
- [01-embedding-models.md](01-embedding-models.md) — Embedding models (OpenAI/Cohere/BGE/E5, dimension trade-off) — đã học
  - 📐 [01-embedding-models-math.md](01-embedding-models-math.md) — toán: dot product, cosine similarity
  - 🎯 [01-embedding-models-interview.md](01-embedding-models-interview.md) — điểm hay bị hỏi phỏng vấn
- [02-chunking-strategy.md](02-chunking-strategy.md) — Chunking strategy (semantic, sliding window, heading-aware) — đã học
  - 🎯 [02-chunking-strategy-interview.md](02-chunking-strategy-interview.md) — điểm hay bị hỏi phỏng vấn
- [03-hybrid-search.md](03-hybrid-search.md) — Hybrid search (vector + BM25) — đã học
  - 📐 [03-hybrid-search-math.md](03-hybrid-search-math.md) — toán: BM25, Reciprocal Rank Fusion (RRF)
  - 🎯 [03-hybrid-search-interview.md](03-hybrid-search-interview.md) — điểm hay bị hỏi phỏng vấn
- [04-reranking.md](04-reranking.md) — Reranking (Cohere Rerank, cross-encoder) — cần ôn lại (còn mơ hồ)
  - 🎯 [04-reranking-interview.md](04-reranking-interview.md) — điểm hay bị hỏi phỏng vấn
- [05-retrieval-eval.md](05-retrieval-eval.md) — Đánh giá retrieval (recall@k, MRR) — đã học (chưa chạy thực hành thật)
- [06-vector-db-hnsw.md](06-vector-db-hnsw.md) — Vector DB internals (HNSW) — cần ôn lại (checkpoint chưa đạt)
  - 🎯 [06-vector-db-hnsw-interview.md](06-vector-db-hnsw-interview.md) — điểm hay bị hỏi phỏng vấn
- [07-agent-patterns.md](07-agent-patterns.md) — Pattern suy luận agent (ReAct/Plan-and-Execute/Reflexion) — đã học
  - 🎯 [07-agent-patterns-interview.md](07-agent-patterns-interview.md) — điểm hay bị hỏi phỏng vấn
- [08-tool-calling.md](08-tool-calling.md) — Tool-calling ở tầng model (structured output/JSON schema) — đã học
  - 🎯 [08-tool-calling-interview.md](08-tool-calling-interview.md) — điểm hay bị hỏi phỏng vấn
  - 🎯 [05-retrieval-eval-interview.md](05-retrieval-eval-interview.md) — điểm hay bị hỏi phỏng vấn
- [09-mcp.md](09-mcp.md) — Model Context Protocol (MCP) — đã học
  - 🎯 [09-mcp-interview.md](09-mcp-interview.md) — điểm hay bị hỏi phỏng vấn
- [10-observability.md](10-observability.md) — Observability (Langfuse/LangSmith) — đã học
  - 🎯 [10-observability-interview.md](10-observability-interview.md) — điểm hay bị hỏi phỏng vấn
- [11-golden-set.md](11-golden-set.md) — Eval dataset / golden set, tránh regression — đã học
  - 🎯 [11-golden-set-interview.md](11-golden-set-interview.md) — điểm hay bị hỏi phỏng vấn
- [12-llm-as-judge.md](12-llm-as-judge.md) — LLM-as-judge — đã học
  - 🎯 [12-llm-as-judge-interview.md](12-llm-as-judge-interview.md) — điểm hay bị hỏi phỏng vấn
- [13-hallucination-detection.md](13-hallucination-detection.md) — Phát hiện hallucination (self-consistency, citation-based) — đã học
  - 🎯 [13-hallucination-detection-interview.md](13-hallucination-detection-interview.md) — điểm hay bị hỏi phỏng vấn
- [14-agent-memory.md](14-agent-memory.md) — Kiến trúc bộ nhớ agent (short/episodic/long-term) — đã học
  - 🎯 [14-agent-memory-interview.md](14-agent-memory-interview.md) — điểm hay bị hỏi phỏng vấn
- [15-multi-agent-orchestration.md](15-multi-agent-orchestration.md) — Multi-agent orchestration (supervisor-worker, debate, blackboard, LangGraph) — đã học
  - 🎯 [15-multi-agent-orchestration-interview.md](15-multi-agent-orchestration-interview.md) — điểm hay bị hỏi phỏng vấn
- [16-transformer-concepts.md](16-transformer-concepts.md) — Transformer khái niệm (attention, context window, lost-in-the-middle) — đã học
  - 📐 [16-transformer-concepts-math.md](16-transformer-concepts-math.md) — toán: attention Q/K/V, scaled dot-product
  - 🎯 [16-transformer-concepts-interview.md](16-transformer-concepts-interview.md) — điểm hay bị hỏi phỏng vấn
- [17-finetune-vs-prompt-rag.md](17-finetune-vs-prompt-rag.md) — Khi nào fine-tune vs prompt/RAG — đã học (độ tin cậy thấp hơn, nhiều phần assistant trả lời hộ)
  - 🎯 [17-finetune-vs-prompt-rag-interview.md](17-finetune-vs-prompt-rag-interview.md) — điểm hay bị hỏi phỏng vấn
- [18-lora-qlora.md](18-lora-qlora.md) — LoRA/QLoRA (PEFT) — đã học
  - 📐 [18-lora-qlora-math.md](18-lora-qlora-math.md) — toán: số tham số tiết kiệm được (d×d vs 2×d×r)
  - 🎯 [18-lora-qlora-interview.md](18-lora-qlora-interview.md) — điểm hay bị hỏi phỏng vấn
- [19-quantization.md](19-quantization.md) — Quantization (INT8/INT4) — đã học (độ tin cậy trung bình-thấp, câu 1 sai lúc đầu, câu 2 assistant trả lời hộ, follow-up chưa trả lời)
  - 📐 [19-quantization-math.md](19-quantization-math.md) — toán: linear quantization (scale/zero-point), VRAM theo bit-width
  - 🎯 [19-quantization-interview.md](19-quantization-interview.md) — điểm hay bị hỏi phỏng vấn
- [20-model-serving.md](20-model-serving.md) — Model serving (vLLM/TGI, batching) — đã học (checkpoint 3/3 tự trả lời đúng)
  - 🎯 [20-model-serving-interview.md](20-model-serving-interview.md) — điểm hay bị hỏi phỏng vấn
