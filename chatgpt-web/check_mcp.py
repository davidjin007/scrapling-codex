"""Protocol smoke test for the local Scrapling Streamable HTTP endpoint.

Install client dependencies separately:
  uv run --with 'mcp>=1.15,<3' --with httpx python chatgpt-web/check_mcp.py
The script only initializes and lists tools; it never scrapes a website.
"""
import argparse
import asyncio
import os

EXPECTED_TOOLS = {
    "make_request", "bulk_get", "fetch", "bulk_fetch", "stealthy_fetch",
    "bulk_stealthy_fetch", "open_session", "open_request_session",
    "session_fetch", "session_make_request", "list_sessions",
    "close_session", "screenshot",
}


async def check(url: str, token: str | None) -> None:
    import httpx
    from mcp import ClientSession
    from mcp.client.streamable_http import streamablehttp_client

    headers = {"Authorization": f"Bearer {token}"} if token else {}
    async with httpx.AsyncClient(headers=headers, timeout=45, follow_redirects=False) as client:
        async with streamablehttp_client(url=url, http_client=client) as streams:
            read, write, _ = streams
            async with ClientSession(read, write) as session:
                await session.initialize()
                listed = await session.list_tools()
                names = {tool.name for tool in listed.tools}
                missing = EXPECTED_TOOLS - names
                print(f"MCP initialize: OK; found {len(names)} tools")
                print("Tool names:", ", ".join(sorted(names)))
                if missing:
                    raise SystemExit(f"Missing {len(missing)} expected tools: {sorted(missing)}")
                print("Scrapling 13-tool discovery: PASS")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", default="http://127.0.0.1:8000/mcp")
    parser.add_argument("--no-auth", action="store_true",
                        help="Only for loopback private tunnel tests, never public URLs")
    args = parser.parse_args()
    if args.no_auth and not args.url.startswith(("http://127.0.0.1:", "http://localhost:")):
        parser.error("--no-auth is only permitted for loopback URLs")
    token = None if args.no_auth else os.getenv("SCRAPLING_MCP_AUTH_TOKEN")
    if not args.no_auth and not token:
        parser.error("SCRAPLING_MCP_AUTH_TOKEN is required; see README")
    asyncio.run(check(args.url, token))


if __name__ == "__main__":
    main()
