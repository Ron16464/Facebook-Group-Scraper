# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.0.0] - 2025-11-19

### Added
- Initial release of Facebook Scraper library
- `FacebookScraper` class with 8 API methods:
  - `get_marketplace_item()` - Retrieve marketplace item details
  - `search_marketplace_by_location()` - Search marketplace by location
  - `search_marketplace_by_keyword()` - Search marketplace by keyword
  - `retrieve_page_posts()` - Get public page posts
  - `get_page_about_info()` - Get page information
  - `retrieve_post_data()` - Get post engagement data
  - `retrieve_profile_photos()` - Get profile photos
  - `retrieve_profile_data()` - Get public profile information
- Comprehensive error handling with custom exceptions:
  - `FacebookScraperError` - Base exception class
  - `AuthenticationError` - API authentication failures
  - `APIError` - API errors and invalid responses
  - `NetworkError` - Network and timeout errors
- Full type hints support (PEP 484)
- Comprehensive docstrings (Google style)
- 18 unit tests with 100% pass rate
- Streamlit web interface (`app.py`)
  - Beautiful UI with sidebar navigation
  - All 8 methods accessible via dropdown
  - JSON output viewer and download
  - Comprehensive error handling
- GitHub Actions CI/CD pipeline
  - Tests on Python 3.7-3.11
  - Multi-OS testing (Ubuntu, macOS, Windows)
  - Automated linting and formatting checks
- Complete documentation:
  - `README.md` - Main documentation
  - `GUI_README.md` - Web interface guide
  - `CONTRIBUTING.md` - Contribution guidelines
  - `LICENSE` - MIT License
- Development tools configuration:
  - `pyproject.toml` - Package configuration
  - `.flake8` - Linting rules
  - `.pylintrc` - Code analysis settings
  - `.gitignore` - Comprehensive ignore patterns
- Example scripts for all 8 API methods
- Requirements files:
  - `requirements.txt` - Runtime dependencies
  - `requirements-dev.txt` - Development dependencies
  - `requirements-gui.txt` - GUI dependencies

### Changed
- N/A (initial release)

### Deprecated
- N/A (initial release)

### Removed
- N/A (initial release)

### Fixed
- N/A (initial release)

### Security
- Secure API key handling with password-type input in web interface
- No credentials stored in code or repository

---

## [Unreleased]

### Planned
- Add data export formats (CSV, Excel)
- Add data visualization in web interface
- Add batch processing support
- Add rate limiting and request throttling
- Add caching layer for API responses
- Add async support for concurrent requests

---

## Version History

- **1.0.0** (2025-11-19) - Initial release with full feature set
