# 🌐 Facebook Scraper Web Interface

A beautiful, user-friendly web interface for the Facebook Scraper API built with Streamlit.

![Streamlit](https://img.shields.io/badge/Streamlit-FF4B4B?style=for-the-badge&logo=Streamlit&logoColor=white)

## ✨ Features

- 🎨 **Modern UI** - Clean, intuitive interface
- 🔐 **Secure** - API key stored in session (password field)
- 📊 **JSON Viewer** - Beautiful formatted output
- 💾 **Export Data** - Download results as JSON
- ⚡ **Real-time** - Instant scraping results
- 🎯 **8 Methods** - All scraper methods available
- 🚨 **Error Handling** - Clear error messages

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements-gui.txt
```

### 2. Get Your API Key

1. Sign up at [RapidAPI](https://rapidapi.com/)
2. Subscribe to [Facebook Scraper API](https://rapidapi.com/taskagi-2-taskagi-2-default/api/facebook-scraper4/)
3. Copy your API key

### 3. Run the Web App

```bash
streamlit run app.py
```

The app will automatically open in your browser at `http://localhost:8501`

## 📖 How to Use

### Step 1: Enter API Key
- In the sidebar, paste your RapidAPI key
- It's stored securely in your session only

### Step 2: Select Method
Choose what you want to scrape:
- **Get Marketplace Item** - Single item details
- **Search Marketplace by Location** - Items in a location
- **Search Marketplace by Keyword** - Search results
- **Retrieve Page Posts** - Public page posts
- **Get Page About Info** - Page information
- **Retrieve Post Data** - Post engagement data
- **Retrieve Profile Photos** - Profile pictures
- **Retrieve Profile Data** - Public profile info

### Step 3: Enter URL
- Paste the Facebook URL you want to scrape
- See the example in the info box for guidance

### Step 4: Scrape
- Click "🚀 Scrape Data"
- View results in formatted JSON
- Download as file if needed

## 🎯 Examples

### Marketplace Item
```
URL: https://www.facebook.com/marketplace/item/1030745568732697
Method: Get Marketplace Item
```

### Page Posts
```
URL: https://www.facebook.com/zippo
Method: Retrieve Page Posts
```

### Profile Data
```
URL: https://www.facebook.com/username
Method: Retrieve Profile Data
```

## 🐛 Troubleshooting

### "Authentication Error"
- ❌ Invalid API key
- ✅ Check your RapidAPI subscription
- ✅ Verify the key is copied correctly

### "Network Error"
- ❌ Connection timeout
- ✅ Check your internet connection
- ✅ Try again in a few moments

### "API Error"
- ❌ Invalid URL or endpoint issue
- ✅ Verify the Facebook URL is correct
- ✅ Check API rate limits

## 🎨 Screenshot Preview

The interface includes:
- **Left Panel**: Input area with URL field and method selection
- **Right Panel**: Output area with formatted JSON results
- **Sidebar**: Configuration (API key, method selector, help)
- **Download Button**: Export results as JSON file

## 🔧 Advanced Usage

### Run on Custom Port
```bash
streamlit run app.py --server.port 8080
```

### Run in Headless Mode
```bash
streamlit run app.py --server.headless true
```

### Deploy to Cloud
The app can be deployed to:
- **Streamlit Cloud** (Free, recommended)
- **Heroku**
- **AWS/GCP/Azure**
- **Docker**

### Deploy to Streamlit Cloud:
1. Push code to GitHub
2. Go to [share.streamlit.io](https://share.streamlit.io)
3. Connect your repository
4. Deploy!

## 📚 Documentation

For API documentation and library usage, see the main [README.md](README.md)

## 🤝 Contributing

Contributions welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md)

## 📄 License

MIT License - see [LICENSE](LICENSE) file
