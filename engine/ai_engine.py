"""
WebMagic AI Enhancement Providers Integration
Supports:
1. Replicate (Real-ESRGAN, GFPGAN face restoration, CodeFormer, NightMareAI)
2. Stability AI (SDXL Creative / Conservative Upscale, Fast Upscale)
3. OpenAI (DALL-E 3 / GPT-4o Vision Edit / Variations)
4. Hugging Face Inference API (SwinIR, Real-ESRGAN, Restormer)
"""
import io
import base64
import asyncio
from typing import Optional, Dict, Any
import httpx
from PIL import Image

class AIEnhancementError(Exception):
    pass

class AIEnhancementEngine:
    """Unified client for invoking state-of-the-art AI enhancement APIs."""

    @staticmethod
    def get_supported_models() -> Dict[str, Any]:
        return {
            "replicate": {
                "name": "Replicate AI",
                "doc_url": "https://replicate.com",
                "key_header": "X-Replicate-Key",
                "models": {
                    "real-esrgan": {
                        "name": "Real-ESRGAN (General Super-Resolution)",
                        "version": "f121d5f38e8eccbe3ab47d0bdec97106e54ce8f9e5f0a2164745ab0e97ffde8f",
                        "description": "State-of-the-art general super-resolution 2x/4x/8x upscaling.",
                        "default_scale": 4,
                        "supports_face_enhance": True
                    },
                    "gfpgan": {
                        "name": "GFPGAN (TencentARC Face Restoration)",
                        "version": "9283608cc6b7be6b65a8e44983db012355fde41320b9bf6b41043ba9efc4e20b",
                        "description": "Practical face restoration algorithm for vintage & degraded portrait photos.",
                        "default_scale": 2,
                        "supports_face_enhance": True
                    },
                    "codeformer": {
                        "name": "CodeFormer (Robust Face & Detail Restorer)",
                        "version": "7de2ea26c616d5bf9945f7757da026737ea42f040d089a6ca094202141aebd9d",
                        "description": "Codebook-based face reconstruction and artifact removal.",
                        "default_scale": 2,
                        "supports_face_enhance": True
                    }
                }
            },
            "stability": {
                "name": "Stability AI",
                "doc_url": "https://stability.ai",
                "key_header": "X-Stability-Key",
                "models": {
                    "creative-upscale": {
                        "name": "Stability Creative Upscaler",
                        "endpoint": "https://api.stability.ai/v2beta/stable-image/upscale/creative",
                        "description": "Generative hallucination upscaler up to 4K resolution.",
                        "default_scale": 4
                    },
                    "conservative-upscale": {
                        "name": "Stability Conservative Upscaler",
                        "endpoint": "https://api.stability.ai/v2beta/stable-image/upscale/conservative",
                        "description": "High-fidelity preservation upscaler with minimal distortion.",
                        "default_scale": 4
                    },
                    "fast-upscale": {
                        "name": "Stability Fast Upscale (ESRGAN)",
                        "endpoint": "https://api.stability.ai/v2beta/stable-image/upscale/fast",
                        "description": "Rapid 4x super-resolution.",
                        "default_scale": 4
                    }
                }
            },
            "openai": {
                "name": "OpenAI Vision & DALL-E",
                "doc_url": "https://openai.com",
                "key_header": "X-OpenAI-Key",
                "models": {
                    "dall-e-3": {
                        "name": "DALL-E 3 Creative Remaster",
                        "description": "Generative remastering & hyper-detail regeneration with visual prompting."
                    },
                    "gpt-4o-vision": {
                        "name": "GPT-4o Vision Intelligent Analysis & Masking",
                        "description": "Vision assessment and targeted prompt generation."
                    }
                }
            },
            "huggingface": {
                "name": "Hugging Face Inference",
                "doc_url": "https://huggingface.co",
                "key_header": "X-HF-Token",
                "models": {
                    "swinir": {
                        "name": "SwinIR Super-Resolution",
                        "repo_id": "caidas/swin2SR-classical-sr-x2-64",
                        "description": "Transformer-based classical super-resolution."
                    },
                    "restormer": {
                        "name": "Restormer Image Restoration",
                        "repo_id": "swook/restormer-real-world-denoising",
                        "description": "Transformer model for real-world denoising and deblurring."
                    }
                }
            }
        }

    @classmethod
    async def enhance_with_replicate(
        cls,
        image_bytes: bytes,
        api_token: str,
        model_name: str = "real-esrgan",
        scale: int = 4,
        face_enhance: bool = True,
        prompt: Optional[str] = None
    ) -> bytes:
        """Call Replicate AI models with polling for completion."""
        models = cls.get_supported_models()["replicate"]["models"]
        if model_name not in models:
            raise AIEnhancementError(f"Unsupported Replicate model: {model_name}. Available: {list(models.keys())}")

        version_id = models[model_name]["version"]
        base64_img = f"data:image/png;base64,{base64.b64encode(image_bytes).decode('utf-8')}"

        input_payload = {
            "image": base64_img,
            "scale": scale,
            "face_enhance": face_enhance
        }
        if model_name == "codeformer":
            input_payload["fidelity"] = 0.7
            input_payload["upscale"] = scale
            input_payload["face_upsample"] = face_enhance

        headers = {
            "Authorization": f"Token {api_token}",
            "Content-Type": "application/json"
        }

        async with httpx.AsyncClient(timeout=120.0) as client:
            create_url = "https://api.replicate.com/v1/predictions"
            payload = {
                "version": version_id,
                "input": input_payload
            }
            resp = await client.post(create_url, headers=headers, json=payload)
            if resp.status_code != 201:
                error_msg = resp.text
                try:
                    error_msg = resp.json().get("detail", resp.text)
                except Exception:
                    pass
                raise AIEnhancementError(f"Replicate API error ({resp.status_code}): {error_msg}")

            pred = resp.json()
            pred_id = pred["id"]
            poll_url = f"https://api.replicate.com/v1/predictions/{pred_id}"

            for _ in range(60):
                await asyncio.sleep(2)
                poll_resp = await client.get(poll_url, headers=headers)
                if poll_resp.status_code != 200:
                    continue
                poll_data = poll_resp.json()
                status = poll_data.get("status")
                if status == "succeeded":
                    output_url = poll_data.get("output")
                    if isinstance(output_url, list):
                        output_url = output_url[0]
                    img_resp = await client.get(output_url)
                    if img_resp.status_code == 200:
                        return img_resp.content
                    raise AIEnhancementError(f"Failed to fetch enhanced image from {output_url}")
                elif status in ["failed", "canceled"]:
                    err = poll_data.get("error", "Unknown error during AI processing")
                    raise AIEnhancementError(f"Replicate prediction failed: {err}")

            raise AIEnhancementError("Replicate request timed out after 120 seconds.")

    @classmethod
    async def enhance_with_stability(
        cls,
        image_bytes: bytes,
        api_key: str,
        model_name: str = "conservative-upscale",
        prompt: Optional[str] = "Masterpiece, ultra-sharp detail, high fidelity, 8k resolution, crisp textures"
    ) -> bytes:
        """Call Stability AI Upscaling APIs."""
        models = cls.get_supported_models()["stability"]["models"]
        if model_name not in models:
            model_name = "conservative-upscale"

        endpoint = models[model_name]["endpoint"]
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Accept": "image/*"
        }

        files = {
            "image": ("image.png", image_bytes, "image/png")
        }
        data = {}
        if model_name == "creative-upscale":
            data["prompt"] = prompt or "high detail, sharp focus, 4k ultra realistic"
            data["creativity"] = 0.35
        elif model_name == "conservative-upscale":
            data["prompt"] = prompt or "high resolution, pristine clarity"
            data["creativity"] = 0.2

        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(endpoint, headers=headers, files=files, data=data)
            if resp.status_code == 200:
                return resp.content

            if resp.headers.get("content-type", "").startswith("application/json"):
                res_json = resp.json()
                if "id" in res_json:
                    generation_id = res_json["id"]
                    poll_url = f"https://api.stability.ai/v2beta/stable-image/upscale/result/{generation_id}"
                    for _ in range(60):
                        await asyncio.sleep(2)
                        p_resp = await client.get(poll_url, headers=headers)
                        if p_resp.status_code == 200 and p_resp.headers.get("content-type", "").startswith("image/"):
                            return p_resp.content
                        elif p_resp.status_code == 202:
                            continue
                        else:
                            raise AIEnhancementError(f"Stability processing failed: {p_resp.text}")

                raise AIEnhancementError(f"Stability API error: {res_json}")

            raise AIEnhancementError(f"Stability API error ({resp.status_code}): {resp.text}")

    @classmethod
    async def enhance_with_huggingface(
        cls,
        image_bytes: bytes,
        api_token: str,
        model_name: str = "swinir"
    ) -> bytes:
        """Call Hugging Face Inference API for image restoration."""
        models = cls.get_supported_models()["huggingface"]["models"]
        model_info = models.get(model_name, models["swinir"])
        repo_id = model_info["repo_id"]

        url = f"https://api-inference.huggingface.co/models/{repo_id}"
        headers = {
            "Authorization": f"Bearer {api_token}",
            "Content-Type": "application/octet-stream"
        }

        async with httpx.AsyncClient(timeout=90.0) as client:
            resp = await client.post(url, headers=headers, content=image_bytes)
            if resp.status_code == 200:
                return resp.content
            if resp.status_code == 503:
                raise AIEnhancementError(f"Hugging Face model is currently loading. Please try again in 20 seconds. ({resp.text})")
            raise AIEnhancementError(f"Hugging Face API error ({resp.status_code}): {resp.text}")
