"""
ChromaDB Vector Store for semantic search of tourism content
"""
import chromadb
from chromadb.config import Settings
from typing import List, Dict, Any, Optional
from datetime import datetime
import hashlib

from config.settings import settings


class VectorStore:
    """ChromaDB manager for vector storage and semantic search"""

    def __init__(self, persist_directory: str = None):
        self.persist_directory = persist_directory or settings.CHROMA_DB_PATH

        # Initialize ChromaDB client
        self.client = chromadb.Client(Settings(
            persist_directory=self.persist_directory,
            anonymized_telemetry=False
        ))

        # Create or get collections
        self.posts_collection = self.client.get_or_create_collection(
            name="facebook_posts",
            metadata={"description": "Facebook posts from tourism groups"}
        )

        self.tips_collection = self.client.get_or_create_collection(
            name="tourism_tips",
            metadata={"description": "General tourism tips and recommendations"}
        )

    def _generate_id(self, content: str) -> str:
        """Generate unique ID for content"""
        return hashlib.md5(content.encode()).hexdigest()

    # ============================================
    # Add Content
    # ============================================

    def add_post(self, post_data: Dict[str, Any]) -> str:
        """Add Facebook post to vector store"""
        content = post_data.get('content', '')
        post_id = post_data.get('post_id', self._generate_id(content))

        # Prepare metadata
        metadata = {
            'post_id': post_id,
            'group_url': post_data.get('group_url', ''),
            'author': post_data.get('author', ''),
            'posted_date': post_data.get('posted_date', ''),
            'location': post_data.get('location', ''),
            'category': post_data.get('category', 'general'),
            'likes': post_data.get('likes', 0),
            'comments': post_data.get('comments', 0),
            'shares': post_data.get('shares', 0),
            'has_images': post_data.get('has_images', False),
            'scraped_at': datetime.now().isoformat()
        }

        # Add to collection
        try:
            self.posts_collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[post_id]
            )
            return post_id
        except Exception as e:
            print(f"Error adding post to vector store: {e}")
            return None

    def add_posts_batch(self, posts: List[Dict[str, Any]]) -> List[str]:
        """Add multiple posts in batch"""
        documents = []
        metadatas = []
        ids = []

        for post_data in posts:
            content = post_data.get('content', '')
            if not content:
                continue

            post_id = post_data.get('post_id', self._generate_id(content))

            metadata = {
                'post_id': post_id,
                'group_url': post_data.get('group_url', ''),
                'author': post_data.get('author', ''),
                'posted_date': post_data.get('posted_date', ''),
                'location': post_data.get('location', ''),
                'category': post_data.get('category', 'general'),
                'likes': post_data.get('likes', 0),
                'comments': post_data.get('comments', 0),
                'shares': post_data.get('shares', 0),
                'has_images': post_data.get('has_images', False),
                'scraped_at': datetime.now().isoformat()
            }

            documents.append(content)
            metadatas.append(metadata)
            ids.append(post_id)

        try:
            self.posts_collection.add(
                documents=documents,
                metadatas=metadatas,
                ids=ids
            )
            return ids
        except Exception as e:
            print(f"Error adding posts batch to vector store: {e}")
            return []

    def add_tip(self, tip_data: Dict[str, Any]) -> str:
        """Add tourism tip to vector store"""
        content = tip_data.get('content', '')
        tip_id = tip_data.get('tip_id', self._generate_id(content))

        metadata = {
            'tip_id': tip_id,
            'category': tip_data.get('category', 'general'),
            'location': tip_data.get('location', ''),
            'tip_type': tip_data.get('tip_type', 'general'),
            'source': tip_data.get('source', 'manual'),
            'created_at': datetime.now().isoformat()
        }

        try:
            self.tips_collection.add(
                documents=[content],
                metadatas=[metadata],
                ids=[tip_id]
            )
            return tip_id
        except Exception as e:
            print(f"Error adding tip to vector store: {e}")
            return None

    # ============================================
    # Semantic Search
    # ============================================

    def search_posts(self, query: str, n_results: int = 10,
                     location: str = None, category: str = None) -> List[Dict[str, Any]]:
        """Search posts by semantic similarity"""
        where_filter = {}

        if location:
            where_filter['location'] = location
        if category:
            where_filter['category'] = category

        try:
            results = self.posts_collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None
            )

            # Format results
            posts = []
            if results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    posts.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })

            return posts
        except Exception as e:
            print(f"Error searching posts: {e}")
            return []

    def search_tips(self, query: str, n_results: int = 5,
                   category: str = None, tip_type: str = None) -> List[Dict[str, Any]]:
        """Search tips by semantic similarity"""
        where_filter = {}

        if category:
            where_filter['category'] = category
        if tip_type:
            where_filter['tip_type'] = tip_type

        try:
            results = self.tips_collection.query(
                query_texts=[query],
                n_results=n_results,
                where=where_filter if where_filter else None
            )

            # Format results
            tips = []
            if results['documents'] and len(results['documents']) > 0:
                for i, doc in enumerate(results['documents'][0]):
                    tips.append({
                        'content': doc,
                        'metadata': results['metadatas'][0][i],
                        'distance': results['distances'][0][i] if 'distances' in results else None
                    })

            return tips
        except Exception as e:
            print(f"Error searching tips: {e}")
            return []

    def search_by_location(self, location: str, query: str = None,
                          n_results: int = 20) -> List[Dict[str, Any]]:
        """Search posts for specific location"""
        if query:
            return self.search_posts(query, n_results=n_results, location=location)
        else:
            # Get all posts for location
            try:
                results = self.posts_collection.get(
                    where={"location": location},
                    limit=n_results
                )

                posts = []
                if results['documents']:
                    for i, doc in enumerate(results['documents']):
                        posts.append({
                            'content': doc,
                            'metadata': results['metadatas'][i]
                        })
                return posts
            except Exception as e:
                print(f"Error searching by location: {e}")
                return []

    def search_by_category(self, category: str, query: str = None,
                          n_results: int = 20) -> List[Dict[str, Any]]:
        """Search posts by category (restaurants, hotels, beaches, etc.)"""
        if query:
            return self.search_posts(query, n_results=n_results, category=category)
        else:
            try:
                results = self.posts_collection.get(
                    where={"category": category},
                    limit=n_results
                )

                posts = []
                if results['documents']:
                    for i, doc in enumerate(results['documents']):
                        posts.append({
                            'content': doc,
                            'metadata': results['metadatas'][i]
                        })
                return posts
            except Exception as e:
                print(f"Error searching by category: {e}")
                return []

    # ============================================
    # Stats & Management
    # ============================================

    def get_stats(self) -> Dict[str, Any]:
        """Get vector store statistics"""
        return {
            'total_posts': self.posts_collection.count(),
            'total_tips': self.tips_collection.count(),
            'persist_directory': self.persist_directory
        }

    def delete_post(self, post_id: str):
        """Delete post from vector store"""
        try:
            self.posts_collection.delete(ids=[post_id])
        except Exception as e:
            print(f"Error deleting post: {e}")

    def clear_all_posts(self):
        """Clear all posts (use with caution!)"""
        try:
            self.client.delete_collection("facebook_posts")
            self.posts_collection = self.client.get_or_create_collection(
                name="facebook_posts",
                metadata={"description": "Facebook posts from tourism groups"}
            )
        except Exception as e:
            print(f"Error clearing posts: {e}")


# Singleton instance
vector_store = VectorStore()
