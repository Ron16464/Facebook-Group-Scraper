# 🏖️ Tourism Content Generator

**Automated Tourism Content Creation System**

Scrape Facebook groups for tourism content, generate AI-powered articles with smart image placement, and publish directly to WordPress - all from a beautiful dashboard.

---

## ✨ Features

### 🔍 **Multi-Source Content Scraping**
- ✅ Scrape Facebook groups for tourism content
- ✅ Automatic content categorization (restaurants, hotels, beaches, activities, etc.)
- ✅ Extract images from posts
- ✅ Smart deduplication
- ✅ Vector database storage for semantic search

### 🤖 **AI-Powered Article Generation**
- ✅ Multi-LLM support (Claude, GPT-4, Gemini)
- ✅ Pre-built templates (Top Lists, Travel Guides, Hidden Gems, etc.)
- ✅ Custom prompt support
- ✅ Smart image placement with [IMAGE: description] placeholders
- ✅ Article paste & enhance feature
- ✅ RAG (Retrieval Augmented Generation) using scraped content

### 🖼️ **Multi-Source Image Integration**
- ✅ Pexels API
- ✅ Unsplash API
- ✅ Pixabay API
- ✅ Wikimedia Commons
- ✅ Facebook post images
- ✅ Automatic attribution and licensing

### 🚀 **WordPress Publishing**
- ✅ One-click publishing to WordPress
- ✅ Automatic image upload
- ✅ Category management
- ✅ Featured image support
- ✅ Draft and scheduled publishing
- ✅ Markdown to HTML conversion

### 📊 **Beautiful Dashboard**
- ✅ Streamlit-based UI
- ✅ Facebook groups management (add/edit/delete)
- ✅ LLM provider management
- ✅ Image source configuration
- ✅ Real-time scraping progress
- ✅ Article preview and editing
- ✅ System logs and statistics

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  Streamlit Dashboard (UI)                    │
└─────────────────────────────────────────────────────────────┘
                          │
        ┌─────────────────┼─────────────────┐
        ↓                 ↓                 ↓
   ┌─────────┐     ┌──────────┐     ┌────────────┐
   │ Scrapers│     │Generators│     │ Publishers │
   └─────────┘     └──────────┘     └────────────┘
        │                 │                 │
        ↓                 ↓                 ↓
   ┌──────────────────────────────────────────────┐
   │  Database Layer (SQLite + ChromaDB)          │
   │  - Structured data (SQLite)                  │
   │  - Vector embeddings (ChromaDB)              │
   └──────────────────────────────────────────────┘
```

### Directory Structure

```
tourism-content-generator/
├── config/              # Configuration management
│   └── settings.py
├── database/            # Database models and storage
│   ├── models.py        # SQLite models
│   └── vector_store.py  # ChromaDB vector storage
├── scrapers/            # Content scrapers
│   ├── facebook_scraper.py
│   └── image_scrapers.py
├── generators/          # Content generation
│   ├── llm_providers.py # Multi-LLM integration
│   └── article_generator.py
├── publishers/          # Publishing modules
│   └── wordpress_publisher.py
├── ui/                  # User interface
│   └── streamlit_app.py
├── utils/               # Utilities
│   ├── helpers.py
│   └── init_templates.py
├── data/                # Data storage (created automatically)
│   ├── tourism_content.db
│   └── chroma_db/
├── templates/           # Article templates
├── .env.example         # Environment variables template
├── requirements.txt     # Python dependencies
└── README.md           # This file
```

---

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- pip (Python package manager)

### Installation

1. **Clone the repository**
```bash
git clone <your-repo-url>
cd Facebook-Group-Scraper
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Configure environment variables**
```bash
cp .env.example .env
```

Edit `.env` file and add your API keys:

```env
# Required for Facebook scraping
RAPIDAPI_KEY=your_rapidapi_key_here

# Required for article generation (choose at least one)
ANTHROPIC_API_KEY=sk-ant-your_key_here
OPENAI_API_KEY=sk-your_openai_key_here
GOOGLE_API_KEY=your_google_api_key_here

# Optional - Image sources (at least one recommended)
PEXELS_API_KEY=your_pexels_key_here
UNSPLASH_ACCESS_KEY=your_unsplash_key_here
PIXABAY_API_KEY=your_pixabay_key_here

# Optional - WordPress publishing
WORDPRESS_URL=https://yoursite.com
WORDPRESS_USERNAME=your_username
WORDPRESS_APP_PASSWORD=xxxx xxxx xxxx xxxx
```

4. **Initialize database and templates**
```bash
python utils/init_templates.py
```

5. **Launch the dashboard**
```bash
streamlit run ui/streamlit_app.py
```

The dashboard will open in your browser at `http://localhost:8501`

---

## 📚 Getting API Keys

### RapidAPI (Facebook Scraping)
1. Sign up at [RapidAPI](https://rapidapi.com/)
2. Subscribe to [Facebook Scraper API](https://rapidapi.com/neoscrap-api/api/facebook-scraper4)
3. Copy your API key from the dashboard

### Anthropic Claude (Recommended for article generation)
1. Sign up at [Anthropic](https://console.anthropic.com/)
2. Generate an API key
3. Copy the key (starts with `sk-ant-`)

### OpenAI (Alternative LLM)
1. Sign up at [OpenAI](https://platform.openai.com/)
2. Generate an API key
3. Copy the key (starts with `sk-`)

### Google Gemini (Alternative LLM)
1. Sign up at [Google AI Studio](https://makersuite.google.com/)
2. Generate an API key
3. Copy the key

### Pexels (Free Images)
1. Sign up at [Pexels](https://www.pexels.com/api/)
2. Generate an API key (free tier available)
3. Copy the key

### Unsplash (Free Images)
1. Sign up at [Unsplash Developers](https://unsplash.com/developers)
2. Create an application
3. Copy the Access Key

### Pixabay (Free Images)
1. Sign up at [Pixabay](https://pixabay.com/api/docs/)
2. Get your API key from the dashboard
3. Copy the key

### WordPress (Publishing)
1. Go to your WordPress Admin → Users → Profile
2. Scroll to "Application Passwords"
3. Create a new application password
4. Copy the generated password (format: `xxxx xxxx xxxx xxxx`)

---

## 💡 Usage Guide

### 1. **Add Facebook Groups**

Navigate to **📱 Facebook Groups** → **Add Page** tab:

1. Enter the Facebook group URL (e.g., `https://www.facebook.com/groups/RhodesTourism`)
2. Provide a friendly name (optional)
3. Select category (restaurant, hotel, beach, etc.)
4. Add description (optional)
5. Click **Add Page**

### 2. **Scrape Content**

Navigate to **📱 Facebook Groups** → **Scrape Content** tab:

1. Select groups to scrape (or leave empty for all active groups)
2. Click **Start Scraping**
3. Watch the progress bar
4. Review results (posts scraped, images found, errors)

**Note:** Content is automatically:
- Categorized (restaurants, hotels, beaches, etc.)
- Stored in both SQLite and ChromaDB
- Deduplicated
- Ready for article generation

### 3. **Generate Articles**

Navigate to **✍️ Generate Articles** → **Generate New** tab:

1. **Enter location** (e.g., "Rhodes", "Santorini")
2. **Select category** (restaurant, hotel, beach, etc.)
3. **Choose article type**:
   - Top List (Top 5, Top 10, etc.)
   - Complete Guide
   - Custom
4. **Select LLM provider** (Claude, GPT-4, or Gemini)
5. **Optional:** Add custom prompt
6. Click **Generate Article**

The system will:
- Search the vector database for relevant content
- Generate article using AI with local insights
- Find and insert relevant images
- Add proper attribution
- Save as draft

### 4. **Paste & Enhance Articles**

Navigate to **✍️ Generate Articles** → **Paste Article** tab:

1. Paste your existing article content
2. Enter location and category
3. Click **Enhance Article**

The system will:
- Add local recommendations from scraped content
- Insert relevant images
- Add proper attributions
- Enhance with local insights

### 5. **Publish to WordPress**

Navigate to **✍️ Generate Articles** → **View Articles** tab:

1. Find your article in the list
2. Expand the article
3. Click **🚀 Publish to WordPress**
4. Wait for upload (images + content)
5. Get the WordPress post URL

**Note:** WordPress must be configured in Settings first!

### 6. **Manage Settings**

Navigate to **⚙️ Settings**:

- **LLM Providers:** Test connections, set default provider
- **Image Sources:** View configured sources
- **WordPress:** Test connection, view configuration
- **System Info:** View database stats, logs, and system status

---

## 🎯 Best Practices

### Content Scraping
- ✅ Scrape regularly (weekly) to keep content fresh
- ✅ Focus on 10-20 high-quality tourism pages
- ✅ Enable active pages only for scraping
- ✅ Monitor system logs for errors

### Article Generation
- ✅ Use specific locations for better results
- ✅ Choose the right category for accurate recommendations
- ✅ Review generated content before publishing
- ✅ Customize prompts for unique voice
- ✅ Use paste & enhance for existing content

### Image Management
- ✅ Enable multiple image sources for variety
- ✅ Always include proper attribution
- ✅ Check image licenses before commercial use
- ✅ Prefer high-quality sources (Unsplash, Pexels)

### WordPress Publishing
- ✅ Test connection before bulk publishing
- ✅ Review articles in preview first
- ✅ Use categories for better organization
- ✅ Set featured images for better SEO
- ✅ Consider scheduling posts instead of immediate publish

---

## 🔧 Advanced Configuration

### Database Settings

Edit `.env` to customize database paths:

```env
SQLITE_DB_PATH=data/tourism_content.db
CHROMA_DB_PATH=data/chroma_db
```

### LLM Models

Change default models in `.env`:

```env
ANTHROPIC_MODEL=claude-sonnet-4-20250514
OPENAI_MODEL=gpt-4-turbo-preview
GOOGLE_MODEL=gemini-pro
DEFAULT_LLM_PROVIDER=anthropic
```

### Scraping Limits

```env
MAX_POSTS_PER_PAGE=50
MAX_IMAGES_PER_ARTICLE=10
IMAGE_QUALITY=high
```

### Content Retention

```env
# Keep content for X days (0 = keep forever)
CONTENT_RETENTION_DAYS=0
```

---

## 📊 Storage Estimates

Based on **100 active Facebook groups**:

| Time Period | Estimated Storage |
|-------------|------------------|
| 1 month     | ~100 MB          |
| 6 months    | ~600 MB          |
| 1 year      | ~1.2 GB          |

**Notes:**
- Images are stored as URLs (not downloaded unless publishing)
- Vector embeddings are efficient
- SQLite is lightweight
- Very manageable on any laptop!

---

## 🐛 Troubleshooting

### "RapidAPI key not configured"
→ Add your RapidAPI key to `.env` file

### "No LLM provider configured"
→ Add at least one LLM API key (Claude, OpenAI, or Gemini)

### "WordPress connection failed"
→ Check WordPress URL, username, and application password

### "Image upload failed"
→ Check image source API keys in Settings

### "Scraping returns no posts"
→ Verify Facebook group URL is public and correct

### Database errors
→ Delete `data/` folder and restart to reinitialize

---

## 🚧 Future Enhancements

- [ ] Scheduled scraping (cron jobs)
- [ ] Multi-language article generation
- [ ] SEO optimization tools
- [ ] Article analytics
- [ ] Bulk publishing
- [ ] Custom image editing
- [ ] Social media publishing
- [ ] Content calendar
- [ ] A/B testing for titles
- [ ] Advanced NLP for categorization

---

## 📝 License

This project is licensed under the MIT License.

---

## 🤝 Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

---

## 💬 Support

For issues or questions:
1. Check the Troubleshooting section
2. Review system logs in Settings → System Info
3. Open an issue on GitHub

---

## 🎉 Credits

Built with:
- [Streamlit](https://streamlit.io/) - Dashboard UI
- [ChromaDB](https://www.trychroma.com/) - Vector database
- [Anthropic Claude](https://www.anthropic.com/) - AI generation
- [RapidAPI](https://rapidapi.com/) - Facebook scraping
- [Pexels](https://www.pexels.com/) / [Unsplash](https://unsplash.com/) - Images

---

**Happy Content Generating! 🏖️✨**
