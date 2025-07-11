import google.generativeai as genai
from typing import Dict, Any, List
import json
import logging
from datetime import datetime

from app.config import settings
from app.models.ai_models import (
    PlanGenerationRequest, PlanGenerationResponse,
    TodoGenerationRequest, TodoGenerationResponse, TodoItem,
    AnalysisRequest, AnalysisResponse,
    AdviceRequest, AdviceResponse,
    GoalsRequest, GoalsResponse, Goal,
    Priority, Category
)

logger = logging.getLogger(__name__)


class GeminiService:
    def __init__(self):
        """Initialize Gemini service"""
        try:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel("gemini-2.0-flash-exp")
            logger.info("Gemini service initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize Gemini service: {e}")
            raise

    async def generate_learning_plan(
        self, 
        request: PlanGenerationRequest, 
        user_data: Dict[str, Any]
    ) -> PlanGenerationResponse:
        """Generate personalized learning plan"""
        
        prompt = f"""
        あなたは学習プラン作成の専門家です。以下の情報を基に、効果的な学習プランを作成してください。

        ユーザー情報:
        - 科目: {request.subject}
        - 目標達成日: {request.target_date}
        - 難易度レベル: {request.difficulty_level}
        - 1日の学習時間: {request.available_time_per_day}分

        学習履歴:
        {json.dumps(user_data, ensure_ascii=False, indent=2)}

        以下の形式でJSONレスポンスを生成してください:
        {{
            "plan_content": {{
                "overview": "プラン概要",
                "phases": [
                    {{
                        "phase_name": "フェーズ名",
                        "duration_weeks": 2,
                        "objectives": ["目標1", "目標2"],
                        "key_topics": ["トピック1", "トピック2"]
                    }}
                ]
            }},
            "daily_tasks": [
                {{
                    "day": 1,
                    "tasks": ["タスク1", "タスク2"],
                    "estimated_time": 60
                }}
            ]
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            plan_data = json.loads(response.text)
            
            return PlanGenerationResponse(
                plan_id=f"plan_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                subject=request.subject,
                generated_at=datetime.now(),
                plan_content=plan_data["plan_content"],
                daily_tasks=plan_data["daily_tasks"],
                estimated_completion_date=request.target_date
            )
        except Exception as e:
            logger.error(f"Failed to generate learning plan: {e}")
            raise

    async def generate_daily_todo(
        self, 
        request: TodoGenerationRequest, 
        learning_history: List[Dict[str, Any]]
    ) -> TodoGenerationResponse:
        """Generate daily TODO list"""
        
        target_date = request.date or datetime.now()
        
        prompt = f"""
        あなたは学習アドバイザーです。以下の学習履歴を基に、{target_date.strftime('%Y年%m月%d日')}の効果的なTODOリストを作成してください。

        学習履歴:
        {json.dumps(learning_history, ensure_ascii=False, indent=2)}

        利用可能時間: {request.available_time}分

        以下の形式でJSONレスポンスを生成してください:
        {{
            "todos": [
                {{
                    "id": 1,
                    "title": "数学 - 微分の復習",
                    "description": "昨日の理解度が70%だったので復習推奨",
                    "priority": "high",
                    "estimated_time": 30,
                    "category": "復習",
                    "reason": "理解度向上のため"
                }}
            ],
            "total_estimated_time": 60,
            "motivational_message": "今日も頑張りましょう！"
        }}

        priority: "low", "medium", "high" のいずれか
        category: "復習", "新規学習", "練習", "試験対策" のいずれか
        """

        try:
            response = self.model.generate_content(prompt)
            todo_data = json.loads(response.text)
            
            todos = [
                TodoItem(
                    id=item["id"],
                    title=item["title"],
                    description=item["description"],
                    priority=Priority(item["priority"]),
                    estimated_time=item["estimated_time"],
                    category=Category(item["category"]),
                    reason=item["reason"]
                )
                for item in todo_data["todos"]
            ]
            
            return TodoGenerationResponse(
                date=target_date,
                todos=todos,
                total_estimated_time=todo_data["total_estimated_time"],
                motivational_message=todo_data["motivational_message"]
            )
        except Exception as e:
            logger.error(f"Failed to generate TODO list: {e}")
            raise

    async def analyze_learning_progress(
        self, 
        request: AnalysisRequest, 
        learning_data: Dict[str, Any]
    ) -> AnalysisResponse:
        """Analyze learning progress"""
        
        prompt = f"""
        学習データを分析して、進捗レポートを作成してください。

        分析期間: {request.period.value}
        学習データ:
        {json.dumps(learning_data, ensure_ascii=False, indent=2)}

        以下の形式でJSONレスポンスを生成してください:
        {{
            "overall_progress": {{
                "completion_rate": 85,
                "consistency_score": 75,
                "improvement_trend": "上昇傾向"
            }},
            "subject_breakdown": [
                {{
                    "subject": "数学",
                    "progress": 80,
                    "time_spent": 300,
                    "areas_of_strength": ["基礎計算"],
                    "areas_for_improvement": ["応用問題"]
                }}
            ],
            "strengths": ["継続的な学習", "基礎理解"],
            "weaknesses": ["応用力不足", "時間管理"],
            "recommendations": ["毎日30分の復習", "応用問題への挑戦"]
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            analysis_data = json.loads(response.text)
            
            return AnalysisResponse(
                user_id=request.user_id,
                period=request.period,
                analysis_date=datetime.now(),
                overall_progress=analysis_data["overall_progress"],
                subject_breakdown=analysis_data["subject_breakdown"],
                strengths=analysis_data["strengths"],
                weaknesses=analysis_data["weaknesses"],
                recommendations=analysis_data["recommendations"]
            )
        except Exception as e:
            logger.error(f"Failed to analyze learning progress: {e}")
            raise

    async def generate_learning_advice(
        self, 
        request: AdviceRequest, 
        user_profile: Dict[str, Any]
    ) -> AdviceResponse:
        """Generate personalized learning advice"""
        
        prompt = f"""
        学習アドバイスを提供してください。

        現在の課題: {request.current_challenge}
        文脈: {request.context}
        ユーザープロフィール:
        {json.dumps(user_profile, ensure_ascii=False, indent=2)}

        以下の形式でJSONレスポンスを生成してください:
        {{
            "advice_text": "具体的なアドバイス内容",
            "action_items": ["実行すべきアクション1", "実行すべきアクション2"],
            "resources": [
                {{"type": "書籍", "title": "推奨書籍名", "url": ""}},
                {{"type": "動画", "title": "推奨動画", "url": ""}}
            ]
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            advice_data = json.loads(response.text)
            
            return AdviceResponse(
                advice_id=f"advice_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                generated_at=datetime.now(),
                advice_text=advice_data["advice_text"],
                action_items=advice_data["action_items"],
                resources=advice_data["resources"]
            )
        except Exception as e:
            logger.error(f"Failed to generate learning advice: {e}")
            raise

    async def suggest_learning_goals(
        self, 
        request: GoalsRequest, 
        current_goals: List[Dict[str, Any]]
    ) -> GoalsResponse:
        """Suggest SMART learning goals"""
        
        prompt = f"""
        SMART目標（具体的、測定可能、達成可能、関連性、時間制限）を提案してください。

        目標タイプ: {request.goal_type}
        科目: {request.subject}
        現在のレベル: {request.current_level}
        既存の目標:
        {json.dumps(current_goals, ensure_ascii=False, indent=2)}

        以下の形式でJSONレスポンスを生成してください:
        {{
            "goals": [
                {{
                    "title": "目標タイトル",
                    "description": "詳細説明",
                    "target_date": "2025-08-12T00:00:00",
                    "measurable_criteria": "測定可能な基準",
                    "action_steps": ["ステップ1", "ステップ2"]
                }}
            ],
            "rationale": "この目標を推奨する理由"
        }}
        """

        try:
            response = self.model.generate_content(prompt)
            goals_data = json.loads(response.text)
            
            goals = [
                Goal(
                    goal_id=f"goal_{i}_{datetime.now().strftime('%Y%m%d_%H%M%S')}",
                    title=goal["title"],
                    description=goal["description"],
                    target_date=datetime.fromisoformat(goal["target_date"]),
                    measurable_criteria=goal["measurable_criteria"],
                    action_steps=goal["action_steps"]
                )
                for i, goal in enumerate(goals_data["goals"])
            ]
            
            return GoalsResponse(
                generated_at=datetime.now(),
                goals=goals,
                rationale=goals_data["rationale"]
            )
        except Exception as e:
            logger.error(f"Failed to suggest learning goals: {e}")
            raise
