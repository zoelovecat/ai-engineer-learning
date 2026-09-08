"""
Bai thuc hanh #10: Observability - tu xay co che TRACE / SPAN toi gian
(dung cai san toolkit nhu Langfuse/LangSmith de hieu ban chat truoc).
Ly thuyet day du: ../lessons/10-observability.md

Muc tieu: bọc quanh agent ReAct da viet o BAI 7 (practice/07-agent-patterns.py)
bang 1 class Tracer tu viet, de thay ro:
  - 1 TRACE = toan bo 1 lan agent chay tu dau den cuoi (co 1 span goc).
  - 1 SPAN  = 1 don vi cong viec ben trong trace (1 buoc ReAct, 1 lan goi
    "LLM", 1 lan goi tool) - co start/end time (-> latency_ms), co parent_id
    de dung lai CAY (span cha - span con).
  - Sau khi chay xong, in ra CAY trace dang thut le + latency tung buoc -
    day chinh xac la thu Langfuse/LangSmith hien thi tren dashboard, chi
    khac la o day render bang text thay vi UI web.

Khong can cai dat package ngoai - chi dung standard library (time,
contextlib, itertools, dataclasses, importlib de tai lai file bai 7).
"""
import importlib.util
import itertools
import pathlib
import time
from contextlib import contextmanager
from dataclasses import dataclass, field


# =====================================================================
# PHAN 1: Tracer toi gian - day la "lam bang tay" thu ma Langfuse SDK lam
# san cho ban (nhung co gui du lieu len server + ve dashboard that).
# =====================================================================

@dataclass
class Span:
    """1 don vi cong viec trong trace. Tuong duong 1 dong trong bang
    'observations' cua Langfuse.
    """
    span_id: int
    name: str
    parent_id: int | None       # None = day la span GOC cua 1 trace
    start: float                # time.perf_counter() luc bat dau (giay)
    end: float | None = None    # duoc dien khi span ket thuc
    metadata: dict = field(default_factory=dict)  # vd: {"tool": "...", "args": {...}}

    @property
    def duration_ms(self) -> float:
        """Latency cua rieng span nay (KHONG tinh thoi gian cua span con
        cho vao span cha 2 lan - end/start cua chinh no da bao gom het
        thoi gian cac span con chay ben trong, vi span con chay TRONG
        khoang [start, end] cua span cha).
        """
        if self.end is None:
            raise RuntimeError(f"Span '{self.name}' chua duoc dong (thieu 'end').")
        return (self.end - self.start) * 1000


class Tracer:
    """Quan ly toan bo cac span cua (co the nhieu) trace trong 1 lan chay
    chuong trinh. Dung 1 stack (_stack) de biet "hien tai dang o trong
    span nao" -> span moi mo ra se tu dong nhan span dinh stack lam CHA.
    Day chinh la co che Langfuse SDK dung "current span" ngam (context-local)
    de tu noi cha-con ma ban khong phai truyen parent_id tay.
    """

    _id_counter = itertools.count(1)  # sinh span_id tang dan, dung chung moi Tracer

    def __init__(self):
        self.spans: dict[int, Span] = {}
        self._stack: list[int] = []

    @contextmanager
    def span(self, name: str, **metadata):
        """Context manager: `with tracer.span("ten_buoc", key=value):`
        - Luc ENTER: tao Span moi, cha = span dang o dinh stack (hoac None
          neu day la span goc dau tien), day span_id nay len stack.
        - Luc EXIT (ke ca khi co exception - nho `finally`): ghi lai
          thoi gian ket thuc, pop stack de tra "vi tri hien tai" ve span cha.
        """
        span_id = next(Tracer._id_counter)
        parent_id = self._stack[-1] if self._stack else None
        current_span = Span(
            span_id=span_id,
            name=name,
            parent_id=parent_id,
            start=time.perf_counter(),
            metadata=metadata,
        )
        self.spans[span_id] = current_span
        self._stack.append(span_id)
        try:
            yield current_span
        finally:
            # QUAN TRONG: dung finally (khong phai dat sau yield binh
            # thuong) de span van duoc dong dung neu code ben trong `with`
            # nem exception - neu khong, span se "treo" mai mai o trang
            # thai end=None va lam sai lech ca cay trace.
            current_span.end = time.perf_counter()
            self._stack.pop()

    def print_tree(self):
        """In cay trace dang thut le theo do sau, giong cach Langfuse/
        LangSmith hien thi (chi khac la text thay vi UI web co the click).
        """
        children_of: dict[int | None, list[Span]] = {}
        for s in self.spans.values():
            children_of.setdefault(s.parent_id, []).append(s)

        def _print(span: Span, depth: int):
            indent = "  " * depth
            extra = f"  {span.metadata}" if span.metadata else ""
            print(f"{indent}- {span.name} [{span.duration_ms:.1f} ms]{extra}")
            for child in children_of.get(span.span_id, []):
                _print(child, depth + 1)

        for root in children_of.get(None, []):
            _print(root, 0)

    def slowest_span(self) -> Span:
        """Tra ve span co duration_ms lon nhat trong TOAN BO trace hien co.
        Day la cau hoi thuc te dau tien ban hoi khi debug latency: 'buoc
        nao la thu pham'.
        """
        return max(self.spans.values(), key=lambda s: s.duration_ms)


# =====================================================================
# PHAN 2: Tai su dung agent ReAct + tool tu bai 7 (khong sua file goc)
# =====================================================================
#
# File bai 7 ten "07-agent-patterns.py" - co dau gach ngang nen KHONG THE
# `import` binh thuong (khong phai identifier hop le). Dung importlib de
# load truc tiep tu duong dan file, giong cach 1 he thong that "instrument"
# (gan tracing vao) 1 agent co san ma khong can sua source code cua no.
_AGENT_07_PATH = pathlib.Path(__file__).parent / "07-agent-patterns.py"
_spec = importlib.util.spec_from_file_location("agent_patterns_07", _AGENT_07_PATH)
agent_07 = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(agent_07)  # chay file 07 nhu 1 module (dinh nghia ham/class, KHONG chay __main__ vi no nam trong if __name__ == "__main__")


# Gia lap latency THAT cua tung loai cong viec (giay). Trong he thong that:
# - goi "LLM" that ton thoi gian network + inference (thuong 0.3s - vai giay).
# - goi tool "get_shipping_estimate" gia lap la goi API van chuyen ben thu 3
#   (cham hon DB noi bo get_order_status) - co tinh de checkpoint co gia
#   tri quan sat ro rang (khong phai moi thu deu nhanh nhu nhau).
FAKE_LLM_LATENCY_S = 0.15
TOOL_LATENCY_S = {
    "get_order_status": 0.05,        # gia lap: query DB noi bo, nhanh
    "get_shipping_estimate": 0.35,   # gia lap: goi API hang van chuyen ngoai, cham hon han
}


def run_react_traced(query: str, tracer: Tracer, max_steps: int = 5) -> str:
    """Ban sao co INSTRUMENT (gan tracing) cua ham `run_react` trong bai 7.
    Logic dieu khien (control flow) giu NGUYEN - van la vong lap ReAct
    Thought -> Action -> Observation, van goi lai dung cac ham
    `agent_07.fake_llm_react_step` va `agent_07.TOOL_REGISTRY` cua bai 7,
    KHONG viet lai logic reasoning. Phan them vao CHI la `with tracer.span(...)`
    bao quanh moi buoc - day chinh xac la viec ban se lam khi gan Langfuse
    SDK vao 1 agent co san: khong sua logic, chi bao them lop quan sat.
    """
    state = agent_07.ReActState(query=query)

    # Span GOC cua ca 1 trace: dai dien cho "toan bo qua trinh tra loi 1 cau hoi".
    # Moi span khac tao ra BEN TRONG khoi `with` nay se tu dong co parent la
    # span nay (nho co che stack trong Tracer.span o tren).
    with tracer.span("agent_run", query=query):
        for step in range(max_steps):
            # Moi buoc ReAct la 1 span con truc tiep cua "agent_run".
            with tracer.span(f"react_step_{step + 1}"):
                # Span con cua react_step: buoc "LLM suy nghi quyet dinh lam gi tiep".
                with tracer.span("llm_reasoning"):
                    time.sleep(FAKE_LLM_LATENCY_S)  # gia lap do tre goi LLM that
                    decision = agent_07.fake_llm_react_step(state)

                if decision["action"] == "final_answer":
                    # Khong con tool nao de goi nua - dong het cac `with` dang
                    # mo (react_step_N, roi agent_run) va tra ve ket qua.
                    return decision["text"]

                tool_name = decision["tool"]
                # Span con cua react_step: buoc goi tool that su - dat ten tool
                # va args vao metadata de xem duoc trong cay trace in ra.
                with tracer.span(f"tool_call:{tool_name}", args=decision["args"]):
                    time.sleep(TOOL_LATENCY_S.get(tool_name, 0.05))  # gia lap latency tool that
                    tool_fn = agent_07.TOOL_REGISTRY[tool_name]
                    observation = tool_fn(**decision["args"])

                state.history.append({**decision, "observation": observation})

        raise RuntimeError("Vượt quá max_steps mà chưa có final_answer.")


if __name__ == "__main__":
    tracer = Tracer()

    print("########## Trace 1: 'Đơn #A1023 của tôi bao giờ tới?' ##########")
    answer_1 = run_react_traced("Đơn #A1023 của tôi bao giờ tới?", tracer)
    print(f"Final answer: {answer_1}\n")

    print("########## Trace 2: 'Đơn #A2099 đã tới chưa?' (ít bước hơn) ##########")
    answer_2 = run_react_traced("Đơn #A2099 đã tới chưa?", tracer)
    print(f"Final answer: {answer_2}\n")

    # ---- Day la phan tuong duong voi mo dashboard Langfuse len xem ----
    print("=" * 70)
    print("CAY TRACE (ca 2 trace nam chung 1 Tracer, moi trace 1 goc rieng):")
    print("=" * 70)
    tracer.print_tree()

    slowest = tracer.slowest_span()
    print(f"\nSpan CHAM NHAT toan bo: '{slowest.name}' ({slowest.duration_ms:.1f} ms) {slowest.metadata}")

    # Checkpoint quan sat (tu tra loi sau khi doc/chay code):
    # 1. Trace 1 va Trace 2 co so luong "react_step_N" khac nhau khong?
    #    Doi chieu voi ket qua bai 7 (query A2099 di thang final_answer o
    #    buoc dau vi status = 'đã giao', khong can goi get_shipping_estimate).
    # 2. Span cham nhat toan bo la span nao? Co phai la "llm_reasoning" hay
    #    "tool_call:get_shipping_estimate"? Vi sao (doi chieu FAKE_LLM_LATENCY_S
    #    va TOOL_LATENCY_S o tren)? Neu ban la nguoi debug production that va
    #    thay ket qua nay, ban se di toi uu cho phan nao truoc?
    # 3. Neu 1 request that bi loi (vd tool nem exception giua chung), doan
    #    code `finally: current_span.end = ...` trong Tracer.span co con
    #    dam bao span do duoc dong dung khong? Vi sao co che nay quan trong
    #    de trace khong bi "mat du lieu" khi co loi that trong production?
