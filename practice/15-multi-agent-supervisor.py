"""
Bai thuc hanh #15: Multi-agent orchestration - pattern Supervisor-Worker
Ly thuyet day du: ../lessons/15-multi-agent-orchestration.md

Use case: "Tro ly nhan su noi bo" - nhan vien hoi 1 cau, co the la:
  - Cau hoi VE CHINH SACH/luat lao dong (vd "nghi thai san duoc bao nhieu ngay?")
    -> can tra loi CHINH XAC, dua tren van ban that -> PolicyWorker
       (tai su dung THAT HybridSearchIndex tu bai 3, khong viet lai logic search)
  - Yeu cau XU LY THAT (vd "toi con bao nhieu ngay phep?", "xin nghi 3 ngay")
    -> can tra cuu/ghi vao he thong HR that -> LeaveWorker (mock database)
  - Ca 2 (vd "toi con phep khong va quy dinh toi da nghi lien tuc bao nhieu ngay?")

Diem hoc chinh: SUPERVISOR khong tu tra loi noi dung - no CHI ROUTING (quyet
dinh worker nao xu ly) va TONG HOP ket qua. Neu gop het logic nay vao 1 agent
don, system prompt se phai nhoi ca luat lao dong LAN schema HR database ->
model de nham lan (day la ly do thuc su can tach, khong phai "cho vui").

Chay: python practice/13-multi-agent-supervisor.py
"""
import sys
from dataclasses import dataclass
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from _09_hybrid_search_lib import HybridSearchIndex  # tai su dung That tu bai 3/9

# ---- Mock he thong HR that (gia lap database that, khong phai van ban luat) ----

LEAVE_DB = {
    "emp001": {"name": "Lan", "remaining_days": 5, "used_this_year": 7},
    "emp002": {"name": "Minh", "remaining_days": 0, "used_this_year": 12},
}


def get_leave_balance(employee_id: str) -> dict:
    return LEAVE_DB.get(employee_id, {"error": "khong tim thay nhan vien"})


def submit_leave_request(employee_id: str, days: int) -> dict:
    emp = LEAVE_DB.get(employee_id)
    if emp is None:
        return {"error": "khong tim thay nhan vien"}
    if emp["remaining_days"] < days:
        return {"status": "tu choi", "ly_do": f"chi con {emp['remaining_days']} ngay phep"}
    emp["remaining_days"] -= days
    emp["used_this_year"] += days
    return {"status": "da duyet", "con_lai": emp["remaining_days"]}


# ---- Worker 1: PolicyWorker - boc quanh hybrid search THAT cua bai 3 ----


class PolicyWorker:
    """Chi biet tra loi cau hoi ve VAN BAN LUAT. Khong biet gi ve LEAVE_DB."""

    def __init__(self):
        self._index = HybridSearchIndex()

    def handle(self, query: str) -> str:
        chunks = self._index.search(query, top_k=2)
        return "\n---\n".join(chunks)


# ---- Worker 2: LeaveWorker - chi biet thao tac LEAVE_DB, khong biet gi ve luat ----


class LeaveWorker:
    def handle(self, employee_id: str, action: str, days: int | None = None) -> str:
        if action == "check_balance":
            info = get_leave_balance(employee_id)
            if "error" in info:
                return info["error"]
            return f"{info['name']} con {info['remaining_days']} ngay phep (da dung {info['used_this_year']} ngay)."
        if action == "submit_request":
            result = submit_leave_request(employee_id, days)
            if "error" in result:
                return result["error"]
            if result["status"] == "tu choi":
                return f"Yeu cau bi tu choi: {result['ly_do']}"
            return f"Da duyet don nghi {days} ngay. Con lai {result['con_lai']} ngay phep."
        return "khong ro hanh dong"


# ---- Supervisor: chi ROUTING, khong tu tra loi noi dung ----
#
# TODO (diem hoc quan trong nhat): day la "LLM gia" (rule-based, giong style
# bai 7) dong vai supervisor. Voi model that, day chinh la 1 lan goi LLM voi
# structured output (bai 8) tra ve {"route": "policy"|"leave"|"both", ...} -
# KHONG PHAI tra loi cau hoi, chi phan loai + trich tham so.


@dataclass
class RouteDecision:
    needs_policy: bool
    needs_leave: bool
    leave_action: str | None = None
    leave_days: int | None = None


def fake_supervisor_route(query: str) -> RouteDecision:
    q = query.lower()
    needs_policy = any(kw in q for kw in ["quy dinh", "luat", "toi da", "duoc bao nhieu", "dieu"])
    needs_leave = any(kw in q for kw in ["con bao nhieu ngay phep", "xin nghi", "con phep"])

    leave_action = None
    leave_days = None
    if "xin nghi" in q:
        leave_action = "submit_request"
        for token in q.split():
            if token.isdigit():
                leave_days = int(token)
        leave_days = leave_days or 1
    elif needs_leave:
        leave_action = "check_balance"

    return RouteDecision(needs_policy, needs_leave, leave_action, leave_days)


class Supervisor:
    def __init__(self):
        self.policy_worker = PolicyWorker()
        self.leave_worker = LeaveWorker()

    def handle(self, query: str, employee_id: str) -> str:
        route = fake_supervisor_route(query)
        parts = []

        if route.needs_policy:
            parts.append("[Chinh sach] " + self.policy_worker.handle(query))

        if route.needs_leave:
            parts.append(
                "[Phep cua ban] "
                + self.leave_worker.handle(employee_id, route.leave_action, route.leave_days)
            )

        if not parts:
            return "Khong xac dinh duoc yeu cau thuoc nhom nao (policy/leave)."

        return "\n\n".join(parts)


if __name__ == "__main__":
    supervisor = Supervisor()

    print("=== Query 1: chi hoi chinh sach ===")
    print(supervisor.handle("Quy dinh nghi thai san duoc bao nhieu ngay?", "emp001"))

    print("\n=== Query 2: chi hoi phep cua minh (leave) ===")
    print(supervisor.handle("Toi con bao nhieu ngay phep?", "emp001"))

    print("\n=== Query 3: CA 2 - can ca policy worker LAN leave worker ===")
    print(
        supervisor.handle(
            "Quy dinh toi da nghi lien tuc bao nhieu ngay va toi con bao nhieu ngay phep?",
            "emp001",
        )
    )

    print("\n=== Query 4: xin nghi that - se bi TU CHOI (emp002 het phep) ===")
    print(supervisor.handle("Xin nghi 2 ngay", "emp002"))
