# Contributing to Facebook Scraper

First off, thank you for considering contributing to Facebook Scraper! It's people like you that make this project such a great tool.

## Code of Conduct

This project and everyone participating in it is governed by our commitment to providing a welcoming and inspiring community for all. Please be respectful and constructive.

## How Can I Contribute?

### Reporting Bugs

Before creating bug reports, please check the existing issues to avoid duplicates. When you create a bug report, include as many details as possible:

**Bug Report Template:**
```markdown
**Describe the bug**
A clear and concise description of what the bug is.

**To Reproduce**
Steps to reproduce the behavior:
1. Initialize scraper with '...'
2. Call method '....'
3. See error

**Expected behavior**
A clear description of what you expected to happen.

**Error messages**
```
Paste error messages here
```

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11.0]
- Library version: [e.g., 1.0.0]

**Additional context**
Add any other context about the problem here.
```

### Suggesting Enhancements

Enhancement suggestions are tracked as GitHub issues. When creating an enhancement suggestion, include:

- **Clear title and description** of the suggested enhancement
- **Use case**: Explain why this enhancement would be useful
- **Possible implementation**: If you have ideas on how to implement it
- **Alternatives considered**: What alternatives have you thought about?

### Pull Requests

1. **Fork the repository** and create your branch from `main`:
   ```bash
   git checkout -b feature/amazing-feature
   ```

2. **Make your changes** following our coding standards (see below)

3. **Add tests** if you're adding functionality

4. **Ensure all tests pass**:
   ```bash
   pytest tests/ -v
   ```

5. **Ensure code quality checks pass**:
   ```bash
   flake8 facebook_scraper.py tests/
   black --check facebook_scraper.py tests/
   mypy facebook_scraper.py --ignore-missing-imports
   ```

6. **Update documentation** if needed (README.md, docstrings, etc.)

7. **Commit your changes** with a clear commit message:
   ```bash
   git commit -m "Add feature: brief description"
   ```

8. **Push to your fork**:
   ```bash
   git push origin feature/amazing-feature
   ```

9. **Open a Pull Request** with a clear description of your changes

## Development Setup

### 1. Fork and Clone

```bash
git clone https://github.com/YOUR_USERNAME/facebook-scraper.git
cd facebook-scraper
```

### 2. Create Virtual Environment

```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

### 3. Install Development Dependencies

```bash
pip install -r requirements-dev.txt
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
```

## Coding Standards

### Python Style Guide

- Follow [PEP 8](https://www.python.org/dev/peps/pep-0008/)
- Use **Black** for code formatting (line length: 88)
- Use **type hints** for all function parameters and return values
- Write **docstrings** for all public methods (Google style)

### Code Formatting

Format your code with Black before committing:

```bash
black facebook_scraper.py tests/
```

### Type Hints

All new code should include type hints:

```python
from typing import Dict, Any

def my_function(url: str) -> Dict[str, Any]:
    """Function description.

    Args:
        url: Description of url parameter.

    Returns:
        Description of return value.
    """
    return {}
```

### Docstrings

Use Google-style docstrings:

```python
def example_function(param1: str, param2: int) -> bool:
    """Brief description of function.

    Longer description if needed, explaining what the function does
    in more detail.

    Args:
        param1: Description of param1.
        param2: Description of param2.

    Returns:
        Description of return value.

    Raises:
        ValueError: When param2 is negative.

    Example:
        >>> example_function("test", 5)
        True
    """
    if param2 < 0:
        raise ValueError("param2 must be positive")
    return True
```

## Testing Guidelines

### Writing Tests

- Write tests for all new features
- Use **pytest** for testing
- Use **mocks** for API calls (no real API requests in tests)
- Aim for high code coverage (>90%)

### Test Structure

```python
import pytest
from unittest.mock import Mock, patch

def test_feature_name():
    """Test description."""
    # Arrange
    expected_result = {"key": "value"}

    # Act
    result = function_to_test()

    # Assert
    assert result == expected_result
```

### Running Tests

```bash
# Run all tests
pytest tests/ -v

# Run with coverage
pytest tests/ -v --cov=facebook_scraper --cov-report=term-missing

# Run specific test
pytest tests/test_facebook_scraper.py::TestClassName::test_method_name -v
```

## Commit Message Guidelines

### Format

```
<type>: <subject>

<body>

<footer>
```

### Types

- **feat**: A new feature
- **fix**: A bug fix
- **docs**: Documentation changes
- **style**: Code formatting (no code change)
- **refactor**: Code refactoring
- **test**: Adding or updating tests
- **chore**: Maintenance tasks

### Examples

```
feat: add caching support for API responses

Add LRU cache to reduce redundant API calls and improve performance.
Cache expires after 5 minutes by default.

Closes #42
```

```
fix: handle network timeout errors correctly

Previously, network timeouts were not caught and would crash the app.
Now they raise a NetworkError exception with a clear message.

Fixes #123
```

## Pull Request Process

1. **Update the README.md** with details of changes if applicable
2. **Update CHANGELOG.md** under the [Unreleased] section
3. **Ensure all tests pass** and code quality checks succeed
4. **Request review** from maintainers
5. **Address review feedback** promptly
6. Once approved, a maintainer will merge your PR

## Code Review Process

- All submissions require review before merging
- Reviewers will check:
  - Code quality and style
  - Test coverage
  - Documentation completeness
  - Performance implications
  - Breaking changes
- Be patient and respectful during the review process

## Adding New Features

When adding a new API method or major feature:

1. **Discuss first**: Open an issue to discuss the feature
2. **Update documentation**: Add examples and usage instructions
3. **Add tests**: Comprehensive test coverage required
4. **Update type hints**: All new code must be type-hinted
5. **Update CHANGELOG.md**: Document the new feature

## Release Process

(For maintainers)

1. Update version in `pyproject.toml` and `setup.py`
2. Update CHANGELOG.md with release date
3. Create a git tag: `git tag -a v1.0.0 -m "Release v1.0.0"`
4. Push tag: `git push origin v1.0.0`
5. Create GitHub release with changelog
6. Build and publish to PyPI (if applicable)

## Questions?

Feel free to open an issue with the label `question` if you need help or clarification.

## License

By contributing, you agree that your contributions will be licensed under the MIT License.

---

Thank you for contributing to Facebook Scraper! 🎉
