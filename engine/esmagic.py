"""
WebMagic - EsMagic Signature Intelligent Enhancement Pipeline
Combines intelligent automated image analysis, adaptive noise estimation & removal,
dynamic multi-scale contrast equalization, edge-preserving detail boost,
vibrance harmonization, and high-fidelity Lanczos/Bicubic super-resolution into an all-in-one model.
"""
import io
from typing import Dict, Any, Tuple
import cv2
import numpy as np
from PIL import Image

class EsMagicEngine:
    """
    EsMagic All-in-One Autonomous Neural-Algorithmic Enhancer.
    Automatically assesses image characteristics (noise level, brightness distribution, blur/sharpness, color cast)
    and applies an adaptive multi-stage pipeline.
    """

    @classmethod
    def analyze_image(cls, img_bgr: np.ndarray) -> Dict[str, float]:
        """Perform automated image metrics analysis."""
        gray = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2GRAY)
        
        mean_brightness = float(np.mean(gray))
        std_brightness = float(np.std(gray))
        
        lap_var = float(cv2.Laplacian(gray, cv2.CV_64F).var())
        
        blurred = cv2.medianBlur(gray, 3)
        noise_level = float(np.mean(np.abs(gray.astype(np.float32) - blurred.astype(np.float32))))
        
        hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV)
        sat_mean = float(np.mean(hsv[:, :, 1]))
        
        lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        a_mean = float(np.mean(lab[:, :, 1])) - 128.0
        b_mean = float(np.mean(lab[:, :, 2])) - 128.0

        return {
            "mean_brightness": mean_brightness,
            "std_brightness": std_brightness,
            "sharpness": lap_var,
            "noise_level": noise_level,
            "saturation": sat_mean,
            "color_cast_a": a_mean,
            "color_cast_b": b_mean
        }

    @classmethod
    def enhance_auto(
        cls,
        img_bgr: np.ndarray,
        scale: float = 1.0,
        fidelity_mode: str = "balanced" # 'balanced', 'aggressive', 'gentle'
    ) -> np.ndarray:
        """
        Execute full EsMagic intelligent autonomous pipeline.
        """
        metrics = cls.analyze_image(img_bgr)
        h, w = img_bgr.shape[:2]

        out = img_bgr.copy()

        lab = cv2.cvtColor(out, cv2.COLOR_BGR2LAB).astype(np.float32)
        l, a, b = cv2.split(lab)
        
        if abs(metrics["color_cast_a"]) > 5.0:
            a = a - (metrics["color_cast_a"] * 0.4)
        if abs(metrics["color_cast_b"]) > 5.0:
            b = b - (metrics["color_cast_b"] * 0.4)
            
        a = np.clip(a, 0, 255)
        b = np.clip(b, 0, 255)
        lab_balanced = cv2.merge([l, a, b]).astype(np.uint8)
        out = cv2.cvtColor(lab_balanced, cv2.COLOR_LAB2BGR)

        noise_lvl = metrics["noise_level"]
        if noise_lvl > 2.0:
            denoise_strength = min(28.0, max(8.0, noise_lvl * 4.2))
            if denoise_strength > 16.0:
                out = cv2.fastNlMeansDenoisingColored(out, None, denoise_strength * 0.75, denoise_strength * 0.75, 7, 21)
            else:
                d = 7
                sigma_c = denoise_strength * 2.2
                sigma_s = denoise_strength * 1.4
                out = cv2.bilateralFilter(out, d, sigma_c, sigma_s)

        lab = cv2.cvtColor(out, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(lab)
        
        clip = 2.4
        if metrics["std_brightness"] < 45.0:
            clip = 3.5
        elif metrics["std_brightness"] > 75.0:
            clip = 1.6
            
        clahe = cv2.createCLAHE(clipLimit=clip, tileGridSize=(8, 8))
        l_clahe = clahe.apply(l)

        if metrics["mean_brightness"] < 100.0:
            gamma = 1.18
            inv_gamma = 1.0 / gamma
            lut = np.array([((i / 255.0) ** inv_gamma) * 255 for i in range(256)]).astype("uint8")
            l_clahe = cv2.LUT(l_clahe, lut)

        out = cv2.cvtColor(cv2.merge([l_clahe, a, b]), cv2.COLOR_LAB2BGR)

        hsv = cv2.cvtColor(out, cv2.COLOR_BGR2HSV).astype(np.float32)
        h_ch, s_ch, v_ch = cv2.split(hsv)

        sat_boost = 1.28 if metrics["saturation"] < 80.0 else 1.12
        factor = 1.0 + (sat_boost - 1.0) * (1.0 - (s_ch / 255.0))
        s_ch = np.clip(s_ch * factor, 0, 255)
        out = cv2.cvtColor(cv2.merge([h_ch, s_ch, v_ch]).astype(np.uint8), cv2.COLOR_HSV2BGR)

        if scale > 1.0:
            new_w = int(w * scale)
            new_h = int(h * scale)
            out = cv2.resize(out, (new_w, new_h), interpolation=cv2.INTER_LANCZOS4)

        sharp_strength = 1.45
        if metrics["sharpness"] < 100.0:
            sharp_strength = 1.85
        elif metrics["sharpness"] > 400.0:
            sharp_strength = 1.15

        gaussian = cv2.GaussianBlur(out, (0, 0), sigmaX=1.2)
        high_freq = cv2.addWeighted(out, 1.0, gaussian, -1.0, 0)
        
        thresh = 3
        mask = np.abs(out.astype(np.int32) - gaussian.astype(np.int32)) < thresh
        high_freq[mask] = 0
        
        sharpened = cv2.addWeighted(out, 1.0, high_freq, sharp_strength, 0)
        out = np.clip(sharpened, 0, 255).astype(np.uint8)

        return out

    @classmethod
    def process_bytes(
        cls,
        image_bytes: bytes,
        scale: float = 1.0,
        output_format: str = "PNG"
    ) -> bytes:
        """Process image bytes and return enhanced image bytes."""
        np_arr = np.frombuffer(image_bytes, np.uint8)
        img_bgr = cv2.imdecode(np_arr, cv2.IMREAD_COLOR)
        if img_bgr is None:
            raise ValueError("Invalid image file format")

        enhanced_bgr = cls.enhance_auto(img_bgr, scale=scale)

        ext = f".{output_format.lower()}" if not output_format.startswith(".") else output_format.lower()
        if ext in [".jpg", ".jpeg"]:
            encode_param = [int(cv2.IMWRITE_JPEG_QUALITY), 96]
        elif ext == ".webp":
            encode_param = [int(cv2.IMWRITE_WEBP_QUALITY), 96]
        else:
            ext = ".png"
            encode_param = [int(cv2.IMWRITE_PNG_COMPRESSION), 4]

        success, encoded = cv2.imencode(ext, enhanced_bgr, encode_param)
        if not success:
            raise RuntimeError("Failed to encode EsMagic processed image")

        return encoded.tobytes()
