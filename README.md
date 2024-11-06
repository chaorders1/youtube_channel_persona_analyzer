# 🎥 YouTube Channel Persona Analyzer

<div align="center">

[![Python](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.68.0+-green.svg)](https://fastapi.tiangolo.com/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](LICENSE)

AI-powered YouTube channel analysis tool that generates detailed persona reports in seconds.

</div>

## ✨ Features

- **AI-Powered Analysis**: Leverages Claude AI for intelligent content understanding
- **Quick Results**: Generate comprehensive reports in under 60 seconds
- **Detailed Insights**: Analyze content strategy, engagement metrics, and channel personality
- **Simple API**: Easy integration with RESTful endpoints
- **Modern Interface**: Clean, responsive design with dark mode

## 🚀 Getting Started

### Prerequisites

- Python 3.8+
- Anthropic API key
- YouTube Data API key

### Installation

1. **Clone the repository**
```bash
git clone https://github.com/your-username/youtube-channel-persona-analyzer.git
cd youtube-channel-persona-analyzer
```

2. **Install dependencies**
```bash
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env
# Edit .env with your API keys
```

4. **Run the application**
```bash
# Start the API server
python -m uvicorn persona_api:app --reload --port 8000

# For development with hot reload
make dev
```

## 💡 Use Cases

- Content creators analyzing competition
- Marketing teams researching influencers
- Brands seeking partnership opportunities
- Researchers studying content trends

## 🛠️ Technology Stack

- **Backend**: FastAPI, Python 3.8+
- **AI**: Claude AI (Anthropic)
- **Data Processing**: Pandas, NumPy
- **Testing**: Pytest
- **CI/CD**: GitHub Actions

## 📊 Example Output

```json
{
    "channel_name": "TechReviewer Pro",
    "brand_personality": "Authoritative yet approachable",
    "target_audience": "Tech enthusiasts (25-45)",
    "content_strategy": {
        "main_topics": ["Tech reviews", "Tutorials"],
        "posting_frequency": "2x weekly",
        "engagement_rate": "8.5%"
    }
}
```

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📝 License

Distributed under the MIT License. See `LICENSE` for more information.

## 📫 Contact

Project Link: [https://github.com/your-username/youtube-channel-persona-analyzer](https://github.com/your-username/youtube-channel-persona-analyzer)

---

<div align="center">
Made with ❤️ by the YouTube Channel Persona Analyzer Team
</div>