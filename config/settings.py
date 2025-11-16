"""
Configuration management for Tourism Content Generator
"""
import os
from pathlib import Path
from dotenv import load_dotenv
from typing import Optional, Dict, Any
import json

# Load environment variables
load_dotenv()

class Settings:
    """Central configuration management"""

    # Base paths
    BASE_DIR = Path(__file__).parent.parent
    DATA_DIR = BASE_DIR / "data"
    TEMPLATES_DIR = BASE_DIR / "templates"

    # Ensure data directory exists
    DATA_DIR.mkdir(exist_ok=True)

    # ============================================
    # FACEBOOK SCRAPING
    # ============================================
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY", "")
    RAPIDAPI_HOST = os.getenv("RAPIDAPI_HOST", "facebook-scraper4.p.rapidapi.com")

    # ============================================
    # LLM PROVIDERS
    # ============================================
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-sonnet-4-20250514")

    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4-turbo-preview")

    GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY", "")
    GOOGLE_MODEL = os.getenv("GOOGLE_MODEL", "gemini-pro")

    DEFAULT_LLM_PROVIDER = os.getenv("DEFAULT_LLM_PROVIDER", "anthropic")

    # ============================================
    # IMAGE SOURCES
    # ============================================
    PEXELS_API_KEY = os.getenv("PEXELS_API_KEY", "")
    UNSPLASH_ACCESS_KEY = os.getenv("UNSPLASH_ACCESS_KEY", "")
    PIXABAY_API_KEY = os.getenv("PIXABAY_API_KEY", "")

    # ============================================
    # WORDPRESS
    # ============================================
    WORDPRESS_URL = os.getenv("WORDPRESS_URL", "")
    WORDPRESS_USERNAME = os.getenv("WORDPRESS_USERNAME", "")
    WORDPRESS_APP_PASSWORD = os.getenv("WORDPRESS_APP_PASSWORD", "")

    # ============================================
    # DATABASE
    # ============================================
    SQLITE_DB_PATH = os.getenv("SQLITE_DB_PATH", str(DATA_DIR / "tourism_content.db"))
    CHROMA_DB_PATH = os.getenv("CHROMA_DB_PATH", str(DATA_DIR / "chroma_db"))

    # ============================================
    # SYSTEM SETTINGS
    # ============================================
    MAX_POSTS_PER_PAGE = int(os.getenv("MAX_POSTS_PER_PAGE", "50"))
    MAX_IMAGES_PER_ARTICLE = int(os.getenv("MAX_IMAGES_PER_ARTICLE", "10"))
    IMAGE_QUALITY = os.getenv("IMAGE_QUALITY", "high")
    SCRAPING_SCHEDULE = os.getenv("SCRAPING_SCHEDULE", "")
    CONTENT_RETENTION_DAYS = int(os.getenv("CONTENT_RETENTION_DAYS", "0"))

    @classmethod
    def get_llm_config(cls, provider: Optional[str] = None) -> Dict[str, Any]:
        """Get LLM configuration for specified provider"""
        provider = provider or cls.DEFAULT_LLM_PROVIDER

        configs = {
            "anthropic": {
                "api_key": cls.ANTHROPIC_API_KEY,
                "model": cls.ANTHROPIC_MODEL,
                "enabled": bool(cls.ANTHROPIC_API_KEY)
            },
            "openai": {
                "api_key": cls.OPENAI_API_KEY,
                "model": cls.OPENAI_MODEL,
                "enabled": bool(cls.OPENAI_API_KEY)
            },
            "google": {
                "api_key": cls.GOOGLE_API_KEY,
                "model": cls.GOOGLE_MODEL,
                "enabled": bool(cls.GOOGLE_API_KEY)
            }
        }

        return configs.get(provider, configs["anthropic"])

    @classmethod
    def get_image_sources_config(cls) -> Dict[str, Any]:
        """Get configuration for all image sources"""
        return {
            "pexels": {
                "enabled": bool(cls.PEXELS_API_KEY),
                "api_key": cls.PEXELS_API_KEY
            },
            "unsplash": {
                "enabled": bool(cls.UNSPLASH_ACCESS_KEY),
                "api_key": cls.UNSPLASH_ACCESS_KEY
            },
            "pixabay": {
                "enabled": bool(cls.PIXABAY_API_KEY),
                "api_key": cls.PIXABAY_API_KEY
            },
            "wikimedia": {
                "enabled": True,
                "api_key": None
            },
            "facebook": {
                "enabled": bool(cls.RAPIDAPI_KEY),
                "api_key": None
            }
        }

    @classmethod
    def is_wordpress_configured(cls) -> bool:
        """Check if WordPress is configured"""
        return bool(cls.WORDPRESS_URL and cls.WORDPRESS_USERNAME and cls.WORDPRESS_APP_PASSWORD)

    @classmethod
    def validate_config(cls) -> Dict[str, Any]:
        """Validate configuration and return status"""
        issues = []

        # Check Facebook scraping
        if not cls.RAPIDAPI_KEY:
            issues.append("RapidAPI key not configured - Facebook scraping disabled")

        # Check LLM providers
        llm_configured = any([cls.ANTHROPIC_API_KEY, cls.OPENAI_API_KEY, cls.GOOGLE_API_KEY])
        if not llm_configured:
            issues.append("No LLM provider configured - Article generation disabled")

        # Check image sources
        image_sources = cls.get_image_sources_config()
        enabled_sources = [k for k, v in image_sources.items() if v["enabled"]]
        if len(enabled_sources) == 0:
            issues.append("No image sources configured")

        return {
            "valid": len(issues) == 0,
            "issues": issues,
            "llm_providers": [k for k, v in {
                "anthropic": cls.ANTHROPIC_API_KEY,
                "openai": cls.OPENAI_API_KEY,
                "google": cls.GOOGLE_API_KEY
            }.items() if v],
            "image_sources": enabled_sources,
            "wordpress_configured": cls.is_wordpress_configured()
        }

# Singleton instance
settings = Settings()
