# WebMagic - Image Enhancement Suite

WebMagic is an image enhancement toolkit featuring both a command line interface and a web studio application. It supports algorithmic enhancement running locally without external keys, as well as generative AI models such as Real-ESRGAN, GFPGAN, CodeFormer, Stability SDXL, SwinIR, and Restormer.

---

## Features

### 1. EsMagic - Autonomous Enhancement Model (Default)
- Automatic Image Assessment: Detects noise levels, dynamic range distribution, blur metrics, and color cast automatically.
- Adaptive Processing Pipeline:
  - Auto white balance and chromatic cast correction.
  - Adaptive noise estimation and edge-preserving non-local means denoising.
  - Dynamic range contrast enhancement via CLAHE and shadow recovery.
  - Perceptual vibrance adjustment without over-saturating skin tones.
  - Halo-suppressed unsharp frequency sharpening.
  - Created by Eskrid.
- Zero API keys needed, runs locally and instantaneously.

### 2. Presets and Fine-Tuning
- `auto_vibrant`: Dynamic range boost, rich colors, and micro-sharpening.
- `crisp_portrait`: Smooth skin tones with eye and hair detail sharpening.
- `night_restore`: Shadow recovery and heavy low-light noise reduction.
- `clarify_document`: High-contrast document whitening and text clarification.
- `vintage_cleanup`: Faded photo restoration and color rejuvenation.
- `super_sharp_2x`: 2x Lanczos super-resolution and edge sharpening.

### 3. AI Models (Connect Your API Keys)
- Replicate:
  - `real-esrgan`: General super-resolution 2x, 4x, 8x.
  - `gfpgan`: TencentARC face restoration.
  - `codeformer`: Codebook-based facial detail reconstruction.
- Stability AI:
  - `creative-upscale`: Generative upscaling up to 4K.
  - `conservative-upscale`: High-fidelity upscaler with minimal distortion.
  - `fast-upscale`: Rapid ESRGAN upscaler.
- Hugging Face:
  - `swinir`: Swin Transformer classical super-resolution.
  - `restormer`: Real-world denoising and deblurring.
- OpenAI:
  - `dall-e-3` and `gpt-4o-vision`: Generative remastering with visual prompting.

---

## Quick Start

### Installation

```bash
git clone https://github.com/44tl/WebMagic.git
cd WebMagic
pip install -r requirements.txt
```

---

## Web Studio Application

Run the local web server:

```bash
python -m uvicorn server.app:app --host 0.0.0.0 --port 8067
```

Open `http://localhost:8067` in your web browser.

### Web Studio Features:
- EsMagic Default: Automated image analysis and enhancement without manual slider adjustments.
- Split Slider and Side-by-Side View: Compare before and after in real time.
- Press and Hold Original: Hold the button or spacebar to view untouched original.
- Live Canvas Filters: Client-side visual preview.
- Local Key Storage: API keys are stored locally in your browser localStorage.
- Export Formats: Download in PNG, JPEG, or WEBP.

---

## CLI Usage

```bash
python magic_cli.py models

python magic_cli.py enhance input.jpg -o output.png

python magic_cli.py enhance input.jpg -o output.png --preset crisp_portrait

python magic_cli.py batch ./input_photos/ -o ./enhanced_photos/

python magic_cli.py enhance input.jpg -o ai_output.png --mode ai --provider replicate --model real-esrgan --scale 4 --api-key "r8_..."
```
