"""Tests for Gemini service."""

import asyncio
from unittest.mock import AsyncMock, Mock, patch

import pytest

from app.core.config import Settings
from app.core.exceptions import GeminiConfigurationError
from app.core.prompts import get_prompt
from app.services.gemini_service import GeminiService, get_gemini_service


class TestGeminiService:
    """Test cases for GeminiService."""

    @pytest.fixture
    def settings(self):
        """Create test settings."""
        settings = Mock(spec=Settings)
        settings.gemini_api_key = "test_api_key"
        return settings

    @pytest.fixture
    def mock_model(self):
        """Create mock Gemini model."""
        model = Mock()
        mock_response = Mock()
        mock_response.text = "Test response from Gemini"
        model.generate_content.return_value = mock_response
        return model

    @pytest.fixture
    def gemini_service(self, settings, mock_model):
        """Create GeminiService instance with mocked dependencies."""
        with patch("app.services.gemini_service.genai") as mock_genai:
            mock_genai.GenerativeModel.return_value = mock_model
            service = GeminiService(settings)
            service.model = mock_model
            return service

    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        settings = Mock(spec=Settings)
        settings.gemini_api_key = ""

        with patch("app.services.gemini_service.genai"):
            with pytest.raises(
                GeminiConfigurationError,
                match="GEMINI_API_KEY environment variable is required",
            ):
                GeminiService(settings)

    @pytest.mark.asyncio
    async def test_generate_text_success(self, gemini_service, mock_model):
        """Test successful text generation."""
        result = await gemini_service.generate_text("Test prompt")
        assert result == "Test response from Gemini"
        mock_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_text_with_system_prompt(self, gemini_service, mock_model):
        """Test text generation with system prompt."""
        await gemini_service.generate_text("User prompt", "System prompt")

        # Check that the full prompt was created correctly
        call_args = mock_model.generate_content.call_args[0][0]
        assert "System prompt" in call_args
        assert "User prompt" in call_args

    @pytest.mark.asyncio
    async def test_generate_text_empty_response(self, gemini_service, mock_model):
        """Test handling of empty response."""
        mock_response = Mock()
        mock_response.text = ""
        mock_model.generate_content.return_value = mock_response

        with pytest.raises(ValueError, match="Empty response from Gemini"):
            await gemini_service.generate_text("Test prompt")

    @pytest.mark.asyncio
    async def test_generate_learning_plan(self, gemini_service, mock_model):
        """Test learning plan generation."""
        result = await gemini_service.generate_learning_plan(
            goal="Learn Python",
            time_available=120,
            current_level="初級",
            focus_areas=["基礎文法", "データ構造"],
            difficulty="easy",
        )

        assert result == "Test response from Gemini"
        mock_model.generate_content.assert_called_once()

        # Check that the prompt was formatted correctly
        call_args = mock_model.generate_content.call_args[0][0]
        assert "Learn Python" in call_args
        assert "120" in call_args

    @pytest.mark.asyncio
    async def test_generate_todo_list(self, gemini_service, mock_model):
        """Test TODO list generation."""
        result = await gemini_service.generate_todo_list(
            time_available=60,
            recent_progress="良い進捗",
            weak_areas=["文法", "語彙"],
            daily_goal="基礎固め",
        )

        assert result == "Test response from Gemini"
        mock_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_analyze_progress(self, gemini_service, mock_model):
        """Test progress analysis."""
        result = await gemini_service.analyze_progress(
            period="1週間", learning_records="毎日2時間学習", goals="英語力向上", progress_rate=0.7
        )

        assert result == "Test response from Gemini"
        mock_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_give_advice(self, gemini_service, mock_model):
        """Test advice generation."""
        result = await gemini_service.give_advice(
            current_issues="モチベーション低下",
            learning_status="停滞中",
            concerns="時間不足",
            target_goal="資格取得",
        )

        assert result == "Test response from Gemini"
        mock_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_set_goals(self, gemini_service, mock_model):
        """Test goal setting."""
        result = await gemini_service.set_goals(
            desired_outcome="TOEIC 800点",
            timeline="3ヶ月",
            current_level="中級",
            available_resources="教材、アプリ",
            constraints="平日のみ",
        )

        assert result == "Test response from Gemini"
        mock_model.generate_content.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_success(self, gemini_service, mock_model):
        """Test successful health check."""
        result = await gemini_service.health_check()

        assert result["status"] == "healthy"
        assert result["service"] == "gemini"
        assert result["model"] == "gemini-2.0-flash-exp"
        assert "test_response_length" in result

    @pytest.mark.asyncio
    async def test_health_check_failure(self, gemini_service, mock_model):
        """Test health check with failure."""
        mock_model.generate_content.side_effect = Exception("API Error")

        result = await gemini_service.health_check()

        assert result["status"] == "unhealthy"
        assert result["service"] == "gemini"
        assert "error" in result

    def test_build_full_prompt(self, gemini_service):
        """Test full prompt building."""
        # Test with system prompt
        result = gemini_service._build_full_prompt("System", "User")
        assert result == "System\n\nUser"

        # Test without system prompt
        result = gemini_service._build_full_prompt(None, "User")
        assert result == "User"

    def test_parse_api_error_rate_limit(self, gemini_service):
        """Test parsing of rate limit error."""
        error_msg = "429 You exceeded your current quota, please check your plan and billing details. FreeTier retry_delay { seconds: 20 }"
        original_error = Exception(error_msg)

        parsed_error = gemini_service._parse_api_error(original_error)

        assert parsed_error.__class__.__name__ == "GeminiRateLimitError"
        assert "無料枠のレート制限" in str(parsed_error)

    def test_parse_api_error_quota_exceeded(self, gemini_service):
        """Test parsing of quota exceeded error."""
        error_msg = "quota exceeded for this request"
        original_error = Exception(error_msg)

        parsed_error = gemini_service._parse_api_error(original_error)

        assert parsed_error.__class__.__name__ == "GeminiQuotaExceededError"
        assert "利用制限" in str(parsed_error)

    def test_should_log_error(self, gemini_service):
        """Test error logging decision."""
        from app.core.exceptions import GeminiAPIError, GeminiRateLimitError

        # Rate limit errors should not be logged
        rate_limit_error = GeminiRateLimitError("Rate limit")
        assert not gemini_service._should_log_error(rate_limit_error)

        # API errors should be logged
        api_error = GeminiAPIError("API error")
        assert gemini_service._should_log_error(api_error)


class TestGeminiServiceIntegration:
    """Integration tests for GeminiService."""

    def test_get_gemini_service_singleton(self):
        """Test that get_gemini_service returns singleton."""
        with patch("app.services.gemini_service.GeminiService") as mock_service_class:
            mock_instance = Mock()
            mock_service_class.return_value = mock_instance

            # Reset global instance
            import app.services.gemini_service

            app.services.gemini_service._gemini_service = None

            # First call should create instance
            service1 = get_gemini_service()

            # Second call should return same instance
            service2 = get_gemini_service()

            assert service1 is service2
            mock_service_class.assert_called_once()


class TestPromptsIntegration:
    """Test prompt system integration."""

    def test_learning_plan_prompts(self):
        """Test learning plan prompt retrieval."""
        system_prompt = get_prompt("learning_plan", "system")
        user_template = get_prompt("learning_plan", "user_template")

        assert "学習プランを以下の形式で出力してください" in system_prompt
        assert "{goal}" in user_template
        assert "{time_available}" in user_template

    def test_invalid_prompt_category(self):
        """Test invalid prompt category raises error."""
        with pytest.raises(ValueError, match="Unknown prompt category"):
            get_prompt("invalid_category", "system")

    def test_invalid_prompt_type(self):
        """Test invalid prompt type raises error."""
        with pytest.raises(ValueError, match="Unknown prompt type"):
            get_prompt("learning_plan", "invalid_type")
