from pathlib import Path

from fastapi import APIRouter, Form, HTTPException, Request
from fastapi.responses import FileResponse, HTMLResponse
from fastapi.templating import Jinja2Templates

from app.config import PROJECT_ROOT, get_settings
from app.models import ImageTestRequest, PromptRequest
from app.services.comic import create_comic
from app.services.images import generate_image

router = APIRouter()
templates = Jinja2Templates(directory=str(PROJECT_ROOT / "templates"))


@router.get("/", response_class=HTMLResponse)
def home(request: Request):
    return templates.TemplateResponse(request=request, name="index.html", context={})


def _generate(request: PromptRequest) -> dict:
    try:
        return create_comic(request)
    except (ValueError, RuntimeError) as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Comic generation failed: {exc}") from exc


@router.post("/generate", response_class=HTMLResponse)
def generate_form(request: Request, prompt: str = Form(...), character_name: str = Form("Alex"), setting: str = Form("a curious little town"), tone: str = Form("adventurous"), art_style: str = Form("colorful comic book")):
    try:
        comic = _generate(PromptRequest(prompt=prompt, character_name=character_name, setting=setting, tone=tone, art_style=art_style))
        return templates.TemplateResponse(request=request, name="comic_preview.html", context={"comic": comic})
    except HTTPException as exc:
        return templates.TemplateResponse(request=request, name="index.html", context={"error": exc.detail, "values": {"prompt": prompt, "character_name": character_name, "setting": setting, "tone": tone, "art_style": art_style}}, status_code=exc.status_code)


@router.post("/generate-comic/json", include_in_schema=False)
@router.post("/api/comics")
def generate_json(payload: PromptRequest):
    return _generate(payload)


@router.post("/test-image", include_in_schema=False)
@router.post("/api/test-image")
def test_image(payload: ImageTestRequest):
    try:
        url, demo = generate_image(payload.prompt, "test", 1)
        return {"image_url": url, "demo_mode": demo}
    except Exception as exc:
        raise HTTPException(status_code=502, detail=str(exc)) from exc


@router.get("/api/comics/{comic_id}/pdf")
def download_pdf(comic_id: str):
    if not comic_id.isalnum() or len(comic_id) != 12:
        raise HTTPException(status_code=404, detail="Comic not found")
    path = get_settings().output_path / comic_id / "comic.pdf"
    if not path.is_file():
        raise HTTPException(status_code=404, detail="Comic PDF not found")
    return FileResponse(path, media_type="application/pdf", filename=f"comiccraft-{comic_id}.pdf")


@router.get("/export-success", response_class=HTMLResponse)
def export_success(request: Request, comic_id: str):
    return templates.TemplateResponse(request=request, name="export_success.html", context={"comic_id": comic_id})
