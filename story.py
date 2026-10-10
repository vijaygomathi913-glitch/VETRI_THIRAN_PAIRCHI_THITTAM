import json
import re

from app.config import get_settings
from app.models import Panel, PromptRequest


def _parse_json(text: str) -> dict:
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", text.strip(), flags=re.I)
    try:
        return json.loads(cleaned)
    except json.JSONDecodeError:
        match = re.search(r"\{.*\}", cleaned, re.S)
        if not match:
            raise ValueError("Gemini returned an invalid story outline. Please try again.")
        return json.loads(match.group(0))


def _demo_panels(req: PromptRequest) -> list[Panel]:
    beats = [
        ("A Curious Beginning", f"{req.character_name} discovers a strange clue in {req.setting}.", "What could this mean?"),
        ("The First Clue", f"Following the clue, {req.character_name} finds a surprising trail.", "I should see where it leads!"),
        ("A Difficult Choice", f"A small setback tests {req.character_name}'s courage and kindness.", "There has to be another way."),
        ("A Helping Hand", f"A new friend helps turn the setback into an unexpected opportunity.", "Together, we can do this!"),
        ("A Bright Finish", f"{req.character_name} solves the mystery and leaves {req.setting} a little brighter.", "This is only the beginning."),
    ]
    return [Panel(number=i + 1, title=title, scene=scene, image_prompt=f"{req.art_style} illustration, {scene}, starring {req.character_name}, setting: {req.setting}, {req.tone} mood, no text, cohesive comic panel", narration=scene, dialogue=dialogue) for i, (title, scene, dialogue) in enumerate(beats)]


def generate_panels(req: PromptRequest) -> tuple[list[Panel], bool]:
    settings = get_settings()
    if not settings.gemini_api_key:
        return _demo_panels(req), True
    from google import genai
    from google.genai import types

    client = genai.Client(api_key=settings.gemini_api_key)
    shared = f"User idea: {req.prompt}\nHero: {req.character_name}\nSetting: {req.setting}\nTone: {req.tone}\nArt style: {req.art_style}"
    outline = client.models.generate_content(
        model=settings.gemini_flash_model,
        contents=f"Create exactly five sequential comic panels. Return only JSON object {{\"panels\":[{{\"number\":1,\"title\":\"\",\"scene\":\"\",\"image_prompt\":\"\"}}]}}. Keep the same hero and visual details in every image prompt. No lettering in image prompts. {shared}",
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.8),
    )
    raw = _parse_json(outline.text or "")
    outline_panels = raw.get("panels", [])
    if len(outline_panels) != 5:
        raise ValueError("Gemini did not return exactly five panels. Please try again.")
    story = client.models.generate_content(
        model=settings.gemini_story_model,
        contents=f"Write exactly five concise comic panel narration lines and short dialogue lines matching this outline. Return JSON {{\"panels\":[{{\"number\":1,\"narration\":\"\",\"dialogue\":\"\"}}]}}. Keep panel numbers and events aligned. Outline: {json.dumps(outline_panels)}",
        config=types.GenerateContentConfig(response_mime_type="application/json", temperature=0.9),
    )
    story_panels = _parse_json(story.text or "").get("panels", [])
    by_number = {int(p.get("number", i + 1)): p for i, p in enumerate(story_panels)}
    panels = []
    for i, item in enumerate(outline_panels):
        n = i + 1
        text = by_number.get(n, {})
        panels.append(Panel(number=n, title=str(item.get("title", f"Panel {n}"))[:100], scene=str(item.get("scene", ""))[:600], image_prompt=str(item.get("image_prompt", item.get("scene", "")))[:800], narration=str(text.get("narration", item.get("scene", "")))[:800], dialogue=str(text.get("dialogue", ""))[:300]))
    return panels, False
