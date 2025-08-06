from fastapi import APIRouter, File, UploadFile, HTTPException
import os
import filetype
from datetime import datetime

router = APIRouter()

UPLOAD_DIR = os.getenv('UPLOAD_DIR', 'uploads')
os.makedirs(UPLOAD_DIR, exist_ok=True)

def generate_safe_filename(original_name: str) -> str:
    name, ext = os.path.splitext(original_name)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    return f"{name}_{timestamp}{ext}"

@router.post("/upload/")
async def upload_file(file: UploadFile = File(...)):
    contents = await file.read()

    kind = filetype.guess(contents)
    if kind is None:
        raise HTTPException(status_code=400, detail="Cannot determine file type")

    original_filename = file.filename
    save_path = os.path.join(UPLOAD_DIR, original_filename)

    # 🚫 If file exists, generate a safe unique filename
    if os.path.exists(save_path):
        original_filename = generate_safe_filename(original_filename)
        save_path = os.path.join(UPLOAD_DIR, original_filename)

    with open(save_path, "wb") as f:
        f.write(contents)

    return {
        "filename": original_filename,
        "mime_type": kind.mime,
        "extension": kind.extension,
        "size_kb": round(len(contents) / 1024, 2),
        "saved_to": save_path
    }
