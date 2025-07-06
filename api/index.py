# api/index.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/")
async def home():
    return JSONResponse({"message": "🎉 FastAPI on Vercel with Neon is working!"})
