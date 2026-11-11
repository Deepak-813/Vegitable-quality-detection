"""Decompress and inspect PDF content stream."""
import sys
sys.path.insert(0, '.')

import zlib
import re
from pathlib import Path

pdf_path = 'reports/prediction_99999.pdf'
with open(pdf_path, 'rb') as f:
    raw = f.read()

print(f"File size: {len(raw)} bytes")

# Find all stream objects and decompress them
streams = []
for match in re.finditer(rb'stream\r?\n(.*?)\r?\nendstream', raw, re.DOTALL):
    data = match.group(1)
    try:
        decompressed = zlib.decompress(data)
        streams.append(decompressed)
        print(f"Decompress stream: {len(data)} -> {len(decompressed)} bytes")
    except:
        try:
            decompressed = zlib.decompress(data, -15)
            streams.append(decompressed)
            print(f"Decompress (raw) stream: {len(data)} -> {len(decompressed)} bytes")
        except:
            print(f"Cannot decompress stream (size {len(data)}), keeping raw")
            streams.append(data)

# Print the first decompressed content stream (should be the page content)
for i, s in enumerate(streams):
    print(f"\n=== Stream {i} (first 2000 chars) ===")
    # Look for key operators
    s_str = s.decode('latin-1')
    
    # Find page height reference
    if 'cm' in s_str or 'Td' in s_str or 'TJ' in s_str or 're' in s_str:
        # Show positioning operators
        lines = s_str.split('\n')
        for line in lines:
            line = line.strip()
            if any(op in line for op in ['cm', 'Td', 'TJ', 'Tj', 're', 'm ', 'l ', 'c ', 'v ', 'y ', 'h', 'S', 's', 'f', 'F', 'B', 'b', 'q', 'Q', 'BT', 'ET', 'rg', 'RG', 'k', 'K', 'w', 'J', 'j', 'M', 'd']):
                if len(line) < 300:
                    print(f"  {line}")
    
    # Count key operators
    print(f"  Total length: {len(s_str)} chars")
    print(f"  'BT' count: {s_str.count('BT')}")
    print(f"  'Tj' count: {s_str.count('Tj')}")
    print(f"  'TJ' count: {s_str.count('TJ')}")
    print(f"  'cm' count: {s_str.count('cm')}")
    print(f"  're' count: {s_str.count('re')}")
