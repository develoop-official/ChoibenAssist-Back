"""AI prompts collection for different learning tasks."""

import asyncio
import logging
from typing import Dict, Optional

logger = logging.getLogger(__name__)


async def fetch_learning_records(user_id: str) -> Dict[str, str]:
    """
    ユーザーの学習記録をScrapboxから取得する

    Args:
        user_id: ユーザーID

    Returns:
        Dict[str, str]: 学習記録データ
    """
    try:
        from app.services.scrapbox_service import get_scrapbox_service
        from app.services.supabase_service import get_supabase_service

        # ユーザーのScrapboxプロジェクト名を取得
        supabase_service = get_supabase_service()
        project_name = await supabase_service.get_user_scrapbox_project(user_id)

        if not project_name:
            return {
                "recent_progress": "Scrapboxプロジェクトが設定されていません",
                "weak_areas": "Scrapboxプロジェクトが設定されていません",
            }

        # Scrapboxから学習記録を取得
        scrapbox_service = get_scrapbox_service()
        return await scrapbox_service.get_learning_records(project_name, user_id)

    except ImportError:
        logger.warning("Scrapbox/Supabaseサービスが利用できません")
        return {"recent_progress": "サービスが利用できません", "weak_areas": "サービスが利用できません"}
    except Exception as e:
        logger.error(f"学習記録取得中にエラー: {e}")
        return {"recent_progress": "データ取得エラーが発生しました", "weak_areas": "データ取得エラーが発生しました"}


def fetch_learning_records_sync(user_id: str) -> Dict[str, str]:
    """
    同期版の学習記録取得関数

    Args:
        user_id: ユーザーID

    Returns:
        Dict[str, str]: 学習記録データ
    """
    try:
        return asyncio.run(fetch_learning_records(user_id))
    except Exception as e:
        logger.error(f"同期学習記録取得中にエラー: {e}")
        return {"recent_progress": "まだ手をつけていない", "weak_areas": "特に弱点はありません"}


# Base system prompt for all AI interactions
BASE_SYSTEM_PROMPT = """あなたは学習アシスタントです。
効率的で実用的なアドバイスを短時間で提供してください。
回答は日本語で、簡潔かつ具体的にしてください。
ユーザーの学習目標を重視してください。
長い説明や過度な思考過程は避け、直接的で実行可能な提案を心がけてください。
「承知いたしました」「提案します」などの冗長な前置きは一切使わず、直接内容から始めてください。"""

# Learning plan generation prompts
LEARNING_PLAN_PROMPTS = {
    "system": f"""{BASE_SYSTEM_PROMPT}

学習プランを以下の形式で出力してください：
- 目標達成のための具体的なステップ
- 各ステップの推定時間
- 優先順位付け
- 実行可能な行動項目

前置きや挨拶は不要です。直接学習プランから始めてください。""",
    "user_template": """以下の条件で学習プランを作成してください：

目標: {goal}
利用可能時間: {time_available}分
現在のレベル: {current_level}
重点分野: {focus_areas}
難易度: {difficulty}

具体的で実行しやすい学習プランを提案してください。""",
}


# TODO generation prompts
TODO_PROMPTS = {
    "system": f"""{BASE_SYSTEM_PROMPT}

今日の学習TODOを以下の形式で出力してください（個数は利用可能時間に合わせて考えてください）：

1. タスク名
- 推定時間: {{時間}}min
- 内容: {{具体的な作業内容}}

2. タスク名
- 推定時間: {{時間}}min  
- 内容: {{具体的な作業内容}}

補足: {{必要に応じて追加情報}}

前置きや挨拶は不要です。直接TODOリストから始めてください。
実行しやすく、成果が見えるタスクを提案してください。""",
    "user_template": """以下の条件で今日のTODOリストを作成してください：

利用可能時間: {time_available}分
最近の進捗: {recent_progress}
弱点分野: {weak_areas}
今日の目標: {daily_goal}

今日の目標: {daily_goal}にそった課題、今日中に完了できる具体的なタスクを提案してください。""",
}


# Analysis prompts
ANALYSIS_PROMPTS = {
    "system": f"""{BASE_SYSTEM_PROMPT}

学習データ分析を以下の形式で出力してください：
- 現在の状況の要約
- 強みと改善点
- 具体的な次のアクション
- 数値に基づいた客観的評価

前置きや挨拶は不要です。直接分析結果から始めてください。""",
    "user_template": """以下の学習データを分析してください：

期間: {period}
学習記録: {learning_records}
目標: {goals}
進捗率: {progress_rate}

客観的な分析と改善提案を提供してください。""",
}

# Advice prompts
ADVICE_PROMPTS = {
    "system": f"""{BASE_SYSTEM_PROMPT}

学習アドバイスを以下の形式で出力してください：
- 現在の課題の特定
- 解決方法の提案
- 実行可能な改善ステップ
- モチベーション維持のコツ

前置きや挨拶は不要です。直接アドバイスから始めてください。""",
    "user_template": """以下の状況でアドバイスをお願いします：

現在の課題: {current_issues}
学習状況: {learning_status}
困っていること: {concerns}
目標: {target_goal}

具体的で実行しやすいアドバイスをお願いします。""",
}

# Goal setting prompts
GOAL_PROMPTS = {
    "system": f"""{BASE_SYSTEM_PROMPT}

SMART原則に基づいて目標を以下の形式で出力してください：
- 具体的(Specific)で測定可能(Measurable)な目標
- 達成可能(Achievable)で関連性(Relevant)のある内容
- 期限(Time-bound)の設定
- 進捗追跡方法の提案

前置きや挨拶は不要です。直接目標設定から始めてください。""",
    "user_template": """以下の条件でSMART目標を設定してください：

希望する成果: {desired_outcome}
期限: {timeline}
現在のレベル: {current_level}
利用可能なリソース: {available_resources}
制約条件: {constraints}

達成可能で測定可能な目標を提案してください。""",
}


def get_prompt(category: str, prompt_type: str = "system") -> str:
    """カテゴリとタイプに基づいてプロンプトを取得する。

    Args:
        category: プロンプトカテゴリ (learning_plan, todo, analysis, advice, goal)
        prompt_type: プロンプトタイプ (system, user_template)

    Returns:
        str: 要求されたプロンプト

    Raises:
        ValueError: カテゴリまたはプロンプトタイプが見つからない場合
    """
    prompt_mapping = {
        "learning_plan": LEARNING_PLAN_PROMPTS,
        "todo": TODO_PROMPTS,
        "analysis": ANALYSIS_PROMPTS,
        "advice": ADVICE_PROMPTS,
        "goal": GOAL_PROMPTS,
    }

    if category not in prompt_mapping:
        raise ValueError(f"Unknown prompt category: {category}")

    prompts = prompt_mapping[category]

    if prompt_type not in prompts:
        raise ValueError(
            f"Unknown prompt type '{prompt_type}' for category '{category}'"
        )

    return prompts[prompt_type]


def get_dynamic_prompt(
    category: str, user_id: str, prompt_type: str = "user_template"
) -> str:
    """学習記録に基づいて動的なプロンプトを生成する。

    Args:
        category: プロンプトカテゴリ (learning_plan, todo, analysis, advice, goal)
        user_id: ユーザーID
        prompt_type: プロンプトタイプ (system, user_template)

    Returns:
        str: 動的に生成されたプロンプト

    Raises:
        ValueError: カテゴリまたはプロンプトタイプが見つからない場合
    """
    # 学習記録をScrapboxから取得する（同期版）
    learning_records = fetch_learning_records_sync(user_id)

    # recent_progress と weak_areas を生成
    recent_progress = learning_records.get("recent_progress", "まだ手をつけていない")
    weak_areas = learning_records.get("weak_areas", "特に弱点はありません")

    # プロンプトを取得
    prompt_mapping = {
        "learning_plan": LEARNING_PLAN_PROMPTS,
        "todo": TODO_PROMPTS,
        "analysis": ANALYSIS_PROMPTS,
        "advice": ADVICE_PROMPTS,
        "goal": GOAL_PROMPTS,
    }

    if category not in prompt_mapping:
        raise ValueError(f"Unknown prompt category: {category}")

    prompts = prompt_mapping[category]

    if prompt_type not in prompts:
        raise ValueError(
            f"Unknown prompt type '{prompt_type}' for category '{category}'"
        )

    # 動的プロンプトを生成
    return prompts[prompt_type].format(
        recent_progress=recent_progress, weak_areas=weak_areas
    )


async def get_dynamic_prompt_async(
    category: str, user_id: str, prompt_type: str = "user_template"
) -> str:
    """
    学習記録に基づいて動的なプロンプトを生成する（非同期版）

    Args:
        category: プロンプトカテゴリ (learning_plan, todo, analysis, advice, goal)
        user_id: ユーザーID
        prompt_type: プロンプトタイプ (system, user_template)

    Returns:
        str: 動的に生成されたプロンプト

    Raises:
        ValueError: カテゴリまたはプロンプトタイプが見つからない場合
    """
    # 学習記録をScrapboxから取得する（非同期版）
    learning_records = await fetch_learning_records(user_id)

    # recent_progress と weak_areas を生成
    recent_progress = learning_records.get("recent_progress", "まだ手をつけていない")
    weak_areas = learning_records.get("weak_areas", "特に弱点はありません")

    # プロンプトを取得
    prompt_mapping = {
        "learning_plan": LEARNING_PLAN_PROMPTS,
        "todo": TODO_PROMPTS,
        "analysis": ANALYSIS_PROMPTS,
        "advice": ADVICE_PROMPTS,
        "goal": GOAL_PROMPTS,
    }

    if category not in prompt_mapping:
        raise ValueError(f"Unknown prompt category: {category}")

    prompts = prompt_mapping[category]

    if prompt_type not in prompts:
        raise ValueError(
            f"Unknown prompt type '{prompt_type}' for category '{category}'"
        )

    # 動的プロンプトを生成
    return prompts[prompt_type].format(
        recent_progress=recent_progress, weak_areas=weak_areas
    )
