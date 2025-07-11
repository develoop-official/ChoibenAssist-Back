from fastapi import APIRouter, HTTPException, Depends, Request
from typing import List, Dict, Any
import logging

from app.models.ai_models import (
    PlanGenerationRequest, PlanGenerationResponse,
    TodoGenerationRequest, TodoGenerationResponse,
    AnalysisRequest, AnalysisResponse,
    AdviceRequest, AdviceResponse,
    GoalsRequest, GoalsResponse
)
from app.services.gemini_service import GeminiService
from app.services.supabase_service import SupabaseService
from app.dependencies import get_api_key, rate_limit

router = APIRouter()
logger = logging.getLogger(__name__)


@router.post("/plan", response_model=PlanGenerationResponse)
async def generate_learning_plan(
    request: PlanGenerationRequest,
    gemini_service: GeminiService = Depends(lambda: None),  # Will be injected from app state
    supabase_service: SupabaseService = Depends(SupabaseService),
    api_key: str = Depends(get_api_key),
    _: None = Depends(rate_limit)
) -> PlanGenerationResponse:
    """Generate personalized learning plan based on user data"""
    try:
        # Get user learning history from Supabase
        user_data = await supabase_service.get_user_learning_data(request.user_id)
        
        # Generate plan using Gemini
        plan = await gemini_service.generate_learning_plan(request, user_data)
        
        return plan
    except Exception as e:
        logger.error(f"Failed to generate learning plan: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate learning plan")


@router.post("/todo", response_model=TodoGenerationResponse)
async def generate_daily_todo(
    request: TodoGenerationRequest,
    gemini_service: GeminiService = Depends(lambda: None),
    supabase_service: SupabaseService = Depends(SupabaseService),
    api_key: str = Depends(get_api_key),
    _: None = Depends(rate_limit)
) -> TodoGenerationResponse:
    """Generate today's TODO list based on learning history"""
    try:
        # Get recent learning history
        learning_history = await supabase_service.get_recent_learning_history(
            request.user_id, 
            days=7
        )
        
        # Generate TODO list using Gemini
        todo_list = await gemini_service.generate_daily_todo(request, learning_history)
        
        return todo_list
    except Exception as e:
        logger.error(f"Failed to generate TODO list: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate TODO list")


@router.post("/analysis", response_model=AnalysisResponse)
async def analyze_learning_progress(
    request: AnalysisRequest,
    gemini_service: GeminiService = Depends(lambda: None),
    supabase_service: SupabaseService = Depends(SupabaseService),
    api_key: str = Depends(get_api_key),
    _: None = Depends(rate_limit)
) -> AnalysisResponse:
    """Analyze learning progress and provide insights"""
    try:
        # Get comprehensive learning data
        learning_data = await supabase_service.get_learning_analytics_data(
            request.user_id,
            request.period
        )
        
        # Analyze using Gemini
        analysis = await gemini_service.analyze_learning_progress(request, learning_data)
        
        return analysis
    except Exception as e:
        logger.error(f"Failed to analyze learning progress: {e}")
        raise HTTPException(status_code=500, detail="Failed to analyze learning progress")


@router.post("/advice", response_model=AdviceResponse)
async def get_learning_advice(
    request: AdviceRequest,
    gemini_service: GeminiService = Depends(lambda: None),
    supabase_service: SupabaseService = Depends(SupabaseService),
    api_key: str = Depends(get_api_key),
    _: None = Depends(rate_limit)
) -> AdviceResponse:
    """Get personalized learning advice"""
    try:
        # Get user profile and recent performance
        user_profile = await supabase_service.get_user_profile(request.user_id)
        
        # Generate advice using Gemini
        advice = await gemini_service.generate_learning_advice(request, user_profile)
        
        return advice
    except Exception as e:
        logger.error(f"Failed to generate learning advice: {e}")
        raise HTTPException(status_code=500, detail="Failed to generate learning advice")


@router.post("/goals", response_model=GoalsResponse)
async def suggest_learning_goals(
    request: GoalsRequest,
    gemini_service: GeminiService = Depends(lambda: None),
    supabase_service: SupabaseService = Depends(SupabaseService),
    api_key: str = Depends(get_api_key),
    _: None = Depends(rate_limit)
) -> GoalsResponse:
    """Suggest SMART learning goals"""
    try:
        # Get current goals and progress
        current_goals = await supabase_service.get_current_goals(request.user_id)
        
        # Generate goal suggestions using Gemini
        goals = await gemini_service.suggest_learning_goals(request, current_goals)
        
        return goals
    except Exception as e:
        logger.error(f"Failed to suggest learning goals: {e}")
        raise HTTPException(status_code=500, detail="Failed to suggest learning goals")
