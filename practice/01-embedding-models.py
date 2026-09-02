"""
Bai thuc hanh #1: Embedding models
Ly thuyet day du: ../lessons/01-embedding-models.md (muc "Bai thuc hanh")
"""
import numpy as np
from sentence_transformers import SentenceTransformer

# Thu 1 trong 2 model nay (mo hinh mo, khong can API key):
# - "BAAI/bge-small-en-v1.5"
# - "intfloat/multilingual-e5-small"
MODEL_NAME = "intfloat/multilingual-e5-small"

# TODO: viet 5 cau (chu de luat lao dong):
# - 2 cap dong nghia (VD: "sa thai" vs "cham dut hop dong", "luong" vs "tien cong"...)
# - 1 cau khong lien quan (VD ve thoi tiet)
sentences = [
    "Người lao động bị công ty chấm dứt hợp đồng do vi phạm nội quy.",
    "Nhân viên bị doanh nghiệp sa thải vì vi phạm quy định của công ty.",
    "Người lao động có quyền nghỉ việc và thông báo trước cho người sử dụng lao động.",
    "Nhân viên có thể đơn phương chấm dứt quan hệ lao động sau khi báo trước theo quy định.",
    "Cuối tuần này thời tiết ở Tokyo dự báo sẽ có mưa.",
]


def encode(model: SentenceTransformer, texts: list[str], prefix: str = ""):
    """Encode danh sach cau thanh vector. Neu dung E5, thu them prefix 'query: ' hoac 'passage: '."""
    texts_with_prefix = [prefix + t for t in texts]
    # TODO: goi model.encode(...) voi normalize_embeddings=True
    return model.encode(texts_with_prefix, normalize_embeddings=True)


def cosine_sim_matrix(vectors):
    """Tinh ma tran cosine similarity giua tat ca cac cap cau.
    Goi y: neu vector da duoc normalize (normalize_embeddings=True) thi
    cosine similarity chinh la dot product giua cac vector.
    """
    # TODO: tra ve ma tran NxN (N = so cau) chua cosine similarity tung cap
    return np.dot(vectors, vectors.T)


if __name__ == "__main__":
    model = SentenceTransformer(MODEL_NAME)
    vectors = encode(model, sentences, prefix="query: ")
    sim_matrix = cosine_sim_matrix(vectors)

    for row in sim_matrix:
        print(["%.3f" % v for v in row])

    # TODO (checkpoint quan sat):
    # - Cap dong nghia co similarity cao han han cau khong lien quan khong?
    # - Neu dung E5: thu bo prefix "query: " di, similarity co doi nhieu khong?
