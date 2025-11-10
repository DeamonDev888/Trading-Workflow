"""Deamon Dev's Groq Model Implementation

Built with love by Deamon Dev
"""

import time

from groq import Groq
from termcolor import cprint

from .base_model import BaseModel, ModelResponse, safe_cprint


class GroqModel(BaseModel):
    """Implementation for Groq's models"""

    AVAILABLE_MODELS = {
        "mixtral-8x7b-32768": {
            "description": "Mixtral 8x7B - Production - 32k context",
            "input_price": "$0.27/1M tokens",
            "output_price": "$0.27/1M tokens",
        },
        "gemma2-9b-it": {
            "description": "Google Gemma 2 9B - Production - 8k context",
            "input_price": "$0.10/1M tokens",
            "output_price": "$0.10/1M tokens",
        },
        "llama-3.3-70b-versatile": {
            "description": "Llama 3.3 70B Versatile - Production - 128k context",
            "input_price": "$0.70/1M tokens",
            "output_price": "$0.90/1M tokens",
        },
        "llama-3.1-8b-instant": {
            "description": "Llama 3.1 8B Instant - Production - 128k context",
            "input_price": "$0.10/1M tokens",
            "output_price": "$0.10/1M tokens",
        },
        "llama-guard-3-8b": {
            "description": "Llama Guard 3 8B - Production - 8k context",
            "input_price": "$0.20/1M tokens",
            "output_price": "$0.20/1M tokens",
        },
        "llama3-70b-8192": {
            "description": "Llama 3 70B - Production - 8k context",
            "input_price": "$0.70/1M tokens",
            "output_price": "$0.90/1M tokens",
        },
        "llama3-8b-8192": {
            "description": "Llama 3 8B - Production - 8k context",
            "input_price": "$0.10/1M tokens",
            "output_price": "$0.10/1M tokens",
        },
        "deepseek-r1-distill-llama-70b": {
            "description": "DeepSeek R1 Distill Llama 70B - Preview - 128k context",
            "input_price": "$0.70/1M tokens",
            "output_price": "$0.90/1M tokens",
        },
        "llama-3.3-70b-specdec": {
            "description": "Llama 3.3 70B SpecDec - Preview - 8k context",
            "input_price": "$0.70/1M tokens",
            "output_price": "$0.90/1M tokens",
        },
        "llama-3.2-1b-preview": {
            "description": "Llama 3.2 1B - Preview - 128k context",
            "input_price": "$0.05/1M tokens",
            "output_price": "$0.05/1M tokens",
        },
        "llama-3.2-3b-preview": {
            "description": "Llama 3.2 3B - Preview - 128k context",
            "input_price": "$0.07/1M tokens",
            "output_price": "$0.07/1M tokens",
        },
        "qwen/qwen3-32b": {
            "description": "Qwen 3 32B - Production - 32k context",
            "input_price": "$0.50/1M tokens",
            "output_price": "$0.50/1M tokens",
        },
    }

    def __init__(self, api_key: str, model_name: str = "qwen/qwen3-32b", **kwargs):
        try:
            safe_cprint(f"\n🌙 Deamon Dev's Groq Model Initialization", "cyan")

            if not api_key or len(api_key.strip()) == 0:
                raise ValueError("API key is empty or None")

            safe_cprint(f"🔑 API Key validation:", "cyan")
            safe_cprint(f"  ├─ Length: {len(api_key)} chars", "cyan")
            safe_cprint(
                f"  ├─ Contains whitespace: {'yes' if any(c.isspace() for c in api_key) else 'no'}",
                "cyan",
            )
            safe_cprint(
                f"  └─ Starts with 'gsk_': {'yes' if api_key.startswith('gsk_') else 'no'}",
                "cyan",
            )

            safe_cprint(f"\n📝 Model validation:", "cyan")
            safe_cprint(f"  ├─ Requested: {model_name}", "cyan")
            if model_name not in self.AVAILABLE_MODELS:
                safe_cprint(f"  └─ ❌ Invalid model name", "red")
                safe_cprint("\nAvailable models:", "yellow")
                for available_model, info in self.AVAILABLE_MODELS.items():
                    safe_cprint(f"  ├─ {available_model}", "yellow")
                    safe_cprint(f"  │  └─ {info['description']}", "yellow")
                raise ValueError(f"Invalid model name: {model_name}")
            safe_cprint(f"  └─ ✅ Model name valid", "green")

            self.model_name = model_name

            safe_cprint(f"\n📡 Parent class initialization...", "cyan")
            super().__init__(api_key, **kwargs)
            safe_cprint(f"✅ Parent class initialized", "green")

        except Exception as e:
            safe_cprint(f"\n❌ Error in Groq model initialization", "red")
            safe_cprint(f"  ├─ Error type: {type(e).__name__}", "red")
            safe_cprint(f"  ├─ Error message: {str(e)}", "red")
            if "api_key" in str(e).lower():
                safe_cprint(f"  ├─ 🔑 This appears to be an API key issue", "red")
                safe_cprint(f"  └─ Please check your GROQ_API_KEY in .env", "red")
            elif "model" in str(e).lower():
                safe_cprint(f"  ├─ 🤖 This appears to be a model name issue", "red")
                safe_cprint(
                    f"  └─ Available models: {list(self.AVAILABLE_MODELS.keys())}",
                    "red",
                )
            raise

    def initialize_client(self, **kwargs) -> None:
        """Initialize the Groq client"""
        try:
            safe_cprint(f"\n🔌 Initializing Groq client...", "cyan")
            safe_cprint(f"  ├─ API Key length: {len(self.api_key)} chars", "cyan")
            safe_cprint(f"  ├─ Model name: {self.model_name}", "cyan")

            safe_cprint(f"\n  ├─ Creating Groq client...", "cyan")
            self.client = Groq(api_key=self.api_key)
            safe_cprint(f"  ├─ ✅ Groq client created", "green")

            safe_cprint(f"  ├─ Fetching available models from Groq API...", "cyan")
            available_models = self.client.models.list()
            api_models = [model.id for model in available_models.data]
            safe_cprint(f"  ├─ Models available from API: {api_models}", "cyan")

            if self.model_name not in api_models:
                safe_cprint(f"  ├─ ⚠️ Requested model not found in API", "yellow")
                safe_cprint(f"  ├─ Falling back to mixtral-8x7b-32768", "yellow")
                self.model_name = "mixtral-8x7b-32768"

            safe_cprint(f"  ├─ Testing connection with model: {self.model_name}", "cyan")
            test_response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[{"role": "user", "content": "Hello"}],
                max_tokens=10,
            )
            safe_cprint(f"  ├─ ✅ Test response received", "green")
            safe_cprint(
                f"  ├─ Response content: {test_response.choices[0].message.content}",
                "cyan",
            )

            model_info = self.AVAILABLE_MODELS.get(self.model_name, {})
            safe_cprint(f"  ├─ ✨ Groq model initialized: {self.model_name}", "green")
            safe_cprint(f"  ├─ Model info: {model_info.get('description', '')}", "cyan")
            safe_cprint(
                f"  └─ Pricing: Input {model_info.get('input_price', '')} | Output {model_info.get('output_price', '')}",
                "yellow",
            )

        except Exception as e:
            safe_cprint(f"\n❌ Failed to initialize Groq client", "red")
            safe_cprint(f"  ├─ Error type: {type(e).__name__}", "red")
            safe_cprint(f"  ├─ Error message: {str(e)}", "red")

            if "api_key" in str(e).lower():
                safe_cprint(f"  ├─ 🔑 This appears to be an API key issue", "red")
                safe_cprint(f"  ├─ Make sure your GROQ_API_KEY is correct", "red")
                safe_cprint(f"  └─ Key length: {len(self.api_key)} chars", "red")
            elif "model" in str(e).lower():
                safe_cprint(f"  ├─ 🤖 This appears to be a model name issue", "red")
                safe_cprint(f"  ├─ Requested model: {self.model_name}", "red")
                safe_cprint(
                    f"  └─ Available models: {list(self.AVAILABLE_MODELS.keys())}",
                    "red",
                )

            if hasattr(e, "response"):
                safe_cprint(f"  ├─ Response status: {e.response.status_code}", "red")
                safe_cprint(f"  └─ Response body: {e.response.text}", "red")

            if hasattr(e, "__traceback__"):
                import traceback

                safe_cprint(f"\n📋 Full traceback:", "red")
                safe_cprint(traceback.format_exc(), "red")

            self.client = None
            raise

    def generate_response(self, system_prompt, user_content, temperature=0.7, max_tokens=None):
        """Generate response with no caching"""
        try:
            timestamp = int(time.time() * 1000)  # Millisecond precision

            response = self.client.chat.completions.create(
                model=self.model_name,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": f"{user_content}_{timestamp}",
                    },  # Make each request unique
                ],
                temperature=temperature,
                max_tokens=max_tokens if max_tokens else self.max_tokens,
                stream=False,  # Disable streaming to prevent caching
            )

            raw_content = response.choices[0].message.content

            import re

            filtered_content = re.sub(
                r"<think>.*?</think>", "", raw_content, flags=re.DOTALL
            ).strip()

            if "<think>" in filtered_content:
                filtered_content = filtered_content.split("<think>")[0].strip()

            final_content = filtered_content if filtered_content else raw_content

            return ModelResponse(
                content=final_content,
                raw_response=response,
                model_name=self.model_name,
                usage=response.usage,
            )

        except Exception as e:
            error_str = str(e)

            if "413" in error_str or "rate_limit_exceeded" in error_str:
                safe_cprint(f"⚠️  Groq rate limit exceeded (request too large)", "yellow")
                safe_cprint(f"   Model: {self.model_name}", "yellow")
                if "Requested" in error_str and "Limit" in error_str:
                    import re

                    limit_match = re.search(r"Limit (\d+)", error_str)
                    requested_match = re.search(r"Requested (\d+)", error_str)
                    if limit_match and requested_match:
                        safe_cprint(
                            f"   Limit: {limit_match.group(1)} tokens | Requested: {requested_match.group(1)} tokens",
                            "yellow",
                        )
                safe_cprint(f"   💡 Skipping this model for this request...", "cyan")
                return None

            if "503" in error_str:
                raise e

            safe_cprint(f"❌ Groq error: {error_str}", "red")
            return None

    def is_available(self) -> bool:
        """Check if Groq is available"""
        return self.client is not None

    @property
    def model_type(self) -> str:
        return "groq"
