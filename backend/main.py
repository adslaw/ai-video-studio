from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import json, uuid, pathlib, time, shutil, subprocess, logging, io, wave

from parts.db import db
from parts.schemas import ProjectCreate, HookSelect
from parts.config import BASE_DIR, PROJECTS_ROOT
from parts.mocks import llm, img_gen, tts_gen
from parts.helpers import content_to_entities

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title='AI Video Automation Studio', version='0.1.0')
app.add_middleware(CORSMiddleware, allow_origins=['*'], allow_credentials=True, allow_methods=['*'], allow_headers=['*'])

@app.get('/health')
async def health():
    return {'ok': True}

@app.get('/models')
async def list_models():
    return {
        'chat_models': [{'id': 'mock-gpt-4o', 'name': 'Mock LLM', 'provider': 'mock'}],
        'image_models': [{'id': 'mock-image', 'name': 'Mock Image', 'provider': 'mock'}],
        'tts_models': [{'id': 'mock-tts', 'name': 'Mock TTS', 'provider': 'mock'}]
    }

@app.post('/projects')
async def create_project(req: ProjectCreate):
    return db.create(req.model_dump())

@app.get('/projects')
async def list_projects():
    return db.list()

@app.get('/projects/{pid}')
async def get_project(pid: str):
    p = db.get(pid)
    if not p: raise HTTPException(404, detail='not found')
    return p

@app.post('/projects/{pid}/generate-hooks')
async def generate_hooks(pid: str):
    p = db.get(pid)
    if not p: raise HTTPException(404)
    opts = [
        'Did you know the ocean hides giants?',
        'What creature weighs 180 tons and still swims?',
        'This animal heart is the size of a small car.'
    ]
    db.update(pid, {'hook_options': opts})
    return {'options': opts}

@app.post('/projects/{pid}/select-hook')
async def select_hook(pid: str, req: HookSelect):
    p = db.get(pid)
    if not p: raise HTTPException(404)
    db.update(pid, {'selected_hook': req.hook})
    return {'ok': True}

@app.post('/projects/{pid}/generate-content')
async def generate_content(pid: str):
    p = db.get(pid)
    if not p: raise HTTPException(404)
    hook = p.get('selected_hook', 'Hook')
    raw = await llm.chat([{'role': 'user', 'content': hook}], 'mock')
    content = json.loads(raw)
    p = content_to_entities(p, content)
    p['status'] = 'content_reviewed'
    db.update(pid, p)
    return p

@app.post('/projects/{pid}/images/generate')
async def generate_images(pid: str):
    p = db.get(pid)
    if not p: raise HTTPException(404)
    if not p.get('scenes'): raise HTTPException(400, detail='no scenes')
    img_dir = PROJECTS_ROOT / pid / 'images'
    img_dir.mkdir(parents=True, exist_ok=True)
    for s in p['scenes']:
        data = await img_gen.generate(s['visual_prompt'], 'mock')
        path = img_dir / ('scene_%03d.png' % s['order'])
        path.write_bytes(data)
        s['image_path'] = str(path.relative_to(BASE_DIR))
        s['status'] = 'generated'
    db.update(pid, {'scenes': p['scenes']})
    return {'ok': True, 'images': len(p['scenes'])}

@app.post('/projects/{pid}/tts')
async def tts_endpoint(pid: str):
    p = db.get(pid)
    if not p: raise HTTPException(404)
    c = p.get('content_json') or {}
    full = ' '.join([c.get('hook',''), c.get('narration',''), c.get('cta','')])
    data = await tts_gen.synthesize(full, 'mock', p.get('language','en'))
    audio_dir = PROJECTS_ROOT / pid / 'audio'
    audio_dir.mkdir(parents=True, exist_ok=True)
    wav_path = audio_dir / 'narration.wav'
    wav_path.write_bytes(data)
    with wave.open(str(wav_path), 'rb') as wf:
        duration = wf.getnframes() / wf.getframerate()
    db.update(pid, {'audio_path': str(wav_path.relative_to(BASE_DIR)), 'audio_duration': duration})
    return {'ok': True, 'duration': duration}

@app.post('/projects/{pid}/timeline')
async def timeline_endpoint(pid: str):
    p = db.get(pid)
    if not p: raise HTTPException(404)
    scenes = p.get('scenes', [])
    total = p.get('audio_duration') or len(scenes) * 3.0
    total_chars = max(1, sum(len(s.get('narration','')) for s in scenes))
    timeline = []
    start = 0.0
    for s in scenes:
        dur = (len(s.get('narration','')) / total_chars) * total
        end = start + dur
        s['start'] = start
        s['end'] = end
        timeline.append({'id': s['id'], 'order': s['order'], 'image': s.get('image_path'), 'start': start, 'end': end, 'motion': s.get('motion','none')})
        start = end
    data = {'scenes': timeline, 'audio': {'path': p.get('audio_path'), 'duration': total}}
    db.update(pid, {'timeline_json': data, 'scenes': scenes})
    return data

@app.post('/projects/{pid}/render')
async def render_endpoint(pid: str):
    p = db.get(pid)
    if not p: raise HTTPException(404)
    if not shutil.which('ffmpeg'): raise HTTPException(500, detail='ffmpeg not available')
    scenes = p.get('timeline_json', {}).get('scenes', [])
    if not scenes: raise HTTPException(400, detail='no timeline')
    audio_path = BASE_DIR / p['audio_path']
    out_dir = PROJECTS_ROOT / pid / 'video'
    out_dir.mkdir(parents=True, exist_ok=True)
    concat = out_dir / 'concat.txt'
    with open(concat, 'w') as f:
        for s in scenes:
            img = BASE_DIR / s['image']
            dur = s['end'] - s['start']
            f.write('file \'%s\'\n' % img)
            f.write('duration %f\n' % dur)
        f.write('file \'%s\'\n' % (BASE_DIR / scenes[-1]['image']))
    out = out_dir / 'output.mp4'
    cmd = ['ffmpeg','-y','-f','concat','-safe','0','-i',str(concat),'-i',str(audio_path),'-vf','scale=1080:1920:force_original_aspect_ratio=decrease,pad=1080:1920:(ow-iw)/2:(oh-ih)/2,setsar=1','-c:v','libx264','-preset','fast','-crf','23','-c:a','aac','-b:a','128k','-pix_fmt','yuv420p','-movflags','+faststart',str(out)]
    proc = subprocess.run(cmd, capture_output=True, text=True)
    if proc.returncode != 0:
        logger.error(proc.stderr)
        raise HTTPException(500, detail=proc.stderr[:300])
    db.update(pid, {'video_path': str(out.relative_to(BASE_DIR))})
    return {'ok': True, 'video_path': str(out.relative_to(BASE_DIR))}

@app.get('/projects/{pid}/package')
async def get_package(pid: str):
    p = db.get(pid)
    if not p: raise HTTPException(404)
    c = p.get('content_json') or {}
    return {
        'title': c.get('title', p['name']),
        'hook': p.get('selected_hook',''),
        'narration': c.get('narration',''),
        'cta': c.get('cta',''),
        'caption': p.get('caption') or c.get('caption',''),
        'keywords': p.get('keywords') or c.get('keywords',[]),
        'hashtags': p.get('hashtags') or c.get('hashtags',[]),
        'video_path': p.get('video_path'),
        'audio_path': p.get('audio_path')
    }

@app.get('/settings/status')
async def status():
    return {'checks': {'backend': True, 'ffmpeg': bool(shutil.which('ffmpeg'))}}

if __name__ == '__main__':
    import uvicorn
    uvicorn.run(app, host='0.0.0.0', port=8000)
