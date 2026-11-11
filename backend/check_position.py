"""Check positioning of logo vs text on the PDF page."""
import sys
sys.path.insert(0, '.')

import fitz  # PyMuPDF
from pathlib import Path

doc = fitz.open('reports/prediction_99999.pdf')
page = doc[0]
page_height = page.rect.height  # should be 792 for letter
page_width = page.rect.width    # should be 612 for letter
print(f"Page size: {page_width} x {page_height}")

# Get text blocks with positions
print("\n=== Text blocks (top of page) ===")
blocks = page.get_text("dict")["blocks"]
for b in blocks:
    if "lines" in b:
        for line in b["lines"]:
            for span in line["spans"]:
                y_pos = span["bbox"][1]  # top y
                text = span["text"][:50]
                print(f"  y={y_pos:.1f}: '{text}' (size={span['size']:.1f}, color={span.get('color')})")

# Get drawing blocks with positions
print("\n=== Vector drawings (should be at top = high y) ===")
drawings = page.get_drawings()
for i, d in enumerate(drawings):
    r = d["rect"]
    print(f"  Drawing {i}: x={r.x0:.1f}-{r.x1:.1f}, y={r.y0:.1f}-{r.y1:.1f}, fill={d.get('fill')}")

doc.close()
