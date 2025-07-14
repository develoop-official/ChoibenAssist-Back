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
    """Google Gemini AI service for fast text generation."""
    
    def __init__(self, settings: Settings):
        """Initialize Gemini service.
        
        Args:
            settings: Application settings containing API key
        """
        self.settings = settings
        self._configure_gemini()
        self.model = self._create_model()
    
    def _configure_gemini(self) -> None:
        """Configure Gemini with API key and safety settings."""
        if not self.settings.gemini_api_key:
            raise GeminiConfigurationError("GEMINI_API_KEY environment variable is required")
        
        genai.configure(api_key=self.settings.gemini_api_key)
        logger.info("Gemini API configured successfully")
    
    def _create_model(self) -> genai.GenerativeModel:
        """Create Gemini model with optimized settings for fast response.
        
        Returns:
            genai.GenerativeModel: Configured Gemini model
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
        """Parse Gemini API error and return appropriate custom exception.
        
        Args:
            error: Original exception from Gemini API
            
        Returns:
            Exception: Custom exception with user-friendly message
        """
        error_str = str(error)
        
        # Rate limit error (429)
        if "429" in error_str and "quota" in error_str.lower():
            # Extract retry delay if available
            retry_match = re.search(r'retry_delay.*?seconds: (\d+)', error_str)
            retry_seconds = int(retry_match.group(1)) if retry_match else None
            
            # Check if it's free tier rate limit
            if "FreeTier" in error_str:
                message = "APIの無料枠のレート制限に達しました。しばらく待ってから再試行してください。"
                logger.warning(f"Rate limit reached (free tier): retry in {retry_seconds}s")
                return GeminiRateLimitError(message, retry_seconds)
            else:
                message = "APIのレート制限に達しました。しばらく待ってから再試行してください。"
                logger.warning(f"Rate limit reached: retry in {retry_seconds}s")
                return GeminiRateLimitError(message, retry_seconds)
        
        # Quota exceeded error
        if "quota" in error_str.lower() and "exceeded" in error_str.lower():
            message = "APIの利用制限に達しました。プランの確認をお願いします。"
            logger.error("Quota exceeded")
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
        """Determine if error should be logged based on its type.
        
        Args:
            error: Exception to check
            
        Returns:
            bool: True if error should be logged
        """
        # Don't log rate limit errors as they are expected with free tier
        if isinstance(error, GeminiRateLimitError):
            return False
        
        # Log other errors
        return True
    
    async def generate_text(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        **kwargs: Any
    ) -> str:
        """Generate text using Gemini with fast response optimization.
        
        Args:
            prompt: User prompt
            system_prompt: Optional system prompt for context
            **kwargs: Additional parameters
        
        Returns:
            str: Generated text response
        
        Raises:
            GeminiRateLimitError: If rate limit is exceeded
            GeminiQuotaExceededError: If quota is exceeded  
            GeminiAPIError: If API returns an error
            ValueError: If response is empty
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
        """Generate learning plan using predefined prompts.
        
        Args:
            goal: Learning goal
            time_available: Available time in minutes
            current_level: Current skill level
            focus_areas: Areas to focus on
            difficulty: Difficulty level
        
        Returns:
            str: Generated learning plan
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
        """Generate daily TODO list.
        
        Args:
            time_available: Available time in minutes
            recent_progress: Recent learning progress
            weak_areas: Areas that need improvement
            daily_goal: Today's specific goal
        
        Returns:
            str: Generated TODO list
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
        """Analyze learning progress.
        
        Args:
            period: Analysis period
            learning_records: Learning records data
            goals: Learning goals
            progress_rate: Current progress rate
        
        Returns:
            str: Generated analysis
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
        """Provide learning advice.
        
        Args:
            current_issues: Current learning issues
            learning_status: Current learning status
            concerns: Specific concerns
            target_goal: Target goal
        
        Returns:
            str: Generated advice
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
        """Generate SMART goals.
        
        Args:
            desired_outcome: Desired learning outcome
            timeline: Goal timeline
            current_level: Current skill level
            available_resources: Available resources
            constraints: Any constraints
        
        Returns:
            str: Generated SMART goals
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
    
    async def quick_response(self, response_type: str) -> str:
        """Generate quick motivational or tip responses.
        
        Args:
            response_type: Type of quick response (motivation, tip, encouragement)
        
        Returns:
            str: Generated quick response
        
        Raises:
            ValueError: If response_type is invalid
        """
        try:
            prompt = get_prompt("quick", response_type)
            return await self.generate_text(prompt)
        except ValueError as e:
            raise ValueError(f"Invalid quick response type: {response_type}") from e
    
    def _build_full_prompt(self, system_prompt: Optional[str], user_prompt: str) -> str:
        """Build full prompt combining system and user prompts.
        
        Args:
            system_prompt: Optional system prompt
            user_prompt: User prompt
        
        Returns:
            str: Combined prompt
        """
        if system_prompt:
            return f"{system_prompt}\n\n{user_prompt}"
        return user_prompt
    
    async def health_check(self) -> Dict[str, Any]:
        """Check if Gemini service is working.
        
        Returns:
            Dict[str, Any]: Health check result
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


# Global instance to be used throughout the application
_gemini_service: Optional[GeminiService] = None


def get_gemini_service(settings: Optional[Settings] = None) -> GeminiService:
    """Get or create Gemini service instance.
    
    Args:
        settings: Optional settings to use for initialization
    
    Returns:
        GeminiService: Gemini service instance
    """
    global _gemini_service
    
    if _gemini_service is None:
        if settings is None:
            settings = Settings()
        _gemini_service = GeminiService(settings)
    
    return _gemini_service
