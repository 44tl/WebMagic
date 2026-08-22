"""
WebMagic FastAPI Backend Server
Provides image processing endpoints for both Non-AI and AI models,
manages user-supplied API keys per request securely, and serves the static web UI.
"""
import io
import os
import json
from pathlib import Path
from typing import Optional, Dict, Any

from fastapi import FastAPI, File, UploadFile, Form, Header, HTTPException, Query, Response
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
from PIL import Image

from engine.enhancer import EnhancementPipeline
from engine.esmagic import EsMagicEngine
from engine.ai_engine import AIEnhancementEngine, AIEnhancementError
from engine.presets import PRESETS

BASE_DIR = Path(__file__).resolve().parent.parent
STATIC_DIR = BASE_DIR / "web"

app = FastAPI(
    title="WebMagic Enhancement Suite",
    description="Professional Image Enhancement API with Non-AI filters and State-of-the-Art Generative AI models.",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    """Serve main web application index.html."""
    index_path = STATIC_DIR / "index.html"
    if not index_path.exists():
        raise HTTPException(status_code=404, detail="Index HTML not found")
    return HTMLResponse(content=index_path.read_text(encoding="utf-8"))

app.mount("/static", StaticFiles(directory=str(STATIC_DIR)), name="static")

@app.get("/app.js")
async def serve_app_js():
    return FileResponse(STATIC_DIR / "app.js", media_type="application/javascript")

@app.get("/style.css")
async def serve_style_css():
    return FileResponse(STATIC_DIR / "style.css", media_type="text/css")

@app.get("/api/presets")
async def get_presets():
    """Retrieve list of all pre-configured algorithmic presets."""
    return {"presets": PRESETS}

@app.get("/api/models")
async def get_ai_models():
    """Retrieve all supported state-of-the-art AI enhancement models and required headers."""
    return {
        "providers": AIEnhancementEngine.get_supported_models()
    }

@app.post("/api/enhance/non-ai")
async def enhance_non_ai(
    file: UploadFile = File(...),
    preset: Optional[str] = Form(None),
    clahe_clip: float = Form(2.0),
    clahe_grid: int = Form(8),
    sharpness: float = Form(1.3),
    saturation: float = Form(1.2),
    vibrance: float = Form(1.15),
    denoise: float = Form(10.0),
    contrast: float = Form(1.1),
    brightness: float = Form(1.0),
    warmth: float = Form(0.0),
    gamma: float = Form(1.0),
    scale: float = Form(1.0),
    output_format: str = Form("PNG")
):
    """
    Process image using local non-AI computer vision algorithms.
    Zero external calls or API keys required.
    """
    try:
        raw_bytes = await file.read()
        if not raw_bytes:
            raise HTTPException(status_code=400, detail="Empty image uploaded")

        if preset == "esmagic":
            result_bytes = EsMagicEngine.process_bytes(
                raw_bytes,
                scale=scale,
                output_format=output_format
            )
        elif preset and preset in PRESETS:
            params = PRESETS[preset]["params"].copy()
            if scale > 1.0:
                params["scale"] = scale
            result_bytes = EnhancementPipeline.process_bytes(
                raw_bytes,
                params=params,
                output_format=output_format
            )
        else:
            params = {
                "clahe_clip": clahe_clip,
                "clahe_grid": clahe_grid,
                "sharpness": sharpness,
                "saturation": saturation,
                "vibrance": vibrance,
                "denoise": denoise,
                "contrast": contrast,
                "brightness": brightness,
                "warmth": warmth,
                "gamma": gamma,
                "scale": scale
            }
            result_bytes = EnhancementPipeline.process_bytes(
                raw_bytes,
                params=params,
                output_format=output_format
            )

        media_type = f"image/{output_format.lower().replace('jpg', 'jpeg')}"
        return Response(
            content=result_bytes,
            media_type=media_type,
            headers={
                "Content-Disposition": f'inline; filename="enhanced_{file.filename or "image.png"}"'
            }
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/enhance/ai")
async def enhance_ai(
    file: UploadFile = File(...),
    provider: str = Form("replicate"),
    model_name: str = Form("real-esrgan"),
    scale: int = Form(4),
    face_enhance: bool = Form(True),
    prompt: Optional[str] = Form(None),
    x_replicate_key: Optional[str] = Header(None, alias="X-Replicate-Key"),
    x_stability_key: Optional[str] = Header(None, alias="X-Stability-Key"),
    x_openai_key: Optional[str] = Header(None, alias="X-OpenAI-Key"),
    x_hf_token: Optional[str] = Header(None, alias="X-HF-Token")
):
    """
    Process image using State-of-the-Art generative super-resolution and restoration AI models.
    Supports user provided API keys passed securely via request headers or server env.
    """
    try:
        raw_bytes = await file.read()
        if not raw_bytes:
            raise HTTPException(status_code=400, detail="Empty image uploaded")

        if provider == "replicate":
            token = x_replicate_key or os.environ.get("REPLICATE_API_TOKEN")
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Replicate API Token is required. Add it in API Key settings (X-Replicate-Key header) or set REPLICATE_API_TOKEN."
                )
            result_bytes = await AIEnhancementEngine.enhance_with_replicate(
                raw_bytes,
                api_token=token,
                model_name=model_name,
                scale=scale,
                face_enhance=face_enhance,
                prompt=prompt
            )

        elif provider == "stability":
            key = x_stability_key or os.environ.get("STABILITY_API_KEY")
            if not key:
                raise HTTPException(
                    status_code=401,
                    detail="Stability API Key is required. Add it in API Key settings (X-Stability-Key header) or set STABILITY_API_KEY."
                )
            result_bytes = await AIEnhancementEngine.enhance_with_stability(
                raw_bytes,
                api_key=key,
                model_name=model_name,
                prompt=prompt
            )

        elif provider == "huggingface":
            token = x_hf_token or os.environ.get("HF_TOKEN")
            if not token:
                raise HTTPException(
                    status_code=401,
                    detail="Hugging Face User Access Token is required. Add it in API Key settings (X-HF-Token header) or set HF_TOKEN."
                )
            result_bytes = await AIEnhancementEngine.enhance_with_huggingface(
                raw_bytes,
                api_token=token,
                model_name=model_name
            )

        else:
            raise HTTPException(status_code=400, detail=f"Unsupported AI Provider: {provider}")

        return Response(
            content=result_bytes,
            media_type="image/png",
            headers={
                "Content-Disposition": f'inline; filename="ai_enhanced_{file.filename or "image.png"}"'
            }
        )

    except AIEnhancementError as aie:
        raise HTTPException(status_code=502, detail=str(aie))
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
