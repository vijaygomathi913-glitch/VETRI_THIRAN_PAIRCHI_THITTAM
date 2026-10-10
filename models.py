from pydantic import BaseModel, Field


class PromptRequest(BaseModel):
    prompt: str = Field(min_length=8, max_length=1200)
    character_name: str = Field(default="Alex", min_length=1, max_length=40)
    setting: str = Field(default="a curious little town", min_length=1, max_length=100)
    tone: str = Field(default="adventurous", max_length=40)
    art_style: str = Field(default="colorful comic book", max_length=60)


class ImageTestRequest(BaseModel):
    prompt: str = Field(min_length=4, max_length=600)


class Panel(BaseModel):
    number: int
    title: str
    scene: str
    image_prompt: str
    narration: str
    dialogue: str
