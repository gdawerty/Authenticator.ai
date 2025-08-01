from fastapi import FastAPI, File, UploadFile
from fastapi.middleware.cors import CORSMiddleware
import filetype

app = FastAPI()

# Enable CORS for frontend support (e.g., drag & drop, file input)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Replace with specific domain in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()
    kind = filetype.guess(contents)

    if kind is None:
        return {"error": "Cannot determine file type"}

    return {
        "filename": file.filename,
        "mime_type": kind.mime,
        "extension": kind.extension,
        "size_kb": round(len(contents) / 1024, 2)
    }

