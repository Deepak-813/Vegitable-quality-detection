"""Check logo visibility at specific pixel positions."""
import sys
sys.path.insert(0, '.')

import fitz  # PyMuPDF

doc = fitz.open('reports/prediction_99999.pdf')
page = doc[0]

mat = fitz.Matrix(2, 2)
pix = page.get_pixmap(matrix=mat)
print(f"Image: {pix.width} x {pix.height} pixels, alpha={pix.alpha}")

def get_rgb(x, y):
    px = pix.pixel(x, y)
    if len(px) == 4:
        return px[:3]
    return px

# Scan entire image for non-white pixels and group by PDF y-coordinate
print("\n=== Scanning entire image for colored pixels ===")
colored_by_pdf_y = {}
for y in range(0, pix.height, 2):
    pdf_y = 792 - (y / 2)
    for x in range(0, pix.width, 2):
        rgb = get_rgb(x, y)
        if rgb != (255, 255, 255):
            pdf_x = x / 2
            band = int(pdf_y / 50)
            if band not in colored_by_pdf_y:
                colored_by_pdf_y[band] = {'count': 0, 'colors': set(), 'xmin': pdf_x, 'xmax': pdf_x}
            colored_by_pdf_y[band]['count'] += 1
            colored_by_pdf_y[band]['colors'].add(rgb)
            colored_by_pdf_y[band]['xmin'] = min(colored_by_pdf_y[band]['xmin'], pdf_x)
            colored_by_pdf_y[band]['xmax'] = max(colored_by_pdf_y[band]['xmax'], pdf_x)

total = sum(v['count'] for v in colored_by_pdf_y.values())
print(f"Total colored pixels: {total} in {len(colored_by_pdf_y)} bands")
for band in sorted(colored_by_pdf_y.keys()):
    v = colored_by_pdf_y[band]
    y_lo = band * 50
    y_hi = (band + 1) * 50
    print(f"  PDF y {792-y_hi} to {792-y_lo}: {v['count']} px, colors={list(v['colors'])[:5]}, x={v['xmin']:.0f}-{v['xmax']:.0f}")

pix.save('reports/test_page_render.png')
doc.close()
