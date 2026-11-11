"""Use PyMuPDF to inspect page content."""
import sys
sys.path.insert(0, '.')

import fitz  # PyMuPDF

doc = fitz.open('reports/prediction_99999.pdf')
page = doc[0]
page_height = page.rect.height
print(f"Page height: {page_height}")

# Get text blocks with positions
print("\n=== Text blocks with bbox ===")
blocks = page.get_text("dict")["blocks"]
for b in blocks:
    if "lines" in b:
        print(f"  Block bbox: {b['bbox']}")
        for line in b["lines"]:
            y_top = line["bbox"][1]  # top y coord
            y_bottom = line["bbox"][3]
            for span in line["spans"]:
                print(f"    Text '{span['text'][:40]}' at y={span['bbox'][1]:.1f} (size={span['size']:.1f})")
                print(f"      span bbox: x0={span['bbox'][0]:.1f}, y0={span['bbox'][1]:.1f}, x1={span['bbox'][2]:.1f}, y1={span['bbox'][3]:.1f}")

# Get all drawings with full details - check coordinates
print("\n=== All drawings ===")
drawings = page.get_drawings()
print(f"Total drawings: {len(drawings)}")
for i, d in enumerate(drawings):
    r = d["rect"]
    print(f"  Drawing {i}: x0={r.x0:.2f}, y0={r.y0:.2f}, x1={r.x1:.2f}, y1={r.y1:.2f}, fill={d.get('fill')}, stroke={d.get('stroke')}")

# Also check the full page text with positions
print("\n=== First few text lines ===")
text = page.get_text("text")
for i, line in enumerate(text.split('\n')[:8]):
    print(f"  Line {i}: {repr(line[:60])}")

doc.close()
