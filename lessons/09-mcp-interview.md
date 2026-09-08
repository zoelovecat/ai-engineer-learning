# 09 — MCP: ghi chú phỏng vấn

Xem lý thuyết đầy đủ: [09-mcp.md](09-mcp.md)

## Q&A

**Q: MCP là gì, giải thích ngắn gọn?**
A: Giao thức chuẩn (JSON-RPC 2.0) tách agent/host (MCP client) khỏi nơi implement tool thật (MCP server). Server expose tools/resources/prompts; client discovery (`list_tools`) rồi gọi (`call_tool`) khi model quyết định dùng.

**Q: MCP có thay thế tool-calling ở tầng model không?**
A: Không. Tool-calling (model sinh JSON theo schema — bài 8) là cơ chế *bên trong* model. MCP là lớp *transport + discovery* nằm ngoài, chuẩn hóa cách tool được đăng ký/gọi giữa nhiều host và nhiều server khác nhau. Hai thứ độc lập, MCP dùng lại chính cơ chế tool-calling đó.

**Q: Vì sao cần MCP thay vì tự viết tool trực tiếp trong code agent?**
A: Khi có nhiều consumer (nhiều agent/host) cùng cần dùng chung nhiều nguồn tool (filesystem, DB, SaaS API...), viết tích hợp riêng lẻ cho từng cặp agent-tool tạo ra ma trận N×M không quản được. MCP chuẩn hóa 1 lần, dùng lại nhiều nơi.

**Q: Khi nào KHÔNG nên dùng MCP?**
A: Khi chỉ có 1 agent, vài tool cố định, không ai khác dùng lại — tự định nghĩa tool trực tiếp đơn giản hơn, tránh thêm overhead process/transport (latency round-trip, lifecycle management, auth cho server riêng).

**Q: MCP server có bao nhiêu loại capability, khác nhau thế nào?**
A: 3 loại — Tools (hàm có side-effect, agent *gọi*), Resources (dữ liệu chỉ đọc, giống GET), Prompts (template prompt dựng sẵn server cung cấp).

**Q: Discovery trong MCP hoạt động thế nào, vì sao quan trọng?**
A: Client gọi `list_tools()`/`list_resources()` tại runtime để biết server có gì, thay vì hard-code trước lúc build. Quan trọng khi tool nguồn thay đổi thường xuyên hoặc số lượng lớn — agent tự nhận tool mới mà không cần deploy lại code agent.

## Điểm dễ bị hỏi xoáy / bẫy thường gặp

- **Nhầm MCP = framework tool-calling mới**: đây là bẫy phổ biến nhất. Junior hay nói "MCP giúp model biết cách gọi tool" — sai, model vẫn dùng cơ chế structured-output/JSON schema y hệt (bài 8). MCP chỉ chuẩn hóa *nơi tool sống* và *cách client tìm ra + gọi nó*.
- **Bỏ qua cost của cache/load-once**: MCP server thường giữ state (model đã load, index đã build) qua nhiều request — nếu không cache, chi phí thật không chỉ là RAM mà là **latency cold-start lặp lại mỗi request** (load model, rebuild index), có thể biến 1 tool nhanh thành nghẽn cổ chai dưới tải. Đây là chỗ checkpoint bài này lộ ra: trả lời "tốn RAM" là đúng nhưng chưa đủ, thiếu vế latency quan trọng hơn.
- **Quên MCP thêm latency thật**: vì tool giờ chạy qua process/network riêng (stdio subprocess hoặc HTTP), không phải gọi hàm trong cùng process nữa — với tool cần độ trễ cực thấp, đây là chi phí thật cần cân nhắc, không phải free lunch.
- **Không phân biệt được khi nào MCP đáng giá**: câu hỏi xoáy thường là "sao không cứ viết function trực tiếp cho nhanh" — câu trả lời đúng phải nói tới **số lượng consumer** (bao nhiêu agent/host khác nhau dùng chung) chứ không phải chỉ "MCP là chuẩn ngành nên phải dùng".

## Bảng so sánh nhanh

| Khía cạnh | Tool-calling (bài 8) | MCP |
|---|---|---|
| Tầng nào | Bên trong model (sinh JSON theo schema) | Lớp transport/discovery bên ngoài model |
| Vấn đề giải quyết | Model gọi đúng tool, đúng tham số | Nhiều agent/host dùng chung nhiều nguồn tool mà không viết lại tích hợp |
| Chi phí thêm | Không (là cơ chế gốc của model) | Latency round-trip, lifecycle process, auth server riêng |
| Khi nào dùng | Luôn cần nếu agent có tool | Khi có ≥2 consumer hoặc nhiều nguồn tool cần chuẩn hóa; bỏ qua nếu 1 agent/tool cố định |
