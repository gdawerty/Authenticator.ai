from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import upload, document, convert, context, auth

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
    upload.router,
    prefix=f"{settings.API_V1_PREFIX}/upload",
    tags=["upload"]
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
