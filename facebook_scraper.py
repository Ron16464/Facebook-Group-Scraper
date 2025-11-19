# facebook_scraper.py

from typing import Any, Dict

import requests
from requests.exceptions import RequestException, Timeout, ConnectionError


class FacebookScraperError(Exception):
    """Base exception for FacebookScraper errors."""

    pass


class APIError(FacebookScraperError):
    """Raised when the API returns an error response."""

    pass


class AuthenticationError(FacebookScraperError):
    """Raised when API authentication fails."""

    pass


class NetworkError(FacebookScraperError):
    """Raised when network-related errors occur."""

    pass


class FacebookScraper:
    """A Python wrapper for the Facebook Scraper API available on RapidAPI.

    This class provides methods to interact with Facebook Marketplace,
    Pages, Posts, and Profiles through the RapidAPI Facebook Scraper API.

    Attributes:
        rapidapi_key: Your RapidAPI authentication key.
        base_url: The base URL for the Facebook Scraper API.
        headers: HTTP headers required for API authentication.
    """

    def __init__(self, rapidapi_key: str) -> None:
        """Initialize the FacebookScraper with RapidAPI credentials.

        Args:
            rapidapi_key: Your RapidAPI key for authentication.
        """
        self.rapidapi_key: str = rapidapi_key
        self.base_url: str = (
            "https://facebook-scraper4.p.rapidapi.com/api/social-media/facebook-scraper"
        )

        self.headers: Dict[str, str] = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": "facebook-scraper4.p.rapidapi.com",
            "Content-Type": "application/json",
        }

    def _make_request(self, endpoint: str, facebook_url: str) -> Dict[str, Any]:
        """Make a POST request to the API with error handling.

        Args:
            endpoint: The API endpoint path.
            facebook_url: The Facebook URL to scrape.

        Returns:
            The JSON response from the API.

        Raises:
            AuthenticationError: If API authentication fails (401, 403).
            APIError: If the API returns an error response (4xx, 5xx).
            NetworkError: If network-related errors occur.
        """
        url = f"{self.base_url}/{endpoint}"
        payload = {"facebookUrl": facebook_url}

        try:
            response = requests.post(
                url, json=payload, headers=self.headers, timeout=30
            )

            # Check for authentication errors
            if response.status_code in (401, 403):
                raise AuthenticationError(
                    f"Authentication failed: {response.status_code} - {response.text}"
                )

            # Check for other HTTP errors
            if not response.ok:
                raise APIError(f"API error: {response.status_code} - {response.text}")

            return response.json()

        except Timeout as e:
            raise NetworkError(f"Request timeout: {str(e)}") from e
        except ConnectionError as e:
            raise NetworkError(f"Connection error: {str(e)}") from e
        except requests.exceptions.JSONDecodeError as e:
            raise APIError(f"Invalid JSON response: {str(e)}") from e
        except RequestException as e:
            raise NetworkError(f"Network error: {str(e)}") from e

    def get_marketplace_item(self, facebook_url: str) -> Dict[str, Any]:
        """Retrieve information about a specific Facebook Marketplace listing.

        Args:
            facebook_url: The URL of the Facebook Marketplace item.

        Returns:
            A dictionary containing the marketplace item details.

        Raises:
            AuthenticationError: If API authentication fails.
            APIError: If the API returns an error.
            NetworkError: If network-related errors occur.

        Example:
            >>> scraper = FacebookScraper("your_api_key")
            >>> item = scraper.get_marketplace_item(
            ...     "https://www.facebook.com/marketplace/item/123456"
            ... )
        """
        return self._make_request("marketplace-item", facebook_url)

    def search_marketplace_by_location(self, facebook_url: str) -> Dict[str, Any]:
        """Search Facebook Marketplace items in a specific location.

        Args:
            facebook_url: The Facebook Marketplace URL with location parameters.

        Returns:
            A dictionary containing marketplace items in the specified location.

        Raises:
            AuthenticationError: If API authentication fails.
            APIError: If the API returns an error.
            NetworkError: If network-related errors occur.

        Example:
            >>> scraper = FacebookScraper("your_api_key")
            >>> items = scraper.search_marketplace_by_location(
            ...     "https://www.facebook.com/marketplace/category/..."
            ... )
        """
        return self._make_request("marketplace-items-by-location", facebook_url)

    def search_marketplace_by_keyword(self, facebook_url: str) -> Dict[str, Any]:
        """Search Facebook Marketplace items by keyword.

        Args:
            facebook_url: The Facebook Marketplace search URL with keyword.

        Returns:
            A dictionary containing marketplace items matching the keyword.

        Raises:
            AuthenticationError: If API authentication fails.
            APIError: If the API returns an error.
            NetworkError: If network-related errors occur.

        Example:
            >>> scraper = FacebookScraper("your_api_key")
            >>> items = scraper.search_marketplace_by_keyword(
            ...     "https://www.facebook.com/marketplace/search?query=..."
            ... )
        """
        return self._make_request("marketplace-items-by-keyword", facebook_url)

    def retrieve_page_posts(self, facebook_url: str) -> Dict[str, Any]:
        """Retrieve posts from a public Facebook page.

        Args:
            facebook_url: The URL of the Facebook page.

        Returns:
            A dictionary containing posts from the specified page.

        Raises:
            AuthenticationError: If API authentication fails.
            APIError: If the API returns an error.
            NetworkError: If network-related errors occur.

        Example:
            >>> scraper = FacebookScraper("your_api_key")
            >>> posts = scraper.retrieve_page_posts(
            ...     "https://www.facebook.com/page-name"
            ... )
        """
        return self._make_request("page-posts", facebook_url)

    def get_page_about_info(self, facebook_url: str) -> Dict[str, Any]:
        """Get information about a Facebook page.

        Args:
            facebook_url: The URL of the Facebook page.

        Returns:
            A dictionary containing page metadata and about information.

        Raises:
            AuthenticationError: If API authentication fails.
            APIError: If the API returns an error.
            NetworkError: If network-related errors occur.

        Example:
            >>> scraper = FacebookScraper("your_api_key")
            >>> about = scraper.get_page_about_info(
            ...     "https://www.facebook.com/page-name"
            ... )
        """
        return self._make_request("page-about", facebook_url)

    def retrieve_post_data(self, facebook_url: str) -> Dict[str, Any]:
        """Retrieve post data, engagement metrics, and comments from a post.

        Args:
            facebook_url: The URL of the Facebook post.

        Returns:
            A dictionary containing post details, likes, comments, and shares.

        Raises:
            AuthenticationError: If API authentication fails.
            APIError: If the API returns an error.
            NetworkError: If network-related errors occur.

        Example:
            >>> scraper = FacebookScraper("your_api_key")
            >>> post = scraper.retrieve_post_data(
            ...     "https://www.facebook.com/user/posts/123456"
            ... )
        """
        return self._make_request("post-data", facebook_url)

    def retrieve_profile_photos(self, facebook_url: str) -> Dict[str, Any]:
        """Retrieve photos from a public Facebook profile.

        Args:
            facebook_url: The URL of the Facebook profile.

        Returns:
            A dictionary containing photos from the specified profile.

        Raises:
            AuthenticationError: If API authentication fails.
            APIError: If the API returns an error.
            NetworkError: If network-related errors occur.

        Example:
            >>> scraper = FacebookScraper("your_api_key")
            >>> photos = scraper.retrieve_profile_photos(
            ...     "https://www.facebook.com/username"
            ... )
        """
        return self._make_request("profile-photos", facebook_url)

    def retrieve_profile_data(self, facebook_url: str) -> Dict[str, Any]:
        """Retrieve information from a public Facebook profile.

        Args:
            facebook_url: The URL of the Facebook profile.

        Returns:
            A dictionary containing public profile information.

        Raises:
            AuthenticationError: If API authentication fails.
            APIError: If the API returns an error.
            NetworkError: If network-related errors occur.

        Example:
            >>> scraper = FacebookScraper("your_api_key")
            >>> profile = scraper.retrieve_profile_data(
            ...     "https://www.facebook.com/username"
            ... )
        """
        return self._make_request("profile-data", facebook_url)
