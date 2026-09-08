"""
Bai thuc hanh #9: MCP server toi gian, expose 1 tool "search_law".
Ly thuyet: ../lessons/09-mcp.md

Cai dat: pip install mcp rank_bm25 sentence-transformers numpy

Chay server (stdio transport - MCP client tu spawn process nay,
khong can chay tay o che do binh thuong; xem practice/09-mcp-client.py):
    python practice/09-mcp-server.py

Diem quan trong can quan sat: server nay KHONG biet gi ve "agent" hay
"model" goi no - no chi khai bao 1 tool (qua decorator @server.tool(), tu
sinh JSON schema tu type hint cua ham), va thuc thi khi duoc goi. Logic
hybrid search ben trong (BM25 + vector + RRF) giu nguyen 100% tu bai 3,
khong doi 1 dong nao ca - MCP chi la lop boc ben ngoai.

Ghi chu ban SDK: mcp>=2.x doi tu low-level Server (list_tools/call_tool
decorator thu cong) sang MCPServer (FastMCP-style, @server.tool() tu sinh
schema tu type hint). Code duoi day dung API moi nay.
"""
from mcp.server import MCPServer

from _09_hybrid_search_lib import HybridSearchIndex

server = MCPServer("law-search-server")

# Load 1 lan khi server khoi dong (model + BM25 index + embeddings), khong
# load lai moi request - day la ly do dung 1 instance global thay vi tao
# moi trong ham tool.
_index: HybridSearchIndex | None = None


def get_index() -> HybridSearchIndex:
    global _index
    if _index is None:
        _index = HybridSearchIndex()
    return _index


@server.tool()
def search_law(query: str, top_k: int = 5) -> list[str]:
    """Tim cac dieu luat lien quan trong Bo luat Lao dong mau, dung hybrid
    search (ket hop BM25 tu khoa va vector semantic).

    Args:
        query: Cau hoi hoac tinh huong can tra cuu, vi du
            'cong ty cho toi nghi viec'.
        top_k: So luong dieu luat can tra ve, mac dinh 5.
    """
    # Toan bo phan thuc thi chi la goi lai ham da viet o bai 3 - MCP khong
    # them logic nghiep vu nao ca, no chi la lop "expose" ham nay ra ngoai
    # theo chuan giao thuc de client bat ky (Claude Desktop, agent tu viet...)
    # goi duoc ma khong can biet Python ben trong.
    return get_index().search(query, top_k=top_k)


if __name__ == "__main__":
    server.run(transport="stdio")
