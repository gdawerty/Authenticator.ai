from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.core.config import settings
from app.api import upload, document, convert, context, auth, audits, oauth, pipeline, contracts

# Create FastAPI app
app = FastAPI(
    title=settings.PROJECT_NAME,
    openapi_url=f"{settings.API_V1_PREFIX}/openapi.json"
)

# Configure CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins
    allow_credentials=True,  # Enable credentials for auth
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(
    auth.router,
    prefix=f"{settings.API_V1_PREFIX}/auth",
    tags=["auth"]
)
app.include_router(
    oauth.router,
    prefix=f"{settings.API_V1_PREFIX}/oauth",
    tags=["oauth"]
)
app.include_router(
    upload.router,
    prefix=f"{settings.API_V1_PREFIX}/upload",
    tags=["upload"]
)
app.include_router(
    audits.router,
    prefix=f"{settings.API_V1_PREFIX}/audits",
    tags=["audits"]
)
app.include_router(
    document.router,
    prefix=f"{settings.API_V1_PREFIX}/documents",
    tags=["documents"]
)
app.include_router(
    convert.router,
    prefix=settings.API_V1_PREFIX,
    tags=["convert"]
)
app.include_router(
    context.router,
    prefix=settings.API_V1_PREFIX,
    tags=["context"]
)
app.include_router(
    pipeline.router,
    prefix=f"{settings.API_V1_PREFIX}/pipeline",
    tags=["pipeline"]
)
app.include_router(
    contracts.router,
    prefix=f"{settings.API_V1_PREFIX}/contracts",
    tags=["contracts"]
)


@app.on_event("startup")
async def run_migrations():
    """Add any missing columns introduced after initial schema creation."""
    from app.db.session import engine
    with engine.connect() as conn:
        for stmt in [
            "ALTER TABLE contracts ADD COLUMN shared INTEGER NOT NULL DEFAULT 0",
        ]:
            try:
                conn.execute(text(stmt))
                conn.commit()
            except Exception:
                pass  # Column already exists


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "message": "Authenticator.AI Pipeline API",
        "version": "1.0.0",
        "docs": f"{settings.API_V1_PREFIX}/docs"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy"}


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8001)
