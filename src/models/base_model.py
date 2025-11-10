"""
🌙 Deamon Dev's Model Interface
Built with love by Deamon Dev 🚀

This module defines the base interface for all AI models.
"""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any, Dict, Optional

from termcolor import cprint


def safe_cprint(text, color):
    """Safe print that handles Unicode encoding issues"""
    try:
        cprint(text, color)
    except UnicodeEncodeError:
        clean_text = (
            text.replace("✨", "")
            .replace("❌", "")
            .replace("🌙", "")
            .replace("🚀", "")
            .replace("⚡", "")
            .replace("💎", "")
            .replace("📈", "")
            .replace("📉", "")
            .replace("🌟", "")
            .replace("🤖", "")
            .replace("🔥", "")
            .replace("💰", "")
            .replace("⭐", "")
        )
        cprint(clean_text, color)


@dataclass
class ModelResponse:
    """Standardized response format for all models"""

    content: str
    raw_response: Any  # Original response object
    model_name: str
    usage: Optional[Dict] = None


class BaseModel(ABC):
    """Base interface for all AI models"""

    def __init__(self, api_key: str, **kwargs):
        self.api_key = api_key
        self.client = None
        self._model_type = None
        self.max_tokens = 2048  # Default max tokens
        self.initialize_client(**kwargs)

    @property
    def model_type(self):
        """Return model type"""
        return self._model_type

    @abstractmethod
    def initialize_client(self, **kwargs) -> None:
        """Initialize the model's client"""

    @abstractmethod
    def generate_response(self, system_prompt, user_content, temperature=0.7, max_tokens=None):
        """Generate a response from the model with no caching"""
        pass

    @abstractmethod
    def is_available(self) -> bool:
        """Check if the model is available and properly configured"""
