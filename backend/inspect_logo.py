"""Deep inspection of SVG rendering in PDF."""
import sys
sys.path.insert(0, '.')

from svglib.svglib import svg2rlg
from reportlab.graphics import renderPDF
from reportlab.graphics.shapes import Drawing
from pathlib import Path
import io

logo_path = Path('C:/Users/DEEPAK NG/OneDrive/Desktop/vegetable-quality-detection/frontend/assets/icons/logo.svg')
d = svg2rlg(str(logo_path))
print(f"Drawing type: {type(d).__name__}")
print(f"Width: {d.width}, Height: {d.height}")
print(f"Contents count: {len(d.contents)}")

# Inspect each child in the group
for i, child in enumerate(d.contents):
    print(f"\n  Child {i}: type={type(child).__name__}")
    if hasattr(child, 'contents'):
        print(f"    Sub-contents count: {len(child.contents)}")
        for j, sub in enumerate(child.contents):
            print(f"    Sub {j}: type={type(sub).__name__}", end='')
            if hasattr(sub, 'fill'):
                print(f", fill={sub.fill}, fillColor={getattr(sub, 'fillColor', 'N/A')}", end='')
            if hasattr(sub, 'strokeColor'):
                print(f", strokeColor={getattr(sub, 'strokeColor', 'N/A')}", end='')
            print()

# Render to PDF and inspect raw content for gradient operators
buf = io.BytesIO()
renderPDF.drawToFile(d, 'reports/test_logo_detail.pdf')

# Also render as PNG to see visual output
try:
    from reportlab.graphics.renderPM import renderPM
    renderPM(d, 'reports/test_logo_render.png', width=240, height=56, fmt='PNG')
    png_size = Path('reports/test_logo_render.png').stat().st_size
    print(f"\nPNG render: {png_size} bytes")
except Exception as e:
    print(f"\nPNG render error: {e}")

# Check what colors are in the drawing
print("\n=== Color inspection ===")
raw_pdf = open('reports/test_logo_detail.pdf', 'rb').read()
# Look for color operators in the PDF
import re
# cm operator (concat matrix), rg (set fill color RGB), rg, sc, SCN, etc.
colors = re.findall(rb'[\d.]+/[\d.]+/[\d.]+ rg', raw_pdf)
print(f"RGB fill color operators found: {len(colors)}")
for c in colors[:10]:
    print(f"  {c.decode()}")

# Check for gradient/shading operators
shading_count = raw_pdf.count(b'/Shading')
print(f"Shading references: {shading_count}")
pattern_count = raw_pdf.count(b'/Pattern')
print(f"Pattern references: {pattern_count}")
