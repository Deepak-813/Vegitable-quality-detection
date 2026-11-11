"""Render PDF page to image and check logo visibility at top."""
import sys
sys.path.insert(0, '.')

import fitz  # PyMuPDF

doc = fitz.open('reports/prediction_99999.pdf')
page = doc[0]

# Render at 2x resolution for clarity
mat = fitz.Matrix(2, 2)
pix = page.get_pixmap(matrix=mat)
print(f"Rendered image: {pix.width} x {pix.height} pixels")

# Check specific regions:
# Top of page (y near 0 in image = top of page)
# In the image, y=0 is top, but in PDF, y=0 is bottom
# So PDF y=720 (top of page) = image y=0
# PDF y=0 (bottom) = image y=height

# Check top 200 pixels of image (top of page)
top_pixels = []
for y in range(0, 100):  # top 100 pixels of image
    for x in range(0, pix.width, 5):
        px = pix.pixel(x, y)
        if px != (255, 255, 255, 255):  # non-white pixel
            top_pixels.append((x, y, px))

print(f"\nNon-white pixels in top 100 image rows: {len(top_pixels)}")
if top_pixels:
    print(f"  Sample pixels: {top_pixels[:10]}")
    min_x = min(p[0] for p in top_pixels)
    max_x = max(p[0] for p in top_pixels)
    min_y = min(p[1] for p in top_pixels)
    max_y = max(p[1] for p in top_pixels)
    print(f"  Bounding box: x={min_x}-{max_x}, y={min_y}-{max_y}")

# Check middle region (where title text should be)
# Title at PDF y=119.7 -> image y = (792 - 119.7) * 2 = ~1345
# Actually image y = (page_height - pdf_y) * scale
# page_height = 792, scale = 2
# pdf y=119.7 -> image y = (792 - 119.7) * 2 = 1344.6
# pdf y=720 -> image y = (792 - 720) * 2 = 144
# pdf y=792 -> image y = (792 - 792) * 2 = 0

print(f"\nTop region (image y=0-144 = PDF y=792-720):")
for y in range(0, 144):
    for x in range(0, pix.width, 5):
        px = pix.pixel(x, y)
        if px != (255, 255, 255, 255):
            print(f"  Found non-white at x={x}, y={y}: {px}")
            break
    else:
        continue
    break

# Check where the actual logo drawings are in PDF coords (y=84-108)
# PDF y=108 -> image y = (792 - 108) * 2 = 1368
# PDF y=84 -> image y = (792 - 84) * 2 = 1416
print(f"\nDrawing region (PDF y=84-108 -> image y=1416-1368):")
drawings_found = []
for y in range(1368, 1416):
    for x in range(0, pix.width, 2):
        px = pix.pixel(x, y)
        if px != (255, 255, 255, 255):
            drawings_found.append((x, y, px))
print(f"  Non-white pixels in drawing region: {len(drawings_found)}")
if drawings_found:
    colors = set(p[2] for p in drawings_found)
    print(f"  Colors found: {colors}")

# Overall stats
total_non_white = 0
for y in range(pix.height):
    for x in range(pix.width):
        px = pix.pixel(x, y)
        if px[:3] != (255, 255, 255):
            total_non_white += 1
print(f"\nTotal non-white pixels on page: {total_non_white}")

pix.save('reports/test_page_render.png')
print(f"\nFull page rendered to: reports/test_page_render.png")

doc.close()
