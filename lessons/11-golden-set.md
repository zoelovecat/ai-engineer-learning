# 11 — Eval dataset / golden set, tránh regression

**Ngày tạo:** 2026-09-08
**Trạng thái:** Đã học

## Lý thuyết

### 1. Nó là gì — cơ chế thật

Bài 5 đã học recall@k/MRR — eval set chỉ cho tầng retrieval (input = câu hỏi, expected = đúng chunk/Điều luật). Concept này mở rộng ra **toàn bộ pipeline** (agent, RAG, hệ thống LLM bất kỳ, xem [[10-observability]] để biết *tại sao* nó sai — golden set biết *cái gì* sai): một **golden set** gồm:

- **Input**: câu hỏi/tình huống thực tế (đa dạng — case thường gặp, edge case, case từng gây lỗi trong quá khứ).
- **Expected output**: không nhất thiết exact match (LLM output non-deterministic) — thường là 1 trong: exact match (hiếm dùng được), phải chứa key fact/keyphrase bắt buộc, hoặc rubric để LLM-as-judge chấm (bài 12).
- **Harness**: script chạy toàn bộ golden set qua pipeline hiện tại, so khớp, in bảng pass/fail + %.

Dùng thực tế: mỗi khi đổi prompt/model/logic agent → chạy golden set trước/sau → diff. Case nào từ pass thành fail = **regression**, bắt được trước khi merge/deploy.

### 2. Vì sao cần nó

- Hệ thống LLM thay đổi liên tục (sửa prompt, đổi model, thêm tool) — không ai review tay hết mọi case mỗi lần đổi.
- Golden set là "unit test" cho hệ thống non-deterministic: không khẳng định "luôn đúng 100%" nhưng khẳng định "không tệ đi so với trước".
- Tutorial cơ bản luôn bỏ qua ("thử vài câu, thấy ổn") — nhưng agent phức tạp dần (memory, multi-agent) thì mỗi lần sửa 1 chỗ có nguy cơ phá chỗ khác mà không ai biết cho tới khi user report.

### 3. Trade-off / khi nào cần cẩn thận

- Exact match hiếm dùng được với LLM thật — cần key-fact match hoặc LLM-as-judge.
- Xây/maintain tốn công — tốt nhất bổ sung dần từ case lỗi thật đã xảy ra (mỗi bug production → thêm 1 case, tránh tái phát).
- Golden set có thể thành "cái neo" sai theo **2 cách khác nhau**:
  1. Hành vi *mong muốn* thay đổi (đổi chính sách) mà quên cập nhật expected → báo FAIL cho hành vi đúng theo yêu cầu mới.
  2. **Data drift**: dữ liệu nền (không phải logic/code) thay đổi hợp lệ (SLA vận chuyển cập nhật, giá sản phẩm đổi...) → case cũ từng đúng nay báo FAIL dù hệ thống không có bug — false regression, cần phân biệt "code/logic đổi" vs "chỉ data nền đổi" trước khi kết luận có regression thật hay không.
- Coverage vs chi phí chạy — đặc biệt nếu dùng LLM-as-judge (mỗi lần chạy tốn thêm tiền gọi API).

**Chỗ phân biệt junior/middle**: junior nghĩ "eval = thử vài câu xem đúng không". Middle hiểu đây là cơ chế phát hiện regression **có hệ thống, tự động, không phụ thuộc trí nhớ người review** — bug "im lặng" (không crash, chỉ sai 1 phần kết quả) chỉ thực sự an toàn khi có golden set/CI tự động re-verify mọi hành vi cũ, không phải khi con người "cố check kỹ hơn" (con người review thường chỉ nhìn đúng chỗ vừa sửa, không tự nhiên verify lại toàn bộ luồng khác dùng chung dữ liệu/logic đó).

Không có phép toán cốt lõi riêng (đã có recall@k/MRR ở bài 5) — không tạo file toán riêng.

## Ví dụ áp dụng project

Domain: agent tra cứu đơn hàng (dùng lại agent ReAct bài 7/10). Golden set gồm case "đang giao" (phải chứa carrier + ETA + SLA), "đã giao", "chưa gửi", "không tìm thấy" — bao phủ mọi nhánh logic. Mô phỏng 1 code change gây bug im lặng (đổi key dict SLA từ hoa sang thường) → golden set bắt được ngay case "đang giao" bị regression, các case khác không ảnh hưởng vì không dùng chung dữ liệu bug.

## Bài thực hành

File: `practice/11-golden-set.py` — tái dùng agent ReAct bài 7 qua `importlib` (không sửa logic gốc).

1. `GOLDEN_SET`: 4 case bao phủ 4 nhánh logic của agent, mỗi case có `expected_keyphrases` (key fact bắt buộc, không phải exact match cả câu).
2. `check_keyphrases()`: so khớp kiểu "phải chứa cụm từ" — phù hợp cho LLM/agent vì output có thể diễn đạt khác nhau mà vẫn đúng ý.
3. `run_golden_set()`: chạy toàn bộ golden set, in pass/fail, trả về danh sách case fail.
4. Mô phỏng 1 "code change" gây regression thật (đổi key dict SLA từ `"GHTK"` sang `"ghtk"`, không crash, không exception, chỉ sai 1 phần kết quả) → chạy lại golden set → diff với baseline → phát hiện đúng case bị regression.

**Đã chạy thật thành công**: baseline 4/4 PASS → sau bug 3/4 PASS, đúng case `order_in_transit` regression (thiếu keyphrase "1-3 ngày"), 3 case khác không ảnh hưởng vì không gọi `get_shipping_estimate`.

## Checkpoint

Theo yêu cầu user, checkpoint tập trung lý thuyết/áp dụng/trade-off, không hỏi kiểu trace code (đã cập nhật vào `SKILL.md` Bước 5 để áp dụng từ nay về sau).

**Câu 1:** Áp dụng key-fact match cho 1 chatbot dùng LLM thật (không rule-based), sẽ gặp khó khăn gì khi chọn keyphrase — chọn sai gây false pass/false fail kiểu gì?
→ Mình trả lời hộ: keyphrase quá cụ thể/cứng nhắc → model diễn đạt hợp lệ khác đi vẫn bị báo FALSE FAIL (alert fatigue, dần bị user bỏ qua); keyphrase quá lỏng lẻo → câu trả lời sai hoàn toàn vẫn chứa được từ đó → FALSE PASS (an toàn giả). Kết luận: key-fact match chỉ nên dùng cho fact số liệu/tên riêng bắt buộc, phần "đúng ý, đầy đủ, không hallucinate" cần LLM-as-judge (bài 12).

**Câu 2:** Vì sao bug "im lặng" (không crash) nguy hiểm hơn bug crash khi không có golden set/CI?
→ User trả lời đúng 1 phần: "không nhận biết được nếu không check lại kỹ". Bổ sung: "check kỹ" bằng tay không scale — người review thường chỉ nhìn đúng chỗ vừa sửa, không tự nhiên verify lại toàn bộ luồng khác dùng chung dữ liệu/logic đó. Golden set/CI là cơ chế **bắt buộc, tự động, không phụ thuộc sự cẩn thận của người review**.

**Câu 3:** Cho 1 tình huống golden set cũ trở thành "cái neo sai" — cách nhận biết cần cập nhật expected thay vì coi FAIL là regression thật.
→ User trả lời đúng, tự nêu case mới: **data drift** — dữ liệu nền (không phải code/logic) thay đổi hợp lệ khiến case cũ từng đúng nay báo FAIL dù hệ thống không có bug. Cách phân biệt: hỏi "code/logic có đổi không, hay chỉ data nền đổi" trước khi kết luận regression thật.

Kết quả: đạt (câu 2-3 user tự trả lời, câu 2 cần bổ sung ý "không scale"; câu 1 mình trả lời hộ, giống pattern độ tin cậy thấp hơn 1 phần ở bài 7/8/10) → đánh dấu Đã học.
