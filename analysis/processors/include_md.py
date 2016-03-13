import sys
import pathlib
import re

if len(sys.argv) < 2:
    print('include_md.py path')

path = pathlib.Path(sys.argv[1]).resolve()

with path.open() as f:
    content = f.read()

def replace(m):
    include_path = pathlib.Path(m.group(1)).resolve()

    if not include_path.is_absolute():
        include_path = path / include_path

    with include_path.open() as f:
        return f.read()

content = re.sub(r'\{\{\s*include\s+(.*?)\s*\}\}', replace, content)

with path.open('w+') as f:
    f.write(content)
