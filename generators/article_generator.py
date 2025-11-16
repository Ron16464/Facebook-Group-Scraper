"""
Article Generator with smart image placement and template system
"""
from typing import Dict, Any, List, Optional
import re
from datetime import datetime

from config.settings import settings
from database.models import db
from database.vector_store import vector_store
from generators.llm_providers import llm_manager
from scrapers.image_scrapers import image_search


class ArticleGenerator:
    """Generate tourism articles with smart content and image placement"""

    def __init__(self):
        self.llm = llm_manager

    def generate_article(self, article_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a complete article with content and images

        article_config should include:
        - title or topic
        - location
        - category (e.g., 'restaurants', 'hotels', 'beaches')
        - template_id (optional)
        - custom_prompt (optional)
        - num_items (for list articles, e.g., "Top 5...")
        - llm_provider (optional)
        """
        # Extract configuration
        location = article_config.get('location', '')
        category = article_config.get('category', 'general')
        template_id = article_config.get('template_id')
        custom_prompt = article_config.get('custom_prompt')
        num_items = article_config.get('num_items', 5)
        llm_provider = article_config.get('llm_provider')

        # Get relevant content from vector store
        search_query = f"{category} in {location}" if location else category
        relevant_posts = vector_store.search_posts(
            query=search_query,
            n_results=20,
            location=location if location else None,
            category=category if category != 'general' else None
        )

        # Build context from scraped content
        context = self._build_context_from_posts(relevant_posts)

        # Get or build prompt
        if template_id:
            template = db.get_connection().execute(
                "SELECT * FROM article_templates WHERE id = ?",
                (template_id,)
            ).fetchone()
            if template:
                prompt = template['template_prompt']
            else:
                prompt = custom_prompt or self._get_default_template(category)
        else:
            prompt = custom_prompt or self._get_default_template(category)

        # Format prompt with variables
        prompt = prompt.format(
            location=location,
            category=category,
            num_items=num_items,
            context=context
        )

        # Generate article content
        system_prompt = """You are an expert travel writer creating engaging, informative tourism content.
Write in a friendly, enthusiastic tone while being accurate and helpful.
Include specific details, local insights, and practical tips.
Structure the content with clear headings and sections.
Use [IMAGE: description] placeholders where images should be inserted."""

        content = self.llm.generate(
            prompt=prompt,
            system_prompt=system_prompt,
            provider=llm_provider,
            max_tokens=3000,
            temperature=0.7
        )

        if not content:
            return {
                'success': False,
                'error': 'Failed to generate article content'
            }

        # Extract title if not provided
        title = article_config.get('title')
        if not title:
            title = self._extract_title(content)

        # Find and replace image placeholders
        content_with_images = self._insert_images(
            content=content,
            location=location,
            category=category
        )

        # Extract image URLs for storage
        image_urls = self._extract_image_urls(content_with_images)

        # Save article to database
        article_data = {
            'title': title,
            'content': content_with_images,
            'location': location,
            'category': category,
            'template_id': template_id,
            'llm_provider': llm_provider or settings.DEFAULT_LLM_PROVIDER,
            'image_urls': image_urls,
            'metadata': {
                'num_items': num_items,
                'sources_used': len(relevant_posts),
                'generated_at': datetime.now().isoformat()
            },
            'status': 'draft'
        }

        article_id = db.save_article(article_data)

        return {
            'success': True,
            'article_id': article_id,
            'title': title,
            'content': content_with_images,
            'image_urls': image_urls,
            'word_count': len(content.split()),
            'sources_used': len(relevant_posts)
        }

    def _build_context_from_posts(self, posts: List[Dict[str, Any]]) -> str:
        """Build context string from relevant posts"""
        if not posts:
            return "No specific local information available. Use general knowledge."

        context_parts = []
        for i, post in enumerate(posts[:10], 1):  # Limit to top 10
            content = post['content']
            metadata = post.get('metadata', {})
            location = metadata.get('location', '')

            context_parts.append(f"{i}. {content[:300]}")
            if location:
                context_parts[-1] += f" (Location: {location})"

        return "\n\n".join(context_parts)

    def _get_default_template(self, category: str) -> str:
        """Get default article template for category"""
        templates = {
            'restaurant': """Write a comprehensive guide titled "Top {num_items} Restaurants in {location}".

Based on the following local insights and recommendations:
{context}

Create an engaging article that:
1. Has an introduction explaining why {location} is a great food destination
2. Lists {num_items} top restaurants with:
   - Name and location
   - Type of cuisine
   - Signature dishes
   - Ambiance and atmosphere
   - Price range
   - Why it's special
3. Includes practical tips for dining in {location}
4. Ends with a conclusion

Use [IMAGE: restaurant name] placeholders after each restaurant description.""",

            'hotel': """Write a comprehensive guide titled "Best {num_items} Hotels in {location}".

Based on the following local insights and recommendations:
{context}

Create an engaging article that:
1. Has an introduction about accommodations in {location}
2. Lists {num_items} top hotels with:
   - Hotel name and location
   - Type of accommodation (luxury, boutique, budget, etc.)
   - Key amenities
   - Room features
   - Nearby attractions
   - Price range
   - What makes it special
3. Includes tips for booking and best times to visit
4. Ends with a conclusion

Use [IMAGE: hotel name] placeholders after each hotel description.""",

            'beach': """Write a comprehensive guide titled "Top {num_items} Beaches in {location}".

Based on the following local insights:
{context}

Create an engaging article that:
1. Has an introduction about the beaches of {location}
2. Lists {num_items} best beaches with:
   - Beach name and location
   - Beach type (sandy, pebble, secluded, organized)
   - Water conditions
   - Facilities available
   - Activities offered
   - Best time to visit
   - How to get there
3. Includes beach safety tips and what to bring
4. Ends with a conclusion

Use [IMAGE: beach name] placeholders after each beach description.""",

            'general': """Write a comprehensive travel guide about {category} in {location}.

Based on the following local insights and recommendations:
{context}

Create an engaging article that:
1. Has an introduction explaining the topic
2. Provides detailed information organized in clear sections
3. Includes practical tips and local insights
4. Mentions specific places, prices, and logistics when relevant
5. Ends with a helpful conclusion

Use [IMAGE: relevant description] placeholders where images would enhance the content."""
        }

        return templates.get(category, templates['general'])

    def _extract_title(self, content: str) -> str:
        """Extract title from content"""
        # Look for first heading or first line
        lines = content.strip().split('\n')
        for line in lines:
            line = line.strip()
            if line:
                # Remove markdown heading symbols
                title = re.sub(r'^#+\s*', '', line)
                return title[:200]  # Limit length

        return "Travel Guide"

    def _insert_images(self, content: str, location: str, category: str) -> str:
        """Find image placeholders and insert actual image URLs"""
        # Find all [IMAGE: description] placeholders
        pattern = r'\[IMAGE:\s*([^\]]+)\]'
        placeholders = re.findall(pattern, content)

        for description in placeholders:
            # Search for relevant image
            search_query = f"{description} {location}".strip()

            # First try to find from database
            db_images = db.search_images(
                keywords=description,
                location=location,
                limit=1
            )

            if db_images:
                image = db_images[0]
                image_url = image['image_url']
                attribution = image['attribution']
            else:
                # Search from image APIs
                images = image_search.search_best_images(
                    query=search_query,
                    limit=1
                )

                if images:
                    image = images[0]
                    image_url = image['image_url']
                    attribution = image.get('attribution', '')

                    # Save to database for future use
                    image_search.save_images_to_db([image], location)
                else:
                    # No image found, skip
                    continue

            # Replace placeholder with image markdown
            alt_text = f"{description} in {location}".strip()
            image_markdown = f"\n\n![{alt_text}]({image_url})\n*{attribution}*\n\n"

            content = content.replace(
                f"[IMAGE: {description}]",
                image_markdown,
                1  # Replace only first occurrence
            )

        return content

    def _extract_image_urls(self, content: str) -> List[str]:
        """Extract all image URLs from markdown content"""
        pattern = r'!\[.*?\]\((.*?)\)'
        urls = re.findall(pattern, content)
        return urls

    def paste_article(self, pasted_content: str, article_config: Dict[str, Any]) -> Dict[str, Any]:
        """
        Combine pasted article content with recommendations and images

        This allows users to paste an existing article and enhance it with:
        - Local recommendations from scraped data
        - Relevant images
        - Additional tips
        """
        location = article_config.get('location', '')
        category = article_config.get('category', 'general')

        # Get relevant recommendations
        recommendations_query = f"tips and recommendations for {category} in {location}"
        relevant_posts = vector_store.search_posts(
            query=recommendations_query,
            n_results=10,
            location=location if location else None
        )

        # Generate recommendations section
        recommendations_prompt = f"""Based on these local insights:

{self._build_context_from_posts(relevant_posts)}

Create a "Local Tips & Recommendations" section (3-5 bullet points) to add to an article about {category} in {location}.
Be specific and practical."""

        recommendations = self.llm.generate(
            prompt=recommendations_prompt,
            max_tokens=500,
            temperature=0.7
        )

        # Combine content
        combined_content = pasted_content

        # Add recommendations section
        if recommendations:
            combined_content += f"\n\n## Local Tips & Recommendations\n\n{recommendations}"

        # Insert images
        combined_content = self._insert_images(
            content=combined_content,
            location=location,
            category=category
        )

        # Extract title
        title = article_config.get('title') or self._extract_title(combined_content)

        # Extract image URLs
        image_urls = self._extract_image_urls(combined_content)

        # Save article
        article_data = {
            'title': title,
            'content': combined_content,
            'location': location,
            'category': category,
            'llm_provider': settings.DEFAULT_LLM_PROVIDER,
            'image_urls': image_urls,
            'metadata': {
                'pasted': True,
                'sources_used': len(relevant_posts),
                'generated_at': datetime.now().isoformat()
            },
            'status': 'draft'
        }

        article_id = db.save_article(article_data)

        return {
            'success': True,
            'article_id': article_id,
            'title': title,
            'content': combined_content,
            'image_urls': image_urls,
            'word_count': len(combined_content.split())
        }


# Singleton instance
article_generator = ArticleGenerator()
