# ComicCraft

ComicCraft turns a short idea into a five-panel comic, with a web preview and downloadable PDF. It uses Gemini for structured story creation and Hugging Face Inference for illustrations when credentials are configured. Without credentials, it runs in demo mode with a deterministic story and locally generated SVG artwork, so the full UI and export flow remain usable.

## Requirements

- Python 3.10 or newer
- VS Code with the Python extension
- Optional: a Gemini API key and a Hugging Face access token for live AI generation

## Run in VS Code

1. Open this folder in VS Code and open **Terminal → New Terminal**.
2. Create and activate a virtual environment:

   ```powershell
   py -m venv .venv
   .\.venv\Scripts\Activate.ps1
   ```

   On macOS/Linux use `python3 -m venv .venv` and `source .venv/bin/activate`.
3. Install dependencies: `python -m pip install -r requirements.txt`.
4. Copy `.env.example` to `.env`. Add `GEMINI_API_KEY` and optionally `HF_TOKEN`. Leave them blank for demo mode. Never commit `.env`.
5. Start the server: `uvicorn app.main:app --reload`.
6. Open <http://127.0.0.1:8000>. Interactive API documentation is at <http://127.0.0.1:8000/docs>.

Use the home form to generate a comic, view all five panels, and download the PDF. For API clients, POST a `PromptRequest` JSON object to `/api/comics`. The response includes comic data and a PDF download URL. `GET /health` reports which providers are configured.

## Quick smoke check

With the server running, visit `/health` and confirm it returns `{"status":"ok", ...}`. Open `/docs`, expand `POST /api/comics`, select **Try it out**, and submit the example JSON below. A successful response contains five panels and a `pdf_url`; open that URL to verify the PDF download. With blank API keys, the response is marked `demo_mode: true` and still exercises the full application flow.

## Configuration

| Variable | Default | Purpose |
|---|---|---|
| `GEMINI_API_KEY` | blank | Enables Gemini text generation |
| `GEMINI_FLASH_MODEL` | `gemini-2.5-flash` | Generates a JSON panel outline |
| `GEMINI_STORY_MODEL` | `gemini-2.5-flash` | Writes narration and dialogue |
| `HF_TOKEN` | blank | Enables hosted Hugging Face image generation |
| `HF_IMAGE_MODEL` | `black-forest-labs/FLUX.1-schnell` | Image model available through an HF inference provider |
| `HF_PROVIDER` | `auto` | Hugging Face Inference provider selection |
| `IMAGE_MODE` | `auto` | `auto`, `huggingface`, or `demo` |
| `OUTPUT_DIR` | `static/generated` | Generated image and PDF storage |

When a configured provider fails, ComicCraft returns a clear generation error instead of silently substituting demo content. Demo mode is selected automatically only when the relevant API key is absent (or explicitly selected with `IMAGE_MODE=demo`).

## API

- `POST /api/comics` (also `/generate-comic/json`) — JSON body with `prompt`, `character_name`, `setting`, `tone`, and `art_style`; returns panel data and `pdf_url`.
- `POST /api/test-image` (also `/test-image`) — JSON body `{"prompt": "..."}`; returns an image URL.
- `GET /api/comics/{comic_id}/pdf` — downloads the comic PDF.
- `GET /health` — readiness and provider mode.

Example:

```json
{
  "prompt": "A brave fox finds a lost star and returns it to the night sky",
  "character_name": "Mira",
  "setting": "enchanted forest",
  "tone": "hopeful",
  "art_style": "storybook watercolor"
}
```

## Project layout

`app/` contains the FastAPI application, request models, routes, AI provider adapters, comic workflow, and PDF exporter. `templates/` contains the Jinja pages; `static/` holds CSS and generated assets. The app stores generation files under `static/generated/` by default.

## Troubleshooting

- If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process Bypass` in that terminal, then activate again.
- A missing key is fine: the app uses demo text and SVG artwork. Demo output is labeled in the UI.
- Hosted image generation requires a Hugging Face token with access to an available inference provider/model; provider availability and account limits vary.
- If a port is occupied, run `uvicorn app.main:app --reload --port 8001`.
