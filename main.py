from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from routes import upload  # import your routers


app = FastAPI(title='Authenticity MVP Backend')

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(upload.router)

@app.get("/")
def read_root():
    return {"message": "🚀 Authenticator.AI backend is running. Try /upload or /docs"}

