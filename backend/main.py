import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import RedirectResponse
import os
import sys
from pathlib import Path

# Add project root to path so 'python backend/main.py' works
sys.path.insert(0, str(Path(__file__).parent.parent))

# Import DB and routes
from backend.db import connect_to_mongo, close_mongo_connection
from backend.routes import router

app = FastAPI(title="VisionSort API")

# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # For dev purposes
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup & Shutdown events for DB connection
@app.on_event("startup")
async def startup_db_client():
    await connect_to_mongo()

@app.on_event("shutdown")
async def shutdown_db_client():
    await close_mongo_connection()

# Include API Router
app.include_router(router, prefix="/api")

# Serve Frontend static files
frontend_path = Path(__file__).parent.parent / "frontend"
if frontend_path.exists():
    app.mount("/static", StaticFiles(directory=str(frontend_path)), name="frontend")
    
@app.get("/")
async def root():
    # Redirect root to frontend
    return RedirectResponse(url="/static/index.html")

if __name__ == "__main__":
    uvicorn.run("backend.main:app", host="0.0.0.0", port=8000, reload=True)
