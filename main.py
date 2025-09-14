# main.py
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import RedirectResponse, StreamingResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from pydantic_settings import BaseSettings
import time
import logging
import qrcode
from io import BytesIO
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class Settings(BaseSettings):
    google_form: str = "https://docs.google.com/forms/d/e/1FAIpQLSdyNpfYG32plqaArUe0CrY_CyP_juXjhWDDOF-TZqwVgJmILw/viewform?usp=header"
    base_url: str = "http://localhost:8000"
    secret_key: str = "your-secure-secret-key-here"
    token_window: str = "30"

    class Config:
        env_file = ".env"

settings = Settings()

app = FastAPI(
    title="Attendance QR System",
    description="QR code-based attendance system",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")

@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(f"{request.method} {request.url.path} {response.status_code} {duration:.2f}s")
    return response

@app.get("/qr")
async def qr():
    try:
        # Generate a timestamp-based entry
        timestamp = int(time.time())
        
        # Create the Google Form URL with prefilled data
        form_url = f"{settings.google_form}{timestamp}"
        logger.info(f"Generated form URL: {form_url}")
        
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(form_url)
        qr.make(fit=True)
        
        img = qr.make_image(fill_color="black", back_color="white")
        buf = BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        
        return StreamingResponse(
            buf, 
            media_type="image/png",
            headers={"Cache-Control": "no-cache, no-store, must-revalidate"}
        )
    except Exception as e:
        logger.error(f"Error generating QR code: {str(e)}")
        raise HTTPException(status_code=500, detail="Error generating QR code")

# Add root route to serve index.html
@app.get("/", response_class=HTMLResponse)
def root():
    return Path("static/index.html").read_text()
