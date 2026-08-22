import io
import unittest
import numpy as np
from PIL import Image
from engine.enhancer import EnhancementPipeline
from engine.presets import PRESETS
from engine.ai_engine import AIEnhancementEngine

def create_dummy_image(width=100, height=80, color=(120, 150, 200)) -> bytes:
    img = Image.new("RGB", (width, height), color=color)
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()

def test_non_ai_enhancement_pipeline():
    raw = create_dummy_image()
    params = PRESETS["auto_vibrant"]["params"]
    output = EnhancementPipeline.process_bytes(raw, params, output_format="PNG")
    
    assert len(output) > 0
    out_img = Image.open(io.BytesIO(output))
    assert out_img.size == (100, 80)

def test_upscale_2x():
    raw = create_dummy_image(50, 40)
    params = PRESETS["super_sharp_2x"]["params"]
    output = EnhancementPipeline.process_bytes(raw, params, output_format="PNG")
    
    out_img = Image.open(io.BytesIO(output))
    assert out_img.size == (100, 80)

def test_all_presets():
    raw = create_dummy_image(64, 64)
    for p_key, p_val in PRESETS.items():
        out = EnhancementPipeline.process_bytes(raw, p_val["params"], output_format="JPEG")
        assert len(out) > 0
        img = Image.open(io.BytesIO(out))
        assert img.width >= 64

def test_ai_supported_models_registry():
    models = AIEnhancementEngine.get_supported_models()
    assert "replicate" in models
    assert "stability" in models
    assert "huggingface" in models
    assert "real-esrgan" in models["replicate"]["models"]
    assert "gfpgan" in models["replicate"]["models"]
    assert "codeformer" in models["replicate"]["models"]
