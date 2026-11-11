"""Compare PDF with and without logo to verify logo presence."""
import sys
sys.path.insert(0, '.')

import io
from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from svglib.svglib import svg2rlg
import fitz  # PyMuPDF

styles = getSampleStyleSheet()

# --- PDF WITHOUT logo ---
buf_no_logo = io.BytesIO()
doc_no = SimpleDocTemplate(buf_no_logo, pagesize=letter)
story_no = [
    Paragraph("Vegetable Quality Detection Report", styles["Title"]),
    Spacer(1, 12),
    Paragraph("User: testuser", styles["Heading2"]),
    Paragraph("Quality: Fresh", styles["Heading3"]),
    Paragraph("Confidence: 95.5%", styles["Heading3"]),
]
doc_no.build(story_no)
with open('reports/test_no_logo.pdf', 'wb') as f:
    f.write(buf_no_logo.getvalue())

# --- PDF WITH logo ---
buf_with_logo = io.BytesIO()
doc_with = SimpleDocTemplate(buf_with_logo, pagesize=letter)
story_with = []
logo_path = Path('C:/Users/DEEPAK NG/OneDrive/Desktop/vegetable-quality-detection/frontend/assets/icons/logo.svg')
d = svg2rlg(str(logo_path))
if d is not None and getattr(d, 'width', 0):
    _target = 120
    d.scale(_target / d.width, _target / d.width)
    story_with.append(d)
    story_with.append(Spacer(1, 10))
story_with.append(Paragraph("Vegetable Quality Detection Report", styles["Title"]))
story_with.append(Spacer(1, 12))
story_with.append(Paragraph("User: testuser", styles["Heading2"]))
story_with.append(Paragraph("Quality: Fresh", styles["Heading3"]))
story_with.append(Paragraph("Confidence: 95.5%", styles["Heading3"]))
doc_with.build(story_with)
with open('reports/test_with_logo.pdf', 'wb') as f:
    f.write(buf_with_logo.getvalue())

# --- Compare ---
for label, fpath in [("WITHOUT logo", 'reports/test_no_logo.pdf'), ("WITH logo", 'reports/test_with_logo.pdf')]:
    doc = fitz.open(fpath)
    page = doc[0]
    drawings = page.get_drawings()
    size = Path(fpath).stat().st_size
    print(f"=== {label} ===")
    print(f"  File size: {size} bytes")
    print(f"  Vector drawings count: {len(drawings)}")
    if drawings:
        for i, dr in enumerate(drawings[:3]):
            print(f"  Drawing {i}: rect={dr['rect']}, fill={dr.get('fill')}")
    else:
        print("  (no vector drawings)")
    print()
    doc.close()

# Actual generated report
print("=== Actual report (prediction_99999.pdf) ===")
doc = fitz.open('reports/prediction_99999.pdf')
page = doc[0]
drawings = page.get_drawings()
print(f"  File size: {Path('reports/prediction_99999.pdf').stat().st_size} bytes")
print(f"  Vector drawings count: {len(drawings)}")
doc.close()
