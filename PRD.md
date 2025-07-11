# バックエンドPRD

## 1. 目的・背景

- **目的**：学習記録アプリのバックエンドを整備し、フロントと連携して学習データの保存・取得、AIプラン生成、育成ゲーム機能を提供
- **背景**：
  - Next.js/PandaCSSでフロント設計済み
  - Python+FastAPIでビジネスロジックを実装予定
  - SupabaseをDB＆Auth基盤として利用

## 2. 想定ユーザー

- 学習記録アプリの最終ユーザー（学生・社会人）
- フロント開発チーム／QAエンジニア

## 3. 課題

- フロントからのデータ登録・取得APIが未定義
- 安全かつスケーラブルなAIプラン生成APIが必要
- Supabase Auth／RLSを組み込んだ堅牢な認証・権限管理が必須

## 4. 解決策

- FastAPIでRESTfulエンドポイントを実装
- Supabase AuthでJWT認証＋Row-Level Security
- AIプランをモジュール化しAPI経由で提供
- 育成ゲーム機能用の専用エンドポイント群を用意

## 5. 機能要件

| 機能                 | Must (PoC)                                 | Nice-to-have                       |
|:--------------------|:-------------------------------------------|:-----------------------------------|
| 学習記録CRUD        | POST/GET/PUT/DELETE `/api/records`        | バルクインポート、タグ管理        |
| 学習履歴サマリー    | GET `/api/records/summary?period=daily`   | week/month フィルター              |
| AIプラン生成        | POST `/api/plan` → JSON返却              | プラン編集履歴、有効期限管理      |
| ペットステータス更新| GET/POST `/api/game/status`, `/api/game/feed` | ranking、マルチセッション管理      |

## 6. 非機能要件

- **パフォーマンス**：各API応答 ≤ 200ms
- **認証**：Supabase JWT（自動リフレッシュ）
- **セキュリティ**：
  - CORS制限＋JWTでCSRF不要
  - Supabase RLSでテーブル単位アクセス制御
- **テスト**：Pytest＋HTTPX でユニット／統合テスト

## 7. KPI／検証指標

- APIエラー率 ≤ 1%
- プラン生成API平均応答 ≤ 300ms
- テストカバレッジ ≥ 80%

## 8. API設計例
POST   /api/auth/signup    # ユーザー登録
POST   /api/auth/signin    # ログイン
GET    /api/records        # 取得
POST   /api/records        # 登録
GET    /api/records/:id    # 詳細
PUT    /api/records/:id    # 更新
DELETE /api/records/:id    # 削除
GET    /api/records/summary?period={daily,weekly,monthly}
POST   /api/plan           # AIプラン生成
GET    /api/game/status    # ステータス取得
POST   /api/game/feed      # 餌をあげる


## 9. データモデル (Supabase テーブル)

| テーブル名    | 主なカラム                               | RLSポリシー                          |
|:-------------|:------------------------------------------|:-------------------------------------|
| users        | id, email, created_at                    | 自身のレコードのみ読取/更新可       |
| records      | id, user_id, subject, duration, memo, created_at | user_id一致時のみ操作許可    |
| plans        | id, user_id, plan_date, content, created_at     | 同上                              |
| game_status  | id, user_id, hunger, happiness, updated_at      | 同上                              |

## 10. 技術スタック

- **バックエンド**：Python 3.10+, FastAPI
- **DB/Auth**：Supabase (PostgreSQL + Auth + RLS)
- **デプロイ**：Vercel (Edge Functions) or Railway
- **CI/CD**：GitHub Actions (Lint → テスト → デプロイ)

## 11. 開発スケジュール

| Day | タスク                                                        |
|:----|:-------------------------------------------------------------|
| 1   | リポジトリ初期化、FastAPI＋Supabase連携設定、DBマイグレーション |
| 2   | 認証API実装＆テスト                                           |
| 3   | 学習記録CRUD実装＆テスト                                       |
| 4   | サマリーAPI＆ステータス取得API実装                            |
| 5   | AIプラン生成エンドポイント＆LLM連携                          |
| 6   | 餌機能・ステータス更新API実装                                |
| 7   | 統合テスト・ドキュメント整備 → フロント連携確認 → デプロイ準備 |