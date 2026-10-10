from pathlib import Path
import unicodedata

from fpdf import FPDF


def save_pdf(comic_id: str, title: str, panels: list[dict], output_dir: Path) -> Path:
    folder = output_dir / comic_id
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / "comic.pdf"
    pdf = FPDF(orientation="P", unit="mm", format="A4")
    pdf.set_auto_page_break(auto=True, margin=16)
    for panel in panels:
        pdf.add_page()
        pdf.set_font("Helvetica", "B", 20)
        pdf.multi_cell(180, 12, _ascii(f"{title} - Panel {panel['number']}"))
        pdf.ln(3)
        img = Path(panel["image_file"])
        if img.exists():
            pdf.image(str(img), x=15, y=pdf.get_y(), w=180, h=110)
        pdf.ln(116)
        pdf.set_x(pdf.l_margin)
        pdf.set_font("Helvetica", "B", 15)
        pdf.multi_cell(180, 9, _ascii(panel["title"]))
        pdf.set_font("Helvetica", "", 12)
        pdf.multi_cell(180, 7, _ascii(panel["scene"]))
        pdf.ln(3)
        pdf.set_font("Helvetica", "I", 12)
        pdf.multi_cell(180, 7, _ascii(panel["narration"]))
        pdf.set_font("Helvetica", "B", 12)
        pdf.multi_cell(180, 7, _ascii(panel["dialogue"]))
    pdf.output(str(path))
    return path


def _ascii(value: str) -> str:
    normalized = unicodedata.normalize("NFKD", value.replace("’", "'").replace("“", '"').replace("”", '"').replace("—", "-").replace("–", "-"))
    return normalized.encode("ascii", "ignore").decode("ascii")
