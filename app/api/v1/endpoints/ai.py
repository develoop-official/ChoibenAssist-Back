"""AI-related API endpoints."""

from typing import List, Literal, Optional

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field

from app.core.config import Settings
from app.core.exceptions import (GeminiAPIError, GeminiConfigurationError,
                                 GeminiQuotaExceededError,
                                 GeminiRateLimitError)
from app.core.prompts import get_prompt
from app.services.gemini_service import GeminiService, get_gemini_service

router = APIRouter()


# Request models
class LearningPlanRequest(BaseModel):
    """Request model for learning plan generation."""

    goal: str = Field(..., description="Learning goal", min_length=1, max_length=500)
    time_available: int = Field(
        ..., description="Available time in minutes", gt=0, le=480
    )
    current_level: str = Field(default="中級", description="Current skill level")
    focus_areas: Optional[List[str]] = Field(
        default=None, description="Areas to focus on"
    )
    difficulty: Literal["easy", "medium", "hard"] = Field(
        default="medium", description="Difficulty level"
    )


class TodoRequest(BaseModel):
    """Request model for TODO list generation."""

    time_available: int = Field(
        ..., description="Available time in minutes", gt=0, le=480
    )
    recent_progress: Optional[str] = Field(
        default=None, description="Recent learning progress"
    )
    weak_areas: Optional[List[str]] = Field(
        default=None, description="Areas that need improvement"
    )
    daily_goal: Optional[str] = Field(default=None, description="Today's specific goal")


class AnalysisRequest(BaseModel):
    """Request model for progress analysis."""

    period: str = Field(
        ..., description="Analysis period", min_length=1, max_length=100
    )
    learning_records: str = Field(
        ..., description="Learning records data", min_length=1
    )
    goals: str = Field(..., description="Learning goals", min_length=1)
    progress_rate: float = Field(
        ..., description="Current progress rate", ge=0.0, le=1.0
    )


class AdviceRequest(BaseModel):
    """Request model for learning advice."""

    current_issues: str = Field(
        ..., description="Current learning issues", min_length=1
    )
    learning_status: str = Field(
        ..., description="Current learning status", min_length=1
    )
    concerns: Optional[str] = Field(default=None, description="Specific concerns")
    target_goal: Optional[str] = Field(default=None, description="Target goal")


class GoalRequest(BaseModel):
    """Request model for goal setting."""

    desired_outcome: str = Field(
        ..., description="Desired learning outcome", min_length=1
    )
    timeline: str = Field(..., description="Goal timeline", min_length=1)
    current_level: str = Field(..., description="Current skill level", min_length=1)
    available_resources: str = Field(
        ..., description="Available resources", min_length=1
    )
    constraints: Optional[str] = Field(default=None, description="Any constraints")


# Scrapbox integration request models
class ScrapboxTodoRequest(BaseModel):
    """Scrapbox統合TODO生成のリクエストモデル"""

    time_available: int = Field(..., description="利用可能時間（分）", gt=0, le=480)
    daily_goal: Optional[str] = Field(default=None, description="今日の具体的な目標")


# Response models
class AIResponse(BaseModel):
    """Standard AI response model."""

    success: bool = Field(..., description="Whether the request was successful")
    content: str = Field(..., description="Generated content")
    response_type: str = Field(..., description="Type of response")


# Dependency to get Gemini service
def get_gemini_service_dep() -> GeminiService:
    """Dependency to get Gemini service."""
    return get_gemini_service()


def handle_gemini_error(error: Exception) -> HTTPException:
    """Convert Gemini service errors to appropriate HTTP exceptions.

    Args:
        error: Gemini service error

    Returns:
        HTTPException: Appropriate HTTP exception
    """
    if isinstance(error, GeminiRateLimitError):
        return HTTPException(
            status_code=429,
            detail={
                "message": str(error),
                "type": "rate_limit_exceeded",
                "retry_after_seconds": error.retry_after_seconds,
            },
        )

    if isinstance(error, GeminiQuotaExceededError):
        return HTTPException(
            status_code=429, detail={"message": str(error), "type": "quota_exceeded"}
        )

    if isinstance(error, GeminiAPIError):
        status_code = error.status_code if error.status_code else 502
        return HTTPException(
            status_code=status_code, detail={"message": str(error), "type": "api_error"}
        )

    if isinstance(error, GeminiConfigurationError):
        return HTTPException(
            status_code=500,
            detail={"message": "サービス設定エラーが発生しました。", "type": "configuration_error"},
        )

    # Unknown error
    return HTTPException(
        status_code=500, detail={"message": "予期しないエラーが発生しました。", "type": "unknown_error"}
    )


@router.post("/plan", response_model=AIResponse)
async def generate_learning_plan(
    request: LearningPlanRequest,
    gemini_service: GeminiService = Depends(get_gemini_service_dep),
) -> AIResponse:
    """Generate a personalized learning plan.

    Args:
        request: Learning plan request data
        gemini_service: Gemini service instance

    Returns:
        AIResponse: Generated learning plan

    Raises:
        HTTPException: If generation fails
    """
    try:
        content = await gemini_service.generate_learning_plan(
            goal=request.goal,
            time_available=request.time_available,
            current_level=request.current_level,
            focus_areas=request.focus_areas,
            difficulty=request.difficulty,
        )

        return AIResponse(success=True, content=content, response_type="learning_plan")

    except (
        GeminiRateLimitError,
        GeminiQuotaExceededError,
        GeminiAPIError,
        GeminiConfigurationError,
    ) as e:
        raise handle_gemini_error(e)
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate learning plan: {str(e)}"
        )


@router.post("/todo", response_model=AIResponse)
async def generate_todo_list(
    request: TodoRequest,
    gemini_service: GeminiService = Depends(get_gemini_service_dep),
) -> AIResponse:
    """Generate today's TODO list.

    Args:
        request: TODO request data
        gemini_service: Gemini service instance

    Returns:
        AIResponse: Generated TODO list

    Raises:
        HTTPException: If generation fails
    """
    try:
        content = await gemini_service.generate_todo_list(
            time_available=request.time_available,
            recent_progress=request.recent_progress,
            weak_areas=request.weak_areas,
            daily_goal=request.daily_goal,
        )

        return AIResponse(success=True, content=content, response_type="todo_list")

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate TODO list: {str(e)}"
        )


@router.post("/analysis", response_model=AIResponse)
async def analyze_progress(
    request: AnalysisRequest,
    gemini_service: GeminiService = Depends(get_gemini_service_dep),
) -> AIResponse:
    """Analyze learning progress.

    Args:
        request: Analysis request data
        gemini_service: Gemini service instance

    Returns:
        AIResponse: Generated analysis

    Raises:
        HTTPException: If analysis fails
    """
    try:
        content = await gemini_service.analyze_progress(
            period=request.period,
            learning_records=request.learning_records,
            goals=request.goals,
            progress_rate=request.progress_rate,
        )

        return AIResponse(
            success=True, content=content, response_type="progress_analysis"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to analyze progress: {str(e)}"
        )


@router.post("/advice", response_model=AIResponse)
async def give_advice(
    request: AdviceRequest,
    gemini_service: GeminiService = Depends(get_gemini_service_dep),
) -> AIResponse:
    """Provide learning advice.

    Args:
        request: Advice request data
        gemini_service: Gemini service instance

    Returns:
        AIResponse: Generated advice

    Raises:
        HTTPException: If advice generation fails
    """
    try:
        content = await gemini_service.give_advice(
            current_issues=request.current_issues,
            learning_status=request.learning_status,
            concerns=request.concerns,
            target_goal=request.target_goal,
        )

        return AIResponse(
            success=True, content=content, response_type="learning_advice"
        )

    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Failed to generate advice: {str(e)}"
        )


@router.post("/goals", response_model=AIResponse)
async def set_goals(
    request: GoalRequest,
    gemini_service: GeminiService = Depends(get_gemini_service_dep),
) -> AIResponse:
    """Generate SMART learning goals.

    Args:
        request: Goal setting request data
        gemini_service: Gemini service instance

    Returns:
        AIResponse: Generated SMART goals

    Raises:
        HTTPException: If goal generation fails
    """
    try:
        content = await gemini_service.set_goals(
            desired_outcome=request.desired_outcome,
            timeline=request.timeline,
            current_level=request.current_level,
            available_resources=request.available_resources,
            constraints=request.constraints,
        )

        return AIResponse(success=True, content=content, response_type="smart_goals")

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to set goals: {str(e)}")


# Scrapbox integration endpoints
@router.post("/scrapbox-todo/{project_name}", response_model=AIResponse)
async def generate_scrapbox_todo(
    project_name: str,
    request: ScrapboxTodoRequest,
    gemini_service: GeminiService = Depends(get_gemini_service_dep),
) -> AIResponse:
    """
    Scrapbox統合によるTODOリスト生成

    Args:
        project_name: Scrapboxプロジェクト名
        request: ScrapboxTODOリクエストデータ(可能な時間、今日の目標)
        gemini_service: Geminiサービスインスタンス（任意）

    Returns:
        AIResponse: 生成されたTODOリスト

    Raises:
        HTTPException: 生成に失敗した場合
    """
    try:
        from app.core.prompts import get_prompt
        from app.services.scrapbox_service import ScrapboxService

        # Scrapboxサービスから学習記録を取得
        scrapbox_service = ScrapboxService()
        learning_records = await scrapbox_service.get_learning_records(project_name)

        # プロンプト生成
        system_prompt = get_prompt("todo", "system")
        user_prompt = get_prompt("todo", "user_template").format(
            time_available=request.time_available,
            recent_progress=learning_records or "学習記録なし",
            weak_areas="Scrapboxデータから分析中",
            daily_goal=request.daily_goal or "効果的な学習"
        )

        # Geminiでテキスト生成
        content = await gemini_service.generate_text(user_prompt, system_prompt)

        return AIResponse(
            success=True, content=content, response_type="scrapbox_todo_list"
        )

    except Exception as e:
        error_response = handle_gemini_error(e)
        if isinstance(error_response, HTTPException):
            raise error_response
        raise HTTPException(status_code=500, detail=f"Scrapbox TODO生成に失敗しました: {str(e)}")


@router.get("/scrapbox-learning-records/{project_name}", response_model=dict)
async def get_scrapbox_learning_records(project_name: str) -> dict:
    """
    Scrapbox学習記録を取得する

    Args:
        project_name: Scrapboxプロジェクト名

    Returns:
        dict: Scrapbox学習記録データ

    Raises:
        HTTPException: 取得に失敗した場合
    """
    try:
        from app.services.scrapbox_service import ScrapboxService

        scrapbox_service = ScrapboxService()
        learning_records = await scrapbox_service.get_learning_records(project_name)

        return {"project_name": project_name, "learning_records": learning_records}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Scrapbox学習記録取得に失敗しました: {str(e)}")


@router.get("/health", response_model=dict)
async def health_check(
    gemini_service: GeminiService = Depends(get_gemini_service_dep),
) -> dict:
    """Check AI service health.

    Args:
        gemini_service: Gemini service instance

    Returns:
        dict: Health check result
    """
    return await gemini_service.health_check()
