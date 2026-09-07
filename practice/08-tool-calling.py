"""
Bai thuc hanh #8: Tool-calling o tang model (structured output/JSON schema)
Ly thuyet day du: ../lessons/08-tool-calling.md

Cai dat (chi can neu muon goi model THAT): pip install anthropic

Neu co bien moi truong ANTHROPIC_API_KEY -> goi model that (Claude) de thay
dung cach model sinh tool_use block.
Neu KHONG co key -> chay o che do "recorded" (dung lai 1 response THAT da
duoc ghi lai truoc do, dinh dang y het API that) de van thay duoc cau truc
request/response ma khong can mang/API key.
"""
import json
import os

# ---- Dinh nghia tool bang JSON Schema - day chinh la thu gui len model ----
# Day la "hop dong" model dua vao de biet: co nhung tool nao, tool can tham
# so gi, kieu du lieu gi. Model KHONG chay code Python nay - no chi doc
# ban mo ta nay (dang text trong request) de QUYET DINH sinh ra JSON nao.

TOOLS = [
    {
        "name": "get_order_status",
        "description": (
            "Tra cứu trạng thái vận chuyển hiện tại của MỘT đơn hàng theo mã đơn. "
            "Dùng khi khách hỏi đơn hàng đã tới đâu, còn bao lâu nữa tới, hay đã giao chưa."
        ),
        "input_schema": {
            "type": "object",
            "properties": {
                "order_id": {
                    "type": "string",
                    "description": "Mã đơn hàng, định dạng chữ cái + số, ví dụ 'A1023'.",
                }
            },
            "required": ["order_id"],
        },
    },
    {
        "name": "get_customer_info",
        "description": "Tra cứu thông tin tài khoản khách hàng (tên, email, lịch sử mua) theo mã khách hàng.",
        "input_schema": {
            "type": "object",
            "properties": {
                "customer_id": {"type": "string", "description": "Mã khách hàng, ví dụ 'C500'."}
            },
            "required": ["customer_id"],
        },
    },
]

ORDERS_DB = {"A1023": {"status": "đang giao", "eta_days": 2}}


def get_order_status(order_id: str) -> dict:
    return ORDERS_DB.get(order_id, {"status": "không tìm thấy"})


def get_customer_info(customer_id: str) -> dict:
    return {"customer_id": customer_id, "name": "(demo) Nguyễn Văn A"}


TOOL_REGISTRY = {"get_order_status": get_order_status, "get_customer_info": get_customer_info}

USER_QUERY = "Đơn A1023 của tôi bao giờ tới?"


def run_with_real_model(api_key: str):
    """Goi model that (Claude) - se thay model TU SINH ra tool_use block dua
    tren TOOLS schema o tren, khong co if/else nao trong code quyet dinh dieu do.
    """
    import anthropic

    client = anthropic.Anthropic(api_key=api_key)

    print("=== Request gui len model (rut gon) ===")
    print(json.dumps({"tools": TOOLS, "messages": [{"role": "user", "content": USER_QUERY}]}, ensure_ascii=False, indent=2))

    response = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        tools=TOOLS,
        messages=[{"role": "user", "content": USER_QUERY}],
    )

    print("\n=== Response tho tu model (content blocks) ===")
    for block in response.content:
        print(f"  type={block.type}", end="")
        if block.type == "tool_use":
            print(f" name={block.name} input={block.input}")
        elif block.type == "text":
            print(f" text={block.text!r}")
        else:
            print()

    tool_use_blocks = [b for b in response.content if b.type == "tool_use"]
    if not tool_use_blocks:
        print("\n(Model quyết định trả lời trực tiếp, không gọi tool nào.)")
        return

    tool_block = tool_use_blocks[0]
    tool_fn = TOOL_REGISTRY[tool_block.name]
    result = tool_fn(**tool_block.input)
    print(f"\n=== Client tự thực thi tool '{tool_block.name}' -> {result} ===")

    # Gui tool_result nguoc lai cho model o luot tiep theo de model tong hop cau tra loi
    follow_up = client.messages.create(
        model="claude-sonnet-4-5",
        max_tokens=1024,
        tools=TOOLS,
        messages=[
            {"role": "user", "content": USER_QUERY},
            {"role": "assistant", "content": response.content},
            {
                "role": "user",
                "content": [
                    {
                        "type": "tool_result",
                        "tool_use_id": tool_block.id,
                        "content": json.dumps(result, ensure_ascii=False),
                    }
                ],
            },
        ],
    )
    final_text = "".join(b.text for b in follow_up.content if b.type == "text")
    print(f"\n=== Câu trả lời cuối cùng của model ===\n{final_text}")


def run_recorded_example():
    """Che do offline: dung 1 vi du MO PHONG dung dinh dang that Anthropic API
    tra ve (KHONG PHAI output that da goi API - minh tu viet tay vi du nay
    de khop dinh dang thuc te), de phan tich cau truc ma khong can goi mang.
    Khac voi mock if/else o bai 7 (tu quyet dinh logic gia), o day muc dich
    la XEM DUNG HINH DANG du lieu model thuc te se tra ve, khong mo phong logic.
    """
    example_response_content = [
        {
            "type": "text",
            "text": "Để trả lời câu hỏi này, tôi cần tra cứu trạng thái đơn hàng A1023.",
        },
        {
            "type": "tool_use",
            "id": "toolu_01Abc123RecordedExample",
            "name": "get_order_status",
            "input": {"order_id": "A1023"},
        },
    ]

    print("=== Request đã gửi (rút gọn) ===")
    print(json.dumps({"tools": [t["name"] for t in TOOLS], "messages": [{"role": "user", "content": USER_QUERY}]}, ensure_ascii=False, indent=2))

    print("\n=== Ví dụ mô phỏng đúng định dạng response thật (không gọi mạng, chỉ để phân tích cấu trúc) ===")
    for block in example_response_content:
        print(f"  {json.dumps(block, ensure_ascii=False)}")

    # Diem quan trong: model TU QUYET DINH sinh ra block "tool_use" voi dung
    # ten tool ("get_order_status") va dung field "order_id" khop input_schema
    # da khai bao - khong co code Python nao ep buoc dieu nay, chi la ket qua
    # cua qua trinh sinh token duoc huong boi tool schema trong request.
    tool_block = next(b for b in example_response_content if b["type"] == "tool_use")
    tool_fn = TOOL_REGISTRY[tool_block["name"]]
    result = tool_fn(**tool_block["input"])
    print(f"\n=== Client tự thực thi tool '{tool_block['name']}' -> {result} ===")
    print("(Bước tiếp theo trong thực tế: gửi 'result' này ngược lại cho model dạng tool_result")
    print(" để model tổng hợp câu trả lời cuối cùng - xem hàm run_with_real_model() ở trên")
    print(" để thấy chính xác cách gửi tool_result trong request thứ 2.)")


if __name__ == "__main__":
    api_key = os.environ.get("ANTHROPIC_API_KEY")
    if api_key:
        run_with_real_model(api_key)
    else:
        print("(Không thấy ANTHROPIC_API_KEY trong môi trường - chạy chế độ recorded example.")
        print(" Muốn gọi model thật: pip install anthropic, set ANTHROPIC_API_KEY, chạy lại.)\n")
        run_recorded_example()

    # Checkpoint quan sat (tu lam sau khi doc/chay code):
    # - Trong "input" cua tool_use block, ten field la gi? Doi chieu voi
    #   "input_schema" cua tool get_order_status o dau file - co khop chinh
    #   xac ten field "order_id" khong?
    # - Neu doi description cua get_order_status thanh mot cau MO HO (vd chi
    #   ghi "lay thong tin don"), va them 1 tool thu 3 ten gan giong (vd
    #   "check_shipment"), ban nghi model co the chon SAI tool khong? Vi sao
    #   (doi chieu voi phan ly thuyet "vi sao can hieu sau" trong lessons/08).
    # - Neu co ANTHROPIC_API_KEY that, thu doi USER_QUERY thanh mot cau KHONG
    #   lien quan tool nao ca (vd "Cong ty ban co chinh sach doi tra khong?")
    #   - model co goi tool nao khong, hay tra loi text truc tiep?
