"""Supabaseとの連携サービス"""

import asyncio
import logging
from typing import Any, Dict, Optional

import httpx

from app.core.config import settings

logger = logging.getLogger(__name__)


class SupabaseService:
    """Supabaseとの連携を管理するサービス"""

    def __init__(self):
        """
        Supabaseサービスを初期化する
        """
        self.base_url = settings.supabase_url
        self.anon_key = settings.supabase_anon_key
        self.timeout = 10.0

        if not self.base_url or not self.anon_key:
            logger.warning("Supabase認証情報が設定されていません")

    async def get_user_profile(self, user_id: str) -> Optional[Dict[str, Any]]:
        """
        指定されたユーザーのプロファイル情報を取得する

        Args:
            user_id: ユーザーID

        Returns:
            Optional[Dict[str, Any]]: ユーザープロファイル情報、エラー時はNone
        """
        if not self.base_url or not self.anon_key:
            logger.error("Supabase認証情報が設定されていません")
            return None

        url = f"{self.base_url}/rest/v1/user_profiles"
        headers = {
            "apikey": self.anon_key,
            "Authorization": f"Bearer {self.anon_key}",
            "Content-Type": "application/json",
        }

        params = {"id": f"eq.{user_id}", "select": "*"}

        try:
            async with httpx.AsyncClient(timeout=self.timeout) as client:
                response = await client.get(url, headers=headers, params=params)

                if response.status_code == 200:
                    data = response.json()
                    if data and len(data) > 0:
                        return data[0]
                    else:
                        logger.warning(f"ユーザーID {user_id} のプロファイルが見つかりません")
                        return None
                else:
                    logger.error(f"Supabaseプロファイル取得エラー: {response.status_code}")
                    return None

        except Exception as e:
            logger.error(f"Supabaseプロファイル取得中にエラー: {e}")
            return None

    async def get_user_scrapbox_project(self, user_id: str) -> Optional[str]:
        """
        指定されたユーザーのScrapboxプロジェクト名を取得する

        Args:
            user_id: ユーザーID

        Returns:
            Optional[str]: Scrapboxプロジェクト名、設定されていない場合はNone
        """
        profile = await self.get_user_profile(user_id)

        if profile:
            # learning_preferencesからscrapbox_projectを取得
            learning_prefs = profile.get("learning_preferences", {})
            if isinstance(learning_prefs, dict):
                return learning_prefs.get("scrapbox_project")

            # 直接scrapbox_projectフィールドがある場合（将来の拡張用）
            return profile.get("scrapbox_project")

        return None

    async def update_user_scrapbox_project(
        self, user_id: str, project_name: str
    ) -> bool:
        """
        指定されたユーザーのScrapboxプロジェクト名を更新する

        Args:
            user_id: ユーザーID
            project_name: Scrapboxプロジェクト名

        Returns:
            bool: 更新成功フラグ
        """
        if not self.base_url or not self.anon_key:
            logger.error("Supabase認証情報が設定されていません")
            return False

        # 現在のプロファイルを取得
        profile = await self.get_user_profile(user_id)

        if profile:
            # 既存のlearning_preferencesを更新
            learning_prefs = profile.get("learning_preferences", {})
            if not isinstance(learning_prefs, dict):
                learning_prefs = {}

            learning_prefs["scrapbox_project"] = project_name

            # データを更新
            url = f"{self.base_url}/rest/v1/user_profiles"
            headers = {
                "apikey": self.anon_key,
                "Authorization": f"Bearer {self.anon_key}",
                "Content-Type": "application/json",
            }

            params = {"id": f"eq.{user_id}"}
            data = {"learning_preferences": learning_prefs}

            try:
                async with httpx.AsyncClient(timeout=self.timeout) as client:
                    response = await client.patch(
                        url, headers=headers, params=params, json=data
                    )

                    if response.status_code == 204:
                        logger.info(
                            f"ユーザー {user_id} のScrapboxプロジェクトを {project_name} に更新しました"
                        )
                        return True
                    else:
                        logger.error(f"Supabaseプロファイル更新エラー: {response.status_code}")
                        return False

            except Exception as e:
                logger.error(f"Supabaseプロファイル更新中にエラー: {e}")
                return False
        else:
            logger.error(f"ユーザーID {user_id} のプロファイルが見つかりません")
            return False


# シングルトンインスタンス
_supabase_service = None


def get_supabase_service() -> SupabaseService:
    """
    Supabaseサービスのシングルトンインスタンスを取得する

    Returns:
        SupabaseService: Supabaseサービスインスタンス
    """
    global _supabase_service
    if _supabase_service is None:
        _supabase_service = SupabaseService()
    return _supabase_service
