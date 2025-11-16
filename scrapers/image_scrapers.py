"""
Multi-source image scrapers: Pexels, Unsplash, Pixabay, Wikimedia
"""
import requests
from typing import List, Dict, Any, Optional
import time

from config.settings import settings
from database.models import db


class ImageScraper:
    """Base class for image scrapers"""

    def search_images(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search for images - to be implemented by subclasses"""
        raise NotImplementedError


class PexelsImageScraper(ImageScraper):
    """Pexels image scraper"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.PEXELS_API_KEY
        self.base_url = "https://api.pexels.com/v1"
        self.headers = {"Authorization": self.api_key}

    def search_images(self, query: str, limit: int = 10,
                     orientation: str = None) -> List[Dict[str, Any]]:
        """Search Pexels for images"""
        if not self.api_key:
            return []

        try:
            params = {
                'query': query,
                'per_page': min(limit, 80),
                'page': 1
            }

            if orientation:
                params['orientation'] = orientation

            response = requests.get(
                f"{self.base_url}/search",
                headers=self.headers,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                images = []

                for photo in data.get('photos', []):
                    images.append({
                        'image_url': photo['src']['large2x'],
                        'thumbnail_url': photo['src']['medium'],
                        'source': 'pexels',
                        'attribution': f"Photo by {photo['photographer']} on Pexels",
                        'photographer': photo['photographer'],
                        'photographer_url': photo['photographer_url'],
                        'width': photo['width'],
                        'height': photo['height'],
                        'keywords': query,
                        'alt_text': photo.get('alt', query)
                    })

                return images

            else:
                db.add_log("ERROR", "PexelsImageScraper",
                         f"API error: {response.status_code}", response.text)
                return []

        except Exception as e:
            db.add_log("ERROR", "PexelsImageScraper",
                     f"Search failed: {str(e)}", f"Query: {query}")
            return []


class UnsplashImageScraper(ImageScraper):
    """Unsplash image scraper"""

    def __init__(self, access_key: str = None):
        self.access_key = access_key or settings.UNSPLASH_ACCESS_KEY
        self.base_url = "https://api.unsplash.com"
        self.headers = {"Authorization": f"Client-ID {self.access_key}"}

    def search_images(self, query: str, limit: int = 10,
                     orientation: str = None) -> List[Dict[str, Any]]:
        """Search Unsplash for images"""
        if not self.access_key:
            return []

        try:
            params = {
                'query': query,
                'per_page': min(limit, 30),
                'page': 1
            }

            if orientation:
                params['orientation'] = orientation

            response = requests.get(
                f"{self.base_url}/search/photos",
                headers=self.headers,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                images = []

                for photo in data.get('results', []):
                    images.append({
                        'image_url': photo['urls']['regular'],
                        'thumbnail_url': photo['urls']['small'],
                        'source': 'unsplash',
                        'attribution': f"Photo by {photo['user']['name']} on Unsplash",
                        'photographer': photo['user']['name'],
                        'photographer_url': photo['user']['links']['html'],
                        'width': photo['width'],
                        'height': photo['height'],
                        'keywords': query,
                        'alt_text': photo.get('alt_description', query),
                        'description': photo.get('description', '')
                    })

                return images

            else:
                db.add_log("ERROR", "UnsplashImageScraper",
                         f"API error: {response.status_code}", response.text)
                return []

        except Exception as e:
            db.add_log("ERROR", "UnsplashImageScraper",
                     f"Search failed: {str(e)}", f"Query: {query}")
            return []


class PixabayImageScraper(ImageScraper):
    """Pixabay image scraper"""

    def __init__(self, api_key: str = None):
        self.api_key = api_key or settings.PIXABAY_API_KEY
        self.base_url = "https://pixabay.com/api/"

    def search_images(self, query: str, limit: int = 10,
                     image_type: str = "photo") -> List[Dict[str, Any]]:
        """Search Pixabay for images"""
        if not self.api_key:
            return []

        try:
            params = {
                'key': self.api_key,
                'q': query,
                'image_type': image_type,
                'per_page': min(limit, 200),
                'page': 1
            }

            response = requests.get(
                self.base_url,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                images = []

                for photo in data.get('hits', []):
                    images.append({
                        'image_url': photo['largeImageURL'],
                        'thumbnail_url': photo['previewURL'],
                        'source': 'pixabay',
                        'attribution': f"Image by {photo['user']} from Pixabay",
                        'photographer': photo['user'],
                        'photographer_url': f"https://pixabay.com/users/{photo['user']}-{photo['user_id']}/",
                        'width': photo['imageWidth'],
                        'height': photo['imageHeight'],
                        'keywords': photo.get('tags', query),
                        'alt_text': photo.get('tags', query),
                        'downloads': photo.get('downloads', 0),
                        'likes': photo.get('likes', 0)
                    })

                return images

            else:
                db.add_log("ERROR", "PixabayImageScraper",
                         f"API error: {response.status_code}", response.text)
                return []

        except Exception as e:
            db.add_log("ERROR", "PixabayImageScraper",
                     f"Search failed: {str(e)}", f"Query: {query}")
            return []


class WikimediaImageScraper(ImageScraper):
    """Wikimedia Commons image scraper"""

    def __init__(self):
        self.base_url = "https://commons.wikimedia.org/w/api.php"

    def search_images(self, query: str, limit: int = 10) -> List[Dict[str, Any]]:
        """Search Wikimedia Commons for images"""
        try:
            params = {
                'action': 'query',
                'format': 'json',
                'generator': 'search',
                'gsrnamespace': 6,  # File namespace
                'gsrsearch': query,
                'gsrlimit': min(limit, 50),
                'prop': 'imageinfo',
                'iiprop': 'url|size|user|extmetadata',
                'iiurlwidth': 1024
            }

            response = requests.get(
                self.base_url,
                params=params,
                timeout=15
            )

            if response.status_code == 200:
                data = response.json()
                images = []

                pages = data.get('query', {}).get('pages', {})
                for page_id, page in pages.items():
                    if 'imageinfo' not in page:
                        continue

                    info = page['imageinfo'][0]
                    metadata = info.get('extmetadata', {})

                    # Extract attribution
                    artist = metadata.get('Artist', {}).get('value', 'Unknown')
                    license_name = metadata.get('LicenseShortName', {}).get('value', '')
                    credit = metadata.get('Credit', {}).get('value', '')

                    images.append({
                        'image_url': info.get('url', ''),
                        'thumbnail_url': info.get('thumburl', ''),
                        'source': 'wikimedia',
                        'attribution': f"{artist} - {license_name}",
                        'photographer': artist,
                        'license': license_name,
                        'width': info.get('width', 0),
                        'height': info.get('height', 0),
                        'keywords': query,
                        'alt_text': page.get('title', '').replace('File:', ''),
                        'description': metadata.get('ImageDescription', {}).get('value', ''),
                        'credit': credit
                    })

                return images

            else:
                db.add_log("ERROR", "WikimediaImageScraper",
                         f"API error: {response.status_code}", response.text)
                return []

        except Exception as e:
            db.add_log("ERROR", "WikimediaImageScraper",
                     f"Search failed: {str(e)}", f"Query: {query}")
            return []


class MultiSourceImageSearch:
    """Unified interface for searching images across multiple sources"""

    def __init__(self):
        self.scrapers = {
            'pexels': PexelsImageScraper(),
            'unsplash': UnsplashImageScraper(),
            'pixabay': PixabayImageScraper(),
            'wikimedia': WikimediaImageScraper()
        }

    def search_all_sources(self, query: str, limit_per_source: int = 5,
                          sources: List[str] = None) -> Dict[str, List[Dict[str, Any]]]:
        """Search all enabled image sources"""
        if sources is None:
            sources = list(self.scrapers.keys())

        results = {}

        for source_name in sources:
            if source_name not in self.scrapers:
                continue

            scraper = self.scrapers[source_name]
            images = scraper.search_images(query, limit=limit_per_source)
            results[source_name] = images

            # Rate limiting
            time.sleep(0.5)

        return results

    def search_best_images(self, query: str, limit: int = 10,
                          prefer_sources: List[str] = None) -> List[Dict[str, Any]]:
        """
        Search across sources and return best images
        Prioritizes high-quality, well-attributed images
        """
        all_images = []

        # Determine search order
        if prefer_sources:
            search_order = prefer_sources + [s for s in self.scrapers.keys()
                                            if s not in prefer_sources]
        else:
            search_order = ['unsplash', 'pexels', 'pixabay', 'wikimedia']

        images_needed = limit
        per_source = max(3, limit // len(search_order))

        for source_name in search_order:
            if images_needed <= 0:
                break

            if source_name not in self.scrapers:
                continue

            scraper = self.scrapers[source_name]
            images = scraper.search_images(query, limit=per_source)

            all_images.extend(images)
            images_needed -= len(images)

            time.sleep(0.5)

        # Return up to limit
        return all_images[:limit]

    def save_images_to_db(self, images: List[Dict[str, Any]], location: str = None):
        """Save image metadata to database"""
        for image in images:
            image_data = {
                'image_url': image['image_url'],
                'source': image['source'],
                'keywords': image.get('keywords', ''),
                'location': location or '',
                'attribution': image.get('attribution', ''),
                'width': image.get('width', 0),
                'height': image.get('height', 0)
            }
            db.add_image(image_data)


# Singleton instance
image_search = MultiSourceImageSearch()
