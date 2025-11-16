"""
WordPress Publisher - Publish articles with images to WordPress
"""
import requests
from typing import Dict, Any, Optional, List
import base64
from datetime import datetime
import re
from io import BytesIO

from config.settings import settings
from database.models import db


class WordPressPublisher:
    """Publish articles to WordPress using REST API"""

    def __init__(self, site_url: str = None, username: str = None,
                 app_password: str = None):
        self.site_url = (site_url or settings.WORDPRESS_URL).rstrip('/')
        self.username = username or settings.WORDPRESS_USERNAME
        self.app_password = app_password or settings.WORDPRESS_APP_PASSWORD

        # REST API endpoints
        self.api_base = f"{self.site_url}/wp-json/wp/v2"
        self.posts_endpoint = f"{self.api_base}/posts"
        self.media_endpoint = f"{self.api_base}/media"
        self.categories_endpoint = f"{self.api_base}/categories"

        # Setup authentication
        if self.username and self.app_password:
            credentials = f"{self.username}:{self.app_password}"
            token = base64.b64encode(credentials.encode()).decode()
            self.headers = {
                "Authorization": f"Basic {token}",
                "Content-Type": "application/json"
            }
        else:
            self.headers = {}

    def is_configured(self) -> bool:
        """Check if WordPress is properly configured"""
        return bool(self.site_url and self.username and self.app_password)

    def test_connection(self) -> Dict[str, Any]:
        """Test WordPress connection"""
        if not self.is_configured():
            return {
                'success': False,
                'error': 'WordPress not configured'
            }

        try:
            # Try to get site info
            response = requests.get(
                f"{self.site_url}/wp-json",
                timeout=10
            )

            if response.status_code == 200:
                # Test authentication by getting posts
                auth_test = requests.get(
                    self.posts_endpoint,
                    headers=self.headers,
                    params={'per_page': 1},
                    timeout=10
                )

                if auth_test.status_code == 200:
                    return {
                        'success': True,
                        'message': 'WordPress connection successful',
                        'site_url': self.site_url
                    }
                else:
                    return {
                        'success': False,
                        'error': f'Authentication failed: {auth_test.status_code}'
                    }
            else:
                return {
                    'success': False,
                    'error': f'Cannot connect to WordPress: {response.status_code}'
                }

        except Exception as e:
            return {
                'success': False,
                'error': f'Connection error: {str(e)}'
            }

    def upload_image(self, image_url: str, title: str = None) -> Optional[int]:
        """
        Upload image to WordPress media library

        Returns: WordPress media ID or None
        """
        if not self.is_configured():
            return None

        try:
            # Download image
            img_response = requests.get(image_url, timeout=15)
            if img_response.status_code != 200:
                db.add_log("ERROR", "WordPressPublisher",
                         f"Failed to download image: {img_response.status_code}",
                         f"URL: {image_url}")
                return None

            # Get filename from URL or use default
            filename = image_url.split('/')[-1].split('?')[0]
            if not filename or '.' not in filename:
                filename = f"image_{datetime.now().timestamp()}.jpg"

            # Prepare upload
            files = {
                'file': (filename, BytesIO(img_response.content), img_response.headers.get('content-type', 'image/jpeg'))
            }

            upload_headers = {
                "Authorization": self.headers["Authorization"]
            }

            if title:
                upload_headers['Content-Disposition'] = f'attachment; filename="{filename}"'

            # Upload to WordPress
            response = requests.post(
                self.media_endpoint,
                headers=upload_headers,
                files=files,
                timeout=30
            )

            if response.status_code == 201:
                media_data = response.json()
                media_id = media_data.get('id')

                db.add_log("INFO", "WordPressPublisher",
                         f"Image uploaded successfully: {media_id}",
                         f"URL: {image_url}")

                return media_id
            else:
                db.add_log("ERROR", "WordPressPublisher",
                         f"Image upload failed: {response.status_code}",
                         f"Response: {response.text}")
                return None

        except Exception as e:
            db.add_log("ERROR", "WordPressPublisher",
                     f"Image upload error: {str(e)}",
                     f"URL: {image_url}")
            return None

    def get_or_create_category(self, category_name: str) -> Optional[int]:
        """Get or create WordPress category"""
        if not self.is_configured():
            return None

        try:
            # Search for existing category
            response = requests.get(
                self.categories_endpoint,
                headers=self.headers,
                params={'search': category_name},
                timeout=10
            )

            if response.status_code == 200:
                categories = response.json()
                for cat in categories:
                    if cat['name'].lower() == category_name.lower():
                        return cat['id']

            # Create new category
            create_response = requests.post(
                self.categories_endpoint,
                headers=self.headers,
                json={'name': category_name},
                timeout=10
            )

            if create_response.status_code == 201:
                return create_response.json()['id']

            return None

        except Exception as e:
            db.add_log("ERROR", "WordPressPublisher",
                     f"Category error: {str(e)}",
                     f"Category: {category_name}")
            return None

    def publish_article(self, article_id: int,
                       status: str = 'publish',
                       schedule_date: str = None) -> Dict[str, Any]:
        """
        Publish article to WordPress

        Args:
            article_id: Database article ID
            status: 'publish', 'draft', or 'future' (for scheduling)
            schedule_date: ISO format date for scheduling (requires status='future')
        """
        if not self.is_configured():
            return {
                'success': False,
                'error': 'WordPress not configured'
            }

        # Get article from database
        conn = db.get_connection()
        article = conn.execute(
            "SELECT * FROM generated_articles WHERE id = ?",
            (article_id,)
        ).fetchone()
        conn.close()

        if not article:
            return {
                'success': False,
                'error': 'Article not found'
            }

        article = dict(article)

        try:
            # Extract images from content
            content = article['content']
            image_pattern = r'!\[([^\]]*)\]\(([^\)]+)\)'
            images = re.findall(image_pattern, content)

            # Upload images and replace URLs with WordPress media
            uploaded_images = []
            for alt_text, image_url in images:
                media_id = self.upload_image(image_url, alt_text)

                if media_id:
                    uploaded_images.append({
                        'media_id': media_id,
                        'original_url': image_url,
                        'alt_text': alt_text
                    })

                    # Get WordPress image URL
                    media_response = requests.get(
                        f"{self.media_endpoint}/{media_id}",
                        headers=self.headers,
                        timeout=10
                    )

                    if media_response.status_code == 200:
                        wp_image_url = media_response.json()['source_url']
                        # Replace in content
                        content = content.replace(image_url, wp_image_url)

            # Convert markdown to HTML (basic conversion)
            html_content = self._markdown_to_html(content)

            # Get category ID
            category_id = None
            if article['category']:
                category_id = self.get_or_create_category(article['category'])

            # Prepare post data
            post_data = {
                'title': article['title'],
                'content': html_content,
                'status': status,
                'excerpt': self._generate_excerpt(article['content'])
            }

            if category_id:
                post_data['categories'] = [category_id]

            if schedule_date and status == 'future':
                post_data['date'] = schedule_date

            # Set featured image if available
            if uploaded_images:
                post_data['featured_media'] = uploaded_images[0]['media_id']

            # Publish post
            response = requests.post(
                self.posts_endpoint,
                headers=self.headers,
                json=post_data,
                timeout=30
            )

            if response.status_code == 201:
                wp_post = response.json()
                wp_post_id = wp_post['id']
                wp_post_url = wp_post['link']

                # Update article in database
                db.update_article_status(
                    article_id,
                    status='published',
                    wordpress_post_id=wp_post_id
                )

                db.add_log("INFO", "WordPressPublisher",
                         f"Article published successfully: {wp_post_id}",
                         f"Title: {article['title']}")

                return {
                    'success': True,
                    'wordpress_post_id': wp_post_id,
                    'wordpress_url': wp_post_url,
                    'images_uploaded': len(uploaded_images),
                    'status': status
                }
            else:
                error_msg = f"Publishing failed: {response.status_code}"
                db.add_log("ERROR", "WordPressPublisher",
                         error_msg, response.text)

                return {
                    'success': False,
                    'error': error_msg,
                    'details': response.text
                }

        except Exception as e:
            error_msg = f"Publishing error: {str(e)}"
            db.add_log("ERROR", "WordPressPublisher",
                     error_msg, f"Article ID: {article_id}")

            return {
                'success': False,
                'error': error_msg
            }

    def _markdown_to_html(self, content: str) -> str:
        """Basic markdown to HTML conversion"""
        html = content

        # Headers
        html = re.sub(r'^### (.+)$', r'<h3>\1</h3>', html, flags=re.MULTILINE)
        html = re.sub(r'^## (.+)$', r'<h2>\1</h2>', html, flags=re.MULTILINE)
        html = re.sub(r'^# (.+)$', r'<h1>\1</h1>', html, flags=re.MULTILINE)

        # Bold
        html = re.sub(r'\*\*(.+?)\*\*', r'<strong>\1</strong>', html)
        html = re.sub(r'__(.+?)__', r'<strong>\1</strong>', html)

        # Italic
        html = re.sub(r'\*(.+?)\*', r'<em>\1</em>', html)
        html = re.sub(r'_(.+?)_', r'<em>\1</em>', html)

        # Images (already processed)
        html = re.sub(r'!\[([^\]]*)\]\(([^\)]+)\)',
                     r'<img src="\2" alt="\1" />', html)

        # Links
        html = re.sub(r'\[([^\]]+)\]\(([^\)]+)\)',
                     r'<a href="\2">\1</a>', html)

        # Line breaks
        html = html.replace('\n\n', '</p><p>')
        html = '<p>' + html + '</p>'

        # Lists
        html = re.sub(r'<p>([•\-\*])', r'<ul><li>', html)
        html = re.sub(r'([•\-\*].+?)</p>', r'\1</li></ul>', html)

        return html

    def _generate_excerpt(self, content: str, max_length: int = 160) -> str:
        """Generate excerpt from content"""
        # Remove markdown syntax
        text = re.sub(r'[#\*_\[\]\(\)]', '', content)
        # Remove image placeholders
        text = re.sub(r'!\[.*?\]\(.*?\)', '', text)
        # Get first paragraph
        paragraphs = text.split('\n\n')
        excerpt = paragraphs[0] if paragraphs else text

        if len(excerpt) > max_length:
            excerpt = excerpt[:max_length].rsplit(' ', 1)[0] + '...'

        return excerpt


# Singleton instance
wordpress_publisher = WordPressPublisher()
