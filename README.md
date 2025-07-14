# ChoibenAssist AI Backend

[![Python](https://img.shields.io/badge/Python-3.12+-blue?style=flat-square&logo=python)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-green?style=flat-square&logo=fastapi)](https://fastapi.tiangolo.com/)
[![License](https://img.shields.io/badge/License-MIT-yellow?style=flat-square)](#license)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg?style=flat-square)](https://github.com/psf/black)

学習記録アプリのAI機能を提供するマイクロサービス

## Table of Contents

- [概要](#概要)
- [機能](#機能)
- [技術スタック](#技術スタック)
- [プロジェクト構造](#プロジェクト構造)
- [セットアップ](#セットアップ)
- [API エンドポイント](#api-エンドポイント)
- [開発](#開発)
- [テスト](#テスト)
- [デプロイメント](#デプロイメント)
- [コントリビューション](#コントリビューション)

## 概要

ChoibenAssist AI BackendはFastAPIで構築されたマイクロサービスで、学習記録アプリにAI機能を提供します。Google Gemini 2.0 Flash-Liteを活用し、個人化された学習プラン生成、進捗分析、学習アドバイスを提供します。

### 主な特徴

- 🤖 **AI駆動**: Google Gemini 2.0 Flash-Liteによる高品質なAI応答
- 🚀 **高パフォーマンス**: FastAPIによる非同期処理
- 🔒 **セキュア**: API キー認証とレート制限
- 📊 **データ連携**: Supabaseとのシームレスな統合
- 🧪 **テスト済み**: 包括的なテストスイート

## 機能

| 機能 | エンドポイント | 説明 |
|-----|-------------|------|
| **TODOリスト生成** | `POST /api/ai/todo` | 日々の効果的な学習タスクの自動生成 |
| **学習進捗分析** | `POST /api/ai/analysis` | データに基づいた進捗分析と改善提案 |
| **学習アドバイス** | `POST /api/ai/advice` | パーソナライズされた学習指導 |
| **目標設定支援** | `POST /api/ai/goals` | SMART目標の提案とトラッキング |

## 技術スタック

### コア技術
- **Runtime**: Python 3.12+
- **Web Framework**: FastAPI 0.104+
- **ASGI Server**: Uvicorn
- **AI/LLM**: Google Gemini 2.0 Flash-Lite

### データ & 外部連携
- **External API**: Supabase REST API
- **Data Validation**: Pydantic 2.5+
- **Environment**: python-dotenv

### 開発・テスト
- **Testing**: Pytest + HTTPX
- **Code Quality**: Black, isort, Flake8, MyPy
- **Documentation**: Swagger UI (FastAPI自動生成)

## プロジェクト構造

```
ChoibenAssist-Back/
├── 📁 app/                              # メインアプリケーション
│   ├── 📄 __init__.py
│   ├── 📄 main.py                       # FastAPIアプリケーションエントリーポイント
│   │
│   ├── 📁 api/                          # API層 - エンドポイント定義
│   │   ├── 📄 __init__.py
│   │   ├── 📄 deps.py                   # API依存関係
│   │   └── 📁 v1/                       # APIバージョン管理
│   │       ├── 📄 __init__.py
│   │       ├── 📄 api.py                # APIルーター統合
│   │       └── 📁 endpoints/            # 個別エンドポイント
│   │           ├── 📄 __init__.py
│   │           ├── 📄 ai.py             # AI機能エンドポイント
│   │           └── 📄 health.py         # ヘルスチェック
│   │
│   ├── 📁 core/                         # コア機能 - アプリケーション基盤
│   │   ├── 📄 __init__.py
│   │   ├── 📄 config.py                 # 設定管理
│   │   ├── 📄 security.py               # セキュリティ機能
│   │   ├── 📄 logging.py                # ログ設定
│   │   └── 📄 exceptions.py             # カスタム例外
│   │
│   ├── 📁 models/                       # データモデル - ドメインモデル
│   │   ├── 📄 __init__.py
│   │   ├── 📄 ai_models.py              # AI機能のPydanticモデル
│   │   └── 📄 base.py                   # 基底モデル
│   │
│   ├── 📁 schemas/                      # スキーマ - API入出力
│   │   ├── 📄 __init__.py
│   │   ├── 📄 ai_schemas.py             # AI機能関連スキーマ
│   │   ├── 📄 requests.py               # リクエストスキーマ
│   │   ├── 📄 responses.py              # レスポンススキーマ
│   │   └── 📄 enums.py                  # 列挙型定義
│   │
│   ├── 📁 services/                     # ビジネスロジック層
│   │   ├── 📄 __init__.py
│   │   ├── 📁 ai/                       # AI機能専用サービス
│   │   │   ├── 📄 __init__.py
│   │   │   ├── 📄 plan_generator.py     # 学習プラン生成
│   │   │   ├── 📄 todo_generator.py     # TODO生成
│   │   │   ├── 📄 analyzer.py           # 学習分析
│   │   │   └── 📄 advisor.py            # アドバイス生成
│   │   │
│   │   └── 📁 external/                 # 外部サービス連携
│   │       ├── 📄 __init__.py
│   │       ├── 📄 gemini_client.py      # Gemini APIクライアント
│   │       └── 📄 supabase_client.py    # Supabase APIクライアント
│   │
│   └── 📁 utils/                        # ユーティリティ
│       ├── 📄 __init__.py
│       ├── 📄 helpers.py                # 汎用ヘルパー関数
│       └── 📄 validators.py             # バリデーション機能
│
├── 📁 tests/                            # テスト
│   ├── 📄 __init__.py
│   ├── 📄 conftest.py                   # pytest設定
│   ├── 📄 test_main.py                  # メインアプリケーションテスト
│   ├── 📁 api/                          # APIテスト
│   └── 📁 services/                     # サービス層テスト
│
├── 📁 docs/                             # ドキュメント
│   ├── 📄 class_diagram.md              # システム設計図
│   ├── 📄 SOW.md                        # 作業範囲書
│   └── 📄 directory_structure.md        # ディレクトリ構造説明
│
├── 📁 scripts/                          # 運用スクリプト
│   └── 📄 start.py                      # 開発サーバー起動
│
├── 📄 .env.example                      # 環境変数テンプレート
├── 📄 .gitignore                        # Git無視ファイル
├── 📄 requirements.txt                  # Python依存関係
├── 📄 requirements-dev.txt              # 開発用依存関係
├── 📄 run.py                            # 開発サーバー起動スクリプト
├── 📄 PRD.md                            # プロダクト要求仕様
└── 📄 README.md                         # プロジェクト説明
```

### 設計原則

#### 1. **レイヤードアーキテクチャ**
```
API層 → サービス層 → モデル層
  ↓        ↓         ↓
エンドポイント → ビジネスロジック → データ構造
```

#### 2. **責務の分離**
- **API層**: HTTPリクエスト/レスポンス処理
- **サービス層**: ビジネスロジックとAI機能
- **モデル層**: データ構造とバリデーション
- **コア層**: 横断的関心事（設定、セキュリティ、ログ）

#### 3. **依存関係の方向**
- 外側から内側への依存のみ
- コア機能は外部ライブラリに依存しない
- 依存関係注入によるテスタビリティ向上

## セットアップ

### 前提条件

- Python 3.12+ がインストールされていること
- Git がインストールされていること
- make がインストールされていること（macOSには標準でインストール済み）
- Google Gemini API キーを取得済みであること
- Supabase プロジェクトが作成済みであること

### 🚀 クイックスタート（推奨）

Makefileを使用した自動セットアップ：

```bash
# 1. プロジェクトのクローン
git clone https://github.com/develoop-official/ChoibenAssist-Back.git
cd ChoibenAssist-Back

# 2. 自動セットアップ（仮想環境作成 + 依存関係インストール + 環境変数設定）
make setup

# 3. .envファイルを編集（API キーなどを設定）
nano .env  # または お好みのエディタで編集

# 4. 開発サーバー起動
make run
```

**さらにクイックなセットアップ（ワンライナー）：**

```bash
# 自動セットアップスクリプトを使用
git clone https://github.com/develoop-official/ChoibenAssist-Back.git && cd ChoibenAssist-Back && chmod +x scripts/quick-setup.sh && ./scripts/quick-setup.sh
```

利用可能なMakeコマンド一覧：

```bash
# ヘルプを表示
make help

# 主要コマンド
make setup          # 完全な初期セットアップ
make run            # 開発サーバー起動
make test           # テスト実行
make test-gemini    # Gemini APIのリアルテスト
make quality        # コード品質チェック（フォーマット + リント + 型チェック）
make clean          # キャッシュファイルの削除
```

### 📋 手動セットアップ

Makefileを使わない場合の手動セットアップ手順：

#### 1. プロジェクトのクローン

```bash
git clone https://github.com/develoop-official/ChoibenAssist-Back.git
cd ChoibenAssist-Back
```

#### 2. 仮想環境の作成と有効化

```bash
# 仮想環境の作成
python -m venv .venv

# 仮想環境の有効化
# Windows (PowerShell)
.venv\Scripts\Activate.ps1
# Windows (Command Prompt)
.venv\Scripts\activate
# macOS/Linux
source .venv/bin/activate
```

#### 3. 依存関係のインストール

```bash
# 本番用依存関係
pip install -r requirements.txt

# 開発用依存関係
pip install -r requirements-dev.txt
```

#### 4. 環境変数の設定

```bash
# 環境変数ファイルをコピー
cp .env.example .env

# .envファイルを編集
# Windows
notepad .env
# macOS/Linux
nano .env
```

#### 必須環境変数

```env
# AI/LLM設定
GEMINI_API_KEY=your_google_gemini_api_key_here

# Supabase設定
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=your_supabase_anonymous_key_here

# API設定
API_SECRET_KEY=your_strong_secret_key_here

# アプリケーション設定
DEBUG=True
ENVIRONMENT=development
ALLOWED_ORIGINS=http://localhost:3000,http://127.0.0.1:3000

# Server設定
HOST=127.0.0.1
PORT=8000

# レート制限
RATE_LIMIT_PER_MINUTE=100

# ログレベル
LOG_LEVEL=INFO
```

#### 5. 開発サーバーの起動

**Makefileを使用（推奨）：**

```bash
# 通常起動
make run

# 自動リロード付き起動
make run-reload
```

**手動起動：**

```bash
# 推奨方法: run.pyスクリプトを使用
python run.py

# 代替方法: uvicornを直接使用
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```

#### 6. 動作確認

サーバーが起動したら、以下のURLでアクセス確認：

- **API ルート**: http://127.0.0.1:8000
- **ヘルスチェック**: http://127.0.0.1:8000/api/health
- **API ドキュメント**: http://127.0.0.1:8000/docs
- **ReDoc**: http://127.0.0.1:8000/redoc

**Makefileでのヘルスチェック：**

```bash
# APIが起動しているかチェック
make check-health

# ブラウザでAPI ドキュメントを開く
make docs
```

## 🛠️ Makefile コマンドリファレンス

### 🚀 セットアップコマンド

| コマンド | 説明 |
|---------|------|
| `make setup` | **完全な初期セットアップ**（仮想環境 + 依存関係 + 環境変数） |
| `make venv` | Python仮想環境の作成 |
| `make install-deps` | すべての依存関係をインストール |
| `make setup-env` | `.env`ファイルをテンプレートから作成 |
| `make verify-setup` | セットアップが正しく完了したかの確認 |

### 🔧 開発コマンド

| コマンド | 説明 |
|---------|------|
| `make run` | 開発サーバー起動 |
| `make run-reload` | 自動リロード付きサーバー起動 |
| `make shell` | 仮想環境のアクティベート手順を表示 |

### ✅ コード品質コマンド

| コマンド | 説明 |
|---------|------|
| `make format` | Black + isort でコードフォーマット |
| `make lint` | Flake8 でリント実行 |
| `make typecheck` | MyPy で型チェック |
| `make quality` | 上記3つを一括実行 |

### 🧪 テストコマンド

| コマンド | 説明 |
|---------|------|
| `make test` | テスト実行 |
| `make test-verbose` | 詳細出力付きテスト |
| `make test-coverage` | カバレッジ付きテスト |
| `make test-watch` | ファイル変更監視でテスト自動実行 |
| `make test-gemini` | **Gemini APIのリアルテスト** |

### 🌐 API関連コマンド

| コマンド | 説明 |
|---------|------|
| `make check-health` | APIヘルスチェック |
| `make docs` | ブラウザでAPI ドキュメントを開く |

### 🧹 クリーンアップコマンド

| コマンド | 説明 |
|---------|------|
| `make clean` | キャッシュファイル削除 |
| `make clean-venv` | 仮想環境削除 |
| `make reset` | 完全リセット（clean + clean-venv） |

### 🚀 本番環境コマンド

| コマンド | 説明 |
|---------|------|
| `make install-prod` | 本番用依存関係のみインストール |
| `make run-prod` | Gunicorn での本番サーバー起動 |

### 🔧 ユーティリティコマンド

| コマンド | 説明 |
|---------|------|
| `make info` | プロジェクト情報表示 |
| `make update` | 全依存関係の更新 |
| `make requirements` | 現在の環境から requirements.txt 生成 |
| `make help` | 利用可能なコマンド一覧表示 |

## 🚨 トラブルシューティング

### よくある問題と解決法

#### 1. `pydantic-core` のビルドエラー

**問題:** `ERROR: Failed building wheel for pydantic-core`

**解決法:**
```bash
# 1. 仮想環境をリセット
make reset

# 2. 新しい環境でセットアップ
make setup

# または手動で：
make clean-venv
make venv
.venv/bin/pip install --upgrade pip setuptools wheel
.venv/bin/pip install --no-cache-dir -r requirements.txt
```

#### 2. Python 3.13での依存関係解決の遅延

**問題:** pipインストール時に「This is taking longer than usual」

**解決法:**
- これは正常な動作です。Python 3.13ではパッケージの互換性チェックに時間がかかることがあります
- しばらく待つか、Ctrl+Cで中断してから再実行してください

#### 3. makeコマンドが見つからない

**問題:** `make: command not found`

**解決法:**
```bash
# macOS
xcode-select --install

# Ubuntu/Debian
sudo apt-get install build-essential

# CentOS/RHEL
sudo yum groupinstall 'Development Tools'
```

#### 4. 仮想環境の有効化

**問題:** 仮想環境が有効化されない

**解決法:**
```bash
# 手動で有効化
source .venv/bin/activate

# または makeで確認
make shell
```

#### 5. ポート使用中エラー

**問題:** `Address already in use`

**解決法:**
```bash
# ポート8000を使用しているプロセスを確認
lsof -i :8000

# プロセスを終了
kill -9 <PID>

# または別のポートを使用
uvicorn app.main:app --host 127.0.0.1 --port 8001
```

## Supabase データベース

### ユーザープロファイル

#### `user_profiles` テーブル（ユーザープロファイル）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| `id` | UUID | ユーザーID | PRIMARY KEY, REFERENCES auth.users(id) |
| `username` | TEXT | ユーザー名 | UNIQUE |
| `full_name` | TEXT | フルネーム | |
| `avatar_url` | TEXT | アバター画像URL | |
| `learning_preferences` | JSONB | 学習設定 | DEFAULT '{}' |
| `timezone` | TEXT | タイムゾーン | DEFAULT 'Asia/Tokyo' |
| `created_at` | TIMESTAMP | 作成日時 | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | 更新日時 | DEFAULT NOW() |

### 学習記録

#### `study_records` テーブル（学習記録）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| `id` | UUID | 記録ID | PRIMARY KEY |
| `user_id` | UUID | ユーザーID | REFERENCES auth.users(id) |
| `subject` | TEXT | 学習科目 | NOT NULL |
| `date` | DATE | 学習日 | NOT NULL |
| `duration_minutes` | INTEGER | 学習時間（分） | NOT NULL, > 0 |
| `score` | INTEGER | スコア | 0-100 |
| `difficulty` | TEXT | 難易度 | 'easy', 'medium', 'hard' |
| `notes` | TEXT | メモ | |
| `tags` | TEXT[] | タグ | DEFAULT '{}' |
| `goals` | TEXT | 学習目標 | |
| `progress_rate` | DECIMAL(5,2) | 進捗率 | DEFAULT 0.0 |
| `created_at` | TIMESTAMP | 作成日時 | DEFAULT NOW() |
| `updated_at` | TIMESTAMP | 更新日時 | DEFAULT NOW() |

### TODOリスト

#### `todo_items` テーブル（TODOリスト）
| カラム名 | 型 | 説明 | 制約 |
|---------|---|------|------|
| `id` | UUID | タスクID | PRIMARY KEY, DEFAULT gen_random_uuid() |
| `user_id` | UUID | ユーザーID | NOT NULL, REFERENCES auth.users(id) ON DELETE CASCADE |
| `task` | TEXT | タスク内容 | NOT NULL |
| `due_date` | DATE | 締切日 | |
| `status` | TEXT | タスクの状態 | DEFAULT 'pending' ('pending', 'completed'など) |
| `created_at` | TIMESTAMPTZ | 作成日時 | NOT NULL, DEFAULT NOW() |
| `updated_at` | TIMESTAMPTZ | 更新日時 | NOT NULL, DEFAULT NOW() |




### セキュリティ設定

すべてのテーブルにRow Level Security (RLS)を設定し、ユーザーは自分のデータのみアクセス可能にします。

### 必要なインデックス

各テーブルに以下のインデックスを作成することを推奨：
- `user_id`カラムへのインデックス
- よく使用される検索条件（`date`, `subject`など）
- 複合インデックス（`user_id + date`など）

## API エンドポイント

### 認証

すべてのAI関連エンドポイントには認証が必要です：

```http
Authorization: Bearer {API_SECRET_KEY}
Content-Type: application/json
```

### ヘルスチェック

| メソッド | エンドポイント | 説明 | 認証 |
|---------|-------------|------|-----|
| `GET` | `/api/health` | 基本ヘルスチェック | 不要 |
| `GET` | `/api/health/detailed` | 詳細ヘルスチェック | 不要 |

### AI サービス

| メソッド | エンドポイント | 説明 | 認証 |
|---------|-------------|------|-----|
| `POST` | `/api/ai/todo/{user_id}` | 今日のTODOリスト生成 | 必要 |
| `POST` | `/api/ai/analysis/{user_id}` | 学習進捗分析 | 必要 |
| `POST` | `/api/ai/advice/{user_id}` | 学習アドバイス | 必要 |
| `POST` | `/api/ai/goals/{user_id}` | 学習目標設定支援 | 必要 |

### リクエスト例

#### 今日のTODO提案

```bash
curl -X POST "http://127.0.0.1:8000/api/ai/todo/user123?date=2025-07-14" \
  -H "Authorization: Bearer your_api_secret_key" \
  -H "Content-Type: application/json" \
  -d '{
    "time_available": 90,
    "recent_progress": [
      {"subject": "数学", "progress": 70},
      {"subject": "英語", "progress": 50}
    ]
  }'
```

## 開発

### 開発環境のセットアップ

**Makefileを使用（推奨）：**

```bash
# 開発用の完全セットアップ
make setup

# コード品質ツールの一括実行
make quality
```

**手動セットアップ：**

```bash
# 開発用依存関係のインストール
pip install -r requirements-dev.txt

# pre-commit フックの設定（オプション）
pre-commit install
```

### コード品質ツール

**Makefileを使用：**

```bash
# コードフォーマット + リント + 型チェックを一括実行
make quality

# 個別実行
make format      # Black + isort でフォーマット
make lint        # Flake8 でリント
make typecheck   # MyPy で型チェック
```

**手動実行：**

```bash
# コードフォーマット
black app/ tests/
isort app/ tests/

# リント
flake8 app/ tests/

# 型チェック
mypy app/

# 全て一括実行
python scripts/lint.py
```

### ホットリロード開発

**Makefileを使用：**

```bash
# 自動リロード付きサーバー起動
make run-reload
```

**手動実行：**

開発中は`run.py`を使用することで、ファイル変更時の自動リロードが有効になります：

```bash
python run.py
```

### デバッグ

VS Codeでのデバッグ設定例（`.vscode/launch.json`）：

```json
{
    "version": "0.2.0",
    "configurations": [
        {
            "name": "FastAPI",
            "type": "python",
            "request": "launch",
            "program": "run.py",
            "console": "integratedTerminal",
            "env": {
                "PYTHONPATH": "${workspaceFolder}"
            }
        }
    ]
}
```

## テスト

### テストの実行

**Makefileを使用（推奨）：**

```bash
# 基本テスト実行
make test

# 詳細出力付きテスト
make test-verbose

# カバレッジ付きテスト
make test-coverage

# ファイル変更監視でテスト自動実行
make test-watch
```

**手動実行：**

```bash
# 全テスト実行
pytest

# カバレッジ付きテスト
pytest --cov=app --cov-report=html

# 特定のテストファイル
pytest tests/test_main.py

# 特定のテスト関数
pytest tests/test_main.py::test_health_check

# 詳細出力
pytest -v

# 失敗時のデバッグ情報
pytest -vvv --tb=long
```

### テストカバレッジ

**Makefileを使用：**

```bash
# カバレッジレポート生成
make test-coverage

# HTMLレポートは htmlcov/ ディレクトリに生成されます
```

**手動実行：**

```bash
# カバレッジレポートの生成
pytest --cov=app --cov-report=html --cov-report=term

# カバレッジレポートの確認
open htmlcov/index.html  # macOS
start htmlcov/index.html # Windows
```

### テスト環境の設定

テスト用の環境変数は`tests/conftest.py`で管理：

```python
# テスト用の設定オーバーライド
@pytest.fixture
def test_settings():
    return Settings(
        environment="testing",
        debug=False,
        gemini_api_key="test_key"
    )
```

### 🤖 Gemini AIサービスのテスト

**リアルAPIテスト（APIキー必要）:**

```bash
# .envファイルにGEMINI_API_KEYを設定してから実行
make test-gemini

# 手動実行
python scripts/test_gemini.py
```

**ユニットテスト（モック使用）:**

```bash
# Geminiサービスのユニットテスト
pytest tests/test_gemini_service.py -v

# 特定のテストケース
pytest tests/test_gemini_service.py::TestGeminiService::test_generate_learning_plan -v
```

**テスト内容:**
- 基本的なテキスト生成
- 学習プラン生成
- TODO生成
- クイックレスポンス（モチベーション、ティップ、励まし）
- レスポンス速度測定
- ヘルスチェック
- プロンプトシステム検証

## デプロイメント

### Railway

1. **Railwayアカウントの作成**
   - [Railway](https://railway.app)でアカウント作成

2. **GitHubリポジトリの接続**
   ```bash
   # Railway CLIのインストール
   npm install -g @railway/cli
   
   # ログイン
   railway login
   
   # プロジェクトの初期化
   railway init
   ```

3. **環境変数の設定**
   - Railway ダッシュボードで環境変数を設定
   - `.env.example`を参考に必要な値を入力

4. **デプロイ**
   ```bash
   # 手動デプロイ
   railway up
   
   # 自動デプロイはmainブランチへのpushで実行
   ```

### Google Cloud Run

```bash
# Google Cloud SDKのインストールとログイン
gcloud auth login
gcloud config set project your-project-id

# コンテナのビルドとデプロイ
gcloud run deploy choibenassist-ai \
  --source . \
  --platform managed \
  --region asia-northeast1 \
  --allow-unauthenticated \
  --set-env-vars GEMINI_API_KEY=your_key,SUPABASE_URL=your_url
```

### Docker（ローカル確認用）

```bash
# イメージのビルド
docker build -t choibenassist-ai .

# コンテナの実行
docker run -p 8000:8000 --env-file .env choibenassist-ai
```

### パフォーマンス最適化

#### 本番環境での推奨設定

```bash
# Gunicornでの起動例
gunicorn app.main:app \
  --workers 4 \
  --worker-class uvicorn.workers.UvicornWorker \
  --bind 0.0.0.0:8000 \
  --preload \
  --max-requests 1000 \
  --max-requests-jitter 100
```

## コントリビューション

### 開発フロー

1. **Issue の作成**
   - バグレポートや機能要求をIssueで報告

2. **ブランチの作成**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **開発とテスト**
   ```bash
   # 開発
   # ...
   
   # テスト
   pytest
   
   # コード品質チェック
   black app/ tests/
   flake8 app/ tests/
   ```

4. **プルリクエスト**
   - 詳細な説明とテスト結果を含める
   - レビューを経てmainブランチにマージ

### コーディング規約

- **PEP 8** に準拠
- **Black** によるコードフォーマット
- **型ヒント** の使用を推奨。APIスキーマやPydanticモデルでの型定義は必須。
- **ドキュメンテーション** の充実
  - **APIドキュメント** はFastAPIの自動生成機能を利用
  - **コードコメント** は必要な箇所に記述
  - **関数・クラス** の説明は必須
  - **Docstring** 記述（Google Style）
  - できれば日本語で記述

### コミットメッセージ

```
feat: 新機能の追加
fix: バグ修正
docs: ドキュメントの更新
style: コードスタイルの修正
refactor: リファクタリング
test: テストの追加・修正
chore: ビルドやツールの変更
```

---

## ライセンス

このプロジェクトはMITライセンスの下で公開されています。詳細は[LICENSE](LICENSE)ファイルを参照してください。

## サポート

- **Issue**: [GitHub Issues](https://github.com/develoop-official/ChoibenAssist-Back/issues)
- **ドキュメント**: [docs/](docs/)
- **チーム**: develoop-official

---

**ChoibenAssist** - 学習を加速するAIアシスタント
