# ChoibenAssist AI Backend - クラス図

```mermaid
classDiagram
    %% FastAPI Application Layer
    class FastAPIApp {
        +app: FastAPI
        +lifespan()
        +include_routers()
    }
    
    %% Router Classes
    class AIRouter {
        +generate_learning_plan()
        +generate_daily_todo()
        +analyze_learning_progress()
        +get_learning_advice()
        +suggest_learning_goals()
    }
    
    class HealthRouter {
        +health_check()
        +detailed_health_check()
    }
    
    %% Service Classes
    class GeminiService {
        -model: GenerativeModel
        -api_key: str
        +__init__()
        +generate_learning_plan()
        +generate_daily_todo()
        +analyze_learning_progress()
        +generate_learning_advice()
        +suggest_learning_goals()
    }
    
    class SupabaseService {
        -base_url: str
        -api_key: str
        -headers: dict
        +__init__()
        +get_user_learning_data()
        +get_recent_learning_history()
        +get_learning_analytics_data()
        +get_user_profile()
        +get_current_goals()
        +_analyze_learning_patterns()
    }
    
    %% Model Classes
    class PlanGenerationRequest {
        +user_id: str
        +subject: str
        +target_date: datetime
        +difficulty_level: str
        +available_time_per_day: int
    }
    
    class PlanGenerationResponse {
        +plan_id: str
        +subject: str
        +generated_at: datetime
        +plan_content: dict
        +estimated_completion_date: datetime
        +daily_tasks: list
    }
    
    class TodoGenerationRequest {
        +user_id: str
        +date: datetime
        +available_time: int
        +preferences: dict
    }
    
    class TodoGenerationResponse {
        +date: datetime
        +todos: list[TodoItem]
        +total_estimated_time: int
        +motivational_message: str
    }
    
    class TodoItem {
        +id: int
        +title: str
        +description: str
        +priority: Priority
        +estimated_time: int
        +category: Category
        +reason: str
    }
    
    class AnalysisRequest {
        +user_id: str
        +period: Period
        +subjects: list[str]
    }
    
    class AnalysisResponse {
        +user_id: str
        +period: Period
        +analysis_date: datetime
        +overall_progress: dict
        +subject_breakdown: list
        +strengths: list[str]
        +weaknesses: list[str]
        +recommendations: list[str]
    }
    
    %% Configuration and Dependencies
    class Settings {
        +gemini_api_key: str
        +supabase_url: str
        +supabase_anon_key: str
        +api_secret_key: str
        +debug: bool
        +allowed_origins: list[str]
        +rate_limit_per_minute: int
    }
    
    class Dependencies {
        +get_api_key()
        +rate_limit()
        +get_current_user()
    }
    
    %% Enum Classes
    class Priority {
        <<enumeration>>
        LOW
        MEDIUM
        HIGH
    }
    
    class Category {
        <<enumeration>>
        REVIEW
        NEW_LEARNING
        PRACTICE
        EXAM_PREP
    }
    
    class Period {
        <<enumeration>>
        DAILY
        WEEKLY
        MONTHLY
    }
    
    %% Relationships
    FastAPIApp --> AIRouter
    FastAPIApp --> HealthRouter
    FastAPIApp --> Settings
    
    AIRouter --> GeminiService
    AIRouter --> SupabaseService
    AIRouter --> Dependencies
    
    AIRouter --> PlanGenerationRequest
    AIRouter --> PlanGenerationResponse
    AIRouter --> TodoGenerationRequest
    AIRouter --> TodoGenerationResponse
    AIRouter --> AnalysisRequest
    AIRouter --> AnalysisResponse
    
    TodoGenerationResponse --> TodoItem
    TodoItem --> Priority
    TodoItem --> Category
    AnalysisRequest --> Period
    
    GeminiService --> Settings
    SupabaseService --> Settings
```

## 📐 アーキテクチャ概要

### レイヤー構成
1. **Application Layer**: FastAPI アプリケーション、ルーター
2. **Service Layer**: Gemini AI、Supabase連携サービス
3. **Model Layer**: Pydanticモデル、レスポンス/リクエスト定義
4. **Infrastructure Layer**: 設定、依存関係、認証

### 主要コンポーネント
- **GeminiService**: AI機能の中核、LLMとの通信
- **SupabaseService**: 学習データの取得・分析
- **AIRouter**: AI機能のエンドポイント群
- **Dependencies**: 認証・レート制限などの横断的関心事
