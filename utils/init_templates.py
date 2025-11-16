"""
Initialize default article templates in the database
Run this once to populate default templates
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from database.models import db


def init_default_templates():
    """Initialize default article templates"""

    templates = [
        {
            'name': 'Top Restaurants',
            'type': 'restaurant',
            'prompt': """Write a comprehensive guide titled "Top {num_items} Restaurants in {location}".

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
            'example': 'Top 5 Restaurants in Rhodes'
        },
        {
            'name': 'Best Hotels',
            'type': 'hotel',
            'prompt': """Write a comprehensive guide titled "Best {num_items} Hotels in {location}".

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
            'example': 'Best 5 Hotels in Santorini'
        },
        {
            'name': 'Top Beaches',
            'type': 'beach',
            'prompt': """Write a comprehensive guide titled "Top {num_items} Beaches in {location}".

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
            'example': 'Top 5 Beaches in Crete'
        },
        {
            'name': 'Complete Travel Guide',
            'type': 'general',
            'prompt': """Write a complete travel guide to {location} covering {category}.

Based on the following local insights and recommendations:
{context}

Create a comprehensive guide that includes:
1. Introduction to {location} and why it's a great destination for {category}
2. Best time to visit
3. Top recommendations (at least {num_items} items)
4. Practical information (getting there, getting around, costs)
5. Local tips and insider information
6. Things to avoid or be aware of
7. Conclusion with final recommendations

Use [IMAGE: relevant description] placeholders where images would enhance the content.""",
            'example': 'Complete Travel Guide to Athens'
        },
        {
            'name': 'Hidden Gems',
            'type': 'attraction',
            'prompt': """Write an article titled "{num_items} Hidden Gems in {location}" focusing on {category}.

Based on the following local insights:
{context}

Create an engaging article that:
1. Introduces the concept of hidden gems in {location}
2. Lists {num_items} lesser-known spots with:
   - Name and exact location
   - What makes it special/hidden
   - Best time to visit
   - How to find it
   - What to expect
   - Insider tips
3. Includes practical advice for exploring off-the-beaten-path locations
4. Ends with encouragement to explore

Use [IMAGE: location name] placeholders after each item.""",
            'example': '7 Hidden Gems in Mykonos'
        },
        {
            'name': 'Local Food Guide',
            'type': 'restaurant',
            'prompt': """Write a local food guide titled "What to Eat in {location}: A Foodie's Guide".

Based on the following local insights:
{context}

Create a delicious article that:
1. Introduces the food culture of {location}
2. Lists must-try dishes and where to find them
3. Recommends {num_items} best local eateries
4. Includes:
   - Traditional dishes to try
   - Modern interpretations
   - Street food options
   - Best local products to buy
   - Food customs and etiquette
5. Provides budget tips for different dining options
6. Ends with a food lover's itinerary suggestion

Use [IMAGE: food or restaurant] placeholders throughout.""",
            'example': "What to Eat in Rhodes: A Foodie's Guide"
        },
        {
            'name': 'Day Trip Itinerary',
            'type': 'activity',
            'prompt': """Write a detailed day trip itinerary titled "Perfect Day Trip in {location}".

Based on the following local insights:
{context}

Create a helpful itinerary that:
1. Introduces {location} as a day trip destination
2. Provides a hour-by-hour schedule including:
   - Morning activities
   - Lunch recommendations
   - Afternoon activities
   - Evening options
3. Includes {num_items} must-see spots or activities
4. Provides:
   - Transportation tips
   - Budget estimates
   - What to bring
   - Alternative options for different interests
5. Ends with practical tips and alternatives

Use [IMAGE: activity or location] placeholders for key stops.""",
            'example': 'Perfect Day Trip in Lindos'
        },
        {
            'name': 'Budget Travel Guide',
            'type': 'general',
            'prompt': """Write a budget travel guide titled "How to Visit {location} on a Budget".

Based on the following local insights:
{context}

Create a money-saving guide that:
1. Introduces budget travel to {location}
2. Covers:
   - Affordable accommodation options
   - Budget-friendly restaurants
   - Free or cheap activities
   - Transportation savings
   - Best time to visit for deals
3. Lists {num_items} budget tips specific to {location}
4. Includes estimated daily budget
5. Provides money-saving hacks
6. Ends with a sample budget itinerary

Use [IMAGE: relevant budget option] placeholders.""",
            'example': 'How to Visit Santorini on a Budget'
        }
    ]

    print("Initializing default templates...")

    for template in templates:
        template_id = db.add_article_template(
            template_name=template['name'],
            template_prompt=template['prompt'],
            template_type=template['type'],
            example_output=template['example']
        )

        if template_id:
            print(f"✓ Added template: {template['name']} (ID: {template_id})")
        else:
            print(f"✗ Template already exists: {template['name']}")

    print("\nTemplate initialization complete!")


if __name__ == "__main__":
    init_default_templates()
