from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Category(str, Enum):
    REVIEW = "復習"
    NEW_LEARNING = "新規学習"
    PRACTICE = "練習"
    EXAM_PREP = "試験対策"


class Period(str, Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"


# Request Models
class PlanGenerationRequest(BaseModel):
    user_id: str = Field(..., description="ユーザーID")
    subject: str = Field(..., description="学習科目")
    target_date: Optional[datetime] = Field(None, description="目標達成日")
    difficulty_level: Optional[str] = Field("medium", description="難易度レベル")
    available_time_per_day: Optional[int] = Field(60, description="1日の利用可能時間（分）")


class TodoGenerationRequest(BaseModel):
    user_id: str = Field(..., description="ユーザーID")
    date: Optional[datetime] = Field(None, description="対象日（デフォルト：今日）")
    available_time: Optional[int] = Field(120, description="利用可能時間（分）")
    preferences: Optional[Dict[str, Any]] = Field(None, description="学習設定")


class AnalysisRequest(BaseModel):
    user_id: str = Field(..., description="ユーザーID")
    period: Period = Field(Period.WEEKLY, description="分析期間")
    subjects: Optional[List[str]] = Field(None, description="分析対象科目")


class AdviceRequest(BaseModel):
    user_id: str = Field(..., description="ユーザーID")
    current_challenge: Optional[str] = Field(None, description="現在の課題")
    context: Optional[str] = Field(None, description="アドバイス要求の文脈")


class GoalsRequest(BaseModel):
    user_id: str = Field(..., description="ユーザーID")
    goal_type: str = Field(..., description="目標タイプ（短期/長期）")
    subject: Optional[str] = Field(None, description="科目")
    current_level: Optional[str] = Field(None, description="現在のレベル")


# Response Models
class TodoItem(BaseModel):
    id: int = Field(..., description="TODO項目ID")
    title: str = Field(..., description="TODO項目タイトル")
    description: str = Field(..., description="詳細説明")
    priority: Priority = Field(..., description="優先度")
    estimated_time: int = Field(..., description="推定時間（分）")
    category: Category = Field(..., description="カテゴリ")
    reason: str = Field(..., description="推奨理由")


class PlanGenerationResponse(BaseModel):
    plan_id: str = Field(..., description="プランID")
    subject: str = Field(..., description="科目")
    generated_at: datetime = Field(..., description="生成日時")
    plan_content: Dict[str, Any] = Field(..., description="プラン内容")
    estimated_completion_date: Optional[datetime] = Field(None, description="完了予定日")
    daily_tasks: List[Dict[str, Any]] = Field(..., description="日別タスク")


class TodoGenerationResponse(BaseModel):
    date: datetime = Field(..., description="対象日")
    todos: List[TodoItem] = Field(..., description="TODO項目リスト")
    total_estimated_time: int = Field(..., description="総推定時間（分）")
    motivational_message: str = Field(..., description="モチベーションメッセージ")


class AnalysisResponse(BaseModel):
    user_id: str = Field(..., description="ユーザーID")
    period: Period = Field(..., description="分析期間")
    analysis_date: datetime = Field(..., description="分析実行日")
    overall_progress: Dict[str, Any] = Field(..., description="全体進捗")
    subject_breakdown: List[Dict[str, Any]] = Field(..., description="科目別分析")
    strengths: List[str] = Field(..., description="強み")
    weaknesses: List[str] = Field(..., description="弱み")
    recommendations: List[str] = Field(..., description="推奨事項")


class AdviceResponse(BaseModel):
    advice_id: str = Field(..., description="アドバイスID")
    generated_at: datetime = Field(..., description="生成日時")
    advice_text: str = Field(..., description="アドバイス内容")
    action_items: List[str] = Field(..., description="アクションアイテム")
    resources: List[Dict[str, str]] = Field(..., description="推奨リソース")


class Goal(BaseModel):
    goal_id: str = Field(..., description="目標ID")
    title: str = Field(..., description="目標タイトル")
    description: str = Field(..., description="目標説明")
    target_date: datetime = Field(..., description="目標達成日")
    measurable_criteria: str = Field(..., description="測定可能な基準")
    action_steps: List[str] = Field(..., description="アクションステップ")


class GoalsResponse(BaseModel):
    generated_at: datetime = Field(..., description="生成日時")
    goals: List[Goal] = Field(..., description="推奨目標リスト")
    rationale: str = Field(..., description="推奨理由")
