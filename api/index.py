import sys
import os

# Add root to import path so FastAPI can load from app/
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from app.main import app
