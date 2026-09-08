"""
Bai thuc hanh #12: LLM-as-judge - dung 1 "giam khao" LLM de cham diem cau
tra loi cua agent/LLM khac, VA tu kiem chung do tin cay cua giam khao do
truoc khi tin no (khong phai cu cham la xong).
Ly thuyet day du: ../lessons/12-llm-as-judge.md

Dung mock judge (rule-based, KHONG goi API that) de tap trung vao CO CHE
va DIEM YEU cua LLM-as-judge, giong cach bai 7 dung "fake_llm" de tap trung
vao control-flow. Khong can cai dat gi them.

Diem quan trong nhat bai nay muon minh hoa: mock judge duoi day CO CHU Y
KHONG duoc cap ground truth (dung carrier/eta la gi) - giong nhieu tinh
huong LLM-as-judge that trong production, judge thuong chi co CAU HOI +
CAU TRA LOI, khong co san "dap an dung" de doi chieu. He qua: judge se
DANH GIA CAO cau tra loi troi chay, chi tiet, dung tu ngu "dang tin cay" -
KE CA KHI noi dung do bi hallucinate (bia dat sai su that).
"""

# =====================================================================
# PHAN 1: Bo case - moi case co cau tra loi + diem HUMAN (ground truth
# thuc su, do NGUOI cham dua tren viec CO doi chieu voi du lieu that:
# carrier/eta dung trong ORDERS_DB) + diem JUDGE (mock LLM giam khao).
# =====================================================================

CASES = [
    {
        "id": "correct_detailed",
        "query": "Đơn #A1023 của tôi bao giờ tới?",
        "answer": (
            "Đơn hàng đang giao qua GHTK, dự kiến 2 ngày nữa (SLA GHTK: 1-3 ngày)."
        ),
        # Doi chieu ORDERS_DB that (bai 7): carrier=GHTK, eta=2 ngay -> DUNG.
        "human_score": 5,  # dung fact + du chi tiet -> diem cao, hop ly
    },
    {
        "id": "correct_terse",
        "query": "Đơn #A1023 của tôi bao giờ tới?",
        "answer": "Đang giao.",
        # Van DUNG (khong sai fact nao), nhung thieu chi tiet (carrier, so
        # ngay) nen nguoi cham khong cho diem tuyet doi.
        "human_score": 3,
    },
    {
        "id": "hallucinated_fluent",
        "query": "Đơn #A1023 của tôi bao giờ tới?",
        "answer": (
            "Đơn hàng của bạn đang được vận chuyển qua Viettel Post, dự kiến "
            "sẽ đến trong 5 ngày tới theo SLA tiêu chuẩn của đơn vị vận chuyển."
        ),
        # BIA DAT: ORDERS_DB that ghi carrier=GHTK, eta=2 ngay - cau tra
        # loi nay SAI CA carrier LAN so ngay, nhung viet troi chay, chi
        # tiet, dung tu ngu nghe "chuyen nghiep" y het cau dung o tren.
        "human_score": 1,  # sai fact hoan toan -> diem THAP du van doc muot
    },
    {
        "id": "biased_style_mediocre",
        "query": "Đơn #A1023 của tôi bao giờ tới?",
        "answer": (
            "Chắc chắn rằng đơn hàng sẽ được xử lý, nhưng hiện tại chưa có "
            "thông tin cụ thể về ngày giao."
        ),
        # Noi dung THUC SU ngheo nan (khong neu duoc carrier/eta du DA CO
        # trong DB that - dang le phai tra loi duoc), nhung mo dau bang cum
        # tu "Chắc chắn rằng..." - dung de test judge co bi "an" boi van
        # phong cach quen thuoc thay vi noi dung that hay khong.
        "human_score": 2,
    },
    {
        "id": "correct_different_wording",
        "query": "Đơn #A1023 của tôi bao giờ tới?",
        "answer": "Kiện hàng đang trên đường, đơn vị GHTK sẽ giao trong khoảng 2 ngày nữa.",
        # DUNG fact (GHTK, 2 ngay), chi khac cach dien dat so voi case 1 -
        # dai dien tinh huong LLM that: cau chu khac nhau nhung cung dung y.
        "human_score": 5,
    },
]


def fake_llm_judge(query: str, answer: str) -> dict:
    """Mo phong 1 LLM giam khao (KHONG duoc cap ground truth - chi co
    query + answer, giong nhieu pipeline LLM-as-judge that khi khong co
    san dap an tham chieu de doi chieu).

    Rubric (dang le phai ghi trong system prompt neu la LLM that):
      +1 neu cau tra loi du dai/chi tiet (>= 40 ky tu)
      +1 neu co de cap thong tin van chuyen cu the (ngay/giao/SLA)
      +1 (THIEN VI) neu mo dau bang cum tu quen thuoc "Chắc chắn rằng" -
         mo phong hien tuong SELF-PREFERENCE BIAS: judge co xu huong danh
         gia cao hon cau tra loi mang "phong cach" giong voi cach no hay
         sinh ra, BAT KE noi dung ben trong co tot hay khong.

    QUAN TRONG: ham nay KHONG he kiem tra carrier/eta co dung voi ORDERS_DB
    that hay khong - vi no KHONG duoc cap du lieu do (dung y he 1 judge that
    khi khong co ground truth/citation de doi chieu).
    """
    score = 3
    reasons = []

    if len(answer) >= 40:
        score += 1
        reasons.append("câu trả lời đủ chi tiết (>= 40 ký tự)")

    if any(kw in answer for kw in ["ngày", "giao", "SLA"]):
        score += 1
        reasons.append("có đề cập thông tin vận chuyển cụ thể (ngày/giao/SLA)")

    if answer.startswith("Chắc chắn rằng"):
        score += 1
        reasons.append("(bias) mở đầu bằng cụm từ nghe đáng tin cậy/quen thuộc")

    score = max(1, min(score, 5))
    return {"score": score, "reasoning": "; ".join(reasons) or "không có tín hiệu tích cực rõ ràng"}


# =====================================================================
# PHAN 2: Do AGREEMENT giua judge va human - buoc BAT BUOC truoc khi tin
# judge, khong duoc bo qua (day la trong tam thuc su cua bai hoc).
# =====================================================================

def evaluate_judge_agreement(cases: list[dict]) -> None:
    print(f"{'case':<24} {'human':>6} {'judge':>6} {'lệch':>6}  lý do judge")
    print("-" * 100)

    exact_match = 0
    within_1 = 0
    big_mismatch_cases = []

    for case in cases:
        verdict = fake_llm_judge(case["query"], case["answer"])
        human = case["human_score"]
        judge = verdict["score"]
        diff = abs(human - judge)

        print(f"{case['id']:<24} {human:>6} {judge:>6} {diff:>6}  {verdict['reasoning']}")

        if diff == 0:
            exact_match += 1
        if diff <= 1:
            within_1 += 1
        if diff >= 2:
            big_mismatch_cases.append(case["id"])

    n = len(cases)
    print("-" * 100)
    print(f"Exact match: {exact_match}/{n} ({exact_match / n:.0%})")
    print(f"Trong sai số 1 điểm: {within_1}/{n} ({within_1 / n:.0%})")
    if big_mismatch_cases:
        print(f"LỆCH LỚN (>= 2 điểm), cần review tay: {big_mismatch_cases}")


if __name__ == "__main__":
    evaluate_judge_agreement(CASES)

    # Checkpoint quan sat (tu tra loi sau khi doc/chay code):
    # 1. Case "hallucinated_fluent" - human cham 1 diem (sai fact hoan
    #    toan), judge cham bao nhieu? Vi sao judge KHONG bat duoc loi nay
    #    (doi chieu voi viec judge duoc cap nhung thong tin gi lam input)?
    # 2. Case "biased_style_mediocre" - noi dung thuc su ngheo nan (human
    #    cham 2 diem), judge cham bao nhieu? Day la vi du cho hien tuong
    #    gi (xem lai phan ly thuyet muc Trade-off)?
    # 3. Voi ket qua agreement in ra (exact match / within-1), ban co dam
    #    tin tuong dung mock judge nay standalone de tu dong loc cau tra
    #    loi "kem chat luong" trong production khong? Vi sao co/khong?
