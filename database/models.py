"""
Database models for Tourism Content Generator
SQLite for structured data, ChromaDB for vector storage
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path
import json

from config.settings import settings


class Database:
    """SQLite database manager for structured data"""

    def __init__(self, db_path: str = None):
        self.db_path = db_path or settings.SQLITE_DB_PATH
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        self.init_database()

    def get_connection(self):
        """Get database connection"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        return conn

    def init_database(self):
        """Initialize database schema"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Facebook pages table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS facebook_pages (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_url TEXT UNIQUE NOT NULL,
                page_name TEXT,
                page_category TEXT,
                description TEXT,
                is_active INTEGER DEFAULT 1,
                last_scraped TIMESTAMP,
                total_posts_scraped INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Scraped posts metadata table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS posts_metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                post_id TEXT UNIQUE NOT NULL,
                page_id INTEGER,
                post_url TEXT,
                author TEXT,
                posted_date TIMESTAMP,
                engagement_likes INTEGER DEFAULT 0,
                engagement_comments INTEGER DEFAULT 0,
                engagement_shares INTEGER DEFAULT 0,
                has_images INTEGER DEFAULT 0,
                image_count INTEGER DEFAULT 0,
                category TEXT,
                scraped_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES facebook_pages(id)
            )
        """)

        # Images table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS images (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                image_url TEXT UNIQUE NOT NULL,
                source TEXT NOT NULL,
                post_id TEXT,
                keywords TEXT,
                location TEXT,
                attribution TEXT,
                downloaded INTEGER DEFAULT 0,
                local_path TEXT,
                width INTEGER,
                height INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (post_id) REFERENCES posts_metadata(post_id)
            )
        """)

        # LLM providers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS llm_providers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                provider_name TEXT UNIQUE NOT NULL,
                api_key_encrypted TEXT,
                model_name TEXT,
                is_active INTEGER DEFAULT 1,
                is_default INTEGER DEFAULT 0,
                tokens_used INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Image sources table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS image_sources (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                source_name TEXT UNIQUE NOT NULL,
                api_key_encrypted TEXT,
                is_active INTEGER DEFAULT 1,
                requests_made INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Article templates table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS article_templates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                template_name TEXT UNIQUE NOT NULL,
                template_prompt TEXT NOT NULL,
                template_type TEXT,
                example_output TEXT,
                is_active INTEGER DEFAULT 1,
                usage_count INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Generated articles table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS generated_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                content TEXT NOT NULL,
                location TEXT,
                category TEXT,
                template_id INTEGER,
                llm_provider TEXT,
                image_urls TEXT,
                metadata TEXT,
                status TEXT DEFAULT 'draft',
                wordpress_post_id INTEGER,
                published_at TIMESTAMP,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (template_id) REFERENCES article_templates(id)
            )
        """)

        # Scraping schedule table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS scraping_schedule (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                page_id INTEGER,
                frequency TEXT,
                last_run TIMESTAMP,
                next_run TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (page_id) REFERENCES facebook_pages(id)
            )
        """)

        # System logs table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS system_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                log_level TEXT,
                module TEXT,
                message TEXT,
                details TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        conn.commit()
        conn.close()

    # ============================================
    # Facebook Pages Operations
    # ============================================

    def add_facebook_page(self, page_url: str, page_name: str = None,
                          page_category: str = None, description: str = None) -> int:
        """Add a new Facebook page to scrape"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO facebook_pages (page_url, page_name, page_category, description)
                VALUES (?, ?, ?, ?)
            """, (page_url, page_name, page_category, description))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def get_facebook_pages(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all Facebook pages"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM facebook_pages"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY created_at DESC"

        cursor.execute(query)
        pages = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return pages

    def update_facebook_page(self, page_id: int, **kwargs):
        """Update Facebook page details"""
        conn = self.get_connection()
        cursor = conn.cursor()

        fields = []
        values = []
        for key, value in kwargs.items():
            fields.append(f"{key} = ?")
            values.append(value)

        fields.append("updated_at = CURRENT_TIMESTAMP")
        values.append(page_id)

        query = f"UPDATE facebook_pages SET {', '.join(fields)} WHERE id = ?"
        cursor.execute(query, values)
        conn.commit()
        conn.close()

    def delete_facebook_page(self, page_id: int):
        """Delete a Facebook page"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM facebook_pages WHERE id = ?", (page_id,))
        conn.commit()
        conn.close()

    # ============================================
    # Posts Metadata Operations
    # ============================================

    def add_post_metadata(self, post_data: Dict[str, Any]) -> int:
        """Add post metadata"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO posts_metadata
                (post_id, page_id, post_url, author, posted_date, engagement_likes,
                 engagement_comments, engagement_shares, has_images, image_count, category)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                post_data.get('post_id'),
                post_data.get('page_id'),
                post_data.get('post_url'),
                post_data.get('author'),
                post_data.get('posted_date'),
                post_data.get('engagement_likes', 0),
                post_data.get('engagement_comments', 0),
                post_data.get('engagement_shares', 0),
                post_data.get('has_images', 0),
                post_data.get('image_count', 0),
                post_data.get('category')
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    # ============================================
    # Images Operations
    # ============================================

    def add_image(self, image_data: Dict[str, Any]) -> int:
        """Add image metadata"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO images
                (image_url, source, post_id, keywords, location, attribution,
                 width, height, local_path)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                image_data.get('image_url'),
                image_data.get('source'),
                image_data.get('post_id'),
                image_data.get('keywords'),
                image_data.get('location'),
                image_data.get('attribution'),
                image_data.get('width'),
                image_data.get('height'),
                image_data.get('local_path')
            ))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def search_images(self, keywords: str = None, location: str = None,
                     source: str = None, limit: int = 20) -> List[Dict[str, Any]]:
        """Search images by keywords, location, or source"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM images WHERE 1=1"
        params = []

        if keywords:
            query += " AND keywords LIKE ?"
            params.append(f"%{keywords}%")

        if location:
            query += " AND location LIKE ?"
            params.append(f"%{location}%")

        if source:
            query += " AND source = ?"
            params.append(source)

        query += f" ORDER BY created_at DESC LIMIT {limit}"

        cursor.execute(query, params)
        images = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return images

    # ============================================
    # Article Templates Operations
    # ============================================

    def add_article_template(self, template_name: str, template_prompt: str,
                           template_type: str = None, example_output: str = None) -> int:
        """Add article template"""
        conn = self.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("""
                INSERT INTO article_templates
                (template_name, template_prompt, template_type, example_output)
                VALUES (?, ?, ?, ?)
            """, (template_name, template_prompt, template_type, example_output))
            conn.commit()
            return cursor.lastrowid
        except sqlite3.IntegrityError:
            return None
        finally:
            conn.close()

    def get_article_templates(self, active_only: bool = True) -> List[Dict[str, Any]]:
        """Get all article templates"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM article_templates"
        if active_only:
            query += " WHERE is_active = 1"
        query += " ORDER BY usage_count DESC, created_at DESC"

        cursor.execute(query)
        templates = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return templates

    # ============================================
    # Generated Articles Operations
    # ============================================

    def save_article(self, article_data: Dict[str, Any]) -> int:
        """Save generated article"""
        conn = self.get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO generated_articles
            (title, content, location, category, template_id, llm_provider,
             image_urls, metadata, status)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            article_data.get('title'),
            article_data.get('content'),
            article_data.get('location'),
            article_data.get('category'),
            article_data.get('template_id'),
            article_data.get('llm_provider'),
            json.dumps(article_data.get('image_urls', [])),
            json.dumps(article_data.get('metadata', {})),
            article_data.get('status', 'draft')
        ))
        conn.commit()
        article_id = cursor.lastrowid
        conn.close()
        return article_id

    def get_articles(self, status: str = None, limit: int = 50) -> List[Dict[str, Any]]:
        """Get generated articles"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM generated_articles"
        params = []

        if status:
            query += " WHERE status = ?"
            params.append(status)

        query += f" ORDER BY created_at DESC LIMIT {limit}"

        cursor.execute(query, params)
        articles = [dict(row) for row in cursor.fetchall()]

        # Parse JSON fields
        for article in articles:
            article['image_urls'] = json.loads(article['image_urls']) if article['image_urls'] else []
            article['metadata'] = json.loads(article['metadata']) if article['metadata'] else {}

        conn.close()
        return articles

    def update_article_status(self, article_id: int, status: str,
                            wordpress_post_id: int = None):
        """Update article status"""
        conn = self.get_connection()
        cursor = conn.cursor()

        if status == 'published':
            cursor.execute("""
                UPDATE generated_articles
                SET status = ?, wordpress_post_id = ?, published_at = CURRENT_TIMESTAMP,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, wordpress_post_id, article_id))
        else:
            cursor.execute("""
                UPDATE generated_articles
                SET status = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (status, article_id))

        conn.commit()
        conn.close()

    # ============================================
    # System Logs Operations
    # ============================================

    def add_log(self, log_level: str, module: str, message: str, details: str = None):
        """Add system log"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO system_logs (log_level, module, message, details)
            VALUES (?, ?, ?, ?)
        """, (log_level, module, message, details))
        conn.commit()
        conn.close()

    def get_logs(self, log_level: str = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Get system logs"""
        conn = self.get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM system_logs"
        params = []

        if log_level:
            query += " WHERE log_level = ?"
            params.append(log_level)

        query += f" ORDER BY created_at DESC LIMIT {limit}"

        cursor.execute(query, params)
        logs = [dict(row) for row in cursor.fetchall()]
        conn.close()
        return logs


# Singleton instance
db = Database()
