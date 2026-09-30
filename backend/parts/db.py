from sqlalchemy.orm import Session
from .models import Base, engine, SessionLocal, Project
import time, uuid

def init_db():
    Base.metadata.create_all(bind=engine)

class DB:
    def __init__(self):
        init_db()

    def create(self, d: dict) -> dict:
        with SessionLocal() as session:
            now = time.time()
            p = Project(
                name=d.get('name',''),
                topic=d.get('topic',''),
                language=d.get('language','en'),
                platform=d.get('platform','tiktok'),
                target_duration=d.get('target_duration','30-60'),
                content_type=d.get('content_type','facts'),
                content_style=d.get('content_style','informational'),
                target_audience=d.get('target_audience','general'),
                visual_style=d.get('visual_style','realistic documentary'),
                script_model=d.get('script_model'),
                image_model=d.get('image_model'),
                tts_model=d.get('tts_model'),
                status='draft',
                created_at=now,
                updated_at=now,
                hook_options=[],
                scenes=[],
            )
            session.add(p)
            session.commit()
            session.refresh(p)
            return self._to_dict(p)

    def get(self, pid: str) -> dict | None:
        with SessionLocal() as session:
            p = session.get(Project, pid)
            return self._to_dict(p) if p else None

    def list(self) -> list:
        with SessionLocal() as session:
            rows = session.query(Project).order_by(Project.created_at.desc()).all()
            return [self._to_dict(r) for r in rows]

    def update(self, pid: str, u: dict) -> dict | None:
        with SessionLocal() as session:
            p = session.get(Project, pid)
            if not p:
                return None
            for k, v in u.items():
                if hasattr(p, k):
                    setattr(p, k, v)
            p.updated_at = time.time()
            session.commit()
            session.refresh(p)
            return self._to_dict(p)

    def _to_dict(self, p: Project) -> dict:
        return {
            'id': p.id,
            'name': p.name,
            'topic': p.topic,
            'language': p.language,
            'platform': p.platform,
            'target_duration': p.target_duration,
            'content_type': p.content_type,
            'content_style': p.content_style,
            'target_audience': p.target_audience,
            'visual_style': p.visual_style,
            'script_model': p.script_model,
            'image_model': p.image_model,
            'tts_model': p.tts_model,
            'status': p.status,
            'created_at': p.created_at,
            'updated_at': p.updated_at,
            'hook_options': p.hook_options or [],
            'selected_hook': p.selected_hook,
            'content_json': p.content_json,
            'scenes': p.scenes or [],
            'audio_path': p.audio_path,
            'audio_duration': p.audio_duration,
            'timeline_json': p.timeline_json,
            'video_path': p.video_path,
            'caption': p.caption,
            'keywords': p.keywords,
            'hashtags': p.hashtags,
        }

db = DB()
