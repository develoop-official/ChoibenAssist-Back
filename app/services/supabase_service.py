import httpx
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timedelta

from app.config import settings

logger = logging.getLogger(__name__)


class SupabaseService:
    def __init__(self):
        """Initialize Supabase service"""
        self.base_url = settings.supabase_url
        self.api_key = settings.supabase_anon_key
        self.headers = {
            "apikey": self.api_key,
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }

    async def get_user_learning_data(self, user_id: str) -> Dict[str, Any]:
        """Get comprehensive user learning data"""
        try:
            async with httpx.AsyncClient() as client:
                # Get user profile
                user_response = await client.get(
                    f"{self.base_url}/rest/v1/users?id=eq.{user_id}",
                    headers=self.headers
                )
                
                # Get learning records
                records_response = await client.get(
                    f"{self.base_url}/rest/v1/records?user_id=eq.{user_id}&order=created_at.desc&limit=50",
                    headers=self.headers
                )
                
                return {
                    "user_profile": user_response.json(),
                    "learning_records": records_response.json(),
                    "total_records": len(records_response.json())
                }
        except Exception as e:
            logger.error(f"Failed to get user learning data: {e}")
            return {"user_profile": [], "learning_records": [], "total_records": 0}

    async def get_recent_learning_history(
        self, 
        user_id: str, 
        days: int = 7
    ) -> List[Dict[str, Any]]:
        """Get recent learning history for TODO generation"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).isoformat()
            
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/records",
                    params={
                        "user_id": f"eq.{user_id}",
                        "created_at": f"gte.{cutoff_date}",
                        "order": "created_at.desc"
                    },
                    headers=self.headers
                )
                
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get recent learning history: {e}")
            return []

    async def get_learning_analytics_data(
        self, 
        user_id: str, 
        period: str
    ) -> Dict[str, Any]:
        """Get data for learning analytics"""
        try:
            # Calculate date range based on period
            if period == "daily":
                start_date = datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
            elif period == "weekly":
                start_date = datetime.now() - timedelta(days=7)
            else:  # monthly
                start_date = datetime.now() - timedelta(days=30)
            
            async with httpx.AsyncClient() as client:
                # Get records for the period
                records_response = await client.get(
                    f"{self.base_url}/rest/v1/records",
                    params={
                        "user_id": f"eq.{user_id}",
                        "created_at": f"gte.{start_date.isoformat()}",
                        "order": "created_at.desc"
                    },
                    headers=self.headers
                )
                
                records = records_response.json()
                
                # Calculate analytics
                total_time = sum(record.get("duration", 0) for record in records)
                subjects = list(set(record.get("subject", "") for record in records))
                
                return {
                    "period": period,
                    "records": records,
                    "total_time": total_time,
                    "subjects": subjects,
                    "study_days": len(set(record.get("created_at", "")[:10] for record in records))
                }
        except Exception as e:
            logger.error(f"Failed to get learning analytics data: {e}")
            return {"records": [], "total_time": 0, "subjects": [], "study_days": 0}

    async def get_user_profile(self, user_id: str) -> Dict[str, Any]:
        """Get user profile for personalized advice"""
        try:
            async with httpx.AsyncClient() as client:
                # Get user basic info
                user_response = await client.get(
                    f"{self.base_url}/rest/v1/users?id=eq.{user_id}",
                    headers=self.headers
                )
                
                # Get recent performance data
                recent_records = await self.get_recent_learning_history(user_id, 14)
                
                return {
                    "user_info": user_response.json(),
                    "recent_performance": recent_records,
                    "learning_patterns": self._analyze_learning_patterns(recent_records)
                }
        except Exception as e:
            logger.error(f"Failed to get user profile: {e}")
            return {"user_info": [], "recent_performance": [], "learning_patterns": {}}

    async def get_current_goals(self, user_id: str) -> List[Dict[str, Any]]:
        """Get current learning goals"""
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/rest/v1/goals?user_id=eq.{user_id}&is_active=eq.true",
                    headers=self.headers
                )
                
                return response.json()
        except Exception as e:
            logger.error(f"Failed to get current goals: {e}")
            return []

    def _analyze_learning_patterns(self, records: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Analyze learning patterns from records"""
        if not records:
            return {}
        
        # Calculate average session duration
        durations = [record.get("duration", 0) for record in records if record.get("duration")]
        avg_duration = sum(durations) / len(durations) if durations else 0
        
        # Find most studied subjects
        subjects = {}
        for record in records:
            subject = record.get("subject", "")
            if subject:
                subjects[subject] = subjects.get(subject, 0) + 1
        
        # Find preferred study times (hour of day)
        study_hours = []
        for record in records:
            created_at = record.get("created_at", "")
            if created_at:
                try:
                    hour = datetime.fromisoformat(created_at.replace("Z", "+00:00")).hour
                    study_hours.append(hour)
                except:
                    pass
        
        return {
            "average_session_duration": avg_duration,
            "favorite_subjects": dict(sorted(subjects.items(), key=lambda x: x[1], reverse=True)[:3]),
            "preferred_study_hours": study_hours,
            "study_consistency": len(set(record.get("created_at", "")[:10] for record in records))
        }
