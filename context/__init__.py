"""
Context building package for Reddit bot.
Provides modular, testable context generation system.
"""

from .config import ContextConfig, PromptConfig
from .builders import ContextBuilder

__all__ = ['ContextConfig', 'PromptConfig', 'ContextBuilder']
