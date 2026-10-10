import re
import uuid

from app.config import get_settings
from app.models import PromptRequest
from app.services.exporter import save_pdf
from app.services.images import generate_image
from app.services.story import generate_panels


def create_comic(request: PromptRequest) -> dict:
    comic_id = uuid.uuid4().hex[:12]
    panels, text_demo = generate_panels(request)
    data = []
    image_demo = False
    settings = get_settings()
    for panel in panels:
        image_url, is_demo = generate_image(panel.image_prompt, comic_id, panel.number)
        image_demo |= is_demo
        data.append({**panel.model_dump(), "image_url": image_url, "image_file": str(settings.output_path / comic_id / image_url.rsplit("/", 1)[-1])})
    title = re.sub(r"\s+", " ", panels[0].title).strip() or "My Comic"
    save_pdf(comic_id, request.character_name + "'s Comic", data, settings.output_path)
    public_panels = [{key: value for key, value in panel.items() if key != "image_file"} for panel in data]
    return {"id": comic_id, "title": title, "character_name": request.character_name, "panels": public_panels, "pdf_url": f"/api/comics/{comic_id}/pdf", "demo_mode": text_demo or image_demo}
