from pathlib import Path

from app.config import get_settings


def _demo_png(prompt: str, target: Path, number: int = 1) -> None:
    from PIL import Image, ImageDraw

    colors = [("#d8efff", "#304f8a"), ("#ffe5ca", "#b45654"), ("#e6e0ff", "#674d93"), ("#d9f2dc", "#376d58"), ("#fff1b8", "#a45e36")]
    bg, ink = colors[(number - 1) % len(colors)]
    im = Image.new("RGB", (900, 600), bg)
    d = ImageDraw.Draw(im)
    d.ellipse((635, 55, 765, 185), fill="#fff8d9")
    d.polygon([(0, 450), (140, 350), (310, 440), (480, 360), (650, 440), (900, 350), (900, 600), (0, 600)], fill=ink)
    d.ellipse((375, 205, 515, 345), fill="#f5bd86")
    d.polygon([(365, 270), (390, 180), (485, 195), (525, 280), (460, 240), (420, 280)], fill="#342d44")
    d.polygon([(380, 350), (510, 350), (565, 490), (325, 490)], fill="#fff")
    d.ellipse((415, 270, 430, 285), fill="#222")
    d.ellipse((465, 270, 480, 285), fill="#222")
    d.rounded_rectangle((25, 25, 875, 100), radius=18, fill="white")
    d.text((50, 48), f"PANEL {number} · {prompt[:62]}", fill="#202c4d")
    d.text((35, 555), "ComicCraft demo illustration", fill="white")
    im.save(target)


def generate_image(prompt: str, comic_id: str, number: int = 1) -> tuple[str, bool]:
    settings = get_settings()
    folder = settings.output_path / comic_id
    folder.mkdir(parents=True, exist_ok=True)
    target = folder / f"panel-{number}.png"
    mode = settings.image_mode.lower()
    if mode not in {"auto", "demo", "huggingface"}:
        raise ValueError("IMAGE_MODE must be auto, demo, or huggingface.")
    use_demo = mode == "demo" or (mode == "auto" and not settings.hf_token)
    if use_demo:
        _demo_png(prompt, target, number)
        return f"/generated/{comic_id}/{target.name}", True
    if not settings.hf_token:
        raise ValueError("Set HF_TOKEN or set IMAGE_MODE=demo to generate images.")
    try:
        from huggingface_hub import InferenceClient

        client = InferenceClient(provider=settings.hf_provider, api_key=settings.hf_token)
        image = client.text_to_image(prompt, model=settings.hf_image_model, width=768, height=512)
        image.save(target)
        return f"/generated/{comic_id}/{target.name}", False
    except Exception as exc:
        raise RuntimeError(f"Hugging Face image generation failed: {exc}") from exc
