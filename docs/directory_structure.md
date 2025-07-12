# ChoibenAssist AI Backend - 推奨ディレクトリ構造

## 🏗️ プロジェクト構造

```
ChoibenAssist-Back/
├── app/                              # メインアプリケーション
│   ├── __init__.py
│   ├── main.py                       # FastAPI アプリケーションのエントリーポイント
│   ├── config.py                     # 設定管理
│   ├── dependencies.py               # 認証・レート制限などの依存関係
│   │
│   ├── api/                          # API層
│   │   ├── __init__.py
│   │   ├── deps.py                   # API依存関係
│   │   └── v1/                       # APIバージョン管理
│   │       ├── __init__.py
│   │       ├── api.py                # APIルーター統合
│   │       └── endpoints/            # 個別エンドポイント
│   │           ├── __init__.py
│   │           ├── ai.py            # AI機能エンドポイント
│   │           ├── health.py        # ヘルスチェック
│   │           └── utils.py         # エンドポイント共通機能
│   │
│   ├── core/                         # コア機能
│   │   ├── __init__.py
│   │   ├── config.py                 # コア設定（移動）
│   │   ├── security.py               # セキュリティ機能
│   │   ├── logging.py                # ログ設定
│   │   └── exceptions.py             # カスタム例外
│   │
│   ├── models/                       # データモデル
│   │   ├── __init__.py
│   │   ├── ai_models.py              # AI機能のPydanticモデル
│   │   ├── base.py                   # 基底モデル
│   │   ├── requests.py               # リクエストモデル
│   │   └── responses.py              # レスポンスモデル
│   │
│   ├── services/                     # ビジネスロジック層
│   │   ├── __init__.py
│   │   ├── gemini_service.py         # Gemini AI連携
│   │   ├── supabase_service.py       # Supabase連携
│   │   ├── ai/                       # AI機能専用サービス
│   │   │   ├── __init__.py
│   │   │   ├── plan_generator.py     # 学習プラン生成
│   │   │   ├── todo_generator.py     # TODO生成
│   │   │   ├── analyzer.py           # 学習分析
│   │   │   └── advisor.py            # アドバイス生成
│   │   │
│   │   └── external/                 # 外部サービス連携
│   │       ├── __init__.py
│   │       ├── gemini_client.py      # Gemini APIクライアント
│   │       └── supabase_client.py    # Supabase APIクライアント
│   │
│   ├── schemas/                      # レスポンス・リクエストスキーマ
│   │   ├── __init__.py
│   │   ├── ai_schemas.py             # AI機能関連スキーマ
│   │   ├── common.py                 # 共通スキーマ
│   │   └── enums.py                  # 列挙型定義
│   │
│   └── utils/                        # ユーティリティ
│       ├── __init__.py
│       ├── helpers.py                # 汎用ヘルパー関数
│       ├── validators.py             # バリデーション機能
│       └── formatters.py             # フォーマット機能
│
├── tests/                            # テスト
│   ├── __init__.py
│   ├── conftest.py                   # pytest設定
│   ├── test_main.py                  # メインアプリケーションテスト
│   │
│   ├── api/                          # APIテスト
│   │   ├── __init__.py
│   │   ├── test_ai_endpoints.py      # AIエンドポイントテスト
│   │   └── test_health.py            # ヘルスチェックテスト
│   │
│   ├── services/                     # サービス層テスト
│   │   ├── __init__.py
│   │   ├── test_gemini_service.py    # Geminiサービステスト
│   │   └── test_supabase_service.py  # Supabaseサービステスト
│   │
│   └── utils/                        # ユーティリティテスト
│       ├── __init__.py
│       └── test_helpers.py
│
├── docs/                             # ドキュメント
│   ├── api/                          # API仕様書
│   │   ├── openapi.json              # OpenAPI仕様
│   │   └── postman_collection.json   # Postman コレクション
│   ├── development/                  # 開発者向けドキュメント
│   │   ├── setup.md                  # セットアップガイド
│   │   ├── api_design.md             # API設計ドキュメント
│   │   └── deployment.md             # デプロイガイド
│   ├── class_diagram.md              # クラス図
│   └── SOW.md                        # 作業範囲書
│
├── scripts/                          # 運用スクリプト
│   ├── start.py                      # 開発サーバー起動
│   ├── test.py                       # テスト実行
│   ├── lint.py                       # コード品質チェック
│   └── deploy.py                     # デプロイスクリプト
│
├── config/                           # 設定ファイル
│   ├── development.yaml              # 開発環境設定
│   ├── production.yaml               # 本番環境設定
│   └── testing.yaml                  # テスト環境設定
│
├── .github/                          # GitHub Actions
│   └── workflows/
│       ├── ci.yml                    # CI/CDパイプライン
│       ├── test.yml                  # テスト実行
│       └── deploy.yml                # デプロイメント
│
├── docker/                           # Docker関連（必要に応じて）
│   ├── Dockerfile                    # Docker設定
│   ├── docker-compose.yml            # ローカル開発用
│   └── docker-compose.prod.yml       # 本番用
│
├── .env.example                      # 環境変数テンプレート
├── .env                              # 環境変数（gitignore）
├── .gitignore                        # Git無視ファイル
├── requirements.txt                  # Python依存関係
├── requirements-dev.txt              # 開発用依存関係
├── pyproject.toml                    # Python プロジェクト設定
├── README.md                         # プロジェクト説明
├── CHANGELOG.md                      # 変更ログ
└── run.py                            # 開発サーバー起動スクリプト
```

## 🎯 **設計原則**

### 1. **責務の分離 (Separation of Concerns)**
- **API層**: エンドポイント定義とリクエスト処理
- **サービス層**: ビジネスロジックとAI機能
- **モデル層**: データ構造とバリデーション
- **コア層**: 共通機能とユーティリティ

### 2. **バージョン管理**
```
api/v1/           # Version 1 API
api/v2/           # 将来のVersion 2
```

### 3. **機能別分割**
```
services/ai/      # AI機能に特化
services/external/# 外部サービス連携
```

### 4. **環境別設定**
```
config/development.yaml  # 開発環境
config/production.yaml   # 本番環境
config/testing.yaml      # テスト環境
```

## 🚀 **利点**

### **スケーラビリティ**
- 機能追加時の影響範囲を最小化
- マイクロサービス分割が容易

### **保守性**
- 責務が明確で変更箇所を特定しやすい
- テストの書きやすさ

### **チーム開発**
- 並行開発が可能
- コードレビューの効率化

### **デプロイメント**
- 環境別設定で本番デプロイが安全
- CI/CDパイプラインとの親和性

## 📁 **ファイル命名規則**

### **Python ファイル**
- `snake_case.py` (例: `gemini_service.py`)
- クラス名: `PascalCase` (例: `GeminiService`)
- 関数名: `snake_case` (例: `generate_plan`)

### **ディレクトリ**
- `lowercase` or `snake_case`
- 複数形を使用 (例: `services`, `models`)

### **設定ファイル**
- `environment.yaml` (例: `development.yaml`)
- `.env.example` (環境変数テンプレート)

## 🔧 **推奨移行手順**

1. **コア機能の移動**: `config.py` → `core/config.py`
2. **API層の構築**: `api/v1/endpoints/` 作成
3. **サービス層の分割**: AI機能ごとにファイル分割
4. **テスト構造の整備**: 各層に対応するテスト作成
5. **ドキュメント整備**: API仕様書とセットアップガイド

この構造により、PRDで定義されたAI機能を効率的に開発・保守できます。
