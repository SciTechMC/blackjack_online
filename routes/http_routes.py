from fastapi import APIRouter
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
import os

router = APIRouter()

# Mount /static for other assets (if needed)
router.mount("/static", StaticFiles(directory="static"), name="static")

# Serve actual home.html and table.html from /static
@router.get("/", response_class=FileResponse)
async def serve_home():
    return FileResponse(os.path.join("static", "home.html"))

@router.get("/table.html", response_class=FileResponse)
async def serve_table():
    return FileResponse(os.path.join("static", "table.html"))
