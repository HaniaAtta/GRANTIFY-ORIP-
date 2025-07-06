# api/index.py
from mangum import Mangum
from app.main import app  # your FastAPI app lives here

handler = Mangum(app)  # required for Vercel's Lambda
