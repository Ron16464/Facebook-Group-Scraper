"""
Facebook Scraper Web Interface

A beautiful Streamlit web application for the Facebook Scraper API.
Run with: streamlit run app.py
"""

import streamlit as st
import json
from facebook_scraper import (
    FacebookScraper,
    APIError,
    AuthenticationError,
    NetworkError,
)

# Page configuration
st.set_page_config(
    page_title="Facebook Scraper",
    page_icon="📱",
    layout="wide",
    initial_sidebar_state="expanded",
)

# Custom CSS
st.markdown(
    """
    <style>
    .main {
        padding: 2rem;
    }
    .stAlert {
        margin-top: 1rem;
    }
    </style>
    """,
    unsafe_allow_html=True,
)


# Title and description
st.title("📱 Facebook Scraper Web Interface")
st.markdown(
    """
    Extract data from Facebook Marketplace, Pages, Posts, and Profiles using the RapidAPI Facebook Scraper.

    **Get your API key:** [RapidAPI Facebook Scraper](https://rapidapi.com/taskagi-2-taskagi-2-default/api/facebook-scraper4/)
    """
)

# Sidebar - API Configuration
with st.sidebar:
    st.header("⚙️ Configuration")

    # API Key input
    api_key = st.text_input(
        "RapidAPI Key",
        type="password",
        help="Enter your RapidAPI key for the Facebook Scraper API",
        placeholder="Your API key here...",
    )

    st.divider()

    # Method selection
    st.header("🔧 Scraper Method")
    method = st.selectbox(
        "Choose what to scrape:",
        [
            "Get Marketplace Item",
            "Search Marketplace by Location",
            "Search Marketplace by Keyword",
            "Retrieve Page Posts",
            "Get Page About Info",
            "Retrieve Post Data",
            "Retrieve Profile Photos",
            "Retrieve Profile Data",
        ],
    )

    st.divider()

    # Information section
    st.header("ℹ️ About")
    st.markdown(
        """
        **Features:**
        - 🛒 Marketplace scraping
        - 📄 Page information
        - 💬 Post engagement data
        - 👤 Profile information

        **Error Handling:**
        - Authentication errors
        - Network timeouts
        - API rate limits
        """
    )

# Main content area
col1, col2 = st.columns([1, 1])

with col1:
    st.header("📥 Input")

    # URL input
    facebook_url = st.text_input(
        "Facebook URL",
        placeholder="https://www.facebook.com/...",
        help="Enter the full Facebook URL to scrape",
    )

    # Method-specific help
    help_text = {
        "Get Marketplace Item": "Example: https://www.facebook.com/marketplace/item/1030745568732697",
        "Search Marketplace by Location": "Example: https://www.facebook.com/marketplace/category/vehicles",
        "Search Marketplace by Keyword": "Example: https://www.facebook.com/marketplace/search?query=laptop",
        "Retrieve Page Posts": "Example: https://www.facebook.com/zippo",
        "Get Page About Info": "Example: https://www.facebook.com/zippo",
        "Retrieve Post Data": "Example: https://www.facebook.com/user/posts/123456789",
        "Retrieve Profile Photos": "Example: https://www.facebook.com/username",
        "Retrieve Profile Data": "Example: https://www.facebook.com/username",
    }

    st.info(f"💡 {help_text[method]}")

    # Scrape button
    scrape_button = st.button(
        "🚀 Scrape Data", type="primary", use_container_width=True
    )

with col2:
    st.header("📤 Output")

    # Results container
    results_container = st.container()

# Processing
if scrape_button:
    if not api_key:
        st.error("⚠️ Please enter your RapidAPI key in the sidebar.")
    elif not facebook_url:
        st.error("⚠️ Please enter a Facebook URL.")
    else:
        with results_container:
            with st.spinner("🔄 Scraping data..."):
                try:
                    # Initialize scraper
                    scraper = FacebookScraper(api_key)

                    # Call appropriate method
                    method_map = {
                        "Get Marketplace Item": scraper.get_marketplace_item,
                        "Search Marketplace by Location": scraper.search_marketplace_by_location,
                        "Search Marketplace by Keyword": scraper.search_marketplace_by_keyword,
                        "Retrieve Page Posts": scraper.retrieve_page_posts,
                        "Get Page About Info": scraper.get_page_about_info,
                        "Retrieve Post Data": scraper.retrieve_post_data,
                        "Retrieve Profile Photos": scraper.retrieve_profile_photos,
                        "Retrieve Profile Data": scraper.retrieve_profile_data,
                    }

                    result = method_map[method](facebook_url)

                    # Display success
                    st.success("✅ Data scraped successfully!")

                    # Display formatted JSON
                    st.subheader("📊 Results")
                    st.json(result)

                    # Download button
                    json_str = json.dumps(result, indent=2)
                    st.download_button(
                        label="💾 Download JSON",
                        data=json_str,
                        file_name="facebook_scraper_results.json",
                        mime="application/json",
                    )

                except AuthenticationError as e:
                    st.error(f"🔐 Authentication Error: {str(e)}")
                    st.info("Please check your RapidAPI key and subscription status.")

                except NetworkError as e:
                    st.error(f"🌐 Network Error: {str(e)}")
                    st.info("Please check your internet connection and try again.")

                except APIError as e:
                    st.error(f"⚠️ API Error: {str(e)}")
                    st.info(
                        "The API returned an error. Please check your URL and try again."
                    )

                except Exception as e:
                    st.error(f"❌ Unexpected Error: {str(e)}")
                    st.info("An unexpected error occurred. Please try again.")

# Footer
st.divider()
st.markdown(
    """
    <div style='text-align: center; color: #666;'>
        <p>Built with ❤️ using Streamlit |
        <a href='https://github.com/yourusername/facebook-scraper' target='_blank'>GitHub</a> |
        <a href='https://rapidapi.com/taskagi-2-taskagi-2-default/api/facebook-scraper4/' target='_blank'>API Docs</a>
        </p>
    </div>
    """,
    unsafe_allow_html=True,
)
