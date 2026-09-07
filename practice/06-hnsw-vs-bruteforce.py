"""
Bai thuc hanh #6: Vector DB internals (HNSW) - so sanh brute-force vs HNSW
Ly thuyet day du: ../lessons/06-vector-db-hnsw.md

Cai dat: pip install hnswlib numpy

Muc tieu: dung 1 corpus tong hop (5000 vector ngau nhien, 128 chieu) de:
- Do brute-force lam "dap an dung tuyet doi" (exact nearest neighbor).
- Do HNSW voi nhieu gia tri ef_search khac nhau, so sanh recall@10 va
  thoi gian chay trung binh moi query -> thay ro trade-off tocdo/do chinh xac.
"""
import time

import hnswlib
import numpy as np

N_VECTORS = 5000
DIM = 128
K = 10
N_QUERIES = 20
EF_SEARCH_VALUES = [10, 50, 200]
M = 16
EF_CONSTRUCTION = 200

rng = np.random.default_rng(seed=42)


def normalize(vectors: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(vectors, axis=1, keepdims=True)
    return vectors / norms


def brute_force_search(query: np.ndarray, vectors: np.ndarray, k: int) -> list[int]:
    """Tra ve top-k index gan query nhat, dung cosine similarity (= dot product
    vi vectors va query da normalize). Day la 'dap an dung tuyet doi' de so sanh.
    """
    scores = vectors @ query
    return list(np.argsort(scores)[::-1][:k])


def build_hnsw_index(vectors: np.ndarray, M: int, ef_construction: int) -> hnswlib.Index:
    index = hnswlib.Index(space="cosine", dim=vectors.shape[1])
    index.init_index(max_elements=vectors.shape[0], M=M, ef_construction=ef_construction)
    index.add_items(vectors, np.arange(vectors.shape[0]))
    return index


def recall_at_k(hnsw_result_ids: list[int], brute_force_ids: list[int]) -> float:
    """Ty le % cua brute-force top-k co mat trong ket qua HNSW tra ve."""
    truth = set(brute_force_ids)
    found = set(hnsw_result_ids)
    return len(truth & found) / len(truth)


if __name__ == "__main__":
    vectors = normalize(rng.random((N_VECTORS, DIM), dtype=np.float32))
    queries = normalize(rng.random((N_QUERIES, DIM), dtype=np.float32))

    # --- Brute-force: dap an dung + do thoi gian ---
    ground_truth = []
    t0 = time.perf_counter()
    for q in queries:
        ground_truth.append(brute_force_search(q, vectors, K))
    brute_force_time = (time.perf_counter() - t0) / N_QUERIES
    print(f"Brute-force: {brute_force_time * 1000:.3f} ms/query (recall=1.00 vi la dap an chuan)\n")

    # --- HNSW: build 1 lan, query voi nhieu ef_search khac nhau ---
    index = build_hnsw_index(vectors, M=M, ef_construction=EF_CONSTRUCTION)

    print(f"{'ef_search':>10} | {'recall@' + str(K):>10} | {'ms/query':>10}")
    print("-" * 36)
    for ef_search in EF_SEARCH_VALUES:
        index.set_ef(ef_search)

        recalls = []
        t0 = time.perf_counter()
        for i, q in enumerate(queries):
            labels, _distances = index.knn_query(q, k=K)
            recalls.append(recall_at_k(list(labels[0]), ground_truth[i]))
        elapsed = (time.perf_counter() - t0) / N_QUERIES

        avg_recall = sum(recalls) / len(recalls)
        print(f"{ef_search:>10} | {avg_recall:>10.2f} | {elapsed * 1000:>10.3f}")

    # Checkpoint quan sat (tu lam sau khi chay xong):
    # - ef_search tang thi recall va latency thay doi the nao? Co dung xu huong
    #   "recall tang, latency tang" nhu ly thuyet khong?
    # - Voi ef_search=200 (gan bang N_VECTORS/25), recall co gan 1.0 (~bang brute-force)
    #   khong? Neu co, HNSW luc do co con nhanh hon brute-force nhieu khong, hay
    #   da mat het loi the toc do vi ef qua cao?
    # - Thu doi N_VECTORS len 50000 hoac 200000, brute-force cham di bao nhieu lan?
    #   HNSW (cung ef_search) cham di bao nhieu? Ai scale tot hon?
