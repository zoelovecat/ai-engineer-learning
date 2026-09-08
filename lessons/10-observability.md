# 10 — Observability (Langfuse/LangSmith)

**Ngày tạo:** 2026-09-08
**Trạng thái:** Đã học

## Lý thuyết

### 1. Nó là gì — cơ chế thật

Với 1 API call LLM đơn giản, log = request/response thường là đủ. Nhưng agent nhiều bước (ReAct, tool-calling, MCP — bài 7-9) chạy tuần tự, mỗi bước gọi model + tool khác nhau, kết quả bước trước ảnh hưởng bước sau. Khi agent sai/chậm, câu hỏi là "bước nào trong chuỗi N bước đó gây ra".

Observability cho LLM app (Langfuse, LangSmith...) giải quyết bằng khái niệm **trace** và **span**, mượn từ distributed tracing (OpenTelemetry) + thêm ngữ nghĩa LLM:

- **Trace**: toàn bộ 1 lượt xử lý từ đầu tới cuối (1 `trace_id`).
- **Span** (Langfuse gọi "observation"): 1 đơn vị công việc bên trong trace — 1 lần gọi LLM, 1 lần gọi tool. Mỗi span có input/output, start/end time (→ latency), token dùng (→ cost), và **span cha** để dựng cây lồng nhau.
- Cả trace hiển thị như 1 cây: Trace → Span "ReAct loop" → Span con "gọi tool" → Span con "gọi LLM tổng hợp". Nhìn được chính xác bước nào chậm, tốn token, input/output sai.

Implement: SDK (Langfuse Python SDK, callback LangChain/LangSmith) cung cấp decorator/context-manager bọc quanh mỗi hàm cần track — mỗi lần vào/ra hàm, SDK gửi 1 record (span) kèm `parent_span_id` lên server, server dựng cây và hiển thị dashboard.

### 2. Vì sao cần nó

- **Debug agent nhiều bước**: log rời rạc không cho thấy quan hệ cha-con và không tổng hợp latency/cost tích lũy. Trace-tree trả lời đúng "bước nào là thủ phạm".
- **Đo cost thực tế**: mỗi span LLM ghi token in/out → cộng dồn theo trace/user/ngày.
- **Phát hiện regression khi đổi prompt/model**: so sánh trace cũ vs mới cho cùng input.
- Tutorial cơ bản luôn bỏ qua vì demo không cần — production với agent nhiều bước, nhiều user đồng thời thì không có observability gần như không debug được.

### 3. Trade-off / khi nào KHÔNG cần

- Agent 1 bước, 1 lần gọi LLM duy nhất → log đơn giản là đủ, tracing overkill.
- Thêm latency nhỏ (gửi record) + thêm 1 dependency ngoài (server phải chạy/available).
- Tracing không tự làm agent tốt hơn — chỉ giúp *nhìn thấy* vấn đề nhanh hơn.
- Dữ liệu nhạy cảm trong trace (PII, secret trong input/output) — cần mask/redact trước khi gửi lên cloud service.

**Chỗ phân biệt junior/middle**: junior nghĩ observability = "thêm logging". Middle hiểu đây là structured tracing với quan hệ cha-con (span tree) + cost/latency per-step, và biết phân biệt **inclusive duration** (tổng, gồm cả span con) với **self/exclusive duration** (thời gian riêng, đã trừ con) — chỉ leaf span mới có self-time = duration; span cha luôn cần trừ con mới ra con số dùng để quyết định tối ưu chỗ nào.

Không có phép toán cốt lõi (instrumentation, không phải thuật toán) — không tạo file toán riêng.

## Ví dụ áp dụng project

Domain: e-commerce recommendation agent. Agent nhận câu hỏi user → gọi tool `get_purchase_history` → gọi tool `search_products` (hybrid search) → gọi LLM tổng hợp câu trả lời. Không tracing: user báo "chậm" nhưng không biết bước nào. Có tracing: mở trace, thấy ngay span nào chiếm phần lớn latency.

## Bài thực hành

Tự viết class `Tracer` (context manager `span()`, stack theo dõi span cha hiện tại, `print_tree()`, `slowest_span()`) — không cài Langfuse thật, dừng ở mô phỏng cơ chế cốt lõi.

**File code:** `practice/10-observability.py` — dùng `importlib` load lại `practice/07-agent-patterns.py` (file tên có dấu gạch ngang, không `import` được bình thường) để tái dùng `ReActState`, `fake_llm_react_step`, `TOOL_REGISTRY` mà không sửa logic agent gốc — chỉ bọc `with tracer.span(...)` quanh từng bước, đúng cách 1 hệ thống thật "instrument" agent có sẵn.

**Đã chạy thật thành công**, và phát sinh 2 điều đáng chú ý ngoài dự kiến:
1. **Bắt được 1 bug thật trong code bài 7**: `order_id` bị parse sai (`.strip("#")` không xóa được `#` nằm giữa chuỗi) → agent luôn nhận `order_id="Đơn"` thay vì `"A1023"`. Đã sửa lại theo đúng pattern `.split("#")[1].split()[0]` mà `fake_llm_planner` cùng file đã dùng đúng. Đây là ví dụ thực tế: metadata của span `tool_call:get_order_status` hiển thị `args` sai ngay trong cây trace — giá trị thật của observability.
2. **`slowest_span()` (dựa trên inclusive duration) báo sai "thủ phạm"**: trả về `agent_run` (851ms, span gốc bao trùm cả cây) thay vì `tool_call:get_shipping_estimate` (350ms, span lá thực sự chậm) — minh họa trực tiếp khái niệm self-time vs inclusive duration ở phần lý thuyết.

## Checkpoint

**Câu 1:** Vì sao Trace 1 ("Đơn #A1023" - đang giao) chạy 3 bước còn Trace 2 ("#A2099" - đã giao) chỉ 2 bước?
**Câu 2:** Vì sao `slowest_span()` hiện tại gây hiểu lầm, và self-time tính thế nào?
**Câu 3:** Vì sao `finally: current_span.end = ...` quan trọng khi tool bên trong `with` ném exception?

→ Mình (assistant) trả lời hộ hoàn toàn cả 3 câu (giống pattern bài 7/8) — **độ tin cậy thấp hơn các bài có tự trả lời**, user chỉ đọc và xác nhận hiểu. Nếu ôn lại, ưu tiên hỏi lại đúng 3 câu này để user tự trả lời.

Nội dung câu trả lời (tóm tắt):
1. Quyết định "còn cần làm gì tiếp" trong ReAct chỉ đưa ra SAU KHI có observation — A1023 có status "đang giao" nên rơi vào nhánh gọi thêm `get_shipping_estimate` (bước 2), rồi mới final_answer (bước 3); A2099 có status "đã giao" nên bỏ qua nhánh đó, final_answer ngay ở bước 2.
2. `agent_run.duration_ms` bao gồm cả thời gian mọi span con chạy bên trong nó — không phải "công việc riêng" của nó. Self-time đúng = `duration - tổng duration của các con trực tiếp`; chỉ leaf span (không con) mới có self-time = duration. `tool_call:get_shipping_estimate` là leaf span chậm nhất thật sự (350ms), nên đó mới là nơi cần tối ưu trước.
3. `finally` đảm bảo `end` và `stack.pop()` luôn chạy dù có exception — nếu thiếu, span "treo" ở `end=None` mãi mãi, stack bị kẹt sai parent cho các span sau, và đúng lúc lỗi thật xảy ra (lúc cần trace nhất) thì trace lại hỏng/mất dữ liệu.

Kết quả: user xác nhận hiểu sau khi đọc → đánh dấu Đã học.
