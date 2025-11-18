"""
Enhanced Facebook Scraper with error handling, logging, and database integration
"""
import requests
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from config.settings import settings
from database.models import db
from database.vector_store import vector_store


class FacebookScraperError(Exception):
    """Custom exception for Facebook scraper errors"""
    pass


class FacebookScraper:
    """Enhanced Facebook scraper with robust error handling"""

    def __init__(self, rapidapi_key: str = None):
        self.rapidapi_key = rapidapi_key or settings.RAPIDAPI_KEY
        self.base_url = "https://facebook-scraper4.p.rapidapi.com/api/social-media/facebook-scraper"

        # Create session for connection pooling
        self.session = requests.Session()

        # Setup headers
        self.session.headers.update({
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": settings.RAPIDAPI_HOST,
            "Content-Type": "application/json",
            "Accept": "application/json"
        })

        # Configure retry strategy
        retry_strategy = Retry(
            total=3,
            backoff_factor=1,  # Wait 1, 2, 4 seconds between retries
            status_forcelist=[429, 500, 502, 503, 504],
            allowed_methods=["POST", "GET"],
            raise_on_status=False
        )

        adapter = HTTPAdapter(max_retries=retry_strategy)
        self.session.mount("https://", adapter)
        self.session.mount("http://", adapter)

    def _make_request(self, endpoint: str, facebook_url: str) -> Optional[Dict[str, Any]]:
        """
        Make API request with automatic retry logic and error handling

        Args:
            endpoint: API endpoint (e.g., 'page-posts')
            facebook_url: Facebook URL to scrape

        Returns:
            JSON response or None on error

        Raises:
            FacebookScraperError: On critical errors
        """
        # Validate input
        if not facebook_url or not isinstance(facebook_url, str):
            raise FacebookScraperError("facebook_url must be a non-empty string")

        url = f"{self.base_url}/{endpoint}"
        payload = {"facebookUrl": facebook_url.strip()}

        try:
            # Session handles retries automatically via HTTPAdapter
            response = self.session.post(url, json=payload, timeout=30)

            # Check for HTTP errors
            if response.status_code == 200:
                try:
                    return response.json()
                except ValueError as e:
                    db.add_log("ERROR", "FacebookScraper",
                             "Invalid JSON received from API",
                             f"URL: {facebook_url}")
                    raise FacebookScraperError(f"Invalid JSON from API: {e}")

            elif response.status_code == 403:
                db.add_log("ERROR", "FacebookScraper",
                         "Invalid API key or access denied",
                         f"URL: {facebook_url}")
                raise FacebookScraperError("Invalid API key or access denied")

            elif response.status_code == 429:
                db.add_log("WARNING", "FacebookScraper",
                         "Rate limit exceeded",
                         f"URL: {facebook_url}")
                return None

            else:
                # Try to get error message from response
                error_msg = None
                try:
                    json_body = response.json()
                    error_msg = json_body.get("message") or str(json_body)
                except:
                    error_msg = response.text or str(response.status_code)

                db.add_log("ERROR", "FacebookScraper",
                         f"HTTP {response.status_code}: {error_msg}",
                         f"URL: {facebook_url}")
                return None

        except requests.exceptions.Timeout as e:
            db.add_log("ERROR", "FacebookScraper",
                     "Request timeout",
                     f"URL: {facebook_url}")
            raise FacebookScraperError(f"Request timeout: {e}")

        except requests.exceptions.RequestException as e:
            db.add_log("ERROR", "FacebookScraper",
                     f"Network error: {str(e)}",
                     f"URL: {facebook_url}")
            raise FacebookScraperError(f"Network error: {e}")

        except FacebookScraperError:
            # Re-raise our custom errors
            raise

        except Exception as e:
            db.add_log("ERROR", "FacebookScraper",
                     f"Unexpected error: {str(e)}",
                     f"URL: {facebook_url}")
            raise FacebookScraperError(f"Unexpected error: {e}")

    # ============================================
    # Page Scraping Methods
    # ============================================

    def get_page_about_info(self, facebook_url: str) -> Optional[Dict[str, Any]]:
        """Get page about information"""
        return self._make_request("page-about", facebook_url)

    def retrieve_page_posts(self, facebook_url: str) -> Optional[Dict[str, Any]]:
        """Retrieve posts from a Facebook page"""
        return self._make_request("page-posts", facebook_url)

    def retrieve_post_data(self, facebook_url: str) -> Optional[Dict[str, Any]]:
        """Get detailed post data including engagement"""
        return self._make_request("post-data", facebook_url)

    # ============================================
    # Profile Methods
    # ============================================

    def retrieve_profile_data(self, facebook_url: str) -> Optional[Dict[str, Any]]:
        """Get profile data"""
        return self._make_request("profile-data", facebook_url)

    def retrieve_profile_photos(self, facebook_url: str) -> Optional[Dict[str, Any]]:
        """Retrieve profile photos"""
        return self._make_request("profile-photos", facebook_url)

    # ============================================
    # Marketplace Methods
    # ============================================

    def get_marketplace_item(self, facebook_url: str) -> Optional[Dict[str, Any]]:
        """Get marketplace item details"""
        return self._make_request("marketplace-item", facebook_url)

    def search_marketplace_by_location(self, facebook_url: str) -> Optional[Dict[str, Any]]:
        """Search marketplace by location"""
        return self._make_request("marketplace-items-by-location", facebook_url)

    def search_marketplace_by_keyword(self, facebook_url: str) -> Optional[Dict[str, Any]]:
        """Search marketplace by keyword"""
        return self._make_request("marketplace-items-by-keyword", facebook_url)

    # ============================================
    # Tourism-Specific Methods
    # ============================================

    def scrape_group_for_tourism(self, group_url: str, group_id: int = None,
                                auto_categorize: bool = True) -> Dict[str, Any]:
        """
        Scrape Facebook group and extract tourism-related content
        Stores in both SQLite and ChromaDB
        """
        results = {
            'success': False,
            'group_url': group_url,
            'posts_scraped': 0,
            'posts_stored': 0,
            'images_found': 0,
            'errors': []
        }

        try:
            # Get group posts (using page-posts endpoint - works for both pages and groups)
            try:
                data = self.retrieve_page_posts(group_url)
            except FacebookScraperError as e:
                results['errors'].append(f"API error: {str(e)}")
                return results

            if not data or 'data' not in data:
                results['errors'].append("No data returned from API")
                db.add_log("ERROR", "FacebookScraper",
                         "No data returned from API", f"Group: {group_url}")
                return results

            posts = data.get('data', [])
            results['posts_scraped'] = len(posts)

            # Process each post
            for post in posts:
                try:
                    post_content = post.get('text', '') or post.get('content', '')
                    if not post_content:
                        continue

                    # Extract post info
                    post_id = post.get('id') or post.get('post_id', '')
                    post_url = post.get('url', '')
                    author = post.get('author', '') or post.get('from', {}).get('name', '')
                    posted_date = post.get('created_time', '') or post.get('date', '')

                    # Extract engagement
                    likes = post.get('likes', 0) or post.get('reactions', {}).get('total', 0)
                    comments = post.get('comments', 0) or post.get('comment_count', 0)
                    shares = post.get('shares', 0) or post.get('share_count', 0)

                    # Extract images
                    images = post.get('images', []) or post.get('attachments', {}).get('images', [])
                    has_images = len(images) > 0
                    results['images_found'] += len(images)

                    # Auto-categorize content
                    category = 'general'
                    location = ''

                    if auto_categorize:
                        category = self._categorize_content(post_content)
                        location = self._extract_location(post_content)

                    # Store in SQLite metadata
                    metadata = {
                        'post_id': post_id,
                        'group_id': group_id,
                        'post_url': post_url,
                        'author': author,
                        'posted_date': posted_date,
                        'engagement_likes': likes,
                        'engagement_comments': comments,
                        'engagement_shares': shares,
                        'has_images': 1 if has_images else 0,
                        'image_count': len(images),
                        'category': category
                    }

                    db.add_post_metadata(metadata)

                    # Store in ChromaDB for semantic search
                    vector_data = {
                        'post_id': post_id,
                        'content': post_content,
                        'group_url': group_url,
                        'author': author,
                        'posted_date': posted_date,
                        'location': location,
                        'category': category,
                        'likes': likes,
                        'comments': comments,
                        'shares': shares,
                        'has_images': has_images
                    }

                    vector_store.add_post(vector_data)
                    results['posts_stored'] += 1

                    # Store images
                    for img in images:
                        img_url = img if isinstance(img, str) else img.get('url', '')
                        if img_url:
                            image_data = {
                                'image_url': img_url,
                                'source': 'facebook',
                                'post_id': post_id,
                                'keywords': category,
                                'location': location,
                                'attribution': f"Facebook - {author}"
                            }
                            db.add_image(image_data)

                except Exception as e:
                    results['errors'].append(f"Error processing post: {str(e)}")
                    continue

            # Update group metadata
            if group_id:
                db.update_facebook_group(
                    group_id,
                    last_scraped=datetime.now().isoformat(),
                    total_posts_scraped=db.get_connection().execute(
                        "SELECT COUNT(*) FROM posts_metadata WHERE group_id = ?",
                        (group_id,)
                    ).fetchone()[0]
                )

            results['success'] = True
            db.add_log("INFO", "FacebookScraper",
                     f"Successfully scraped {results['posts_stored']} posts",
                     f"Group: {group_url}")

        except Exception as e:
            results['errors'].append(f"Scraping error: {str(e)}")
            db.add_log("ERROR", "FacebookScraper",
                     f"Scraping failed: {str(e)}", f"Group: {group_url}")

        return results

    def _categorize_content(self, content: str) -> str:
        """Auto-categorize content based on keywords"""
        content_lower = content.lower()

        categories = {
            'restaurant': ['restaurant', 'tavern', 'food', 'dinner', 'lunch', 'breakfast',
                          'cafe', 'menu', 'dish', 'eat', 'cuisine'],
            'hotel': ['hotel', 'accommodation', 'stay', 'resort', 'villa', 'apartment',
                     'room', 'booking', 'check-in'],
            'beach': ['beach', 'sea', 'coast', 'shore', 'swimming', 'sunbed', 'sand'],
            'attraction': ['museum', 'castle', 'monument', 'temple', 'church', 'tour',
                          'sightseeing', 'visit', 'explore'],
            'activity': ['hiking', 'diving', 'sailing', 'adventure', 'tour', 'excursion',
                        'activity', 'experience'],
            'transportation': ['taxi', 'bus', 'car rental', 'transfer', 'airport', 'ferry',
                             'transport']
        }

        for category, keywords in categories.items():
            if any(keyword in content_lower for keyword in keywords):
                return category

        return 'general'

    def _extract_location(self, content: str) -> str:
        """Extract location mentions from content"""
        # This is a simple implementation - can be enhanced with NLP
        # Common Greek tourism locations
        locations = [
            'Rhodes', 'Lindos', 'Faliraki', 'Athens', 'Santorini', 'Mykonos',
            'Crete', 'Corfu', 'Zakynthos', 'Thessaloniki', 'Delphi', 'Meteora',
            'Oia', 'Fira', 'Heraklion', 'Chania', 'Rethymno'
        ]

        for location in locations:
            if location.lower() in content.lower():
                return location

        return ''

    def scrape_multiple_groups(self, group_ids: List[int] = None,
                             progress_callback=None) -> Dict[str, Any]:
        """Scrape multiple Facebook groups"""
        if group_ids:
            groups = [db.get_connection().execute(
                "SELECT * FROM facebook_groups WHERE id = ?", (gid,)
            ).fetchone() for gid in group_ids]
            groups = [dict(g) for g in groups if g]
        else:
            groups = db.get_facebook_groups(active_only=True)

        results = {
            'total_groups': len(groups),
            'successful': 0,
            'failed': 0,
            'total_posts': 0,
            'total_images': 0,
            'errors': []
        }

        for i, group in enumerate(groups):
            if progress_callback:
                progress_callback(i + 1, len(groups), group['group_name'])

            group_result = self.scrape_group_for_tourism(
                group['group_url'],
                group['id']
            )

            if group_result['success']:
                results['successful'] += 1
                results['total_posts'] += group_result['posts_stored']
                results['total_images'] += group_result['images_found']
            else:
                results['failed'] += 1
                results['errors'].extend(group_result['errors'])

            # Rate limiting
            time.sleep(2)

        return results


# Singleton instance
scraper = FacebookScraper()
