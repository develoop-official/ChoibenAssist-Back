# ChoibenAssist AI Backend

学習記録アプリのAI機能を提供するマイクロサービス

## 🚀 Features

- **学習プラン生成**: 個人の学習履歴に基づいたカスタマイズされたプラン
- **今日のTODO提案**: 日々の効果的な学習タスクの自動生成
- **学習進捗分析**: データに基づいた進捗分析と改善提案
- **学習アドバイス**: パーソナライズされた学習指導
- **目標設定支援**: SMART目標の提案とトラッキング

## 🛠 Tech Stack

- **Backend**: Python 3.10+, FastAPI
- **AI/LLM**: Google Gemini 2.0 Flash-Lite
- **External API**: Supabase REST API
- **Testing**: Pytest
- **Development**: Black, Flake8, MyPy

## 📁 Project Structure

```
ChoibenAssist-Back/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application
│   ├── config.py               # Settings and configuration
│   ├── dependencies.py         # Authentication and rate limiting
│   ├── models/
│   │   ├── __init__.py
│   │   └── ai_models.py        # Pydantic models
│   ├── routers/
│   │   ├── __init__.py
│   │   ├── ai.py               # AI endpoints
│   │   └── health.py           # Health check endpoints
│   └── services/
│       ├── __init__.py
│       ├── gemini_service.py   # Gemini AI integration
│       └── supabase_service.py # Supabase data fetching
├── tests/
│   ├── __init__.py
│   └── test_main.py            # Basic tests
├── requirements.txt            # Python dependencies
├── .env.example               # Environment variables template
├── .gitignore
├── run.py                     # Development server
└── README.md
```

## 🔧 Setup

### 1. Environment Setup

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows
venv\Scripts\activate
# macOS/Linux
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 2. Environment Variables

Copy `.env.example` to `.env` and fill in your values:

```bash
cp .env.example .env
```

Required environment variables:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `SUPABASE_URL`: Your Supabase project URL
- `SUPABASE_ANON_KEY`: Your Supabase anonymous key
- `API_SECRET_KEY`: Secret key for API authentication

### 3. Run Development Server

```bash
# Using run.py
python run.py

# Or directly with uvicorn
uvicorn app.main:app --reload
```

The API will be available at `http://localhost:8000`

## 📡 API Endpoints

### Health Check
- `GET /api/health` - Basic health check
- `GET /api/health/detailed` - Detailed health check with dependencies

### AI Services
All AI endpoints require `Authorization: Bearer {API_SECRET_KEY}` header.

- `POST /api/ai/plan` - Generate learning plan
- `POST /api/ai/todo` - Generate daily TODO list
- `POST /api/ai/analysis` - Analyze learning progress
- `POST /api/ai/advice` - Get learning advice
- `POST /api/ai/goals` - Suggest learning goals

### API Documentation
- Swagger UI: `http://localhost:8000/docs` (development only)
- ReDoc: `http://localhost:8000/redoc` (development only)

## 🧪 Testing

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=app

# Run specific test file
pytest tests/test_main.py
```

## 🔐 Authentication

This API uses API key authentication for secure communication with the frontend/Supabase. Include the API key in the Authorization header:

```
Authorization: Bearer your_api_secret_key
```

## 📊 Rate Limiting

- Default: 100 requests per minute per IP
- Configurable via `RATE_LIMIT_PER_MINUTE` environment variable

## 🚀 Deployment

### Railway

1. Connect your GitHub repository to Railway
2. Set environment variables in Railway dashboard
3. Deploy automatically on push to main branch

### Google Cloud Run

```bash
# Build and deploy
gcloud run deploy choibenassist-ai \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated
```

## 🤝 Integration with Frontend

This API is designed to work with the Next.js frontend. The frontend should:

1. Authenticate with the API using the secret key
2. Pass user IDs in request bodies for personalized responses
3. Handle rate limiting (429 status codes)
4. Display AI-generated content to users

## 📝 Example Request

```bash
curl -X POST "http://localhost:8000/api/ai/todo" \
  -H "Authorization: Bearer your_api_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "available_time": 120
  }'
```

## 📄 License

This project is part of ChoibenAssist learning application.
