"""Load the maintenance contract without changing runtime configuration."""
import json
from pathlib import Path
import re


def load_release(root: Path) -> dict:
    data = json.loads((root/'release.json').read_text(encoding='utf-8'))
    for key in ['plugin_version', 'scrapling_version']:
        if not isinstance(data.get(key), str) or not re.fullmatch(
                r'\d+\.\d+\.\d+(?:[-+.][0-9A-Za-z.-]+)?', data[key]):
            raise ValueError(f'Invalid {key} version')
    names = data.get('expected_mcp_tools')
    if not isinstance(names, list) or not names or not all(isinstance(n, str) and n for n in names):
        raise ValueError('expected_mcp_tools must be a nonempty list of names')
    if len(set(names)) != len(names):
        raise ValueError('Duplicate expected_mcp_tools')
    return data
