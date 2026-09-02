"""
Bai thuc hanh #2: Chunking strategy
Ly thuyet day du: ../lessons/02-chunking-strategy.md (muc "Bai thuc hanh")
Du lieu mau: ../lessons/data/sample-luat-lao-dong.txt
"""
import re

SAMPLE_PATH = "lessons/data/sample-luat-lao-dong.txt"


def chunk_fixed(text: str, size: int = 500, overlap: int = 50) -> list[str]:
    """Chia deu theo ky tu, co overlap giua cac chunk lien tiep."""
    chunks = []
    start = 0
    while start < len(text):
        end = start + size
        # TODO: cat text[start:end] va them vao chunks
        chunks.append(text[start:end])

        # TODO: tinh vi tri start tiep theo - nho lui lai `overlap` ky tu
        # so voi `end`, khong phai nhay thang sang end (do chinh la cach
        # tao overlap). Can than: neu overlap >= size se bi lap vo han.
        start = end - overlap
    return chunks


def chunk_heading_aware(text: str) -> list[str]:
    """Chia theo ranh gioi 'Dieu X.' - moi chunk la 1 Dieu tron ven."""
    # Goi y: dung re.finditer voi pattern r"Điều \d+\." de tim vi tri
    # (.start()) cua moi lan xuat hien "Dieu N." trong text.
    pattern = r"Điều \d+\."
    positions = [m.start() for m in re.finditer(pattern, text)]

    chunks = []
    for i, pos in enumerate(positions):
        # TODO: chunk hien tai chay tu `pos` toi vi tri bat dau cua
        # Dieu tiep theo (positions[i+1]), hoac toi het text neu la
        # Dieu cuoi cung. Dung text[pos:end].strip() roi append.
        end = positions[i+1] if i+1 < len(positions) else len(text)
        chunks.append(text[pos:end].strip())
    return chunks


if __name__ == "__main__":
    with open(SAMPLE_PATH, encoding="utf-8") as f:
        text = f.read()

    fixed_chunks = chunk_fixed(text)
    heading_chunks = chunk_heading_aware(text)

    print(f"=== chunk_fixed: {len(fixed_chunks)} chunks ===")
    for i, c in enumerate(fixed_chunks):
        print(f"--- chunk {i} ({len(c)} ky tu) ---")
        print(c)
        print()

    print(f"=== chunk_heading_aware: {len(heading_chunks)} chunks ===")
    for i, c in enumerate(heading_chunks):
        print(f"--- chunk {i} ({len(c)} ky tu) ---")
        print(c)
        print()

    # TODO (checkpoint quan sat):
    # - chunk_fixed cat ngang y o cho nao? (vd: cat giua 1 khoan, hoac
    #   tach roi so dieu khoi noi dung con lai cua dieu do)
    # - chunk_heading_aware xu ly tot hon o do nhu the nao?

    print(f"=== chunk_fixed: {len(fixed_chunks)} chunks ===")
    for i, c in enumerate(fixed_chunks):
        print(f"--- chunk {i} ({len(c)} ky tu) ---")
        print(c)
        print()

    print(f"=== chunk_heading_aware: {len(heading_chunks)} chunks ===")
    for i, c in enumerate(heading_chunks):
        print(f"--- chunk {i} ({len(c)} ky tu) ---")
        print(c)
        print()
