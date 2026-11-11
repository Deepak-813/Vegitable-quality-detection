"""Deep inspect PDF content stream."""
import os, zlib, re
from pathlib import Path

# Clean up old test file if exists
old = Path('backend/inspect_pdf_raw.py')
if old.exists():
    old.unlink()

pdf_path = 'reports/prediction_99999.pdf'
raw = open(pdf_path, 'rb').read()
print(f"File size: {len(raw)} bytes")

# Find streams
stream_positions = []
for m in re.finditer(rb'stream', raw):
    stream_positions.append(m.start())
print(f"Found {len(stream_positions)} 'stream' markers")

for i, start in enumerate(stream_positions):
    nl = raw.find(b'\n', start)
    content_start = nl + 1
    if raw[content_start:content_start+1] == b'\r':
        content_start += 1
    end_idx = raw.find(b'endstream', content_start)
    if end_idx == -1:
        continue
    data = raw[content_start:end_idx]
    if data.endswith(b'\r\n'):
        data = data[:-2]
    elif data.endswith(b'\n'):
        data = data[:-1]

    try:
        dec = zlib.decompress(data)
        print(f"\n=== Stream {i} (decompressed {len(data)} -> {len(dec)} bytes) ===")
    except:
        try:
            dec = zlib.decompress(data, -15)
            print(f"\n=== Stream {i} (decompressed raw {len(data)} -> {len(dec)} bytes) ===")
        except:
            print(f"\n=== Stream {i} (cannot decompress, {len(data)} bytes) ===")
            dec = data

    s = dec.decode('latin-1', errors='replace')
    print(f"  OP counts: BT={s.count('BT')}, Tj={s.count('Tj')}, TJ={s.count('TJ')}, cm={s.count('cm')}, re={s.count('re')}")
    
    # Show relevant lines
    for line in s.split('\n'):
        line = line.strip()
        if not line:
            continue
        # Show operators that include positioning or drawing
        lower = line.lower()
        if any(op in line for op in [' cm', ' Td', 'TJ', 'Tj', ' re', ' m ', ' l ', ' c ', ' v ']):
            if len(line) < 400:
                print(f"  {line[:300]}")
