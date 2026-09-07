"""
Bai thuc hanh #5: Danh gia retrieval (recall@k, MRR)
Ly thuyet day du: ../lessons/05-retrieval-eval.md
Eval set: ../lessons/data/eval-luat-lao-dong.json

Cai dat: pip install rank_bm25 sentence-transformers numpy

So sanh 3 pipeline (BM25-only, vector-only, hybrid RRF) tren cung 1 eval set,
tach rieng theo loai cau hoi (explicit = co "Dieu X", semantic = khong co so).
"""
import json
import re

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

SAMPLE_PATH = "lessons/data/sample-luat-lao-dong.txt"
EVAL_PATH = "lessons/data/eval-luat-lao-dong.json"
EMBED_MODEL_NAME = "intfloat/multilingual-e5-small"
TOP_K = 5


# ---- Cac ham tai dung tu bai 3 (khong doi logic) ----

def chunk_heading_aware(text: str) -> list[str]:
    pattern = r"Điều \d+\."
    positions = [m.start() for m in re.finditer(pattern, text)]
    chunks = []
    for i, pos in enumerate(positions):
        end = positions[i + 1] if i + 1 < len(positions) else len(text)
        chunks.append(text[pos:end].strip())
    return chunks


def tokenize(text: str) -> list[str]:
    return text.lower().split()


def build_bm25_index(chunks: list[str]) -> BM25Okapi:
    return BM25Okapi([tokenize(c) for c in chunks])


def bm25_rank(bm25: BM25Okapi, query: str) -> list[int]:
    scores = bm25.get_scores(tokenize(query))
    return list(np.argsort(scores)[::-1])


def vector_rank(model: SentenceTransformer, chunk_vectors: np.ndarray, query: str) -> list[int]:
    query_vector = model.encode("query: " + query, normalize_embeddings=True)
    scores = np.dot(chunk_vectors, query_vector)
    return list(np.argsort(scores)[::-1])


def rrf_fusion(ranked_lists: list[list[int]], k: int = 60) -> list[int]:
    score = {i: 0 for i in range(len(ranked_lists[0]))}
    for ranked_list in ranked_lists:
        for rank, chunk_index in enumerate(ranked_list, start=1):
            score[chunk_index] += 1 / (k + rank)
    return sorted(score.keys(), key=lambda x: score[x], reverse=True)


def chunk_dieu_number(chunk: str) -> int:
    """Trich so Dieu tu dau chunk, vd 'Điều 36. Quyen...' -> 36."""
    m = re.match(r"Điều (\d+)\.", chunk)
    return int(m.group(1)) if m else -1


# ---- Phan moi cua bai 5: metric danh gia ----

def recall_at_k(ranked_indices: list[int], chunks: list[str], expected_dieu: int, k: int) -> int:
    """Tra ve 1 neu chunk co so Dieu = expected_dieu nam trong top-k, nguoc lai 0.
    Goi y:
    - Lay top-k index: ranked_indices[:k]
    - Voi moi index, tra chunk_dieu_number(chunks[index]) va so voi expected_dieu
    """
    top_k_indices = ranked_indices[:k]
    return int(any(chunk_dieu_number(chunks[i]) == expected_dieu for i in top_k_indices))


def reciprocal_rank(ranked_indices: list[int], chunks: list[str], expected_dieu: int) -> float:
    """Tra ve 1/rank cua chunk dung DAU TIEN (rank bat dau tu 1), hoac 0.0 neu khong tim thay
    trong toan bo ranked_indices.
    Goi y:
    - Duyet enumerate(ranked_indices, start=1) -> (rank, index)
    - Ngay khi tim thay chunk_dieu_number(chunks[index]) == expected_dieu, return 1/rank
    - Het vong lap ma khong tim thay -> return 0.0
    """
    for rank, i in enumerate(ranked_indices, start=1):
        if chunk_dieu_number(chunks[i]) == expected_dieu:
            return 1 / rank
    return 0.0


def evaluate_pipeline(name, get_ranked_fn, eval_set, chunks, k=TOP_K):
    """Chay 1 pipeline tren toan bo eval_set, in bang ket qua tach theo type."""
    rows = []
    for item in eval_set:
        ranked = get_ranked_fn(item["query"])
        r = recall_at_k(ranked, chunks, item["expected_dieu"], k)
        rr = reciprocal_rank(ranked, chunks, item["expected_dieu"])
        rows.append({**item, "recall": r, "rr": rr})

    def summarize(rows_subset, label):
        if not rows_subset:
            return
        recall = sum(r["recall"] for r in rows_subset) / len(rows_subset)
        mrr = sum(r["rr"] for r in rows_subset) / len(rows_subset)
        print(f"  [{label:9s}] recall@{k}={recall:.2f}  MRR={mrr:.2f}  (n={len(rows_subset)})")

    print(f"=== Pipeline: {name} ===")
    summarize(rows, "ALL")
    summarize([r for r in rows if r["type"] == "explicit"], "explicit")
    summarize([r for r in rows if r["type"] == "semantic"], "semantic")
    for r in rows:
        if r["recall"] == 0:
            print(f"    MISS: '{r['query']}' (expected Điều {r['expected_dieu']})")
    print()


if __name__ == "__main__":
    with open(SAMPLE_PATH, encoding="utf-8") as f:
        text = f.read()
    with open(EVAL_PATH, encoding="utf-8") as f:
        eval_set = json.load(f)

    chunks = chunk_heading_aware(text)

    model = SentenceTransformer(EMBED_MODEL_NAME)
    chunk_vectors = model.encode(["passage: " + c for c in chunks], normalize_embeddings=True)
    bm25 = build_bm25_index(chunks)

    evaluate_pipeline("BM25-only", lambda q: bm25_rank(bm25, q), eval_set, chunks)
    evaluate_pipeline("Vector-only", lambda q: vector_rank(model, chunk_vectors, q), eval_set, chunks)
    evaluate_pipeline(
        "Hybrid RRF",
        lambda q: rrf_fusion([bm25_rank(bm25, q), vector_rank(model, chunk_vectors, q)]),
        eval_set,
        chunks,
    )

    # Checkpoint quan sat (tu lam sau khi chay xong):
    # - Pipeline nao recall@5 cao nhat o nhom "explicit"? O nhom "semantic"?
    # - Co pipeline nao recall cao nhung MRR thap hon han khong - nghia la doc dung
    #   CO mat trong top-5 nhung dung o hang thap (vd hang 4-5) thay vi hang 1?
    # - Cau nao bi MISS (recall=0) o ca 3 pipeline? Doi chieu voi case da biet o bai 3/4.
