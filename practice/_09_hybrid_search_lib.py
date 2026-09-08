"""
Tai su dung logic hybrid search tu bai 3 (practice/03-hybrid-search.py),
dong goi thanh 1 module import duoc, khong sua logic ben trong.

MCP server (09-mcp-server.py) import module nay va goi search_law()
lam phan THUC THI ben trong tool - MCP chi la lop boc ben ngoai.
"""
import re

import numpy as np
from rank_bm25 import BM25Okapi
from sentence_transformers import SentenceTransformer

SAMPLE_PATH = "lessons/data/sample-luat-lao-dong.txt"
MODEL_NAME = "intfloat/multilingual-e5-small"


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
    tokenized_query = tokenize(query)
    scores = bm25.get_scores(tokenized_query)
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


class HybridSearchIndex:
    """Load 1 lan (model + BM25 index + embeddings), tai su dung cho nhieu query.
    MCP server se giu 1 instance duy nhat cua class nay (tranh load lai model moi request).
    """

    def __init__(self, sample_path: str = SAMPLE_PATH, model_name: str = MODEL_NAME):
        with open(sample_path, encoding="utf-8") as f:
            text = f.read()

        self.chunks = chunk_heading_aware(text)
        self.model = SentenceTransformer(model_name)
        self.chunk_vectors = self.model.encode(
            ["passage: " + c for c in self.chunks], normalize_embeddings=True
        )
        self.bm25 = build_bm25_index(self.chunks)

    def search(self, query: str, top_k: int = 5) -> list[str]:
        """Day chinh la ham 'search_law' se duoc expose qua MCP tool.
        Tra ve list[str] noi dung chunk (khong phai index) - de client/model
        doc duoc thang, khong can biet gi ve chunk_index/BM25/vector ben trong.
        """
        bm25_ranked = bm25_rank(self.bm25, query)
        vector_ranked = vector_rank(self.model, self.chunk_vectors, query)
        hybrid_ranked = rrf_fusion([bm25_ranked, vector_ranked])
        return [self.chunks[i] for i in hybrid_ranked[:top_k]]
