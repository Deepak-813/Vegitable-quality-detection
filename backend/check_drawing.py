"""Check Drawing dimensions and bounding box."""
import sys
sys.path.insert(0, '.')

from svglib.svglib import svg2rlg
from reportlab.graphics.shapes import Drawing, Group
from pathlib import Path

logo_path = Path('C:/Users/DEEPAK NG/OneDrive/Desktop/vegetable-quality-detection/frontend/assets/icons/logo.svg')
d = svg2rlg(str(logo_path))

print(f"Drawing width={d.width}, height={d.height}")

# Check bounds before scaling
from reportlab.graphics import renderPDF
bounds_before = d.getBounds()
print(f"Bounds before scaling: {bounds_before}")  # (x0, y0, x1, y1)

# Apply the same scaling as the code
_target = 120
d.scale(_target / d.width, _target / d.width)
bounds_after = d.getBounds()
print(f"Bounds after scaling: {bounds_after}")
print(f"Width after scaling: {bounds_after[2] - bounds_after[0]}")
print(f"Height after scaling: {bounds_after[3] - bounds_after[1]}")

# Check the scale transform
print(f"Transform matrix: {d.transform}")

# Render and check the actual PDF content
from reportlab.graphics.renderPDF import drawToString
result = drawToString(d)
print(f"Rendered PDF length: {len(result)} bytes")

# Look for transform/scale operators in the rendered PDF
import re
# Find all cm (concat matrix) operators
cms = re.findall(rb'[0-9.\s]+cm', result)
print(f"\nConcat matrix operators ({len(cms)}):")
for cm in cms[:5]:
    print(f"  {cm.decode()}")

# Find q/Q (save/restore graphics state) to understand coordinate transforms
print(f"\n'q' (save) count: {result.count(b'q\\n')}")
print(f"'Q' (restore) count: {result.count(b'Q\\n')}")
