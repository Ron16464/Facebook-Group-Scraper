"""
Tourism Content Generator - Streamlit Dashboard
Main UI for scraping, generating, and publishing tourism content
"""
import streamlit as st
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from config.settings import settings
from database.models import db
from database.vector_store import vector_store
from scrapers.facebook_scraper import scraper
from scrapers.image_scrapers import image_search
from generators.llm_providers import llm_manager
from generators.article_generator import article_generator
from publishers.wordpress_publisher import wordpress_publisher
import pandas as pd
from datetime import datetime
import json


# Page config
st.set_page_config(
    page_title="Tourism Content Generator",
    page_icon="🏖️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 1rem;
    }
    .sub-header {
        font-size: 1.2rem;
        color: #666;
        margin-bottom: 2rem;
    }
    .stat-box {
        background-color: #f0f2f6;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #1E88E5;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #28a745;
    }
    .error-box {
        background-color: #f8d7da;
        padding: 1rem;
        border-radius: 0.5rem;
        border-left: 4px solid #dc3545;
    }
</style>
""", unsafe_allow_html=True)


# Initialize session state
if 'group' not in st.session_state:
    st.session_state.group = 'Dashboard'


def show_dashboard():
    """Main dashboard with statistics"""
    st.markdown('<div class="main-header">🏖️ Tourism Content Generator</div>', unsafe_allow_html=True)
    st.markdown('<div class="sub-header">Scrape, Generate, and Publish Tourism Content</div>', unsafe_allow_html=True)

    # Validate configuration
    config_status = settings.validate_config()

    if not config_status['valid']:
        st.warning("⚠️ **Configuration Issues Detected**")
        for issue in config_status['issues']:
            st.write(f"• {issue}")
        st.info("👉 Go to **Settings** tab to configure API keys")
        st.divider()

    # Stats
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        groups_count = len(db.get_facebook_groups())
        st.metric("Facebook Groups", groups_count)
        st.markdown('</div>', unsafe_allow_html=True)

    with col2:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        stats = vector_store.get_stats()
        st.metric("Scraped Posts", stats['total_posts'])
        st.markdown('</div>', unsafe_allow_html=True)

    with col3:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        articles = db.get_articles(limit=1000)
        st.metric("Generated Articles", len(articles))
        st.markdown('</div>', unsafe_allow_html=True)

    with col4:
        st.markdown('<div class="stat-box">', unsafe_allow_html=True)
        published = [a for a in articles if a['status'] == 'published']
        st.metric("Published Articles", len(published))
        st.markdown('</div>', unsafe_allow_html=True)

    st.divider()

    # Recent Activity
    st.subheader("📋 Recent Activity")

    col1, col2 = st.columns(2)

    with col1:
        st.write("**Recent Articles**")
        recent_articles = db.get_articles(limit=5)
        if recent_articles:
            for article in recent_articles:
                status_icon = "✅" if article['status'] == 'published' else "📝"
                st.write(f"{status_icon} {article['title'][:50]}...")
        else:
            st.info("No articles yet")

    with col2:
        st.write("**System Logs**")
        logs = db.get_logs(limit=5)
        if logs:
            for log in logs:
                level_icon = {"INFO": "ℹ️", "WARNING": "⚠️", "ERROR": "❌"}.get(log['log_level'], "•")
                st.write(f"{level_icon} {log['message']}")
        else:
            st.info("No recent logs")


def show_facebook_groups():
    """Manage Facebook groups to scrape"""
    st.header("📱 Facebook Groups Management")

    # Tabs for different actions
    tab1, tab2, tab3 = st.tabs(["📋 View Pages", "➕ Add Page", "🔄 Scrape Content"])

    with tab1:
        st.subheader("Configured Facebook Groups")

        groups = db.get_facebook_groups(active_only=False)

        if groups:
            for group in groups:
                with st.expander(f"{'✅' if group['is_active'] else '⏸️'} {group['group_name'] or group['group_url']}", expanded=False):
                    col1, col2 = st.columns([3, 1])

                    with col1:
                        st.write(f"**URL:** {group['group_url']}")
                        st.write(f"**Category:** {group['group_category'] or 'Not set'}")
                        st.write(f"**Description:** {group['description'] or 'No description'}")
                        st.write(f"**Posts Scraped:** {group['total_posts_scraped']}")
                        st.write(f"**Last Scraped:** {group['last_scraped'] or 'Never'}")

                    with col2:
                        if st.button("🗑️ Delete", key=f"delete_{group['id']}"):
                            db.delete_facebook_group(group['id'])
                            st.success("Page deleted!")
                            st.rerun()

                        if group['is_active']:
                            if st.button("⏸️ Deactivate", key=f"deactivate_{group['id']}"):
                                db.update_facebook_group(group['id'], is_active=0)
                                st.rerun()
                        else:
                            if st.button("▶️ Activate", key=f"activate_{group['id']}"):
                                db.update_facebook_group(group['id'], is_active=1)
                                st.rerun()
        else:
            st.info("No Facebook groups configured yet. Add one in the 'Add Page' tab!")

    with tab2:
        st.subheader("Add New Facebook Page")

        with st.form("add_page_form"):
            group_url = st.text_input("Facebook Group URL*", placeholder="https://www.facebook.com/groups/YourGroup")
            group_name = st.text_input("Group Name", placeholder="e.g., Rhodes Tourism")
            group_category = st.selectbox("Category", [
                "general", "restaurant", "hotel", "beach", "attraction",
                "activity", "transportation", "shopping"
            ])
            description = st.text_area("Description (optional)")

            submit = st.form_submit_button("➕ Add Page")

            if submit:
                if not group_url:
                    st.error("Page URL is required!")
                else:
                    group_id = db.add_facebook_group(
                        group_url=group_url,
                        group_name=group_name if group_name else None,
                        group_category=group_category,
                        description=description if description else None
                    )

                    if group_id:
                        st.success(f"✅ Group added successfully! (ID: {group_id})")
                        st.balloons()
                    else:
                        st.error("❌ Failed to add group. It may already exist.")

    with tab3:
        st.subheader("Scrape Facebook Groups")

        if not settings.RAPIDAPI_KEY:
            st.error("❌ RapidAPI key not configured! Go to Settings to add it.")
        else:
            groups = db.get_facebook_groups(active_only=True)

            if not groups:
                st.warning("No active groups to scrape. Add groups first!")
            else:
                st.write(f"**{len(groups)} active group(s) ready to scrape**")

                col1, col2 = st.columns([2, 1])

                with col1:
                    selected_groups = st.multiselect(
                        "Select groups to scrape (leave empty for all):",
                        options=[p['id'] for p in groups],
                        format_func=lambda x: next((p['group_name'] or p['group_url'] for p in groups if p['id'] == x), str(x))
                    )

                with col2:
                    st.write("")
                    st.write("")
                    if st.button("🔄 Start Scraping", type="primary"):
                        with st.spinner("Scraping in progress..."):
                            progress_bar = st.progress(0)
                            status_text = st.empty()

                            def update_progress(current, total, group_name):
                                progress_bar.progress(current / total)
                                status_text.text(f"Scraping {group_name}... ({current}/{total})")

                            group_ids = selected_groups if selected_groups else None
                            results = scraper.scrape_multiple_groups(
                                group_ids=group_ids,
                                progress_callback=update_progress
                            )

                            progress_bar.empty()
                            status_text.empty()

                            st.markdown('<div class="success-box">', unsafe_allow_html=True)
                            st.write("**Scraping Complete!**")
                            st.write(f"✅ Successful: {results['successful']} groups")
                            st.write(f"📝 Total Posts: {results['total_posts']}")
                            st.write(f"🖼️ Total Images: {results['total_images']}")
                            if results['failed'] > 0:
                                st.write(f"❌ Failed: {results['failed']} groups")
                            st.markdown('</div>', unsafe_allow_html=True)

                            if results['errors']:
                                with st.expander("View Errors"):
                                    for error in results['errors']:
                                        st.error(error)


def show_article_generator():
    """Generate articles"""
    st.header("✍️ Article Generator")

    tab1, tab2, tab3 = st.tabs(["📝 Generate New", "📋 View Articles", "📄 Paste Article"])

    with tab1:
        st.subheader("Generate New Article")

        # Check LLM availability
        available_llms = llm_manager.get_available_providers()
        enabled_llms = [p for p in available_llms if p['available']]

        if not enabled_llms:
            st.error("❌ No LLM providers configured! Go to Settings to add API keys.")
        else:
            with st.form("generate_article_form"):
                col1, col2 = st.columns(2)

                with col1:
                    location = st.text_input("Location*", placeholder="e.g., Rhodes, Santorini")
                    category = st.selectbox("Category", [
                        "restaurant", "hotel", "beach", "attraction",
                        "activity", "transportation", "general"
                    ])

                with col2:
                    article_type = st.selectbox("Article Type", [
                        "Top List (Top 5, Top 10...)",
                        "Complete Guide",
                        "Custom"
                    ])

                    if article_type == "Top List (Top 5, Top 10...)":
                        num_items = st.number_input("Number of items", min_value=3, max_value=20, value=5)
                    else:
                        num_items = 5

                # LLM selection
                llm_provider = st.selectbox(
                    "LLM Provider",
                    options=[p['name'] for p in enabled_llms],
                    format_func=lambda x: f"{x.title()} (Default)" if x == settings.DEFAULT_LLM_PROVIDER else x.title()
                )

                custom_prompt = st.text_area(
                    "Custom Prompt (optional)",
                    placeholder="Leave empty to use default template, or provide your own prompt...",
                    height=100
                )

                submit = st.form_submit_button("✨ Generate Article", type="primary")

                if submit:
                    if not location:
                        st.error("Location is required!")
                    else:
                        with st.spinner("Generating article... This may take a minute..."):
                            article_config = {
                                'location': location,
                                'category': category,
                                'num_items': num_items,
                                'llm_provider': llm_provider,
                                'custom_prompt': custom_prompt if custom_prompt else None
                            }

                            result = article_generator.generate_article(article_config)

                            if result['success']:
                                st.success("✅ Article generated successfully!")

                                st.markdown("---")
                                st.subheader(result['title'])
                                st.markdown(result['content'])

                                st.info(f"📊 Word count: {result['word_count']} | Images: {len(result['image_urls'])} | Sources: {result['sources_used']}")

                            else:
                                st.error(f"❌ Failed to generate article: {result.get('error')}")

    with tab2:
        st.subheader("Generated Articles")

        filter_status = st.selectbox("Filter by status", ["all", "draft", "published"])

        articles = db.get_articles(
            status=filter_status if filter_status != "all" else None,
            limit=50
        )

        if articles:
            for article in articles:
                status_badge = "✅ Published" if article['status'] == 'published' else "📝 Draft"

                with st.expander(f"{status_badge} - {article['title']}", expanded=False):
                    st.markdown(article['content'][:500] + "..." if len(article['content']) > 500 else article['content'])

                    col1, col2, col3 = st.columns(3)
                    with col1:
                        st.write(f"**Location:** {article['location'] or 'N/A'}")
                        st.write(f"**Category:** {article['category'] or 'N/A'}")
                    with col2:
                        st.write(f"**Created:** {article['created_at']}")
                        st.write(f"**Images:** {len(article['image_urls'])}")
                    with col3:
                        if article['status'] != 'published' and wordpress_publisher.is_configured():
                            if st.button("🚀 Publish to WordPress", key=f"publish_{article['id']}"):
                                with st.spinner("Publishing..."):
                                    result = wordpress_publisher.publish_article(article['id'])
                                    if result['success']:
                                        st.success(f"Published! View at: {result['wordpress_url']}")
                                        st.rerun()
                                    else:
                                        st.error(f"Failed: {result['error']}")
        else:
            st.info("No articles yet. Generate one in the 'Generate New' tab!")

    with tab3:
        st.subheader("Paste & Enhance Article")
        st.write("Paste your existing article content, and we'll add local recommendations and images!")

        with st.form("paste_article_form"):
            title = st.text_input("Article Title")
            pasted_content = st.text_area(
                "Article Content",
                placeholder="Paste your article content here...",
                height=300
            )

            col1, col2 = st.columns(2)
            with col1:
                location = st.text_input("Location", placeholder="e.g., Rhodes")
            with col2:
                category = st.selectbox("Category", [
                    "general", "restaurant", "hotel", "beach",
                    "attraction", "activity"
                ])

            submit = st.form_submit_button("✨ Enhance Article")

            if submit:
                if not pasted_content:
                    st.error("Please paste article content!")
                else:
                    with st.spinner("Enhancing article..."):
                        article_config = {
                            'title': title,
                            'location': location,
                            'category': category
                        }

                        result = article_generator.paste_article(pasted_content, article_config)

                        if result['success']:
                            st.success("✅ Article enhanced successfully!")
                            st.markdown("---")
                            st.subheader(result['title'])
                            st.markdown(result['content'])
                        else:
                            st.error(f"❌ Failed: {result.get('error')}")


def show_settings():
    """Settings and configuration"""
    st.header("⚙️ Settings & Configuration")

    tab1, tab2, tab3, tab4 = st.tabs(["🤖 LLM Providers", "🖼️ Image Sources", "🌐 WordPress", "📊 System Info"])

    with tab1:
        st.subheader("LLM Provider Configuration")

        providers = llm_manager.get_available_providers()

        for provider in providers:
            with st.expander(f"{provider['name'].title()} {'✅' if provider['available'] else '❌'}", expanded=not provider['available']):
                if provider['available']:
                    st.success(f"✅ Configured and ready!")
                    st.write(f"**Model:** {provider['model']}")

                    if st.button(f"🧪 Test {provider['name'].title()}", key=f"test_{provider['name']}"):
                        with st.spinner("Testing..."):
                            result = llm_manager.test_provider(provider['name'])
                            if result['success']:
                                st.success(f"✅ Working! Response: {result['response']}")
                            else:
                                st.error(f"❌ Error: {result['error']}")

                    if provider['is_default']:
                        st.info("⭐ This is your default provider")
                    else:
                        if st.button(f"Set as Default", key=f"default_{provider['name']}"):
                            llm_manager.set_default_provider(provider['name'])
                            st.success(f"{provider['name'].title()} is now the default!")
                            st.rerun()
                else:
                    st.warning(f"❌ Not configured")
                    st.info(f"Add your API key to the `.env` file to enable {provider['name'].title()}")

        st.markdown("---")
        st.write("**To add/update API keys:**")
        st.code("Edit the `.env` file in the project root and restart the app", language="bash")

    with tab2:
        st.subheader("Image Source Configuration")

        image_sources = settings.get_image_sources_config()

        for source_name, source_config in image_sources.items():
            with st.expander(f"{source_name.title()} {'✅' if source_config['enabled'] else '❌'}"):
                if source_config['enabled']:
                    st.success("✅ Configured and ready!")
                else:
                    st.warning("❌ Not configured")
                    if source_name != 'wikimedia' and source_name != 'facebook':
                        st.info(f"Add your API key to the `.env` file to enable {source_name.title()}")

    with tab3:
        st.subheader("WordPress Configuration")

        if wordpress_publisher.is_configured():
            st.success("✅ WordPress is configured!")
            st.write(f"**Site URL:** {settings.WORDPRESS_URL}")
            st.write(f"**Username:** {settings.WORDPRESS_USERNAME}")

            if st.button("🧪 Test WordPress Connection"):
                with st.spinner("Testing connection..."):
                    result = wordpress_publisher.test_connection()
                    if result['success']:
                        st.success(f"✅ {result['message']}")
                    else:
                        st.error(f"❌ {result['error']}")
        else:
            st.warning("❌ WordPress not configured")
            st.info("Add your WordPress credentials to the `.env` file:")
            st.code("""
WORDPRESS_URL=https://yoursite.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx
            """, language="bash")
            st.write("**How to get WordPress Application Password:**")
            st.write("1. Go to WordPress Admin → Users → Profile")
            st.write("2. Scroll to 'Application Passwords'")
            st.write("3. Create a new application password")
            st.write("4. Copy the generated password to `.env` file")

    with tab4:
        st.subheader("System Information")

        # Config validation
        config_status = settings.validate_config()

        if config_status['valid']:
            st.success("✅ All systems configured!")
        else:
            st.warning("⚠️ Some issues detected:")
            for issue in config_status['issues']:
                st.write(f"• {issue}")

        st.markdown("---")

        # Database stats
        st.write("**Database Statistics:**")
        stats = vector_store.get_stats()
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Posts", stats['total_posts'])
        with col2:
            st.metric("Total Tips", stats['total_tips'])

        st.write(f"**SQLite DB:** `{settings.SQLITE_DB_PATH}`")
        st.write(f"**ChromaDB:** `{settings.CHROMA_DB_PATH}`")

        st.markdown("---")

        # System logs
        st.write("**Recent System Logs:**")
        logs = db.get_logs(limit=20)

        if logs:
            log_df = pd.DataFrame(logs)
            st.dataframe(log_df[['created_at', 'log_level', 'module', 'message']], use_container_width=True)
        else:
            st.info("No logs yet")


# Main app
def main():
    # Sidebar navigation
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1E88E5/FFFFFF/?text=Tourism+CMS", use_column_width=True)
        st.markdown("---")

        if st.button("🏠 Dashboard", use_container_width=True):
            st.session_state.group = 'Dashboard'

        if st.button("📱 Facebook Groups", use_container_width=True):
            st.session_state.group = 'Facebook Groups'

        if st.button("✍️ Generate Articles", use_container_width=True):
            st.session_state.group = 'Articles'

        if st.button("⚙️ Settings", use_container_width=True):
            st.session_state.group = 'Settings'

        st.markdown("---")
        st.caption("Tourism Content Generator v1.0")

    # Route to selected group
    if st.session_state.group == 'Dashboard':
        show_dashboard()
    elif st.session_state.group == 'Facebook Groups':
        show_facebook_groups()
    elif st.session_state.group == 'Articles':
        show_article_generator()
    elif st.session_state.group == 'Settings':
        show_settings()


if __name__ == "__main__":
    main()
