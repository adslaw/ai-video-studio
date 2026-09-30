import pathlib, os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = pathlib.Path(__file__).parent.parent.parent.resolve()
PROJECTS_ROOT = BASE_DIR / 'projects'
PROJECTS_ROOT.mkdir(parents=True, exist_ok=True)

DATABASE_URL = os.getenv('DATABASE_URL', f'sqlite:///{BASE_DIR / "projects.db"}')
DB_PATH = BASE_DIR / 'projects.db'

NINE_ROUTER_BASE_URL = os.getenv('NINE_ROUTER_BASE_URL', '')
NINE_ROUTER_API_KEY = os.getenv('NINE_ROUTER_API_KEY', '')
PORT = int(os.getenv('PORT', '8000'))
