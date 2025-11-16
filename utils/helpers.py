"""
Utility functions for the Tourism Content Generator
"""
from typing import List, Dict, Any
import hashlib
from datetime import datetime
import re


def deduplicate_posts(posts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Remove duplicate posts based on content similarity

    Args:
        posts: List of post dictionaries with 'content' key

    Returns:
        List of unique posts
    """
    seen_hashes = set()
    unique_posts = []

    for post in posts:
        content = post.get('content', '')
        if not content:
            continue

        # Create hash of content
        content_hash = hashlib.md5(content.lower().strip().encode()).hexdigest()

        if content_hash not in seen_hashes:
            seen_hashes.add(content_hash)
            unique_posts.append(post)

    return unique_posts


def extract_locations_from_text(text: str) -> List[str]:
    """
    Extract location names from text
    This is a simple implementation - can be enhanced with NLP
    """
    # Common Greek locations
    common_locations = [
        'Athens', 'Thessaloniki', 'Rhodes', 'Crete', 'Santorini',
        'Mykonos', 'Corfu', 'Zakynthos', 'Paros', 'Naxos',
        'Lindos', 'Faliraki', 'Oia', 'Fira', 'Heraklion',
        'Chania', 'Rethymno', 'Kos', 'Skiathos', 'Delphi',
        'Meteora', 'Olympia', 'Nafplio', 'Monemvasia'
    ]

    found_locations = []
    text_lower = text.lower()

    for location in common_locations:
        if location.lower() in text_lower:
            found_locations.append(location)

    return list(set(found_locations))


def categorize_content_advanced(text: str) -> Dict[str, float]:
    """
    Advanced content categorization with confidence scores

    Returns:
        Dictionary of categories with confidence scores (0-1)
    """
    text_lower = text.lower()

    categories = {
        'restaurant': 0.0,
        'hotel': 0.0,
        'beach': 0.0,
        'attraction': 0.0,
        'activity': 0.0,
        'transportation': 0.0,
        'shopping': 0.0,
        'nightlife': 0.0
    }

    # Keywords with weights
    keywords = {
        'restaurant': [
            ('restaurant', 0.3), ('tavern', 0.3), ('food', 0.1),
            ('dinner', 0.2), ('lunch', 0.2), ('breakfast', 0.2),
            ('cuisine', 0.2), ('dish', 0.1), ('menu', 0.2)
        ],
        'hotel': [
            ('hotel', 0.3), ('resort', 0.3), ('accommodation', 0.3),
            ('room', 0.1), ('suite', 0.2), ('villa', 0.3),
            ('apartment', 0.2), ('booking', 0.2)
        ],
        'beach': [
            ('beach', 0.4), ('sea', 0.2), ('coast', 0.2),
            ('shore', 0.2), ('swimming', 0.2), ('sunbed', 0.1),
            ('sand', 0.1), ('bay', 0.2)
        ],
        'attraction': [
            ('museum', 0.3), ('castle', 0.3), ('monument', 0.3),
            ('temple', 0.3), ('church', 0.2), ('tour', 0.1),
            ('sightseeing', 0.3), ('archaeological', 0.3)
        ],
        'activity': [
            ('hiking', 0.3), ('diving', 0.3), ('sailing', 0.3),
            ('adventure', 0.2), ('excursion', 0.3), ('sports', 0.2),
            ('water sports', 0.3), ('cycling', 0.3)
        ],
        'transportation': [
            ('taxi', 0.3), ('bus', 0.3), ('car rental', 0.4),
            ('transfer', 0.3), ('airport', 0.2), ('ferry', 0.3),
            ('port', 0.2), ('transport', 0.2)
        ],
        'shopping': [
            ('shop', 0.2), ('market', 0.3), ('store', 0.2),
            ('shopping', 0.3), ('boutique', 0.2), ('souvenir', 0.3)
        ],
        'nightlife': [
            ('bar', 0.3), ('club', 0.3), ('nightlife', 0.4),
            ('party', 0.2), ('cocktail', 0.2), ('music', 0.1)
        ]
    }

    # Calculate scores
    for category, keyword_list in keywords.items():
        score = 0.0
        for keyword, weight in keyword_list:
            if keyword in text_lower:
                score += weight

        categories[category] = min(score, 1.0)  # Cap at 1.0

    return categories


def get_best_category(text: str) -> str:
    """Get the best matching category for text"""
    scores = categorize_content_advanced(text)
    best_category = max(scores.items(), key=lambda x: x[1])

    # Return general if confidence is too low
    if best_category[1] < 0.2:
        return 'general'

    return best_category[0]


def format_date(date_str: str) -> str:
    """
    Format date string to readable format

    Args:
        date_str: Date string in various formats

    Returns:
        Formatted date string
    """
    try:
        # Try parsing ISO format
        dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
        return dt.strftime('%B %d, %Y at %I:%M %p')
    except:
        return date_str


def clean_html(html_content: str) -> str:
    """Remove HTML tags from content"""
    clean = re.sub(r'<[^>]+>', '', html_content)
    return clean.strip()


def truncate_text(text: str, max_length: int = 100, suffix: str = '...') -> str:
    """Truncate text to maximum length"""
    if len(text) <= max_length:
        return text

    return text[:max_length].rsplit(' ', 1)[0] + suffix


def validate_url(url: str) -> bool:
    """Validate URL format"""
    url_pattern = re.compile(
        r'^https?://'  # http:// or https://
        r'(?:(?:[A-Z0-9](?:[A-Z0-9-]{0,61}[A-Z0-9])?\.)+[A-Z]{2,6}\.?|'  # domain
        r'localhost|'  # localhost
        r'\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3})'  # or IP
        r'(?::\d+)?'  # optional port
        r'(?:/?|[/?]\S+)$', re.IGNORECASE
    )
    return url_pattern.match(url) is not None


def estimate_reading_time(content: str) -> int:
    """
    Estimate reading time in minutes

    Args:
        content: Text content

    Returns:
        Estimated reading time in minutes
    """
    words = len(content.split())
    # Average reading speed: 200 words per minute
    minutes = words / 200
    return max(1, round(minutes))


def extract_keywords(text: str, limit: int = 10) -> List[str]:
    """
    Extract keywords from text
    Simple implementation - can be enhanced with NLP
    """
    # Remove common words
    stop_words = {
        'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at',
        'to', 'for', 'of', 'with', 'by', 'from', 'as', 'is',
        'was', 'are', 'been', 'be', 'have', 'has', 'had',
        'do', 'does', 'did', 'will', 'would', 'could', 'should'
    }

    # Clean and split
    words = re.findall(r'\b[a-z]{3,}\b', text.lower())

    # Filter and count
    word_freq = {}
    for word in words:
        if word not in stop_words:
            word_freq[word] = word_freq.get(word, 0) + 1

    # Sort by frequency
    sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)

    return [word for word, freq in sorted_words[:limit]]
