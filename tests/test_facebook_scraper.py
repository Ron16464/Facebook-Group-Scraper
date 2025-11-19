# tests/test_facebook_scraper.py

import pytest
from unittest.mock import Mock, patch
from requests.exceptions import Timeout, ConnectionError as RequestsConnectionError

from facebook_scraper import (
    FacebookScraper,
    APIError,
    AuthenticationError,
    NetworkError,
)


class TestFacebookScraperInit:
    """Test FacebookScraper initialization."""

    def test_init_sets_attributes(self):
        api_key = "test_api_key_123"
        scraper = FacebookScraper(api_key)

        assert scraper.rapidapi_key == api_key
        expected_url = (
            "https://facebook-scraper4.p.rapidapi.com"
            "/api/social-media/facebook-scraper"
        )
        assert scraper.base_url == expected_url
        assert scraper.headers["x-rapidapi-key"] == api_key
        assert (
            scraper.headers["x-rapidapi-host"]
            == "facebook-scraper4.p.rapidapi.com"
        )
        assert scraper.headers["Content-Type"] == "application/json"


class TestMakeRequest:
    """Test the _make_request helper method."""

    @patch("facebook_scraper.requests.post")
    def test_successful_request(self, mock_post):
        """Test successful API request."""
        mock_response = Mock()
        mock_response.ok = True
        mock_response.json.return_value = {"status": "success", "data": {}}
        mock_post.return_value = mock_response

        scraper = FacebookScraper("test_key")
        result = scraper._make_request("test-endpoint", "https://facebook.com/test")

        assert result == {"status": "success", "data": {}}
        mock_post.assert_called_once()

    @patch("facebook_scraper.requests.post")
    def test_authentication_error_401(self, mock_post):
        """Test authentication error with 401 status."""
        mock_response = Mock()
        mock_response.status_code = 401
        mock_response.text = "Unauthorized"
        mock_post.return_value = mock_response

        scraper = FacebookScraper("invalid_key")
        with pytest.raises(AuthenticationError, match="Authentication failed: 401"):
            scraper._make_request("test-endpoint", "https://facebook.com/test")

    @patch("facebook_scraper.requests.post")
    def test_authentication_error_403(self, mock_post):
        """Test authentication error with 403 status."""
        mock_response = Mock()
        mock_response.status_code = 403
        mock_response.text = "Forbidden"
        mock_post.return_value = mock_response

        scraper = FacebookScraper("invalid_key")
        with pytest.raises(AuthenticationError, match="Authentication failed: 403"):
            scraper._make_request("test-endpoint", "https://facebook.com/test")

    @patch("facebook_scraper.requests.post")
    def test_api_error_404(self, mock_post):
        """Test API error with 404 status."""
        mock_response = Mock()
        mock_response.ok = False
        mock_response.status_code = 404
        mock_response.text = "Not Found"
        mock_post.return_value = mock_response

        scraper = FacebookScraper("test_key")
        with pytest.raises(APIError, match="API error: 404"):
            scraper._make_request("test-endpoint", "https://facebook.com/test")

    @patch("facebook_scraper.requests.post")
    def test_timeout_error(self, mock_post):
        """Test timeout error."""
        mock_post.side_effect = Timeout("Connection timeout")

        scraper = FacebookScraper("test_key")
        with pytest.raises(NetworkError, match="Request timeout"):
            scraper._make_request("test-endpoint", "https://facebook.com/test")

    @patch("facebook_scraper.requests.post")
    def test_connection_error(self, mock_post):
        """Test connection error."""
        mock_post.side_effect = RequestsConnectionError("Connection failed")

        scraper = FacebookScraper("test_key")
        with pytest.raises(NetworkError, match="Connection error"):
            scraper._make_request("test-endpoint", "https://facebook.com/test")


class TestMarketplaceMethods:
    """Test Marketplace-related methods."""

    @patch.object(FacebookScraper, "_make_request")
    def test_get_marketplace_item(self, mock_request):
        """Test get_marketplace_item method."""
        mock_request.return_value = {
            "title": "Test Item",
            "price": "$100",
        }

        scraper = FacebookScraper("test_key")
        result = scraper.get_marketplace_item(
            "https://facebook.com/marketplace/item/123"
        )

        assert result["title"] == "Test Item"
        mock_request.assert_called_once_with(
            "marketplace-item", "https://facebook.com/marketplace/item/123"
        )

    @patch.object(FacebookScraper, "_make_request")
    def test_search_marketplace_by_location(self, mock_request):
        """Test search_marketplace_by_location method."""
        mock_request.return_value = {"items": [{"id": "1"}, {"id": "2"}]}

        scraper = FacebookScraper("test_key")
        result = scraper.search_marketplace_by_location(
            "https://facebook.com/marketplace/category/vehicles"
        )

        assert len(result["items"]) == 2
        mock_request.assert_called_once_with(
            "marketplace-items-by-location",
            "https://facebook.com/marketplace/category/vehicles",
        )

    @patch.object(FacebookScraper, "_make_request")
    def test_search_marketplace_by_keyword(self, mock_request):
        """Test search_marketplace_by_keyword method."""
        mock_request.return_value = {"items": [{"name": "laptop"}]}

        scraper = FacebookScraper("test_key")
        result = scraper.search_marketplace_by_keyword(
            "https://facebook.com/marketplace/search?query=laptop"
        )

        assert result["items"][0]["name"] == "laptop"
        mock_request.assert_called_once_with(
            "marketplace-items-by-keyword",
            "https://facebook.com/marketplace/search?query=laptop",
        )


class TestPageMethods:
    """Test Page-related methods."""

    @patch.object(FacebookScraper, "_make_request")
    def test_retrieve_page_posts(self, mock_request):
        """Test retrieve_page_posts method."""
        mock_request.return_value = {
            "posts": [{"id": "1", "text": "Post 1"}, {"id": "2", "text": "Post 2"}]
        }

        scraper = FacebookScraper("test_key")
        result = scraper.retrieve_page_posts("https://facebook.com/testpage")

        assert len(result["posts"]) == 2
        mock_request.assert_called_once_with(
            "page-posts", "https://facebook.com/testpage"
        )

    @patch.object(FacebookScraper, "_make_request")
    def test_get_page_about_info(self, mock_request):
        """Test get_page_about_info method."""
        mock_request.return_value = {
            "name": "Test Page",
            "category": "Community",
            "likes": 1000,
        }

        scraper = FacebookScraper("test_key")
        result = scraper.get_page_about_info("https://facebook.com/testpage")

        assert result["name"] == "Test Page"
        assert result["likes"] == 1000
        mock_request.assert_called_once_with(
            "page-about", "https://facebook.com/testpage"
        )


class TestPostMethods:
    """Test Post-related methods."""

    @patch.object(FacebookScraper, "_make_request")
    def test_retrieve_post_data(self, mock_request):
        """Test retrieve_post_data method."""
        mock_request.return_value = {
            "post_id": "123",
            "text": "Test post",
            "likes": 50,
            "comments": 10,
            "shares": 5,
        }

        scraper = FacebookScraper("test_key")
        result = scraper.retrieve_post_data("https://facebook.com/user/posts/123")

        assert result["post_id"] == "123"
        assert result["likes"] == 50
        mock_request.assert_called_once_with(
            "post-data", "https://facebook.com/user/posts/123"
        )


class TestProfileMethods:
    """Test Profile-related methods."""

    @patch.object(FacebookScraper, "_make_request")
    def test_retrieve_profile_photos(self, mock_request):
        """Test retrieve_profile_photos method."""
        mock_request.return_value = {
            "photos": [
                {"id": "1", "url": "https://example.com/photo1.jpg"},
                {"id": "2", "url": "https://example.com/photo2.jpg"},
            ]
        }

        scraper = FacebookScraper("test_key")
        result = scraper.retrieve_profile_photos("https://facebook.com/testuser")

        assert len(result["photos"]) == 2
        mock_request.assert_called_once_with(
            "profile-photos", "https://facebook.com/testuser"
        )

    @patch.object(FacebookScraper, "_make_request")
    def test_retrieve_profile_data(self, mock_request):
        """Test retrieve_profile_data method."""
        mock_request.return_value = {
            "name": "Test User",
            "username": "testuser",
            "verified": False,
        }

        scraper = FacebookScraper("test_key")
        result = scraper.retrieve_profile_data("https://facebook.com/testuser")

        assert result["name"] == "Test User"
        assert result["verified"] is False
        mock_request.assert_called_once_with(
            "profile-data", "https://facebook.com/testuser"
        )


class TestErrorHandling:
    """Test error handling across all methods."""

    @patch.object(FacebookScraper, "_make_request")
    def test_marketplace_item_authentication_error(self, mock_request):
        """Test authentication error propagation."""
        mock_request.side_effect = AuthenticationError("Invalid API key")

        scraper = FacebookScraper("invalid_key")
        with pytest.raises(AuthenticationError):
            scraper.get_marketplace_item("https://facebook.com/marketplace/item/123")

    @patch.object(FacebookScraper, "_make_request")
    def test_page_posts_network_error(self, mock_request):
        """Test network error propagation."""
        mock_request.side_effect = NetworkError("Connection timeout")

        scraper = FacebookScraper("test_key")
        with pytest.raises(NetworkError):
            scraper.retrieve_page_posts("https://facebook.com/testpage")

    @patch.object(FacebookScraper, "_make_request")
    def test_profile_data_api_error(self, mock_request):
        """Test API error propagation."""
        mock_request.side_effect = APIError("Invalid response")

        scraper = FacebookScraper("test_key")
        with pytest.raises(APIError):
            scraper.retrieve_profile_data("https://facebook.com/testuser")
