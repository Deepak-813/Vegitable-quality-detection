from pathlib import Path
from reportlab.lib.pagesizes import letter
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as ReportImage, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet


class PDFService:
    def __init__(self, output_dir: str):
        self.output_dir = output_dir
        Path(output_dir).mkdir(parents=True, exist_ok=True)

    def generate_report(self, username: str, prediction: dict, image_path: str | None = None) -> str:
        output_path = Path(self.output_dir) / f"prediction_{prediction['id']}.pdf"
        doc = SimpleDocTemplate(str(output_path), pagesize=letter)
        styles = getSampleStyleSheet()
        story = []

        # Branding: project logo (frontend/assets/icons/logo.svg). The SVG is
        # turned into a reportlab Drawing via svglib (no native cairo needed).
        # If svglib or the file is unavailable, the report still generates.
        try:
            from svglib.svglib import svg2rlg
            logo_path = Path(__file__).resolve().parents[3] / "frontend" / "assets" / "icons" / "logo.svg"
            if logo_path.exists():
                _d = svg2rlg(str(logo_path))
                if _d is not None and getattr(_d, "width", 0):
                    _target = 120
                    _d.scale(_target / _d.width, _target / _d.width)
                    story.append(_d)
                    story.append(Spacer(1, 10))
        except Exception:
            pass
        story.append(Paragraph("Vegetable Quality Detection Report", styles["Title"]))
        story.append(Spacer(1, 12))
        story.append(Paragraph(f"User: {username}", styles["Heading2"]))
        story.append(Paragraph(f"Quality: {prediction['quality']}", styles["Heading3"]))
        story.append(Paragraph(f"Confidence: {prediction['confidence']}%", styles["Heading3"]))
        story.append(Paragraph(f"Storage Life: {prediction['storage_days']} days", styles["Heading3"]))
        story.append(Paragraph(f"Storage Temperature: {prediction['storage_temperature']}", styles["Heading3"]))
        story.append(Paragraph(f"Recommendation: {prediction['recommendation']}", styles["BodyText"]))
        story.append(Spacer(1, 12))

        if image_path and Path(image_path).exists():
            img = ReportImage(image_path, width=180, height=180)
            story.append(img)

        doc.build(story)
        return str(output_path)


pdf_service = PDFService("reports")
