"""
WebMagic CLI - State-of-the-Art Image Enhancement Tool (AI & Non-AI)
Supports batch and single image enhancement with presets and modern AI models.
"""
import sys
import os
import io
import argparse
import asyncio
from pathlib import Path
from typing import Optional, List

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeRemainingColumn
from rich import print as rprint
from PIL import Image

sys.path.insert(0, str(Path(__file__).resolve().parent))

from engine.enhancer import EnhancementPipeline
from engine.esmagic import EsMagicEngine
from engine.ai_engine import AIEnhancementEngine, AIEnhancementError
from engine.presets import PRESETS

console = Console()

def print_banner():
    banner = """
    [bold cyan]╔════════════════════════════════════════════════════════════╗[/bold cyan]
    [bold cyan]║[/bold cyan]   [bold magenta] WebMagic Image Enhancer[/bold magenta] [dim](CLI & Engine)[/dim]             [bold cyan]║[/bold cyan]
    [bold cyan]║[/bold cyan]   [dim]Algorithmic Non-AI Filters + SOTA Generative AI Upscalers[/dim] [bold cyan]║[/bold cyan]
    [bold cyan]╚════════════════════════════════════════════════════════════╝[/bold cyan]
    """
    console.print(banner)

def list_models_command():
    """Display supported AI Models and presets."""
    print_banner()

    preset_table = Table(title="[bold yellow] Non-AI Enhancement Presets (Local, Instant)[/bold yellow]", show_header=True, header_style="bold green")
    preset_table.add_column("Preset ID", style="cyan", width=18)
    preset_table.add_column("Name", style="bold white", width=24)
    preset_table.add_column("Description", style="dim")

    for key, p in PRESETS.items():
        preset_table.add_row(key, p["name"], p["description"])

    console.print(preset_table)
    console.print()

    ai_table = Table(title="[bold magenta] State-of-the-Art AI Models (API Key Required)[/bold magenta]", show_header=True, header_style="bold magenta")
    ai_table.add_column("Provider", style="bold cyan", width=14)
    ai_table.add_column("Model Key", style="bold yellow", width=22)
    ai_table.add_column("Environment Variable", style="green", width=22)
    ai_table.add_column("Capabilities", style="dim")

    ai_models = AIEnhancementEngine.get_supported_models()

    for provider, pinfo in ai_models.items():
        env_var = {
            "replicate": "REPLICATE_API_TOKEN",
            "stability": "STABILITY_API_KEY",
            "openai": "OPENAI_API_KEY",
            "huggingface": "HF_TOKEN"
        }.get(provider, f"{provider.upper()}_KEY")

        for m_key, m_val in pinfo.get("models", {}).items():
            ai_table.add_row(pinfo["name"], m_key, env_var, m_val["description"])

    console.print(ai_table)
    console.print()

async def process_single_image(
    input_path: Path,
    output_path: Path,
    mode: str,
    preset: Optional[str] = "esmagic",
    clahe_clip: float = 2.0,
    sharpness: float = 1.3,
    saturation: float = 1.2,
    denoise: float = 10.0,
    contrast: float = 1.1,
    brightness: float = 1.0,
    warmth: float = 0.0,
    scale: float = 1.0,
    provider: str = "replicate",
    ai_model: str = "real-esrgan",
    api_key: Optional[str] = None,
    face_enhance: bool = True
) -> bool:
    """Enhance single image."""
    try:
        raw_bytes = input_path.read_bytes()
        orig_img = Image.open(io.BytesIO(raw_bytes))
        orig_w, orig_h = orig_img.size

        out_bytes: bytes

        if mode == "non-ai":
            out_format = output_path.suffix.lstrip(".").upper() or "PNG"
            if preset == "esmagic":
                out_bytes = EsMagicEngine.process_bytes(raw_bytes, scale=scale, output_format=out_format)
            elif preset and preset in PRESETS:
                params = PRESETS[preset]["params"].copy()
                if scale > 1.0:
                    params["scale"] = scale
                out_bytes = EnhancementPipeline.process_bytes(raw_bytes, params, output_format=out_format)
            else:
                params = {
                    "clahe_clip": clahe_clip,
                    "sharpness": sharpness,
                    "saturation": saturation,
                    "denoise": denoise,
                    "contrast": contrast,
                    "brightness": brightness,
                    "warmth": warmth,
                    "gamma": 1.0,
                    "scale": scale
                }
                out_bytes = EnhancementPipeline.process_bytes(raw_bytes, params, output_format=out_format)

        else:
            env_var_map = {
                "replicate": "REPLICATE_API_TOKEN",
                "stability": "STABILITY_API_KEY",
                "openai": "OPENAI_API_KEY",
                "huggingface": "HF_TOKEN"
            }
            resolved_key = api_key or os.environ.get(env_var_map.get(provider, f"{provider.upper()}_KEY"))
            if not resolved_key:
                raise ValueError(
                    f"Missing API key for provider '{provider}'. Pass via --api-key or set environment variable {env_var_map.get(provider)}"
                )

            if provider == "replicate":
                out_bytes = await AIEnhancementEngine.enhance_with_replicate(
                    raw_bytes,
                    api_token=resolved_key,
                    model_name=ai_model,
                    scale=int(scale) if scale >= 2 else 4,
                    face_enhance=face_enhance
                )
            elif provider == "stability":
                out_bytes = await AIEnhancementEngine.enhance_with_stability(
                    raw_bytes,
                    api_key=resolved_key,
                    model_name=ai_model
                )
            elif provider == "huggingface":
                out_bytes = await AIEnhancementEngine.enhance_with_huggingface(
                    raw_bytes,
                    api_token=resolved_key,
                    model_name=ai_model
                )
            else:
                raise ValueError(f"Provider {provider} not supported for direct upscale.")

        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_bytes(out_bytes)

        res_img = Image.open(io.BytesIO(out_bytes))
        new_w, new_h = res_img.size
        console.print(f"  [green] Enhanced:[/green] {input_path.name} ({orig_w}x{orig_h})  [bold cyan]{output_path.name}[/bold cyan] ({new_w}x{new_h})")
        return True

    except Exception as e:
        console.print(f"  [red] Error processing {input_path.name}:[/red] {str(e)}")
        return False

def main():
    import io
    parser = argparse.ArgumentParser(
        description="WebMagic CLI - Professional AI and Non-AI Image Enhancement Suite",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    subparsers = parser.add_subparsers(dest="command", help="Command to execute")

    subparsers.add_parser("models", help="List supported AI models and presets")
    subparsers.add_parser("presets", help="List available non-AI presets")

    p_enhance = subparsers.add_parser("enhance", help="Enhance a single image file")
    p_enhance.add_argument("input", help="Path to input image file")
    p_enhance.add_argument("-o", "--output", help="Path to output image file (defaults to enhanced_<input>)")
    p_enhance.add_argument("--mode", choices=["non-ai", "ai"], default="non-ai", help="Enhancement mode")
    p_enhance.add_argument("--preset", choices=list(PRESETS.keys()), default="esmagic", help="Enhancement preset to apply (default: esmagic)")
    
    p_enhance.add_argument("--clahe", type=float, default=2.0, help="CLAHE contrast clip limit")
    p_enhance.add_argument("--sharpness", type=float, default=1.3, help="Unsharp mask sharpening strength")
    p_enhance.add_argument("--saturation", type=float, default=1.2, help="Saturation boost factor")
    p_enhance.add_argument("--denoise", type=float, default=10.0, help="Denoising filter strength")
    p_enhance.add_argument("--contrast", type=float, default=1.1, help="Contrast adjustment factor")
    p_enhance.add_argument("--brightness", type=float, default=1.0, help="Brightness adjustment factor")
    p_enhance.add_argument("--warmth", type=float, default=0.0, help="Warmth/temperature adjustment (-50 to +50)")
    p_enhance.add_argument("--scale", type=float, default=1.0, help="Upscale factor (e.g. 2, 4)")

    p_enhance.add_argument("--provider", choices=["replicate", "stability", "huggingface"], default="replicate", help="AI Provider")
    p_enhance.add_argument("--model", default="real-esrgan", help="AI Model identifier (e.g. real-esrgan, gfpgan, codeformer)")
    p_enhance.add_argument("--api-key", help="API token/key for the chosen AI provider")
    p_enhance.add_argument("--no-face-enhance", action="store_true", help="Disable facial reconstruction")

    p_batch = subparsers.add_parser("batch", help="Batch process all images in a directory")
    p_batch.add_argument("input_dir", help="Directory containing images")
    p_batch.add_argument("-o", "--output-dir", required=True, help="Directory to save enhanced images")
    p_batch.add_argument("--mode", choices=["non-ai", "ai"], default="non-ai", help="Enhancement mode")
    p_batch.add_argument("--preset", choices=list(PRESETS.keys()), default="auto_vibrant", help="Non-AI preset")
    p_batch.add_argument("--scale", type=float, default=1.0, help="Upscale factor")
    p_batch.add_argument("--provider", choices=["replicate", "stability", "huggingface"], default="replicate")
    p_batch.add_argument("--model", default="real-esrgan")
    p_batch.add_argument("--api-key", help="AI API Key")

    args = parser.parse_args()

    if not args.command or args.command in ["models", "presets"]:
        list_models_command()
        return

    if args.command == "enhance":
        input_p = Path(args.input)
        if not input_p.exists():
            console.print(f"[bold red]File not found:[/bold red] {args.input}")
            sys.exit(1)

        if args.output:
            output_p = Path(args.output)
        else:
            output_p = input_p.parent / f"{input_p.stem}_enhanced{input_p.suffix}"

        console.print(f"[bold magenta]Starting WebMagic Enhancement...[/bold magenta]")
        console.print(f"  • Source: [cyan]{input_p}[/cyan]")
        console.print(f"  • Destination: [cyan]{output_p}[/cyan]")
        engine_color = "yellow" if args.mode == "non-ai" else "green"
        console.print(f"  • Engine: [{engine_color}]{args.mode.upper()}[/{engine_color}]")
        if args.mode == "non-ai":
            console.print(f"  • Preset: [bold white]{PRESETS.get(args.preset, {}).get('name', args.preset)}[/bold white]")
        else:
            console.print(f"  • AI Provider: [bold white]{args.provider}[/bold white] | Model: [bold white]{args.model}[/bold white]")

        success = asyncio.run(
            process_single_image(
                input_p,
                output_p,
                mode=args.mode,
                preset=args.preset,
                clahe_clip=args.clahe,
                sharpness=args.sharpness,
                saturation=args.saturation,
                denoise=args.denoise,
                contrast=args.contrast,
                brightness=args.brightness,
                warmth=args.warmth,
                scale=args.scale,
                provider=args.provider,
                ai_model=args.model,
                api_key=args.api_key,
                face_enhance=not args.no_face_enhance
            )
        )
        if success:
            console.print(f"\n[bold green] Enhancement completed successfully![/bold green]\n")
        else:
            sys.exit(1)

    elif args.command == "batch":
        input_dir = Path(args.input_dir)
        output_dir = Path(args.output_dir)
        if not input_dir.is_dir():
            console.print(f"[bold red]Input directory not found:[/bold red] {args.input_dir}")
            sys.exit(1)

        extensions = {".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff"}
        images = [f for f in input_dir.iterdir() if f.suffix.lower() in extensions]
        if not images:
            console.print(f"[yellow]No images found in {input_dir}[/yellow]")
            return

        console.print(f"[bold magenta]Processing Batch of {len(images)} images...[/bold magenta]")
        output_dir.mkdir(parents=True, exist_ok=True)

        successes = 0
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TimeRemainingColumn(),
            console=console
        ) as progress:
            task = progress.add_task("[cyan]Enhancing batch...", total=len(images))
            for img_file in images:
                out_file = output_dir / f"{img_file.stem}_enhanced{img_file.suffix}"
                ok = asyncio.run(
                    process_single_image(
                        img_file,
                        out_file,
                        mode=args.mode,
                        preset=args.preset,
                        scale=args.scale,
                        provider=args.provider,
                        ai_model=args.model,
                        api_key=args.api_key
                    )
                )
                if ok:
                    successes += 1
                progress.advance(task)

        console.print(f"\n[bold green] Batch Complete![/bold green] Successfully enhanced {successes}/{len(images)} images.")

if __name__ == "__main__":
    main()
