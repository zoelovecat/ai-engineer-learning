"""
Bai thuc hanh #9: MCP client toi gian - tu spawn server 09-mcp-server.py
qua stdio, hoi list_tools(), roi goi call_tool("search_law", ...).

Cai dat: pip install mcp (server da cai o file server)

Chay:
    python practice/09-mcp-client.py

Diem can quan sat (checkpoint): client (doan code duoi day) hoan toan
KHONG import gi tu practice/_09_hybrid_search_lib.py - no khong biet
BM25/vector/RRF la gi. No chi biet: server ten gi, co tool gi (list_tools),
va goi tool bang dung schema (call_tool). Day chinh la ranh gioi MCP tao ra
giua "ai dung tool" va "tool lam gi ben trong".
"""
import asyncio
import sys

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client

# Console Windows mac dinh dung cp932/cp1252, khong encode duoc tieng Viet -
# ep UTF-8 de print khong bi UnicodeEncodeError (khong lien quan gi MCP).
sys.stdout.reconfigure(encoding="utf-8")


async def main():
    server_params = StdioServerParameters(
        command=sys.executable,
        args=["practice/09-mcp-server.py"],
    )

    async with stdio_client(server_params) as (read_stream, write_stream):
        async with ClientSession(read_stream, write_stream) as session:
            await session.initialize()

            # Buoc 1: discovery - hoi server co tool gi (khong hard-code truoc)
            tools_result = await session.list_tools()
            print("=== Tool server cong bo ===")
            for tool in tools_result.tools:
                print(f"- {tool.name}: {tool.description}")
                print(f"  schema: {tool.input_schema}")
            print()

            # Buoc 2: gia lap model quyet dinh goi tool nay voi tham so nay
            # (o agent that, day la ket qua model sinh ra - xem bai 8)
            query = "công ty tự ý cho tôi nghỉ việc thì sao"
            print(f"=== Goi tool search_law voi query: {query!r} ===")
            result = await session.call_tool("search_law", {"query": query, "top_k": 3})

            for content in result.content:
                print(content.text)


if __name__ == "__main__":
    asyncio.run(main())
