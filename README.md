# Facebook Scraper

[![CI](https://github.com/yourusername/facebook-scraper/actions/workflows/ci.yml/badge.svg)](https://github.com/yourusername/facebook-scraper/actions/workflows/ci.yml)
[![Python 3.7+](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A simple Python wrapper for the [Facebook Scraper API](https://rapidapi.com/taskagi-2-taskagi-2-default/api/facebook-scraper4/) available on RapidAPI. This tool allows you to interact with Facebook Marketplace and Page data easily.

## 🌐 Web Interface Available!

**NEW:** Now includes a beautiful Streamlit web interface! No coding required.

```bash
pip install -r requirements-gui.txt
streamlit run app.py
```

👉 See [GUI_README.md](GUI_README.md) for full web interface documentation.

---

## Features

- Retrieve information of a specific Marketplace listing.
- Search Marketplace items by location.
- Search Marketplace items by keyword.
- Retrieve posts from a public Facebook page.
- Get information about a Facebook page.
- Retrieve post, engagement, and comment information from a post URL.
- Retrieve photos from a public Facebook profile.
- Retrieve information from a public Facebook profile.
- **NEW:** Web-based GUI with Streamlit
- Type hints and comprehensive error handling
- Full test coverage (18 unit tests)

## Table of Contents

- [Web Interface](#-web-interface-available)
- [Installation](#installation)
- [Usage](#usage)
  - [Setup](#setup)
  - [Examples](#examples)
- [Error Handling](#error-handling)
- [Development](#development)
  - [Setup Development Environment](#setup-development-environment)
  - [Running Tests](#running-tests)
  - [Code Quality](#code-quality)
- [API Endpoints](#api-endpoints)
- [Contributing](#contributing)
- [License](#license)

## Installation

1. **Clone the repository:**

    ```bash
    git clone https://github.com/yourusername/facebook-scraper.git
    cd facebook-scraper
    ```

2. **Create a virtual environment (optional but recommended):**

    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3. **Install the required packages:**

    ```bash
    pip install -r requirements.txt
    ```

## Usage

### Setup

1. **Obtain a RapidAPI Key:**

   - Sign up or log in to [RapidAPI](https://rapidapi.com/).
   - Subscribe to the [Facebook Scraper API](https://rapidapi.com/your-api-link).
   - Get your unique `x-rapidapi-key`.

2. **Add Your RapidAPI Key:**

   - Open any of the example scripts in the `examples/` directory.
   - Replace `"YOUR_RAPIDAPI_KEY"` with your actual RapidAPI key.

### Examples

Each example script demonstrates how to use a specific endpoint. Below are instructions for each.

#### 1. Get Marketplace Item

Retrieve information of a specific Facebook Marketplace listing.

**Script:** `examples/marketplace_item.py`

```python
from facebook_scraper import FacebookScraper

def main():
    rapidapi_key = "YOUR_RAPIDAPI_KEY"  # Replace with your RapidAPI key
    scraper = FacebookScraper(rapidapi_key)

    facebook_url = "https://www.facebook.com/marketplace/item/1030745568732697"
    data = scraper.get_marketplace_item(facebook_url)

    print(data)

if __name__ == "__main__":
    main()
```

**Run the example:**

```bash
python examples/marketplace_item.py
```

For more examples, see the other scripts in the `examples/` directory. Each script demonstrates a different API method.

---

## Error Handling

The library includes comprehensive error handling with custom exceptions:

### Exception Types

```python
from facebook_scraper import (
    FacebookScraper,
    FacebookScraperError,      # Base exception
    AuthenticationError,        # API key issues (401, 403)
    APIError,                   # API errors (4xx, 5xx)
    NetworkError                # Connection/timeout issues
)
```

### Usage Example

```python
from facebook_scraper import FacebookScraper, AuthenticationError, NetworkError, APIError

scraper = FacebookScraper("YOUR_API_KEY")

try:
    data = scraper.get_marketplace_item("https://facebook.com/marketplace/item/123")
    print(data)
except AuthenticationError as e:
    print(f"Authentication failed: {e}")
    print("Check your API key and subscription")
except NetworkError as e:
    print(f"Network error: {e}")
    print("Check your internet connection")
except APIError as e:
    print(f"API error: {e}")
    print("Check the URL and try again")
```

### Error Details

- **AuthenticationError**: Raised for invalid API keys or subscription issues (HTTP 401/403)
- **NetworkError**: Raised for timeouts (30s), connection errors, or network failures
- **APIError**: Raised for invalid requests, rate limits, or malformed responses
- **FacebookScraperError**: Base class for all scraper exceptions

All methods include automatic timeout handling (30 seconds) and detailed error messages.

---

## Development

### Setup Development Environment

1. **Clone the repository:**

```bash
git clone https://github.com/yourusername/facebook-scraper.git
cd facebook-scraper
```

2. **Create a virtual environment:**

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. **Install development dependencies:**

```bash
pip install -r requirements-dev.txt
```

This installs:
- Runtime dependencies (`requests`)
- Testing tools (`pytest`, `pytest-cov`)
- Linters (`flake8`, `black`, `mypy`)
- Type stubs (`types-requests`)

### Running Tests

The project includes 18 comprehensive unit tests with 100% pass rate.

**Run all tests:**

```bash
pytest tests/ -v
```

**Run with coverage:**

```bash
pytest tests/ -v --cov=facebook_scraper --cov-report=term-missing
```

**Run specific test file:**

```bash
pytest tests/test_facebook_scraper.py -v
```

**Test Structure:**
- `tests/test_facebook_scraper.py` - All unit tests
- Tests cover all 8 API methods
- Mock-based testing (no real API calls)
- Error handling tests for all exception types

### Code Quality

The project maintains high code quality standards:

**Run linters:**

```bash
# Check code style
flake8 facebook_scraper.py tests/

# Check formatting
black --check facebook_scraper.py tests/

# Type checking
mypy facebook_scraper.py --ignore-missing-imports
```

**Auto-format code:**

```bash
black facebook_scraper.py tests/
```

**Run all quality checks:**

```bash
# Lint, format, type check, and test
flake8 facebook_scraper.py tests/ && \
black --check facebook_scraper.py tests/ && \
mypy facebook_scraper.py --ignore-missing-imports && \
pytest tests/ -v
```

### CI/CD

GitHub Actions automatically runs on every push and pull request:
- Tests across Python 3.7-3.11
- Tests on Ubuntu, macOS, and Windows
- Linting with flake8
- Formatting checks with black
- Type checking with mypy

See `.github/workflows/ci.yml` for configuration.

---

## API Endpoints

The library provides access to 8 Facebook Scraper API endpoints:

| Method | Description | Example URL |
|--------|-------------|-------------|
| `get_marketplace_item()` | Get single item details | `facebook.com/marketplace/item/123` |
| `search_marketplace_by_location()` | Search by location | `facebook.com/marketplace/category/vehicles` |
| `search_marketplace_by_keyword()` | Search by keyword | `facebook.com/marketplace/search?query=laptop` |
| `retrieve_page_posts()` | Get page posts | `facebook.com/pagename` |
| `get_page_about_info()` | Get page information | `facebook.com/pagename` |
| `retrieve_post_data()` | Get post engagement | `facebook.com/user/posts/123` |
| `retrieve_profile_photos()` | Get profile photos | `facebook.com/username` |
| `retrieve_profile_data()` | Get profile info | `facebook.com/username` |

### Type Hints

All methods are fully type-hinted:

```python
def get_marketplace_item(self, facebook_url: str) -> Dict[str, Any]:
    """Retrieve marketplace item details."""
    ...
```

Return types: `Dict[str, Any]` (JSON response from API)

---

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

**Quick Start:**
1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Make your changes
4. Run tests and linters
5. Commit your changes (`git commit -m 'Add amazing feature'`)
6. Push to the branch (`git push origin feature/amazing-feature`)
7. Open a Pull Request

---

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## Changelog

See [CHANGELOG.md](CHANGELOG.md) for version history and changes
