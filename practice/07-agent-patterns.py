"""
Bai thuc hanh #7: Pattern suy luan agent - ReAct vs Plan-and-Execute
Ly thuyet day du: ../lessons/07-agent-patterns.md

Khong can API key that: dung 1 "LLM gia" (mock, rule-based) de tap trung vao
KIEN TRUC DIEU KHIEN (control flow) cua tung pattern, khong phu thuoc chat
luong suy luan cua model that.

Khong can cai dat gi them (chi dung standard library).
"""
from dataclasses import dataclass, field


# ---- Mock tools: gia lap he thong e-commerce that ----

ORDERS_DB = {
    "A1023": {"status": "đang giao", "carrier": "GHTK", "eta_days": 2},
    "A2099": {"status": "đã giao", "carrier": "GHN", "eta_days": 0},
    "A3050": {"status": "chưa gửi", "carrier": None, "eta_days": None},
}


def get_order_status(order_id: str) -> dict:
    return ORDERS_DB.get(order_id, {"status": "không tìm thấy đơn hàng"})


def get_shipping_estimate(carrier: str) -> dict:
    # TODO (hoc: day la 1 tool THAT trong he thong that se goi API van chuyen -
    # o day gia lap don gian, carrier khac nhau co SLA khac nhau)
    sla = {"GHTK": "1-3 ngày", "GHN": "2-4 ngày"}
    return {"carrier": carrier, "sla": sla.get(carrier, "không rõ SLA")}


# =====================================================================
# PATTERN 1: ReAct (Reason + Act) - vong lap Thought -> Action -> Observation
# =====================================================================
#
# TODO (diem hoc quan trong nhat cua ReAct): so lan goi "LLM" (o day la ham
# fake_llm_react_step) KHONG CO DINH TRUOC - vong while chay toi khi model
# tu quyet dinh tra ve final_answer. Voi model that, so buoc co the la 1, 2,
# hay 5 tuy cau hoi va observation tra ve - day la diem khac biet cot loi
# so voi Plan-and-Execute o duoi.

@dataclass
class ReActState:
    query: str
    history: list = field(default_factory=list)  # list cac dict {thought, action, observation}


def fake_llm_react_step(state: ReActState) -> dict:
    """Gia lap 1 lan goi LLM trong vong lap ReAct.
    Rule don gian (thay cho suy luan that): buoc dau tien luon tra order
    status; neu status = 'dang giao' thi buoc tiep theo tra shipping estimate;
    cac truong hop khac tra loi luon.
    Tra ve 1 trong 2 dang:
      {"thought": ..., "action": "call_tool", "tool": ..., "args": {...}}
      {"thought": ..., "action": "final_answer", "text": ...}
    """
    n_steps = len(state.history)

    if n_steps == 0:
        # TODO (hoc: buoc dau luon can du lieu tho truoc khi tra loi - khong
        # the tra loi ngay vi chua co observation nao)
        order_id = state.query.split("#")[1].split()[0] if "#" in state.query else "A1023"
        return {
            "thought": f"Cần tra trạng thái đơn hàng {order_id} trước khi trả lời.",
            "action": "call_tool",
            "tool": "get_order_status",
            "args": {"order_id": order_id},
        }

    last_observation = state.history[-1]["observation"]

    if n_steps == 1 and last_observation.get("status") == "đang giao":
        # TODO (hoc: day la buoc THE HIEN RO NHAT tinh chat ReAct - quyet dinh
        # nay CHI duoc dua ra SAU KHI thay observation buoc truoc; neu status
        # la 'da giao' hoac 'chua gui' thi se KHONG di vao nhanh nay, se tra
        # loi luon o nhanh else ben duoi - so buoc thuc te khac nhau tuy du lieu)
        return {
            "thought": "Đơn đang giao, cần tra thêm SLA vận chuyển để ước tính ngày nhận.",
            "action": "call_tool",
            "tool": "get_shipping_estimate",
            "args": {"carrier": last_observation["carrier"]},
        }

    # Du du thong tin -> tong hop cau tra loi cuoi cung
    order_info = state.history[0]["observation"]
    if order_info.get("status") == "đang giao" and len(state.history) > 1:
        shipping_info = state.history[1]["observation"]
        text = (
            f"Đơn hàng đang giao qua {order_info['carrier']}, dự kiến "
            f"{order_info['eta_days']} ngày nữa (SLA {shipping_info['carrier']}: "
            f"{shipping_info['sla']})."
        )
    else:
        text = f"Trạng thái đơn hàng: {order_info.get('status')}."

    return {"thought": "Đã đủ thông tin để trả lời.", "action": "final_answer", "text": text}


TOOL_REGISTRY = {
    "get_order_status": get_order_status,
    "get_shipping_estimate": get_shipping_estimate,
}


def run_react(query: str, max_steps: int = 5) -> str:
    state = ReActState(query=query)
    for step in range(max_steps):
        decision = fake_llm_react_step(state)
        print(f"  [ReAct step {step + 1}] Thought: {decision['thought']}")

        if decision["action"] == "final_answer":
            print(f"  [ReAct step {step + 1}] Final answer: {decision['text']}")
            return decision["text"]

        tool_fn = TOOL_REGISTRY[decision["tool"]]
        observation = tool_fn(**decision["args"])
        print(f"  [ReAct step {step + 1}] Action: {decision['tool']}({decision['args']}) -> Observation: {observation}")
        state.history.append({**decision, "observation": observation})

    raise RuntimeError("Vượt quá max_steps mà chưa có final_answer - dấu hiệu agent 'lạc đường'.")


# =====================================================================
# PATTERN 2: Plan-and-Execute - lap ke hoach TRUOC, roi thuc thi tuan tu
# =====================================================================
#
# TODO (diem hoc quan trong nhat cua Plan-and-Execute): plan duoc sinh ra
# MOT LAN DUY NHAT, TRUOC KHI bat dau thuc thi bat ky buoc nao - khac han
# ReAct (quyet dinh tung buoc dua tren observation truoc do). He qua: co the
# AUDIT/REVIEW toan bo plan truoc khi agent lam gi ca - quan trong voi hanh
# dong co anh huong that (vd tao hoan tien).

def fake_llm_planner(query: str) -> list[dict]:
    """Gia lap Planner: sinh 1 danh sach buoc CO DINH dua tren loai yeu cau,
    khong phu thuoc observation (vi CHUA CO observation nao luc lap ke hoach).
    """
    if "đổi trả" in query or "hoàn tiền" in query:
        order_id = query.split("#")[1].split()[0] if "#" in query else "A1023"
        return [
            {"tool": "get_order_status", "args": {"order_id": order_id}},
            {"step": "kiểm tra điều kiện đổi trả (giả lập: luôn hợp lệ trong bài tập này)"},
            {"step": "tổng hợp câu trả lời xác nhận đã ghi nhận yêu cầu đổi trả"},
        ]
    order_id = query.split("#")[1].split()[0] if "#" in query else "A1023"
    return [
        {"tool": "get_order_status", "args": {"order_id": order_id}},
        {"step": "tổng hợp câu trả lời từ trạng thái đơn hàng"},
    ]


def run_plan_and_execute(query: str) -> str:
    plan = fake_llm_planner(query)

    # TODO (hoc: day la diem "audit truoc khi chay" - voi ReAct KHONG THE in
    # ra toan bo cac buoc truoc, vi buoc 2 chi duoc quyet dinh SAU KHI co
    # observation cua buoc 1)
    print("  [Plan] Kế hoạch đã lập (audit được TRƯỚC khi thực thi):")
    for i, item in enumerate(plan, start=1):
        label = item.get("tool", item.get("step"))
        print(f"    {i}. {label}")

    observations = []
    for i, item in enumerate(plan, start=1):
        if "tool" in item:
            tool_fn = TOOL_REGISTRY[item["tool"]]
            result = tool_fn(**item["args"])
            observations.append(result)
            print(f"  [Execute step {i}] {item['tool']}({item['args']}) -> {result}")
        else:
            print(f"  [Execute step {i}] (bước không gọi tool) {item['step']}")

    order_info = observations[0] if observations else {}
    if "hợp lệ" in str(plan):
        text = f"Đã ghi nhận yêu cầu đổi trả, trạng thái đơn hàng hiện tại: {order_info.get('status')}."
    else:
        text = f"Trạng thái đơn hàng: {order_info.get('status')}."
    print(f"  [Plan-and-Execute] Final answer: {text}")
    return text


if __name__ == "__main__":
    print("########## Query 1: 'Đơn #A1023 của tôi bao giờ tới?' (ReAct) ##########")
    run_react("Đơn #A1023 của tôi bao giờ tới?")

    print("\n########## Query 2: 'Đơn #A2099 đã tới chưa?' (ReAct, ít bước hơn) ##########")
    run_react("Đơn #A2099 đã tới chưa?")

    print("\n########## Query 3: 'Đổi trả đơn #A1023 vì hàng lỗi, xử lý hoàn tiền giúp tôi' (Plan-and-Execute) ##########")
    run_plan_and_execute("Đổi trả đơn #A1023 vì hàng lỗi, xử lý hoàn tiền giúp tôi")

    # Checkpoint quan sat (tu lam sau khi doc/chay code):
    # - Query 1 va Query 2 chay qua BAO NHIEU buoc ReAct? Vi sao khac nhau
    #   (doi chieu voi nhanh if trong fake_llm_react_step)?
    # - O Plan-and-Execute, ke hoach duoc in ra TRUOC khi tool nao duoc goi -
    #   dieu nay co lam duoc voi ReAct khong? Vi sao khong (hoac co, nhung
    #   phai danh doi gi)?
    # - Neu doi order_id thanh "A3050" (chua gui) trong Query 1, ReAct se di
    #   theo nhanh nao trong fake_llm_react_step? Thu sua code va chay lai.
