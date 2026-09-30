# AI Video Studio

Backend Python FastAPI + Frontend React static.

## Quick Start

### Backend
```bash
cd backend
python main.py
```
Buka http://127.0.0.1:8000/health -> {"ok": true}

### Frontend (local serve)
```bash
cd frontend
npx serve . -p 3000
```
Atau buka langsung `frontend/index.html` via live server.

### Test pipeline
```bash
python test_pipeline.py
```

## Struktur
- backend/main.py - entry FastAPI
- backend/parts/ - config, db, models, mocks, helpers, schemas
- frontend/index.html - entry HTML (React CDN)
- frontend/src/app.jsx - aplikasi utama
- frontend/src/styles.css - style
- frontend/vercel.json - config Vercel
- projects/ - output video/image/audio per project

## Environment
Lihat `.env.example` untuk NINE_ROUTER_BASE_URL, DATABASE_URL, PORT.

## Deploy
- Frontend: Vercel (folder frontend/)
- Backend: Railway / Render / Fly.io / VPS (butuh FFmpeg)
- Tidak disarankan cPanel Lite (shared hosting tidak support daemon Python + FFmpeg)
