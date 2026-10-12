"""Independent protocol probe; actual Codex acceptance is recorded separately."""
import argparse
import asyncio
import importlib.metadata
import json
from pathlib import Path

from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client


async def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--uvx', required=True)
    parser.add_argument('--out', default='artifacts/mcp')
    args = parser.parse_args()
    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)
    params = StdioServerParameters(command=args.uvx, args=['--from', 'scrapling[ai]==0.4.15', 'scrapling-mcp'])
    with (out / 'stderr.log').open('w', encoding='utf-8') as err:
        async with stdio_client(params, errlog=err) as (read, write):
            async with ClientSession(read, write) as session:
                init = await session.initialize()
                tool_list = await session.list_tools()
                (out / 'initialize.json').write_text(init.model_dump_json(indent=2), encoding='utf-8')
                (out / 'tools.json').write_text(tool_list.model_dump_json(indent=2), encoding='utf-8')
                versions = {d.metadata['Name']: d.version for d in importlib.metadata.distributions()}
                (out / 'dependencies.json').write_text(json.dumps(versions, indent=2), encoding='utf-8')
                print('Initialized:', init.server_info)
                for tool in tool_list.tools:
                    print(tool.name, list(tool.input_schema.get('properties', {})))
                result = await session.call_tool('make_request', {'url':'https://example.com','css_selector':'h1','extraction_type':'text'})
                (out / 'example.json').write_text(result.model_dump_json(indent=2), encoding='utf-8')
                print(result.model_dump_json()[:1200])


if __name__ == '__main__':
    asyncio.run(main())
