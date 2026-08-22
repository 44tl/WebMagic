"""
WebMagic Non-AI Image Enhancement Engine
Fast, algorithmic enhancement pipelines utilizing OpenCV, NumPy, and PIL.
Features:
- CLAHE (Contrast Limited Adaptive Histogram Equalization) in LAB color space
- Unsharp Masking & High-Pass frequency sharpening
- Bilateral & Fast NLM Denoising (edge-preserving)
- Vibrance, Smart Saturation & Tone Curves
- Temperature/Warmth and Gamma adjustment
- Lanczos-4 Super Resolution / High Quality Resampling
"""
import io
from typing import Optional, Dict, Any, Tuple
import cv2
import numpy as np
from PIL import Image, ImageEnhance, ImageFilter

class EnhancementPipeline:
    """Non-AI High Performance Algorithmic Image Enhancer."""

    @staticmethod
    def adjust_gamma(image_bgr: np.ndarray, gamma: float = 1.0) -> np.ndarray:
        """Adjust image gamma value."""
        if abs(gamma - 1.0) < 0.01:
            return image_bgr
        inv_gamma = 1.0 / max(0.1, gamma)
        table = np.array([((i / 255.0) ** inv_gamma) * 255 for i in np.arange(0, 256)]).astype("uint8")
        return cv2.LUT(image_bgr, table)

    @staticmethod
    def apply_clahe(image_bgr: np.ndarray, clip_limit: float = 2.0, tile_grid_size: int = 8) -> np.ndarray:
        """Apply CLAHE to L-channel in LAB color space for natural contrast enhancement."""
        if clip_limit <= 0:
            return image_bgr
        lab = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        clahe = cv2.createCLAHE(clipLimit=float(clip_limit), tileGridSize=(int(tile_grid_size), int(tile_grid_size)))
        cl = clahe.apply(l)
        limg = cv2.merge((cl, a, b))
        return cv2.cvtColor(limg, cv2.COLOR_LAB2BGR)

    @staticmethod
    def apply_unsharp_mask(
        image_bgr: np.ndarray,
        amount: float = 1.5,
        radius: float = 1.0,
        threshold: int = 0
    ) -> np.ndarray:
        """Sharpen image using unsharp masking without creating harsh halo artifacts."""
        if amount <= 0:
            return image_bgr
        
        blurred = cv2.GaussianBlur(image_bgr, (0, 0), radius)
        diff = cv2.addWeighted(image_bgr, 1.0, blurred, -1.0, 0)
        
        if threshold > 0:
            low_contrast_mask = np.abs(image_bgr.astype(np.int32) - blurred.astype(np.int32)) < threshold
            diff[low_contrast_mask] = 0
            
        sharpened = cv2.addWeighted(image_bgr, 1.0, diff, amount, 0)
        return np.clip(sharpened, 0, 255).astype(np.uint8)

    @staticmethod
    def apply_denoise(image_bgr: np.ndarray, strength: float = 10.0) -> np.ndarray:
        """Edge-preserving bilateral filtering or NLM denoising."""
        if strength <= 0:
            return image_bgr
        
        if strength > 20:
            h = min(strength, 35.0)
            return cv2.fastNlMeansDenoisingColored(image_bgr, None, h, h, 7, 21)
        else:
            d = int(min(9, max(3, strength / 2)))
            sigma_color = strength * 2.5
            sigma_space = strength * 1.5
            return cv2.bilateralFilter(image_bgr, d, sigma_color, sigma_space)

    @staticmethod
    def adjust_vibrance_and_saturation(
        image_bgr: np.ndarray,
        saturation: float = 1.0,
        vibrance: float = 1.0
    ) -> np.ndarray:
        """Boost colors smartly without oversaturating already vivid pixels."""
        if abs(saturation - 1.0) < 0.01 and abs(vibrance - 1.0) < 0.01:
            return image_bgr

        hsv = cv2.cvtColor(image_bgr, cv2.COLOR_BGR2HSV).astype(np.float32)
        h, s, v = cv2.split(hsv)

        s = s * saturation

        if abs(vibrance - 1.0) >= 0.01:
            vib_mult = vibrance - 1.0
            factor = 1.0 + vib_mult * (1.0 - (s / 255.0))
            s = s * factor

        s = np.clip(s, 0, 255)
        hsv_out = cv2.merge([h, s, v]).astype(np.uint8)
        return cv2.cvtColor(hsv_out, cv2.COLOR_HSV2BGR)

    @staticmethod
    def adjust_warmth(image_bgr: np.ndarray, warmth: float = 0.0) -> np.ndarray:
        """Adjust color temperature. Positive = warmer (more red/yellow), Negative = cooler (more blue)."""
        if abs(warmth) < 0.1:
            return image_bgr

        img = image_bgr.astype(np.float32)
        b, g, r = cv2.split(img)

        factor = warmth * 0.8
        r = np.clip(r + factor, 0, 255)
        b = np.clip(b - factor, 0, 255)
        g = np.clip(g + (factor * 0.2), 0, 255)

        return cv2.merge([b, g, r]).astype(np.uint8)

    @staticmethod
    def adjust_brightness_contrast(
        image_bgr: np.ndarray,
        brightness: float = 1.0,
        contrast: float = 1.0
    ) -> np.ndarray:
        """Adjust brightness and contrast around midpoint 128."""
        if abs(brightness - 1.0) < 0.01 and abs(contrast - 1.0) < 0.01:
            return image_bgr

        img = image_bgr.astype(np.float32)
        bright_offset = (brightness - 1.0) * 100.0
        adjusted = contrast * (img - 128.0) + 128.0 + bright_offset
        return np.clip(adjusted, 0, 255).astype(np.uint8)

    @staticmethod
    def upscale_image(image_bgr: np.ndarray, scale: float = 1.0) -> np.ndarray:
        """Upscale image using high quality Lanczos-4 interpolation."""
        if scale <= 1.0 or scale > 8.0:
            return image_bgr

        h, w = image_bgr.shape[:2]
        new_w = int(w * scale)
        new_h = int(h * scale)
        return cv2.resize(image_bgr, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

    @classmethod
    def enhance_cv2(
        cls,
        image_bgr: np.ndarray,
        clahe_clip: float = 2.0,
        clahe_grid: int = 8,
        sharpness: float = 1.3,
        saturation: float = 1.2,
        vibrance: float = 1.15,
        denoise: float = 10.0,
        contrast: float = 1.1,
        brightness: float = 1.0,
        warmth: float = 0.0,
        gamma: float = 1.0,
        scale: float = 1.0
    ) -> np.ndarray:
        """Complete sequential enhancement pipeline."""
        out = image_bgr.copy()

        if scale > 1.0:
            out = cls.upscale_image(out, scale)

        if denoise > 0:
            out = cls.apply_denoise(out, strength=denoise)

        if clahe_clip > 0:
            out = cls.apply_clahe(out, clip_limit=clahe_clip, tile_grid_size=clahe_grid)

        out = cls.adjust_brightness_contrast(out, brightness=brightness, contrast=contrast)

        if abs(gamma - 1.0) >= 0.01:
            out = cls.adjust_gamma(out, gamma=gamma)

        out = cls.adjust_vibrance_and_saturation(out, saturation=saturation, vibrance=vibrance)

        if abs(warmth) >= 0.1:
            out = cls.adjust_warmth(out, warmth=warmth)

        if sharpness > 0:
            out = cls.apply_unsharp_mask(out, amount=sharpness)

        return out

    @classmethod
    def process_bytes(
        cls,
        image_bytes: bytes,
        params: Dict[str, Any],
        output_format: str = "PNG"
    ) -> bytes:
        """Process image bytes with given parameters and return encoded bytes."""
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise ValueError("Invalid or corrupted image format")

        enhanced_bgr = cls.enhance_cv2(
            img_bgr,
            clahe_clip=float(params.get("clahe_clip", 2.0)),
            clahe_grid=int(params.get("clahe_grid", 8)),
            sharpness=float(params.get("sharpness", 1.3)),
            saturation=float(params.get("saturation", 1.2)),
            vibrance=float(params.get("vibrance", 1.15)),
            denoise=float(params.get("denoise", 10.0)),
            contrast=float(params.get("contrast", 1.1)),
            brightness=float(params.get("brightness", 1.0)),
            warmth=float(params.get("warmth", 0.0)),
            gamma=float(params.get("gamma", 1.0)),
            scale=float(params.get("scale", 1.0))
        )

        ext = f".{output_format.lower()}" if not output_format.startswith(".") else output_format.lower()
        if ext in [".jpg", ".jpeg"]:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 95]
        elif ext == ".webp":
            encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), 95]
        elif ext == ".png":
            encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 4]
        else:
            ext = ".png"
            encode_param = []

        success, encoded = cv2.imencode(ext, enhanced_bgr, encode_param)
        if not success:
            raise RuntimeError("Failed to encode processed image")

        return encoded.tobytes()
