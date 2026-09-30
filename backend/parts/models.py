from sqlalchemy import create_engine, Column, String, Float, JSON
from sqlalchemy.orm import declarative_base, sessionmaker
from .config import DATABASE_URL
import uuid

Base = declarative_base()
engine = create_engine(DATABASE_URL, connect_args={'check_same_thread': False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

class Project(Base):
    __tablename__ = 'projects'
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    name = Column(String, nullable=False)
    topic = Column(String, nullable=False)
    language = Column(String, default='en')
    platform = Column(String, default='tiktok')
    target_duration = Column(String, default='30-60')
    content_type = Column(String, default='facts')
    content_style = Column(String, default='informational')
    target_audience = Column(String, default='general')
    visual_style = Column(String, default='realistic documentary')
    script_model = Column(String, nullable=True)
    image_model = Column(String, nullable=True)
    tts_model = Column(String, nullable=True)
    status = Column(String, default='draft')
    created_at = Column(Float)
    updated_at = Column(Float)
    hook_options = Column(JSON, default=list)
    selected_hook = Column(String, nullable=True)
    content_json = Column(JSON, nullable=True)
    scenes = Column(JSON, default=list)
    audio_path = Column(String, nullable=True)
    audio_duration = Column(Float, nullable=True)
    timeline_json = Column(JSON, nullable=True)
    video_path = Column(String, nullable=True)
    caption = Column(String, nullable=True)
    keywords = Column(JSON, nullable=True)
    hashtags = Column(JSON, nullable=True)
