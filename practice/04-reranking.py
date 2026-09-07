"""
Bai thuc hanh #4: Reranking (cross-encoder)
Ly thuyet day du: ../lessons/04-reranking.md

Cai dat: pip install sentence-transformers rank_bm25 numpy

Muc tieu: lay lai dung case shared blind spot da phat hien o bai 3 -
query "cong ty tu y cho toi nghi viec thi sao" bi ca BM25 lan vector
(va ca RRF fusion) xep nham Dieu 35 len tren Dieu 36 - roi dung
cross-encoder rerank de xem co sua duoc khong.

Cac ham chunk/bm25/vector/rrf ben duoi copy nguyen tu practice/03-hybrid-search.py
(khong sua logic) de file nay chay doc lap.
"""
import re

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import CrossEncoder, SentenceTransformer

SAMPLE_PATH = "lessons/data/sample-luat-lao-dong.txt"
EMBED_MODEL_NAME = "intfloat/multilingual-e5-small"
RERANKER_NAME = "BAAI/bge-reranker-base"
QUERY = "công ty tự ý cho tôi nghỉ việc thì sao"
TOP_K_BEFORE_RERANK = 10  # so candidate lay ra tu hybrid truoc khi dua vao rerank


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
    tokenized_chunks = [tokenize(c) for c in chunks]
    return BM25Okapi(tokenized_chunks)


def bm25_rank(bm25: BM25Okapi, query: str) -> list[int]:
    scores = bm25.get_scores(tokenize(query))
    return np.argsort(scores)[::-1]


def vector_rank(model: SentenceTransformer, chunk_vectors: np.ndarray, query: str) -> list[int]:
    query_vector = model.encode("query: " + query, normalize_embeddings=True)
    scores = np.dot(chunk_vectors, query_vector)
    return np.argsort(scores)[::-1]


def rrf_fusion(ranked_lists: list[list[int]], k: int = 60) -> list[int]:
    score = {i: 0 for i in range(len(ranked_lists[0]))}
    for ranked_list in ranked_lists:
        for rank, chunk_index in enumerate(ranked_list, start=1):
            score[chunk_index] += 1 / (k + rank)
    return sorted(score.keys(), key=lambda x: score[x], reverse=True)


def print_top(label: str, chunks: list[str], ranked_indices: list[int], scores: dict | None = None, top_k: int = 5):
    print(f"=== {label} (top {top_k}) ===")
    for rank, idx in enumerate(ranked_indices[:top_k], start=1):
        preview = chunks[idx][:60].replace("\n", " ")
        score_str = f" (score={scores[idx]:.4f})" if scores is not None else ""
        print(f"{rank}. [chunk {idx}]{score_str} {preview}...")
    print()


# ---- Phan moi cua bai 4: cross-encoder rerank ----

def rerank(cross_encoder: CrossEncoder, query: str, candidates: list[str]) -> tuple[list[int], np.ndarray]:
    """Tra ve (danh sach INDEX trong pham vi candidates sap giam dan theo score, mang score goc).
    Goi y:
    - Tao list cap: pairs = [(query, c) for c in candidates]
    - scores = cross_encoder.predict(pairs)  -> mang float, cung do dai voi candidates
    - order = np.argsort(scores)[::-1]
    """
    pairs = [(query, c) for c in candidates]
    scores = cross_encoder.predict(pairs)
    order = list(np.argsort(scores)[::-1])
    return order, scores


if __name__ == "__main__":
    with open(SAMPLE_PATH, encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_heading_aware(text)

    embed_model = SentenceTransformer(EMBED_MODEL_NAME)
    chunk_vectors = embed_model.encode(
        ["passage: " + c for c in chunks], normalize_embeddings=True
    )
    bm25 = build_bm25_index(chunks)

    bm25_ranked = bm25_rank(bm25, QUERY)
    vector_ranked = vector_rank(embed_model, chunk_vectors, QUERY)
    hybrid_ranked = rrf_fusion([bm25_ranked, vector_ranked])

    print(f"########## Query: {QUERY!r} ##########\n")
    print_top("Hybrid (RRF) - TRUOC rerank", chunks, hybrid_ranked, top_k=TOP_K_BEFORE_RERANK)

    # Chi rerank trong pham vi top-K da retrieve tho (khong rerank toan bo corpus)
    candidate_indices = list(hybrid_ranked[:TOP_K_BEFORE_RERANK])
    candidate_chunks = [chunks[i] for i in candidate_indices]

    cross_encoder = CrossEncoder(RERANKER_NAME)
    local_order, ce_scores = rerank(cross_encoder, QUERY, candidate_chunks)

    # Map nguoc lai ve index goc trong `chunks`, va map score theo index goc de print_top dung duoc
    reranked_global_indices = [candidate_indices[i] for i in local_order]
    score_by_global_index = {candidate_indices[i]: ce_scores[i] for i in range(len(candidate_indices))}

    print_top(
        "Cross-encoder rerank - SAU rerank",
        chunks,
        reranked_global_indices,
        scores=score_by_global_index,
        top_k=TOP_K_BEFORE_RERANK,
    )

    print("=== So sanh top-1 ===")
    print(f"Truoc rerank (hybrid RRF): {chunks[hybrid_ranked[0]][:80]}...")
    print(f"Sau rerank (cross-encoder): {chunks[reranked_global_indices[0]][:80]}...")

    # Checkpoint quan sat (tu lam sau khi chay xong):
    # - Top-1 sau rerank co dung la Dieu 36 khong?
    # - Tim score cua chunk chua "Dieu 35" va "Dieu 36" trong score_by_global_index,
    #   in ra so sanh - chenh lech nhieu hay it (model tu tin hay "luong lu")?
