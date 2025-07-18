"""Scrapbox API連携サービス"""

import asyncio
import logging
import re
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional
from urllib.parse import quote

import httpx

from app.services.gemini_service import GeminiService
from app.core.config import Settings

logger = logging.getLogger(__name__)


class ScrapboxService:
    """Scrapboxから学習記録を取得するサービス"""

    def __init__(self, timeout: float = 10.0, settings: Optional[Settings] = None):
        """
        Scrapboxサービスを初期化する

        Args:
            timeout: HTTPリクエストのタイムアウト（秒）
            settings: アプリケーション設定（省略時は自動作成）
        """
        self.base_url = "https://scrapbox.io/api"
        self.timeout = timeout

        # GeminiServiceを初期化
        if settings is None:
            settings = Settings()

        try:
            self.gemini_service: Optional[GeminiService] = GeminiService(settings)
        except Exception as e:
            logger.warning(f"Geminiサービスの初期化に失敗: {e}")
            self.gemini_service = None

    async def get_pages_list(self, project_name: str) -> List[Dict[str, Any]]:
        """
        指定されたプロジェクトのページ一覧を取得する

        Args:
            project_name: Scrapboxプロジェクト名

        Returns:
            List[Dict[str, Any]]: ページ情報のリスト

        Raises:
            Exception: API呼び出しエラー
        """
        url = f"{self.base_url}/pages/{project_name}"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)

                if response.status_code == 200:
                    data = response.json()
                    return data.get("pages", [])
                else:
                    logger.error(f"Scrapboxページ一覧取得エラー: {response.status_code}")
                    return []

        except Exception as e:
            logger.error(f"Scrapboxページ一覧取得中にエラー: {e}")
            return []

    async def get_page_text(self, project_name: str, page_title: str) -> str:
        """
        指定されたページの本文を取得する

        Args:
            project_name: Scrapboxプロジェクト名
            page_title: ページタイトル

        Returns:
            str: ページの本文

        Raises:
            Exception: API呼び出しエラー
        """
        # URLエンコード
        encoded_title = quote(page_title, safe="")
        url = f"{self.base_url}/pages/{project_name}/{encoded_title}/text"

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url)

                if response.status_code == 200:
                    return response.text
                else:
                    logger.error(f"Scrapboxページ本文取得エラー: {response.status_code}")
                    return ""

        except Exception as e:
            logger.error(f"Scrapboxページ本文取得中にエラー: {e}")
            return ""

    async def get_recent_pages(
        self, project_name: str, days: int = 7
    ) -> List[Dict[str, Any]]:
        """
        指定された期間内の最新ページを取得する

        Args:
            project_name: Scrapboxプロジェクト名
            days: 取得する日数（デフォルト7日）

        Returns:
            List[Dict[str, Any]]: 最新ページのリスト
        """
        pages = await self.get_pages_list(project_name)

        if not pages:
            return []

        # 最新の更新日時でソート
        sorted_pages = sorted(pages, key=lambda x: x.get("updated", 0), reverse=True)

        # 指定された日数以内のページをフィルタリング
        cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
        recent_pages = [
            page for page in sorted_pages if page.get("updated", 0) > cutoff_time
        ]

        return recent_pages

    async def get_learning_records(
        self, project_name: str, user_id: Optional[str] = None
    ) -> Dict[str, str]:
        """
        学習記録を取得してAI用に解析・整形する

        Args:
            project_name: Scrapboxプロジェクト名
            user_id: ユーザーID（現在は未使用）

        Returns:
            Dict[str, str]: 解析済み学習記録データ
        """
        if not project_name:
            return {
                "recent_progress": "Scrapboxプロジェクトが設定されていません",
                "weak_areas": "Scrapboxプロジェクトが設定されていません",
            }

        try:
            # 最近のページを取得
            recent_pages = await self.get_recent_pages(project_name, 90)

            if not recent_pages:
                return {
                    "recent_progress": "最近の学習記録が見つかりません",
                    "weak_areas": "分析できるデータがありません",
                }

            # ページの本文を取得
            page_contents = []
            for page in recent_pages[:10]:  # 最新10ページまで解析
                title = page.get("title", "")
                content = await self.get_page_text(project_name, title)

                if content:
                    page_contents.append(
                        {
                            "title": title,
                            "content": content,
                            "updated": page.get("updated", 0),
                        }
                    )

            # AI解析を実行
            ai_result = await self._analyze_with_ai(page_contents)

            # AI解析が失敗した場合は従来の方法にフォールバック
            if ai_result["recent_progress"] in [
                "AIサービスが利用できません",
                "AI解析でエラーが発生しました",
            ] or ai_result["weak_areas"] in ["AIサービスが利用できません", "AI解析でエラーが発生しました"]:
                logger.info("AI解析が利用できないため、従来の解析方法を使用します")

                # 従来のキーワードベース解析
                learning_keywords = []
                weak_areas_keywords = []

                for page in page_contents:
                    title = page["title"]
                    content = page["content"]

                    # 学習関連キーワードを抽出
                    learning_keywords.extend(
                        self._extract_learning_keywords(title, content)
                    )

                    # 弱点・課題関連キーワードを抽出
                    weak_areas_keywords.extend(
                        self._extract_weakness_keywords(title, content)
                    )

                # 従来の方法で結果を生成
                recent_progress = self._generate_recent_progress(page_contents)
                weak_areas = self._generate_weak_areas(weak_areas_keywords)

                return {"recent_progress": recent_progress, "weak_areas": weak_areas}

            # AI解析結果を返す
            return ai_result

        except Exception as e:
            logger.error(f"Scrapbox学習記録取得中にエラー: {e}")
            return {
                "recent_progress": "データ取得エラーが発生しました",
                "weak_areas": "データ取得エラーが発生しました",
            }

    def _extract_learning_keywords(self, title: str, content: str) -> List[str]:
        """
        タイトルと本文から学習関連キーワードを抽出する

        Args:
            title: ページタイトル
            content: ページ本文

        Returns:
            List[str]: 学習関連キーワードのリスト
        """
        text = f"{title} {content}"
        keywords = []

        # 学習関連パターン
        learning_patterns = [
            r"学習.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
            r"勉強.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
            r"習得.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
            r"理解.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
            r"完了.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
            r"実装.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
        ]

        for pattern in learning_patterns:
            matches = re.findall(pattern, text)
            keywords.extend(matches)

        # プログラミング言語やフレームワークを抽出
        tech_keywords = re.findall(
            r"\b(Python|JavaScript|TypeScript|React|Vue|FastAPI|Django|Flask|Node\.js|Docker|Kubernetes|AWS|GCP|SQL|NoSQL|Git|GitHub)\b",
            text,
            re.IGNORECASE,
        )
        keywords.extend(tech_keywords)

        return list(set(keywords))

    def _extract_weakness_keywords(self, title: str, content: str) -> List[str]:
        """
        タイトルと本文から弱点・課題関連キーワードを抽出する

        Args:
            title: ページタイトル
            content: ページ本文

        Returns:
            List[str]: 弱点・課題関連キーワードのリスト
        """
        text = f"{title} {content}"
        keywords = []

        # 弱点関連パターン
        weakness_patterns = [
            r"苦手.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
            r"難しい.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
            r"わからない.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
            r"課題.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
            r"問題.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
            r"エラー.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
            r"つまづ.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
            r"詰まっ.*?([ァ-ヶー一-龯a-zA-Z0-9]+)",
        ]

        for pattern in weakness_patterns:
            matches = re.findall(pattern, text)
            keywords.extend(matches)

        return list(set(keywords))

    def _generate_recent_progress(self, page_contents: List[Dict[str, Any]]) -> str:
        """
        ページ内容から最近の進捗を生成する

        Args:
            page_contents: ページ内容のリスト

        Returns:
            str: 最近の進捗まとめ
        """
        if not page_contents:
            return "最近の学習記録が見つかりません"

        progress_items = []

        for page in page_contents[:3]:  # 最新3ページ
            title = page["title"]
            content = page["content"]

            # タイトルから進捗を抽出
            if title:
                progress_items.append(f"「{title}」について学習")

            # 本文から具体的な活動を抽出
            activity_patterns = [
                r"実装した",
                r"作成した",
                r"学習した",
                r"理解した",
                r"完了した",
                r"試した",
                r"やってみた",
            ]

            for pattern in activity_patterns:
                if pattern in content:
                    # パターンの前後の文脈を取得
                    context_match = re.search(f".{{0,20}}{pattern}.{{0,20}}", content)
                    if context_match:
                        context = context_match.group().strip()
                        progress_items.append(context)
                        break

        if progress_items:
            return " / ".join(progress_items[:3])
        else:
            return "学習活動を継続中"

    def _generate_weak_areas(self, weak_keywords: List[str]) -> str:
        """
        弱点キーワードから弱点分野を生成する

        Args:
            weak_keywords: 弱点関連キーワードのリスト

        Returns:
            str: 弱点分野まとめ
        """
        if not weak_keywords:
            return "特に弱点は見つかりませんでした"

        # 重複を除去し、上位3つを選択
        unique_keywords = list(set(weak_keywords))
        top_keywords = unique_keywords[:3]

        if top_keywords:
            return ", ".join(top_keywords)
        else:
            return "継続的な学習により改善中"

    async def _analyze_with_ai(
        self, page_contents: List[Dict[str, Any]]
    ) -> Dict[str, str]:
        """
        AIを使ってページ内容を解析し、学習記録と弱点分野を抽出する

        Args:
            page_contents: ページ内容のリスト

        Returns:
            Dict[str, str]: 解析結果（recent_progress、weak_areas）
        """
        if not self.gemini_service or not page_contents:
            return {"recent_progress": "AIサービスが利用できません", "weak_areas": "AIサービスが利用できません"}

        # ページ内容をテキストとして整理
        pages_text = []
        for i, page in enumerate(page_contents[:10]):  # 最新10ページまで
            title = page.get("title", "")
            content = page.get("content", "")
            updated = page.get("updated", 0)

            # タイムスタンプを日付に変換
            if updated:
                date = datetime.fromtimestamp(updated).strftime("%Y-%m-%d")
            else:
                date = "不明"

            page_text = f"【{title}】({date})\n{content[:500]}"  # 500文字まで
            pages_text.append(page_text)

        combined_text = "\n\n---\n\n".join(pages_text)

        # AI解析用プロンプト
        analysis_prompt = f"""
以下はScrapboxの学習記録です。これらの記録を分析して、以下の2つの情報を抽出してください：

1. **最近の進捗**: 最近の学習活動、達成した内容、進んでいる分野を簡潔にまとめてください
2. **弱点・課題分野**: 困っていること、苦手分野、エラーや問題、未解決の課題を特定してください

## Scrapboxの記録:
{combined_text}

## 出力形式:
最近の進捗: [具体的な学習活動や達成内容]
弱点分野: [課題や困りごと、苦手分野をカンマ区切り]

注意：
- 日本語の表現や文脈を理解して分析してください
- データがない場合は適切なメッセージを返してください
"""

        try:
            # AI解析を実行
            response = await self.gemini_service.generate_text(analysis_prompt)

            # レスポンスをパース
            recent_progress = "AIによる解析結果が取得できませんでした"
            weak_areas = "AIによる解析結果が取得できませんでした"

            if response:
                lines = response.strip().split("\n")
                for line in lines:
                    if line.startswith("最近の進捗:"):
                        recent_progress = line.replace("最近の進捗:", "").strip()
                    elif line.startswith("弱点分野:"):
                        weak_areas = line.replace("弱点分野:", "").strip()

            return {"recent_progress": recent_progress, "weak_areas": weak_areas}

        except Exception as e:
            logger.error(f"AI解析中にエラー: {e}")
            return {
                "recent_progress": "AI解析でエラーが発生しました",
                "weak_areas": "AI解析でエラーが発生しました",
            }


# シングルトンインスタンス
_scrapbox_service = None


def get_scrapbox_service() -> ScrapboxService:
    """
    Scrapboxサービスのシングルトンインスタンスを取得する

    Returns:
        ScrapboxService: Scrapboxサービスインスタンス
    """
    global _scrapbox_service
    if _scrapbox_service is None:
        _scrapbox_service = ScrapboxService()
    return _scrapbox_service


async def fetch_learning_records_from_scrapbox(
    user_id: str, project_name: str
) -> Dict[str, str]:
    """
    Scrapboxから学習記録を取得し、分析用データを返す

    Args:
        user_id: ユーザーID
        project_name: Scrapboxプロジェクト名

    Returns:
        Dict[str, str]: 分析済み学習記録データ
    """
    service = get_scrapbox_service()
    return await service.get_learning_records(project_name, user_id)
