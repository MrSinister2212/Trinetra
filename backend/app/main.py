from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import init_db, AsyncSessionLocal
from app.auth import ensure_default_analyst
from app.routes.auth_routes import router as auth_router
from app.routes.search_routes import router as search_router
from app.routes.case_routes import router as case_router
from app.routes.report_routes import router as report_router
from app.routes.audit_routes import router as audit_router
from app.routes.ai_routes import router as ai_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Initialize DB schema
    await init_db()
    # Seed default user for analyst login
    async with AsyncSessionLocal() as session:
        await ensure_default_analyst(session)
    yield

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Modular Open-Source Intelligence (OSINT) Platform with defensible reporting, strict safety controls, and multi-format exports.",
    lifespan=lifespan
)

# Enable CORS for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(auth_router, prefix=settings.API_V1_STR)
app.include_router(search_router, prefix=settings.API_V1_STR)
app.include_router(case_router, prefix=settings.API_V1_STR)
app.include_router(report_router, prefix=settings.API_V1_STR)
app.include_router(audit_router, prefix=settings.API_V1_STR)
app.include_router(ai_router, prefix=settings.API_V1_STR)

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "mode": "production"
    }

# Mount static files and SPA fallback for desktop and self-hosted distributions
import os
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

# Check potential locations for frontend dist
dist_candidates = [
    os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend", "dist"),
    os.path.join(os.path.dirname(__file__), "dist"),
    os.path.abspath("dist")
]

dist_dir = next((d for d in dist_candidates if os.path.exists(d)), None)

if dist_dir:
    assets_dir = os.path.join(dist_dir, "assets")
    if os.path.exists(assets_dir):
        app.mount("/assets", StaticFiles(directory=assets_dir), name="assets")

    @app.get("/{full_path:path}")
    async def serve_spa(full_path: str):
        # If static file exists in dist, serve it
        target_path = os.path.join(dist_dir, full_path)
        if full_path and os.path.isfile(target_path):
            return FileResponse(target_path)
        # Fallback to index.html for client-side routing
        index_path = os.path.join(dist_dir, "index.html")
        if os.path.exists(index_path):
            return FileResponse(index_path)
        return {"error": "Frontend bundle not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
