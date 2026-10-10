from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles

from app.config import PROJECT_ROOT, get_settings
from app.routes import router

app = FastAPI(title="ComicCraft", description="Create illustrated five-panel comics from a prompt.", version="1.0.0")
app.mount("/static", StaticFiles(directory=str(PROJECT_ROOT / "static")), name="static")
get_settings().output_path.mkdir(parents=True, exist_ok=True)
app.mount("/generated", StaticFiles(directory=str(get_settings().output_path)), name="generated")
app.include_router(router)


@app.get("/health")
def health():
    settings = get_settings()
    image_mode = "demo" if settings.image_mode == "demo" or (settings.image_mode == "auto" and not settings.hf_token) else "huggingface"
    return {"status": "ok", "text_provider": "gemini" if settings.gemini_api_key else "demo", "image_provider": image_mode}
