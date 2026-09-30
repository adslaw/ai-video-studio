from pydantic import BaseModel
from typing import Optional

class ProjectCreate(BaseModel):
    name: str
    topic: str
    language: str = 'en'
    platform: str = 'tiktok'
    target_duration: str = '30-60'
    content_type: str = 'facts'
    content_style: str = 'informational'
    target_audience: str = 'general'
    visual_style: str = 'realistic documentary'
    script_model: Optional[str] = None
    image_model: Optional[str] = None
    tts_model: Optional[str] = None

class HookSelect(BaseModel):
    hook: str

class SceneUpdate(BaseModel):
    narration: Optional[str] = None
    visual_prompt: Optional[str] = None
    motion: Optional[str] = None
