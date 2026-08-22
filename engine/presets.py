"""
WebMagic Enhancement Engine - Presets Configuration
"""
from typing import Dict, Any

PRESETS: Dict[str, Dict[str, Any]] = {
    "esmagic": {
        "name": " EsMagic (Autonomous Pro)",
        "description": "Our signature all-in-one model: auto noise removal, dynamic shadow/highlight recovery, color harmonization, and edge crispening.",
        "params": {
            "clahe_clip": 2.6,
            "clahe_grid": 8,
            "sharpness": 1.5,
            "saturation": 1.3,
            "denoise": 14,
            "contrast": 1.18,
            "brightness": 1.06,
            "vibrance": 1.35,
            "warmth": 0.0,
            "gamma": 1.05,
            "scale": 1.0
        }
    },
    "auto_vibrant": {
        "name": "Auto Vibrant",
        "description": "Smart dynamic range boost, vivid colors, and subtle micro-sharpening.",
        "params": {
            "clahe_clip": 2.2,
            "clahe_grid": 8,
            "sharpness": 1.4,
            "saturation": 1.35,
            "denoise": 10,
            "contrast": 1.15,
            "brightness": 1.05,
            "vibrance": 1.3,
            "warmth": 0.0,
            "gamma": 1.0,
            "scale": 1.0
        }
    },
    "crisp_portrait": {
        "name": "Crisp Portrait",
        "description": "Smooth skin tones with edge-preserving bilateral filtering and selective eye/hair sharpening.",
        "params": {
            "clahe_clip": 1.5,
            "clahe_grid": 8,
            "sharpness": 1.6,
            "saturation": 1.1,
            "denoise": 22,
            "contrast": 1.1,
            "brightness": 1.08,
            "vibrance": 1.15,
            "warmth": 4.0,
            "gamma": 0.98,
            "scale": 1.0
        }
    },
    "night_restore": {
        "name": "Night Shot Restore",
        "description": "Deep shadow recovery, aggressive multi-stage chroma denoising, and balanced contrast.",
        "params": {
            "clahe_clip": 3.8,
            "clahe_grid": 12,
            "sharpness": 1.2,
            "saturation": 1.2,
            "denoise": 35,
            "contrast": 1.25,
            "brightness": 1.25,
            "vibrance": 1.2,
            "warmth": -2.0,
            "gamma": 1.2,
            "scale": 1.0
        }
    },
    "clarify_document": {
        "name": "Document & Scan Clarify",
        "description": "High-contrast text clarification, shadow removal, and background whitening.",
        "params": {
            "clahe_clip": 4.5,
            "clahe_grid": 16,
            "sharpness": 2.5,
            "saturation": 0.8,
            "denoise": 15,
            "contrast": 1.5,
            "brightness": 1.15,
            "vibrance": 0.9,
            "warmth": 0.0,
            "gamma": 0.9,
            "scale": 1.0
        }
    },
    "vintage_cleanup": {
        "name": "Vintage Photo Restore",
        "description": "Restores faded historical photographs, fixes yellowing/fading, and sharpens soft film scans.",
        "params": {
            "clahe_clip": 2.8,
            "clahe_grid": 8,
            "sharpness": 1.8,
            "saturation": 1.25,
            "denoise": 25,
            "contrast": 1.2,
            "brightness": 1.05,
            "vibrance": 1.2,
            "warmth": -5.0,
            "gamma": 1.05,
            "scale": 1.0
        }
    },
    "super_sharp_2x": {
        "name": "Super Sharp 2x (Non-AI)",
        "description": "High-quality Lanczos-4 upscaling combined with unsharp masking and detail enhancement.",
        "params": {
            "clahe_clip": 2.0,
            "clahe_grid": 8,
            "sharpness": 1.7,
            "saturation": 1.1,
            "denoise": 12,
            "contrast": 1.1,
            "brightness": 1.0,
            "vibrance": 1.1,
            "warmth": 0.0,
            "gamma": 1.0,
            "scale": 2.0
        }
    }
}
