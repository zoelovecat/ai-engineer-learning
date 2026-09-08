# 09 — Model Context Protocol (MCP)

**Ngày tạo:** 2026-09-08
**Trạng thái:** Đã học

## Lý thuyết

### 1. Nó là gì — cơ chế thật

Trước MCP, mỗi agent muốn dùng tool (đọc file, query DB, gọi API Slack...) phải tự viết code tích hợp riêng cho từng tool, theo format riêng của từng framework (LangChain tool, OpenAI function, v.v). Kết quả: N agent × M tool = N×M lần tích hợp.

MCP là một **giao thức chuẩn (client-server, dựa trên JSON-RPC 2.0)** để tách hai phía:

- **MCP Server**: expose "khả năng" (capabilities) — chia làm 3 loại:
  - **Tools**: hàm agent có thể *gọi* (có side-effect), ví dụ `create_ticket(title, desc)`.
  - **Resources**: dữ liệu agent có thể *đọc* (giống GET), ví dụ nội dung 1 file, 1 dòng DB.
  - **Prompts**: template prompt dựng sẵn server cung cấp cho client dùng lại.
- **MCP Client**: sống trong host app (Claude Desktop, Claude Code, IDE...) — kết nối tới 1 hoặc nhiều server, hỏi "bạn có tool/resource gì" (`list_tools`, `list_resources`), rồi gọi (`call_tool`) khi model quyết định cần dùng.

Cơ chế runtime cụ thể:
1. Host khởi động, spawn/connect tới các MCP server đã cấu hình (qua stdio subprocess, hoặc HTTP+SSE cho server chạy remote).
2. Client gửi handshake `initialize`, server trả về danh sách capabilities + schema (giống JSON schema của tool-calling ở bài 8).
3. Client gộp tool list từ *tất cả* server đang kết nối, đưa vào system context cho model như thể chúng là tool nội bộ.
4. Model quyết định gọi tool nào (dùng structured output y hệt bài 8) → client route request đó tới đúng MCP server → server thực thi → trả kết quả → client đưa lại vào context model.

Điểm mấu chốt: **MCP không thay thế tool-calling ở tầng model** (bài 8) — nó là lớp *vận chuyển và khám phá* (transport + discovery) nằm phía trên. Model vẫn sinh JSON gọi tool y hệt; MCP chỉ chuẩn hóa cách tool đó được đăng ký, mô tả, và thực thi ở phía ngoài.

### 2. Vì sao cần nó — bài toán nó giải quyết

- **Tái sử dụng chéo**: 1 MCP server viết cho "GitHub" dùng được với Claude Desktop, Claude Code, Cursor, hoặc agent tự viết bất kỳ — không cần viết lại integration cho từng framework.
- **Tách trách nhiệm**: người viết MCP server không cần biết agent nào sẽ dùng nó; người build agent không cần biết chi tiết implementation bên trong tool.
- **Discovery động**: agent có thể *hỏi* server "bạn có gì" tại runtime thay vì hard-code danh sách tool lúc build — quan trọng khi số lượng tool lớn hoặc thay đổi thường xuyên.
- Đây là điều tutorial cơ bản "gọi 1 function trong Python" hay bỏ qua: khi có **nhiều nguồn tool khác nhau** và **nhiều agent/host khác nhau** cùng cần dùng chung, tự build tích hợp riêng lẻ sẽ nổ ra thành ma trận không quản được — MCP chuẩn hóa lớp đó.

### 3. Trade-off / khi nào KHÔNG cần MCP

- Nếu chỉ có **1 agent, vài tool cố định, không ai khác dùng lại** → tự định nghĩa tool trực tiếp (bài 8) đơn giản hơn, đỡ thêm 1 lớp process/transport không cần thiết.
- MCP thêm **latency** thật (round-trip qua process/network) so với gọi hàm Python trực tiếp trong cùng process.
- MCP server chạy như **process/service riêng** → phải lo thêm: lifecycle (start/stop/crash), auth/permission cho từng server (nhất là remote qua HTTP), version compatibility client/server.
- Không phải "giải pháp agent" — chỉ chuẩn hóa I/O giữa agent và tool. Vẫn cần tự thiết kế đúng tool nào expose (tránh tool sponge — expose quá nhiều tool làm model bối rối chọn sai, giống vấn đề ở bài 8).

**Chỗ phân biệt junior/middle**: junior nghĩ "MCP = tool calling framework mới". Middle hiểu MCP là **transport/discovery layer**, tách biệt với cơ chế tool-calling của model — và biết đánh giá khi nào lớp gián tiếp này đáng giá (nhiều consumer, nhiều tool nguồn khác nhau) hay chỉ là overhead thừa.

Không có phép toán cốt lõi trong concept này (protocol, không phải thuật toán) — không tạo file toán riêng.

## Ví dụ áp dụng project

Domain: internal tooling / coding assistant. Coding assistant nội bộ cần: đọc file trong repo, query bảng "known issues" Postgres, tạo ticket Jira. Không có MCP: viết 3 tool riêng, hard-code trong agent; nếu công ty có agent thứ 2 (Slack bot hỗ trợ dev) cần y hệt 3 khả năng đó → viết lại từ đầu. Có MCP: viết 3 MCP server (filesystem, postgres, jira) một lần — cả coding assistant lẫn Slack bot connect vào, không viết lại integration.

## Bài thực hành

Viết 1 MCP server tối giản expose tool `search_law(query, top_k)`, tái dùng logic hybrid search (BM25 + vector + RRF) từ bài 3 làm phần thực thi bên trong. Kèm 1 client tối giản để chứng minh client không cần biết implementation bên trong.

**File code:**
- `practice/_09_hybrid_search_lib.py` — đóng gói lại logic bài 3 (`chunk_heading_aware`, `bm25_rank`, `vector_rank`, `rrf_fusion`) thành class `HybridSearchIndex` tái dùng được (load model 1 lần).
- `practice/09-mcp-server.py` — MCP server dùng `mcp.server.MCPServer` (API FastMCP-style của SDK `mcp` 2.x), expose 1 tool `search_law` qua decorator `@server.tool()` (tự sinh JSON schema từ type hint).
- `practice/09-mcp-client.py` — client tối giản, tự spawn server qua stdio, gọi `list_tools()` (discovery) rồi `call_tool("search_law", {...})`.

**Đã chạy thật thành công** (không chỉ viết code): cài `mcp` SDK (bản 2.2.0) + `rank_bm25`/`sentence-transformers`/`numpy`, chạy client → discovery lấy đúng schema `{query: str, top_k: int=5}`, gọi tool trả về đúng Điều 35/36 cho query "công ty tự ý cho tôi nghỉ việc thì sao" — khớp kết quả hybrid search đã có ở bài 3.

**Lưu ý phiên bản SDK**: `mcp` 2.x đã đổi API so với tài liệu cũ — không còn `Server` + decorator `@server.list_tools()`/`@server.call_tool()` thủ công (low-level), mà dùng `MCPServer` (FastMCP-style) với `@server.tool()` tự sinh schema từ type hint hàm Python. Field trả về cũng đổi tên: `tool.input_schema` (snake_case) thay vì `tool.inputSchema`.

## Checkpoint

**Câu 1:** Nếu build thêm 1 agent thứ 2 (Slack bot nội bộ) cũng cần tra cứu luật y hệt, có phải viết lại `HybridSearchIndex`/BM25/vector không? Vì sao MCP giúp tránh việc đó?
→ User trả lời đúng: không cần, vì MCP đã định nghĩa tool đó rồi — các agent khác chỉ việc dùng chung bộ tool (kết nối vào cùng MCP server), không cần viết lại logic bên trong.

**Câu 2:** Server hiện tại load model + build BM25 index 1 lần lúc khởi động (biến `_index` global), không load lại mỗi lần gọi tool. Nếu bỏ cache này, hệ quả thực tế khi có nhiều request liên tiếp là gì?
→ User trả lời: tốn RAM (đúng nhưng chưa đủ). Bổ sung: vấn đề nghiêm trọng hơn là **latency** — load model + encode lại toàn bộ corpus mỗi request có thể mất hàng chục giây với corpus lớn, biến tool nhanh thành cực chậm dưới tải; đây là ví dụ tách biệt chi phí cold-start (khởi tạo) khỏi chi phí serving (phục vụ mỗi request).

Kết quả: đạt (sau khi bổ sung ý latency ở câu 2, user xác nhận hiểu) → đánh dấu Đã học.
