#!/usr/bin/env python3
"""
Gemini Service Test Script

このスクリプトはGeminiサービスの機能をテストするためのものです。
実際のAPIキーを使用してテストを実行できます。

使用方法:
    python scripts/test_gemini.py

環境変数:
    GEMINI_API_KEY: Google Gemini APIキー（必須）
"""

import asyncio
import sys
import os
from pathlib import Path

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.services.gemini_service import GeminiService
from app.core.config import Settings
from app.core.prompts import get_prompt
from app.core.exceptions import (
    GeminiRateLimitError,
    GeminiQuotaExceededError,
    GeminiAPIError,
    GeminiConfigurationError
)


async def test_basic_generation():
    """基本的なテキスト生成をテスト."""
    print("🧪 基本的なテキスト生成テスト")
    print("-" * 50)
    
    try:
        settings = Settings()
        service = GeminiService(settings)
        
        # シンプルなテキスト生成
        response = await service.generate_text("こんにちは、調子はどうですか？")
        print(f"✅ 応答: {response}")
        print()
        
    except GeminiRateLimitError as e:
        print(f"⚠️ レート制限: {e}")
        if e.retry_after_seconds:
            print(f"   {e.retry_after_seconds}秒後に再試行してください")
        print()
    except GeminiQuotaExceededError as e:
        print(f"⚠️ 利用制限: {e}")
        print()
    except GeminiAPIError as e:
        print(f"❌ APIエラー: {e}")
        print()
    except Exception as e:
        print(f"❌ 予期しないエラー: {e}")
        print()


async def test_learning_plan():
    """学習プラン生成をテスト."""
    print("📚 学習プラン生成テスト")
    print("-" * 50)
    
    try:
        settings = Settings()
        service = GeminiService(settings)
        
        plan = await service.generate_learning_plan(
            goal="Pythonの基礎をマスターする",
            time_available=120,
            current_level="初級",
            focus_areas=["変数", "関数", "クラス"],
            difficulty="medium"
        )
        
        print(f"✅ 学習プラン:\n{plan}")
        print()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        print()


async def test_todo_generation():
    """TODO生成をテスト."""
    print("📝 TODO生成テスト")
    print("-" * 50)
    
    try:
        settings = Settings()
        service = GeminiService(settings)
        
        todo = await service.generate_todo_list(
            time_available=60,
            recent_progress="関数の基礎を学習済み",
            weak_areas=["ループ", "条件分岐"],
            daily_goal="基本的なアルゴリズムの理解"
        )
        
        print(f"✅ TODO:\n{todo}")
        print()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        print()


async def test_health_check():
    """ヘルスチェックテスト."""
    print("🔍 ヘルスチェックテスト")
    print("-" * 50)
    
    try:
        settings = Settings()
        service = GeminiService(settings)
        
        health = await service.health_check()
        print(f"✅ ヘルス状態: {health}")
        print()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        print()



def test_prompts():
    """プロンプトシステムテスト."""
    print("📄 プロンプトシステムテスト")
    print("-" * 50)
    
    try:
        # 各カテゴリのプロンプトテスト
        categories = ["learning_plan", "todo", "analysis", "advice", "goal"]
        
        for category in categories:
            system_prompt = get_prompt(category, "system")
            user_template = get_prompt(category, "user_template")
            
            print(f"✅ {category}:")
            print(f"  システムプロンプト長: {len(system_prompt)} 文字")
            print(f"  ユーザーテンプレート長: {len(user_template)} 文字")
        
        # クイックプロンプトテスト
        quick_types = ["motivation", "tip", "encouragement"]
        for quick_type in quick_types:
            prompt = get_prompt("quick", quick_type)
            print(f"✅ quick_{quick_type}: {len(prompt)} 文字")
        
        print()
        
    except Exception as e:
        print(f"❌ エラー: {e}")
        print()


async def run_all_tests():
    """すべてのテストを実行."""
    print("🚀 Geminiサービステスト開始")
    print("=" * 60)
    print()
    
    # 環境変数チェック
    if not os.getenv("GEMINI_API_KEY"):
        print("❌ GEMINI_API_KEY 環境変数が設定されていません")
        print("   .envファイルにAPIキーを設定してください")
        return
    
    # プロンプトシステム（非同期でない）
    test_prompts()
    
    # 基本機能テスト
    await test_basic_generation()
    await test_health_check()
    
    # 具体的な機能テスト
    await test_learning_plan()
    await test_todo_generation()

    
    print("🎉 すべてのテストが完了しました！")


if __name__ == "__main__":
    # 非同期でテストを実行
    asyncio.run(run_all_tests())
