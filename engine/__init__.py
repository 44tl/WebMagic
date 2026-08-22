"""
WebMagic - Core engine package initializer
"""
from engine.enhancer import EnhancementPipeline
from engine.ai_engine import AIEnhancementEngine, AIEnhancementError
from engine.presets import PRESETS

__all__ = ["EnhancementPipeline", "AIEnhancementEngine", "AIEnhancementError", "PRESETS"]
