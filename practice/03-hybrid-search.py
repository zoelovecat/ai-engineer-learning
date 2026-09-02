"""
Bai thuc hanh #3: Hybrid search (vector + BM25)
Ly thuyet day du: ../lessons/03-hybrid-search.md (muc "Bai thuc hanh")
Toan (BM25, RRF tinh tay): ../lessons/03-hybrid-search-math.md

Cai dat: pip install rank_bm25 sentence-transformers numpy
"""
import re

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

SAMPLE_PATH = "lessons/data/sample-luat-lao-dong.txt"
MODEL_NAME = "intfloat/multilingual-e5-small"


def chunk_heading_aware(text: str) -> list[str]:
    """Chia theo ranh gioi 'Dieu X.' - da lam o bai 2, dung lai nguyen ban."""
    pattern = r"Điều \d+\."
    positions = [m.start() for m in re.finditer(pattern, text)]
    chunks = []
    for i, pos in enumerate(positions):
        end = positions[i + 1] if i + 1 < len(positions) else len(text)
        chunks.append(text[pos:end].strip())
    return chunks


def tokenize(text: str) -> list[str]:
    """Tokenize don gian de lam input cho BM25.
    Luu y (xem file interview): .split() theo khoang trang la CACH DON GIAN,
    tieng Viet co tu ghep (VD "don phuong" la 1 cum 2 tu) nen BM25Okapi se
    coi day la 2 token rieng - van dung duoc cho bai tap nay, nhung production
    that nen dung tokenizer tieng Viet (underthesea, pyvi) de chinh xac hon.
    """
    return text.lower().split()


def build_bm25_index(chunks: list[str]) -> BM25Okapi:
    """Xay BM25 index tu danh sach chunk.
    Goi y: BM25Okapi nhan vao 1 list cac list-token (moi chunk da tokenize).
    """
    # TODO: tokenize tung chunk trong `chunks`, roi return BM25Okapi(tokenized_chunks)
    tokenized_chunks = [tokenize(c) for c in chunks]
    return BM25Okapi(tokenized_chunks)
    raise NotImplementedError


def bm25_rank(bm25: BM25Okapi, query: str) -> list[int]:
    """Tra ve danh sach INDEX cua chunk, sap theo BM25 score giam dan.
    Goi y:
    - bm25.get_scores(tokenize(query)) tra ve mang score, cung do dai voi so chunk.
    - dung np.argsort(...)[::-1] de lay thu tu index giam dan theo score.
    """
    # TODO
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)
    return np.argsort(scores)[::-1]
    raise NotImplementedError


def vector_rank(model: SentenceTransformer, chunk_vectors: np.ndarray, query: str) -> list[int]:
    """Tra ve danh sach INDEX cua chunk, sap theo cosine similarity giam dan voi query.
    Goi y:
    - encode query bang model.encode([...], normalize_embeddings=True)
    - neu chunk_vectors da normalize, cosine similarity = dot product
    - dung np.argsort(...)[::-1] nhu tren
    """
    # TODO
    query_vector = model.encode("query: " + query, normalize_embeddings=True)  # 1D, shape (dim,)
    scores = np.dot(chunk_vectors, query_vector)  # shape (N,)
    return np.argsort(scores)[::-1]


def rrf_fusion(ranked_lists: list[list[int]], k: int = 60) -> list[int]:
    """Gop nhieu danh sach rank (moi list la 1 list INDEX chunk, da sap theo
    thu hang tu tot nhat) thanh 1 danh sach index cuoi cung theo score_RRF.

    Cong thuc (xem lessons/03-hybrid-search-math.md Phan B):
        score_RRF(d) = sum over moi ranked_list r cua  1 / (k + rank_r(d))
    trong do rank_r(d) la thu hang cua d trong list r, BAT DAU TU 1 (khong
    phai tu 0 - can +1 khi lay index tu enumerate()).

    Neu 1 document khong xuat hien trong 1 ranked_list nao do, no khong nhan
    duoc diem tu list do (khong coi nhu rank = het danh sach, chi bo qua).
    """
    # TODO:
    # 1. Tao dict {chunk_index: score} bat dau tu 0
    # 2. Voi moi ranked_list, voi moi (rank, chunk_index) trong enumerate(ranked_list, start=1):
    #      cong 1 / (k + rank) vao score[chunk_index]
    # 3. Tra ve danh sach chunk_index sap theo score giam dan
    score = {i: 0 for i in range(len(ranked_lists[0]))}
    for ranked_list in ranked_lists:
        for rank, chunk_index in enumerate(ranked_list, start=1):
            score[chunk_index] += 1 / (k + rank)
    return sorted(score.keys(), key=lambda x: score[x], reverse=True)


def print_top(label: str, chunks: list[str], ranked_indices: list[int], top_k: int = 5):
    print(f"=== {label} (top {top_k}) ===")
    for rank, idx in enumerate(ranked_indices[:top_k], start=1):
        preview = chunks[idx][:60].replace("\n", " ")
        print(f"{rank}. [chunk {idx}] {preview}...")
    print()


if __name__ == "__main__":
    with open(SAMPLE_PATH, encoding="utf-8") as f:
        text = f.read()

    chunks = chunk_heading_aware(text)

    model = SentenceTransformer(MODEL_NAME)
    chunk_vectors = model.encode(
        ["passage: " + c for c in chunks], normalize_embeddings=True
    )

    bm25 = build_bm25_index(chunks)

    queries = [
        "Điều 36 quy định gì",
        "công ty tự ý cho tôi nghỉ việc thì sao",
    ]

    for query in queries:
        print(f"\n########## Query: {query!r} ##########\n")

        bm25_ranked = bm25_rank(bm25, query)
        vector_ranked = vector_rank(model, chunk_vectors, query)

        print_top("BM25", chunks, bm25_ranked)
        print_top("Vector search", chunks, vector_ranked)

        hybrid_ranked = rrf_fusion([bm25_ranked, vector_ranked])
        print_top("Hybrid (RRF)", chunks, hybrid_ranked)

    # TODO (checkpoint quan sat):
    # - Query co so Dieu ("Dieu 36..."): top-1 cua vector-only co dung Dieu 36
    #   khong? Top-1 sau hybrid co dung khong?
    # - Query thuan semantic khong co so Dieu: hybrid co lam ket qua TE HON
    #   vector-only khong? Vi sao (doi chieu voi vi du RRF trong file toan)?
    print(f"=== Query: {queries[0]} ===")
    print(f"BM25 top-1: {chunks[bm25_ranked[0]]}")
    print(f"Vector top-1: {chunks[vector_ranked[0]]}")
    print(f"Hybrid top-1: {chunks[hybrid_ranked[0]]}")
