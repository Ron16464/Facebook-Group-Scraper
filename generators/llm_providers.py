"""
Multi-LLM provider integration: Anthropic Claude, OpenAI, Google Gemini
"""
from typing import Dict, Any, Optional, List
from abc import ABC, abstractmethod

from config.settings import settings
from database.models import db


class LLMProvider(ABC):
    """Base class for LLM providers"""

    @abstractmethod
    def generate(self, prompt: str, system_prompt: str = None,
                max_tokens: int = 4000, temperature: float = 0.7) -> Optional[str]:
        """Generate text using the LLM"""
        pass


class ClaudeProvider(LLMProvider):
    """Anthropic Claude provider"""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.ANTHROPIC_API_KEY
        self.model = model or settings.ANTHROPIC_MODEL

        if self.api_key:
            try:
                from anthropic import Anthropic
                self.client = Anthropic(api_key=self.api_key)
            except ImportError:
                db.add_log("ERROR", "ClaudeProvider",
                         "Anthropic package not installed",
                         "Run: pip install anthropic")
                self.client = None
        else:
            self.client = None

    def generate(self, prompt: str, system_prompt: str = None,
                max_tokens: int = 4000, temperature: float = 0.7) -> Optional[str]:
        """Generate text using Claude"""
        if not self.client:
            return None

        try:
            messages = [{"role": "user", "content": prompt}]

            kwargs = {
                "model": self.model,
                "max_tokens": max_tokens,
                "temperature": temperature,
                "messages": messages
            }

            if system_prompt:
                kwargs["system"] = system_prompt

            response = self.client.messages.create(**kwargs)

            # Extract text from response
            if response.content and len(response.content) > 0:
                return response.content[0].text
            return None

        except Exception as e:
            db.add_log("ERROR", "ClaudeProvider",
                     f"Generation failed: {str(e)}", f"Model: {self.model}")
            return None


class OpenAIProvider(LLMProvider):
    """OpenAI GPT provider"""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.OPENAI_API_KEY
        self.model = model or settings.OPENAI_MODEL

        if self.api_key:
            try:
                from openai import OpenAI
                self.client = OpenAI(api_key=self.api_key)
            except ImportError:
                db.add_log("ERROR", "OpenAIProvider",
                         "OpenAI package not installed",
                         "Run: pip install openai")
                self.client = None
        else:
            self.client = None

    def generate(self, prompt: str, system_prompt: str = None,
                max_tokens: int = 4000, temperature: float = 0.7) -> Optional[str]:
        """Generate text using OpenAI"""
        if not self.client:
            return None

        try:
            messages = []

            if system_prompt:
                messages.append({"role": "system", "content": system_prompt})

            messages.append({"role": "user", "content": prompt})

            response = self.client.chat.completions.create(
                model=self.model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            if response.choices and len(response.choices) > 0:
                return response.choices[0].message.content
            return None

        except Exception as e:
            db.add_log("ERROR", "OpenAIProvider",
                     f"Generation failed: {str(e)}", f"Model: {self.model}")
            return None


class GeminiProvider(LLMProvider):
    """Google Gemini provider"""

    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or settings.GOOGLE_API_KEY
        self.model = model or settings.GOOGLE_MODEL

        if self.api_key:
            try:
                import google.generativeai as genai
                genai.configure(api_key=self.api_key)
                self.client = genai.GenerativeModel(self.model)
            except ImportError:
                db.add_log("ERROR", "GeminiProvider",
                         "Google Generative AI package not installed",
                         "Run: pip install google-generativeai")
                self.client = None
        else:
            self.client = None

    def generate(self, prompt: str, system_prompt: str = None,
                max_tokens: int = 4000, temperature: float = 0.7) -> Optional[str]:
        """Generate text using Gemini"""
        if not self.client:
            return None

        try:
            # Combine system prompt and user prompt
            full_prompt = prompt
            if system_prompt:
                full_prompt = f"{system_prompt}\n\n{prompt}"

            generation_config = {
                "temperature": temperature,
                "max_output_tokens": max_tokens,
            }

            response = self.client.generate_content(
                full_prompt,
                generation_config=generation_config
            )

            if response.text:
                return response.text
            return None

        except Exception as e:
            db.add_log("ERROR", "GeminiProvider",
                     f"Generation failed: {str(e)}", f"Model: {self.model}")
            return None


class LLMManager:
    """Unified interface for managing multiple LLM providers"""

    def __init__(self):
        self.providers = {
            'anthropic': ClaudeProvider(),
            'openai': OpenAIProvider(),
            'google': GeminiProvider()
        }

        # Set default provider
        self.default_provider = settings.DEFAULT_LLM_PROVIDER

    def get_provider(self, provider_name: str = None) -> Optional[LLMProvider]:
        """Get specific LLM provider"""
        name = provider_name or self.default_provider
        return self.providers.get(name)

    def generate(self, prompt: str, system_prompt: str = None,
                provider: str = None, max_tokens: int = 4000,
                temperature: float = 0.7) -> Optional[str]:
        """Generate text using specified or default provider"""
        llm = self.get_provider(provider)

        if not llm:
            db.add_log("ERROR", "LLMManager",
                     f"Provider not found: {provider or self.default_provider}")
            return None

        result = llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            max_tokens=max_tokens,
            temperature=temperature
        )

        if result:
            db.add_log("INFO", "LLMManager",
                     f"Generated {len(result)} characters",
                     f"Provider: {provider or self.default_provider}")

        return result

    def get_available_providers(self) -> List[Dict[str, Any]]:
        """Get list of available (configured) providers"""
        available = []

        for name, provider in self.providers.items():
            is_available = False

            if isinstance(provider, ClaudeProvider):
                is_available = bool(provider.client)
            elif isinstance(provider, OpenAIProvider):
                is_available = bool(provider.client)
            elif isinstance(provider, GeminiProvider):
                is_available = bool(provider.client)

            available.append({
                'name': name,
                'available': is_available,
                'model': provider.model if hasattr(provider, 'model') else None,
                'is_default': name == self.default_provider
            })

        return available

    def set_default_provider(self, provider_name: str):
        """Set default LLM provider"""
        if provider_name in self.providers:
            self.default_provider = provider_name
            db.add_log("INFO", "LLMManager",
                     f"Default provider set to: {provider_name}")
            return True
        return False

    def test_provider(self, provider_name: str) -> Dict[str, Any]:
        """Test if a provider is working"""
        provider = self.get_provider(provider_name)

        if not provider:
            return {
                'success': False,
                'error': 'Provider not found'
            }

        test_prompt = "Say 'Hello, I am working correctly!' and nothing else."

        try:
            result = provider.generate(test_prompt, max_tokens=50, temperature=0)

            if result:
                return {
                    'success': True,
                    'response': result,
                    'provider': provider_name
                }
            else:
                return {
                    'success': False,
                    'error': 'No response from provider'
                }

        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }


# Singleton instance
llm_manager = LLMManager()
