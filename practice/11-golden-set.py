"""
Bai thuc hanh #11: Eval dataset / golden set - phat hien regression.
Ly thuyet day du: ../lessons/11-golden-set.md

Tai su dung agent ReAct o bai 7 (practice/07-agent-patterns.py, qua
importlib giong bai 10) lam "he thong duoi test". Khong can cai dat gi
them (chi standard library).

Y tuong cot loi cua bai nay:
1. Xay 1 GOLDEN SET co dinh: danh sach cau hoi + "key fact" BAT BUOC phai
   xuat hien trong cau tra loi cuoi cung (khong doi hoi EXACT MATCH tung
   chu, vi agent/LLM co the dien dat khac nhau ma van dung y).
2. Chay golden set qua agent HIEN TAI -> ghi lai ket qua BASELINE.
3. Gia lap 1 "code change" That co regression (bug tinh huong: sua bang
   SLA van chuyen, vo tinh doi key tu chu HOA sang chu thuong) - KHONG co
   exception nao xay ra, code van chay binh thuong, nhung KET QUA SAI.
4. Chay lai golden set SAU khi co bug -> so sanh voi BASELINE -> phat hien
   dung case nao tu PASS thanh FAIL = REGRESSION, bat duoc TRUOC khi deploy,
   khong phai cho user bao loi.
"""
import importlib.util
import pathlib

# Tai lai module bai 7 (ten file co dau gach ngang nen khong `import` binh
# thuong duoc) - dung lai NGUYEN VEN agent ReAct, khong sua logic ben trong.
_AGENT_07_PATH = pathlib.Path(__file__).parent / "07-agent-patterns.py"
_spec = importlib.util.spec_from_file_location("agent_patterns_07", _AGENT_07_PATH)
agent_07 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(agent_07)


# =====================================================================
# PHAN 1: Golden set - danh sach case CO DINH, dai dien nhieu nhanh logic
# khac nhau cua agent (dang giao / da giao / chua gui / khong tim thay)
# =====================================================================
#
# Moi case la 1 "hop dong" ve hanh vi mong muon: KHONG quan tam agent viet
# cau tra loi chinh xac tu nao, CHI quan tam cac "key fact" nay co mat hay
# khong. Day la ly do dat ten "expected_keyphrases" (nhieu cum, khong phai
# 1 cau dap an duy nhat).
GOLDEN_SET = [
    {
        "id": "order_in_transit",
        "query": "Đơn #A1023 của tôi bao giờ tới?",
        # Don A1023 trong ORDERS_DB (bai 7): status="đang giao", carrier="GHTK",
        # eta_days=2 -> cau tra loi phai neu ro CA 3 fact nay + SLA cua carrier.
        "expected_keyphrases": ["GHTK", "2 ngày", "1-3 ngày"],
    },
    {
        "id": "order_delivered",
        "query": "Đơn #A2099 đã tới chưa?",
        # Don A2099: status="đã giao" -> agent dung o buoc 1, khong goi
        # them get_shipping_estimate (xem lai checkpoint bai 7/10).
        "expected_keyphrases": ["đã giao"],
    },
    {
        "id": "order_not_shipped",
        "query": "Đơn #A3050 ở đâu rồi?",
        # Don A3050: status="chưa gửi", carrier=None -> nhanh "khong dang
        # giao" trong fake_llm_react_step, tra loi truc tiep trang thai.
        "expected_keyphrases": ["chưa gửi"],
    },
    {
        "id": "order_unknown",
        "query": "Đơn #Z999 của tôi đâu rồi?",
        # Ma don khong ton tai trong ORDERS_DB -> get_order_status tra ve
        # {"status": "không tìm thấy đơn hàng"} (xem ham get_order_status bai 7).
        "expected_keyphrases": ["không tìm thấy"],
    },
]


def check_keyphrases(answer: str, expected_keyphrases: list[str]) -> tuple[bool, list[str]]:
    """So khop KIEU 'phai chua cum tu' (khong phai so sanh ca cau tung chu
    mot). Day la lua chon phu hop cho output cua LLM/agent: 2 cau tra loi
    khac nhau ve tu ngu nhung cung dung y van phai duoc coi la PASS - neu
    dung exact string match, agent chi can doi 1 dau cham/1 cach dien dat
    la bi bao FAIL oan, lam golden set vo dung trong thuc te.

    Tra ve (co PASS khong, danh sach keyphrase con THIEU) de bao loi chi
    tiet duoc keyphrase nao mat, khong chi bao PASS/FAIL chung chung.
    """
    missing = [kp for kp in expected_keyphrases if kp.lower() not in answer.lower()]
    return (len(missing) == 0, missing)


def run_golden_set(golden_set: list[dict], agent_fn, label: str) -> dict:
    """Chay toan bo golden set qua `agent_fn` (1 ham nhan query, tra ve
    cau tra loi cuoi cung dang string), in ket qua tung case, tra ve
    tong ket de so sanh giua 2 lan chay (truoc/sau thay doi code).
    """
    print(f"\n{'=' * 70}")
    print(f"GOLDEN SET RUN: {label}")
    print("=" * 70)

    results = {"passed": 0, "failed": 0, "failures": []}
    for case in golden_set:
        answer = agent_fn(case["query"])
        passed, missing = check_keyphrases(answer, case["expected_keyphrases"])
        status = "PASS" if passed else "FAIL"
        print(f"[{status}] {case['id']}: {case['query']!r}")
        print(f"       answer: {answer}")
        if passed:
            results["passed"] += 1
        else:
            print(f"       thiếu keyphrase: {missing}")
            results["failed"] += 1
            results["failures"].append(case["id"])

    total = results["passed"] + results["failed"]
    print(f"\n-> {results['passed']}/{total} PASS")
    return results


def run_agent(query: str) -> str:
    """Wrapper goi thang ham run_react cua bai 7 (khong can tracer o day -
    golden set quan tam DUNG/SAI, khong quan tam latency - do la viec cua
    bai 10)."""
    return agent_07.run_react(query, max_steps=5)


if __name__ == "__main__":
    # ---- Buoc 1: chay golden set voi code HIEN TAI, luu lam baseline ----
    baseline = run_golden_set(GOLDEN_SET, run_agent, "BASELINE (code hiện tại, chưa đổi gì)")

    # =================================================================
    # ---- Buoc 2: MO PHONG 1 "code change" gay regression that -------
    # =================================================================
    #
    # Tinh huong that hay gap: 1 dev sua lai bang tra cuu SLA van chuyen
    # (co the vi them 1 hang van chuyen moi, hoac refactor lai cho "gon"),
    # va VO TINH doi key trong dict tu chu HOA "GHTK" sang chu thuong
    # "ghtk". Code KHONG co loi cu phap, KHONG nem exception, chay binh
    # thuong tu dau den cuoi - nhung vi carrier truyen vao van la "GHTK"
    # (tu ORDERS_DB, khong doi), dict.get("GHTK") tren bang moi (chi co
    # key "ghtk") se KHONG tim thay, roi ve gia tri mac dinh "không rõ SLA".
    #
    # Day chinh la kieu bug NGUY HIEM NHAT: khong on ao (khong crash), chi
    # lam SAI 1 phan nho cua ket qua - neu khong co golden set, se khong ai
    # phat hien ra cho toi khi user complain.
    def buggy_get_shipping_estimate(carrier: str) -> dict:
        sla = {"ghtk": "1-3 ngày", "ghn": "2-4 ngày"}  # BUG: key viết thường
        return {"carrier": carrier, "sla": sla.get(carrier, "không rõ SLA")}

    agent_07.TOOL_REGISTRY["get_shipping_estimate"] = buggy_get_shipping_estimate

    after_change = run_golden_set(
        GOLDEN_SET, run_agent, "SAU KHI CO 1 CODE CHANGE (mô phỏng bug thật)"
    )

    # ---- Buoc 3: DIFF ket qua truoc/sau - day la gia tri that cua golden set ----
    print(f"\n{'=' * 70}")
    print("SO SANH BASELINE vs SAU THAY DOI:")
    print("=" * 70)
    new_failures = set(after_change["failures"]) - set(baseline["failures"])
    if new_failures:
        print(f"REGRESSION PHÁT HIỆN ở case: {sorted(new_failures)}")
        print("-> Case nay TUNG PASS o baseline, gio FAIL sau thay doi code.")
        print("-> Neu day la CI pipeline that, buoc nay se CHAN merge/deploy.")
    else:
        print("Không có regression mới.")

    # Checkpoint quan sat (tu tra loi sau khi doc/chay code):
    # 1. Case "order_in_transit" sau khi co bug co PASS hay FAIL? Neu FAIL,
    #    keyphrase nao bi thieu - co phai TAT CA 3 keyphrase deu mat, hay
    #    chi 1 phan? Giai thich tai sao (doi chieu cau tra loi cuoi cung
    #    trong fake_llm_react_step: no ghep tu CA order_info LAN
    #    shipping_info, chi phan nao lien quan SLA moi bi anh huong).
    # 2. Cac case khac (order_delivered, order_not_shipped, order_unknown)
    #    co bi anh huong boi bug nay khong? Vi sao khong (goi y: chung co
    #    goi toi get_shipping_estimate khong)?
    # 3. Neu check_keyphrases dung EXACT MATCH ca cau (thay vi "phai chua
    #    cum tu") thi golden set nay co con dung duoc voi 1 agent that
    #    (LLM that, khong phai mock rule-based) khong? Vi sao?
