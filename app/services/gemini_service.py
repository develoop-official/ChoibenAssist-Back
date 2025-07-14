"""Google Gemini AI service for text generation."""

import asyncio
import logging
import re
from typing import Dict, Any, Optional, List
import google.generativeai as genai
from google.generativeai.types import HarmCategory, HarmBlockThreshold

from app.core.config import Settings
from app.core.prompts import get_prompt
from app.core.exceptions import (
    GeminiRateLimitError,
    GeminiQuotaExceededError,
    GeminiAPIError,
    GeminiConfigurationError
)

logger = logging.getLogger(__name__)


class GeminiService:
    """高速テキスト生成のためのGoogle Gemini AIサービス。"""
    
    def __init__(self, settings: Settings):
        """Geminiサービスを初期化する。
        
        Args:
            settings: APIキーを含むアプリケーション設定
        """
        self.settings = settings
        self._configure_gemini()
        self.model = self._create_model()
    
    def _configure_gemini(self) -> None:
        """APIキーと安全設定でGeminiを設定する。"""
        if not self.settings.gemini_api_key:
            raise GeminiConfigurationError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=self.settings.gemini_api_key)
        logger.info("Gemini API configured successfully")
    
    def _create_model(self) -> genai.GenerativeModel:
        """高速レスポンス用に最適化されたGeminiモデルを作成する。
        
        Returns:
            genai.GenerativeModel: 設定済みのGeminiモデル
        """
        # Use Gemini 2.0 Flash for fast response
        model = genai.GenerativeModel(
            model_name="gemini-2.0-flash-exp",
            generation_config=genai.types.GenerationConfig(
                temperature=0.7,  # Balanced creativity and consistency
                top_p=0.8,       # Focus on high-probability tokens
                top_k=40,        # Limit token choices for faster response
                max_output_tokens=1024,  # Limit output length for speed
                stop_sequences=[],
            ),
            safety_settings={
                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_MEDIUM_AND_ABOVE,
            }
        )
        logger.info("Gemini model created with fast response configuration")
        return model
    
    def _parse_api_error(self, error: Exception) -> Exception:
        """Gemini APIエラーを解析し、適切なカスタム例外を返す。
        
        Args:
            error: Gemini APIからの元の例外
            
        Returns:
            Exception: ユーザーフレンドリーなメッセージを持つカスタム例外
        """
        error_str = str(error)
        
        # Rate limit error (429)
        if "429" in error_str and "quota" in error_str.lower():
            # Extract retry delay if available
            retry_match = re.search(r'retry_delay.*?seconds: (\d+)', error_str)
            retry_seconds = int(retry_match.group(1)) if retry_match else None
            
            # Check if it's free tier rate limit
            if "FreeTier" in error_str:
                message = f"⏱️ Gemini API無料枠のレート制限に達しました。{retry_seconds}秒後に再試行してください。"
                # Don't log as warning since it's expected behavior for free tier
                logger.info(f"Rate limit reached (free tier): retry in {retry_seconds}s")
                return GeminiRateLimitError(message, retry_seconds)
            else:
                message = f"⏱️ APIレート制限に達しました。{retry_seconds}秒後に再試行してください。"
                logger.info(f"Rate limit reached: retry in {retry_seconds}s")
                return GeminiRateLimitError(message, retry_seconds)
        
        # Quota exceeded error
        if "quota" in error_str.lower() and "exceeded" in error_str.lower():
            message = "📊 APIの月間利用制限に達しました。Gemini APIのプランをご確認ください。"
            logger.warning("Quota exceeded - consider upgrading API plan")
            return GeminiQuotaExceededError(message)
        
        # Generic API error
        if "400" in error_str or "500" in error_str:
            status_match = re.search(r'(\d{3})', error_str)
            status_code = int(status_match.group(1)) if status_match else None
            message = "API接続でエラーが発生しました。しばらく時間をおいて再試行してください。"
            logger.error(f"API error {status_code}: {error_str}")
            return GeminiAPIError(message, status_code)
        
        # Unknown error
        logger.error(f"Unknown error: {error_str}")
        return GeminiAPIError("予期しないエラーが発生しました。")
    
    def _should_log_error(self, error: Exception) -> bool:
        """エラーの種類に基づいてログを出力するかどうかを判定する。
        
        Args:
            error: チェック対象の例外
            
        Returns:
            bool: エラーをログに出力する場合はTrue
        """
        # レート制限エラーは無料枠では想定内のエラーなのでログ出力しない
        if isinstance(error, GeminiRateLimitError):
            return False
        
        # その他のエラーはログ出力する
        return True
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """高速レスポンス最適化を使用してGeminiでテキストを生成する。
        
        Args:
            prompt: ユーザープロンプト
            system_prompt: コンテキスト用のオプションのシステムプロンプト
            **kwargs: 追加パラメータ
        
        Returns:
            str: 生成されたテキストレスポンス
        
        Raises:
            GeminiRateLimitError: レート制限を超過した場合
            GeminiQuotaExceededError: クォータを超過した場合
            GeminiAPIError: APIがエラーを返した場合
            ValueError: レスポンスが空の場合
        """
        try:
            # Combine system and user prompts
            full_prompt = self._build_full_prompt(system_prompt, prompt)
            
            logger.debug(f"Generating text with prompt length: {len(full_prompt)}")
            
            # Generate content asynchronously
            response = await asyncio.to_thread(
                self.model.generate_content,
                full_prompt
            )
            
            if not response.text:
                raise ValueError("Empty response from Gemini")
            
            logger.info("Text generated successfully")
            return response.text.strip()
            
        except Exception as e:
            # Parse and raise appropriate custom exception
            custom_error = self._parse_api_error(e)
            
            # Only log if it's a significant error
            if self._should_log_error(custom_error):
                logger.error(f"Failed to generate text: {str(e)}")
            
            raise custom_error
    
    async def generate_learning_plan(
        self,
        goal: str,
        time_available: int,
        current_level: str = "中級",
        focus_areas: Optional[List[str]] = None,
        difficulty: str = "medium"
    ) -> str:
        """事前定義されたプロンプトを使用して学習プランを生成する。
        
        Args:
            goal: 学習目標
            time_available: 利用可能時間（分）
            current_level: 現在のスキルレベル
            focus_areas: 重点分野
            difficulty: 難易度
        
        Returns:
            str: 生成された学習プラン
        """
        system_prompt = get_prompt("learning_plan", "system")
        user_prompt = get_prompt("learning_plan", "user_template").format(
            goal=goal,
            time_available=time_available,
            current_level=current_level,
            focus_areas=", ".join(focus_areas) if focus_areas else "指定なし",
            difficulty=difficulty
        )
        
        return await self.generate_text(user_prompt, system_prompt)
    
    async def generate_todo_list(
        self,
        time_available: int,
        recent_progress: Optional[str] = None,
        weak_areas: Optional[List[str]] = None,
        daily_goal: Optional[str] = None
    ) -> str:
        """日次TODOリストを生成する。
        
        Args:
            time_available: 利用可能時間（分）
            recent_progress: 最近の学習進捗
            weak_areas: 改善が必要な分野
            daily_goal: 今日の具体的な目標
        
        Returns:
            str: 生成されたTODOリスト
        """
        system_prompt = get_prompt("todo", "system")
        user_prompt = get_prompt("todo", "user_template").format(
            time_available=time_available,
            recent_progress=recent_progress or "データなし",
            weak_areas=", ".join(weak_areas) if weak_areas else "特になし",
            daily_goal=daily_goal or "効果的な学習"
        )
        
        return await self.generate_text(user_prompt, system_prompt)
    
    async def analyze_progress(
        self,
        period: str,
        learning_records: str,
        goals: str,
        progress_rate: float
    ) -> str:
        """学習進捗を分析する。
        
        Args:
            period: 分析期間
            learning_records: 学習記録データ
            goals: 学習目標
            progress_rate: 現在の進捗率
        
        Returns:
            str: 生成された分析結果
        """
        system_prompt = get_prompt("analysis", "system")
        user_prompt = get_prompt("analysis", "user_template").format(
            period=period,
            learning_records=learning_records,
            goals=goals,
            progress_rate=progress_rate
        )
        
        return await self.generate_text(user_prompt, system_prompt)
    
    async def give_advice(
        self,
        current_issues: str,
        learning_status: str,
        concerns: Optional[str] = None,
        target_goal: Optional[str] = None
    ) -> str:
        """学習アドバイスを提供する。
        
        Args:
            current_issues: 現在の学習課題
            learning_status: 現在の学習状況
            concerns: 具体的な懸念事項
            target_goal: 目標
        
        Returns:
            str: 生成されたアドバイス
        """
        system_prompt = get_prompt("advice", "system")
        user_prompt = get_prompt("advice", "user_template").format(
            current_issues=current_issues,
            learning_status=learning_status,
            concerns=concerns or "特になし",
            target_goal=target_goal or "学習の改善"
        )
        
        return await self.generate_text(user_prompt, system_prompt)
    
    async def set_goals(
        self,
        desired_outcome: str,
        timeline: str,
        current_level: str,
        available_resources: str,
        constraints: Optional[str] = None
    ) -> str:
        """SMART目標を生成する。
        
        Args:
            desired_outcome: 希望する学習成果
            timeline: 目標の期限
            current_level: 現在のスキルレベル
            available_resources: 利用可能なリソース
            constraints: 制約条件
        
        Returns:
            str: 生成されたSMART目標
        """
        system_prompt = get_prompt("goal", "system")
        user_prompt = get_prompt("goal", "user_template").format(
            desired_outcome=desired_outcome,
            timeline=timeline,
            current_level=current_level,
            available_resources=available_resources,
            constraints=constraints or "特になし"
        )
        
        return await self.generate_text(user_prompt, system_prompt)
    
    def _build_full_prompt(self, system_prompt: Optional[str], user_prompt: str) -> str:
        """システムプロンプトとユーザープロンプトを結合してフルプロンプトを構築する。
        
        Args:
            system_prompt: オプションのシステムプロンプト
            user_prompt: ユーザープロンプト
        
        Returns:
            str: 結合されたプロンプト
        """
        if system_prompt:
            return f"{system_prompt}\n\n{user_prompt}"
        return user_prompt
    
    async def health_check(self) -> Dict[str, Any]:
        """Geminiサービスが正常に動作しているかチェックする。
        
        Returns:
            Dict[str, Any]: ヘルスチェック結果
        """
        try:
            test_response = await self.generate_text("テスト")
            return {
                "status": "healthy",
                "service": "gemini",
                "model": "gemini-2.0-flash-exp",
                "test_response_length": len(test_response)
            }
        except GeminiRateLimitError as e:
            return {
                "status": "rate_limited",
                "service": "gemini",
                "message": str(e),
                "retry_after_seconds": e.retry_after_seconds
            }
        except Exception as e:
            custom_error = self._parse_api_error(e)
            return {
                "status": "unhealthy",
                "service": "gemini",
                "error": str(custom_error)
            }


# アプリケーション全体で使用するグローバルインスタンス
_gemini_service: Optional[GeminiService] = None


def get_gemini_service(settings: Optional[Settings] = None) -> GeminiService:
    """Geminiサービスのインスタンスを取得または作成する。
    
    Args:
        settings: 初期化に使用するオプションの設定
    
    Returns:
        GeminiService: Geminiサービスのインスタンス
    """
    global _gemini_service
    
    if _gemini_service is None:
        if settings is None:
            settings = Settings()
        _gemini_service = GeminiService(settings)
    
    return _gemini_service
