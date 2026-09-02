# Lộ trình AI Engineer (Junior → Middle) — nội dung tham chiếu

Nguồn: roadmap do user cung cấp, giữ nguyên nội dung kỹ thuật gốc. File này chỉ để tra cứu — việc dạy/luyện tập nằm ở `SKILL.md`.

Bối cảnh áp dụng: không cố định vào 1 project/domain duy nhất — ưu tiên gắn mỗi concept vào project thật user đang build (bất kể domain gì); nếu không có project cụ thể, dùng ví dụ đa dạng, xoay vòng qua nhiều loại use case (RAG tra cứu tài liệu, chatbot hỗ trợ, agent xử lý case, coding assistant...) thay vì học chay hoặc lặp lại mãi 1 domain quen thuộc.

## Thứ tự ưu tiên đề xuất (học xen kẽ với project thật đang build, không học tuần tự cứng)

1. **RAG core** — embedding models, chunking strategy, hybrid search → cần ngay khi bắt đầu dựng bất kỳ hệ thống tra cứu tài liệu nào (RAG).
2. **Đánh giá retrieval** (recall@k, MRR) + **reranking** — làm ngay sau khi RAG chạy được, để biết "tốt tới đâu" trước khi build tiếp.
3. **Agent core** — ReAct / Plan-and-Execute, tool-calling ở tầng model, MCP — khi bắt đầu build agent-loop.
4. **Observability** (Langfuse/LangSmith) — gắn ngay khi agent chạy nhiều bước, để debug được.
5. **Eval / golden set** cho agent — song song, càng sớm càng tránh regression khi đổi prompt/model.
6. **Kiến trúc bộ nhớ agent** (short-term/episodic/long-term) + **multi-agent orchestration** — khi agent phức tạp hơn 1 vòng lặp đơn.
7. **Vector DB internals (HNSW)** — khi cần chọn/tune vector DB thật cho production.
8. **Fine-tuning & tùy biến model** (Transformer khái niệm, LoRA/QLoRA, quantization) — chỉ sau khi prompt+RAG đã tối ưu mà vẫn thiếu.
9. **MLOps còn lại** (model serving vLLM/TGI, AI Gateway/LiteLLM, prompt versioning) — khi cần tối ưu chi phí/scale.
10. **An toàn/Bảo mật** (prompt injection, red-teaming) — bắt buộc trước khi launch thật.
11. **Nền tảng ML cổ điển** (classification/regression, metrics, contrastive learning cho embedding) — học nền song song bất cứ lúc nào rảnh, không chặn tiến độ.

## Giai đoạn 2: RAG — đi sâu kỹ thuật, không chỉ "dùng thư viện"

- **Embedding models**: khác biệt giữa OpenAI text-embedding-3, Cohere embed, model mã nguồn mở (BGE, E5) — chọn model nào cho use case nào; dimension size ảnh hưởng tốc độ/độ chính xác.
- **Chunking strategy**: không chia đều theo số ký tự — semantic chunking, sliding window, chunking theo cấu trúc document (heading-aware). Đây là yếu tố quyết định chất lượng RAG nhiều hơn cả chọn model.
- **Hybrid search**: kết hợp vector search (semantic) với BM25 (keyword/lexical) — vì vector thuần yếu với tên riêng, mã số, thuật ngữ chính xác.
- **Reranking**: model rerank (Cohere Rerank, cross-encoder) sau bước retrieve thô để lọc top kết quả — bước production thật hầu như luôn có mà tutorial cơ bản hay bỏ qua.
- **Đánh giá retrieval**: metric recall@k, MRR (Mean Reciprocal Rank) — đo định lượng thay vì cảm tính.
- **Vector DB internals**: thuật toán HNSW (Hierarchical Navigable Small World) — cơ chế index sau Pinecone/Weaviate/pgvector; trade-off tốc độ/độ chính xác/bộ nhớ khi chọn tham số index.

## Giai đoạn 3: Agent — kiến trúc thật, không chỉ gọi framework

- **Pattern suy luận agent**: ReAct (Reason+Act xen kẽ), Plan-and-Execute (lập kế hoạch trước rồi thực thi), Reflexion (agent tự phê bình kết quả của chính mình) — biết khi nào dùng pattern nào.
- **Tool-calling ở tầng model**: cách model được train để sinh structured call (JSON schema) thay vì "đoán" — quan trọng khi debug agent gọi sai tool.
- **Model Context Protocol (MCP)**: chuẩn giao tiếp agent-tool đang thành chuẩn ngành — nên học sớm.
- **Kiến trúc bộ nhớ agent**: short-term memory (context window), episodic memory (log tương tác trước), long-term memory (vector store riêng cho agent) — phần "khó" khi agent cần tự học từ case trước.
- **Multi-agent orchestration**: supervisor-worker, debate giữa nhiều agent, blackboard pattern — thực hành bằng LangGraph để xây state machine thay vì chuỗi lệnh tuyến tính.

## Giai đoạn 4: Fine-tuning & tùy biến model

- **Transformer ở mức khái niệm**: cơ chế attention, vì sao context window có giới hạn, lost-in-the-middle problem — không cần tự code transformer, cần hiểu để giải thích hành vi model.
- **Khi nào fine-tune, khi nào chỉ cần prompt/RAG**: quyết định kỹ thuật quan trọng nhất — fine-tune tốn kém, chỉ làm khi prompt engineering + RAG đã hết khả năng.
- **LoRA/QLoRA (PEFT)**: fine-tune model mã nguồn mở (Llama, Qwen, Mistral) không cần GPU khủng — dùng Hugging Face `transformers` + `peft`.
- **Quantization**: INT8/INT4 để chạy model nhẹ hơn khi tự host — liên quan trực tiếp ý tưởng "offline-first".

## Giai đoạn 5: Đánh giá & kiểm thử hệ thống AI

- **LLM-as-judge**: dùng chính LLM chấm điểm output của agent khác — kỹ thuật scale đánh giá khi không thể chấm tay mọi case.
- **Eval dataset / golden set**: tập câu hỏi/tình huống chuẩn để test mỗi khi đổi prompt/model, tránh regression.
- **Phát hiện hallucination**: self-consistency check (hỏi nhiều lần, so sánh câu trả lời), citation-based verification (bắt model trích dẫn nguồn để kiểm chứng).

## Giai đoạn 6: MLOps/Hạ tầng triển khai AI

- **Model serving**: vLLM hoặc TGI (Text Generation Inference) nếu tự host model mã nguồn mở — kỹ thuật batching request tăng throughput.
- **AI Gateway**: tự hiểu/tự dựng gateway đơn giản bằng LiteLLM — cơ chế routing, cost tracking, fallback thực sự hoạt động thế nào.
- **Observability**: LangSmith/Langfuse để trace từng bước agent (mỗi lần gọi tool, mỗi token dùng) — bắt buộc khi debug agent phức tạp nhiều bước.
- **Prompt versioning**: quản lý prompt như code (version control, A/B test giữa các version).

## Giai đoạn 7: An toàn/Bảo mật AI

- **Prompt injection**: cơ chế tấn công (nội dung độc hại trong dữ liệu agent đọc vào chiếm quyền điều khiển agent) và phòng thủ (input sanitization, tách rõ system prompt/user data, output validation).
- **Red-teaming**: tự thử tấn công agent của chính mình trước khi launch — kỹ năng yêu cầu ở vị trí middle+ khi công ty quan tâm compliance.

## Giai đoạn 8: Nền tảng ML cổ điển (không bắt buộc nhưng nên có)

- **Khái niệm ML cơ bản**: classification/regression, train/test split, overfitting, metric đánh giá (precision/recall/F1) — biết khi nào dùng ML cổ điển (nhanh, rẻ, dễ giải thích) thay vì "quăng cho LLM" (chậm, đắt, khó kiểm soát). Đây là điểm phân biệt "middle" với "junior chỉ biết gọi API".
- **Cách embedding được train (contrastive learning)** — chọn/đánh giá embedding model có cơ sở thay vì đoán mò.
