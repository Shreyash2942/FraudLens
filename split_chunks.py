import json
from pathlib import Path
from collections import defaultdict
uncached = [f for f in Path('.graphify_uncached.txt').read_text().split('\n') if f]
by_dir = defaultdict(list)
for f in uncached:
    dir = str(Path(f).parent)
    by_dir[dir].append(f)
chunks = []
current = []
for dir, files in by_dir.items():
    if len(current) + len(files) <= 25:
        current.extend(files)
    else:
        if current:
            chunks.append(current)
            current = []
        for i in range(0, len(files), 25):
            chunks.append(files[i:i+25])
if current:
    chunks.append(current)
Path('.graphify_chunks.json').write_text(json.dumps(chunks))
print('Split into ' + str(len(chunks)) + ' chunks')
