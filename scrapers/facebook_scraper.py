"""
Enhanced Facebook Scraper with error handling, logging, and database integration
"""
import requests
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

from config.settings import settings
from database.models import db
from database.vector_store import vector_store


class FacebookScraper:
    """Enhanced Facebook scraper with robust error handling"""

    def __init__(self, rapidapi_key: str = None):
        self.rapidapi_key = rapidapi_key or settings.RAPIDAPI_KEY
        self.base_url = "https://facebook-scraper4.p.rapidapi.com/api/social-media/facebook-scraper"

        self.headers = {
            "x-rapidapi-key": self.rapidapi_key,
            "x-rapidapi-host": settings.RAPIDAPI_HOST,
            "Content-Type": "application/json"
        }

    def _make_request(self, endpoint: str, facebook_url: str,
                     max_retries: int = 3) -> Optional[Dict[str, Any]]:
        """Make API request with retry logic and error handling"""
        url = f"{self.base_url}/{endpoint}"
        payload = {"facebookUrl": facebook_url}

        for attempt in range(max_retries):
            try:
                response = requests.post(url, json=payload, headers=self.headers, timeout=30)

                if response.status_code == 200:
                    return response.json()
                elif response.status_code == 429:
                    # Rate limit - wait and retry
                    wait_time = (attempt + 1) * 5
                    db.add_log("WARNING", "FacebookScraper",
                             f"Rate limit hit, waiting {wait_time}s")
                    time.sleep(wait_time)
                elif response.status_code == 403:
                    db.add_log("ERROR", "FacebookScraper",
                             "Invalid API key or access denied",
                             f"URL: {facebook_url}")
                    return None
                else:
                    db.add_log("ERROR", "FacebookScraper",
                             f"Request failed with status {response.status_code}",
                             f"URL: {facebook_url}, Response: {response.text}")
                    if attempt < max_retries - 1:
                        time.sleep(2)
                        continue
                    return None

            except requests.exceptions.Timeout:
                db.add_log("WARNING", "FacebookScraper",
                         f"Request timeout (attempt {attempt + 1}/{max_retries})",
                         f"URL: {facebook_url}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None

            except requests.exceptions.RequestException as e:
                db.add_log("ERROR", "FacebookScraper",
                         f"Request exception: {str(e)}",
                         f"URL: {facebook_url}")
                if attempt < max_retries - 1:
                    time.sleep(2)
                    continue
                return None

        return None

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

    def scrape_page_for_tourism(self, page_url: str, page_id: int = None,
                                auto_categorize: bool = True) -> Dict[str, Any]:
        """
        Scrape Facebook page and extract tourism-related content
        Stores in both SQLite and ChromaDB
        """
        results = {
            'success': False,
            'page_url': page_url,
            'posts_scraped': 0,
            'posts_stored': 0,
            'images_found': 0,
            'errors': []
        }

        try:
            # Get page posts
            data = self.retrieve_page_posts(page_url)

            if not data or 'data' not in data:
                results['errors'].append("No data returned from API")
                db.add_log("ERROR", "FacebookScraper",
                         "No data returned from API", f"Page: {page_url}")
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
                        'page_id': page_id,
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
                        'page_url': page_url,
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

            # Update page metadata
            if page_id:
                db.update_facebook_page(
                    page_id,
                    last_scraped=datetime.now().isoformat(),
                    total_posts_scraped=db.get_connection().execute(
                        "SELECT COUNT(*) FROM posts_metadata WHERE page_id = ?",
                        (page_id,)
                    ).fetchone()[0]
                )

            results['success'] = True
            db.add_log("INFO", "FacebookScraper",
                     f"Successfully scraped {results['posts_stored']} posts",
                     f"Page: {page_url}")

        except Exception as e:
            results['errors'].append(f"Scraping error: {str(e)}")
            db.add_log("ERROR", "FacebookScraper",
                     f"Scraping failed: {str(e)}", f"Page: {page_url}")

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

    def scrape_multiple_pages(self, page_ids: List[int] = None,
                             progress_callback=None) -> Dict[str, Any]:
        """Scrape multiple Facebook pages"""
        if page_ids:
            pages = [db.get_connection().execute(
                "SELECT * FROM facebook_pages WHERE id = ?", (pid,)
            ).fetchone() for pid in page_ids]
            pages = [dict(p) for p in pages if p]
        else:
            pages = db.get_facebook_pages(active_only=True)

        results = {
            'total_pages': len(pages),
            'successful': 0,
            'failed': 0,
            'total_posts': 0,
            'total_images': 0,
            'errors': []
        }

        for i, page in enumerate(pages):
            if progress_callback:
                progress_callback(i + 1, len(pages), page['page_name'])

            page_result = self.scrape_page_for_tourism(
                page['page_url'],
                page['id']
            )

            if page_result['success']:
                results['successful'] += 1
                results['total_posts'] += page_result['posts_stored']
                results['total_images'] += page_result['images_found']
            else:
                results['failed'] += 1
                results['errors'].extend(page_result['errors'])

            # Rate limiting
            time.sleep(2)

        return results


# Singleton instance
scraper = FacebookScraper()
