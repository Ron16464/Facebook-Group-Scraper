"""Setup script for facebook-scraper package.

This file provides backward compatibility for older build systems.
Modern builds should use pyproject.toml instead.
"""

from setuptools import setup, find_packages

# Read README for long description
with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# Read requirements
with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = [line.strip() for line in fh if line.strip() and not line.startswith("#")]

setup(
    name="facebook-scraper",
    version="1.0.0",
    author="Your Name",
    author_email="your.email@example.com",
    description="A simple Python wrapper for the Facebook Scraper API available on RapidAPI",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/yourusername/facebook-scraper",
    project_urls={
        "Bug Tracker": "https://github.com/yourusername/facebook-scraper/issues",
        "Documentation": "https://github.com/yourusername/facebook-scraper#readme",
        "Source Code": "https://github.com/yourusername/facebook-scraper",
    },
    py_modules=["facebook_scraper"],
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
    install_requires=requirements,
    extras_require={
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "flake8>=6.0.0",
            "black>=23.0.0",
            "mypy>=1.0.0",
            "types-requests>=2.28.0",
        ],
        "gui": [
            "streamlit>=1.28.0",
        ],
    },
    keywords=[
        "facebook",
        "scraper",
        "api",
        "rapidapi",
        "marketplace",
        "social-media",
        "data-extraction",
    ],
    include_package_data=True,
    zip_safe=False,
)
