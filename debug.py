from app.models import PromptRequest
from app.services.comic import create_comic
import traceback
try:
    print(create_comic(PromptRequest(prompt='A brave fox finds a lost star', character_name='Mira')))
except Exception:
    traceback.print_exc()
