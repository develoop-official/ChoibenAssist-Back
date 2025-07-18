#!/usr/bin/env python3
"""
Scrapboxサービスのインタラクティブテストスクリプト
"""

import asyncio
import sys
from typing import Optional
import pytest

from app.services.scrapbox_service import ScrapboxService


@pytest.fixture
def project_name():
    """テスト用のプロジェクト名を提供するfixture"""
    return "test-project"  # デフォルトのテストプロジェクト名


@pytest.mark.asyncio
async def test_scrapbox_service(project_name: str):
    """
    指定されたプロジェクト名でScrapboxサービスをテストする

    Args:
        project_name: テストするScrapboxプロジェクト名
    """
    print(f"🚀 Scrapbox API テスト開始: プロジェクト '{project_name}'")
    print("=" * 50)

    service = ScrapboxService()

    try:
        # 1. ページ一覧取得テスト
        print("📋 1. ページ一覧取得テスト...")
        pages = await service.get_pages_list(project_name)

        if pages:
            print(f"✅ 成功! {len(pages)}ページを取得しました")
            print("   最新のページ:")
            for i, page in enumerate(pages[:3]):
                title = page.get("title", "タイトルなし")
                updated = page.get("updated", 0)
                views = page.get("views", 0)
                print(f"   {i+1}. {title} (更新: {updated}, 閲覧数: {views})")
        else:
            print("❌ ページが取得できませんでした")
            return

        print()

        # 2. 最新ページの本文取得テスト
        print("📄 2. ページ本文取得テスト...")
        if pages:
            first_page = pages[0]
            page_title = first_page.get("title", "")
            print(f"   取得対象: '{page_title}'")

            content = await service.get_page_text(project_name, page_title)
            if content:
                print(f"✅ 成功! {len(content)}文字の本文を取得しました")
                # 最初の200文字を表示
                preview = content[:200] + "..." if len(content) > 200 else content
                print(f"   内容プレビュー: {preview}")
            else:
                print("❌ ページ本文が取得できませんでした")

        print()

        # 3. 最近のページ取得テスト
        print("📅 3. 最近のページ取得テスト (7日以内)...")
        recent_pages = await service.get_recent_pages(project_name, days=7)

        if recent_pages:
            print(f"✅ 成功! {len(recent_pages)}ページを取得しました")
            print("   最近のページ:")
            for i, page in enumerate(recent_pages[:3]):
                title = page.get("title", "タイトルなし")
                updated = page.get("updated", 0)
                print(f"   {i+1}. {title} (更新: {updated})")
        else:
            print("⚠️  最近のページが見つかりませんでした（7日以内に更新されたページなし）")

        print()

        # 4. 学習記録取得テスト
        print("🧠 4. 学習記録分析テスト...")
        learning_records = await service.get_learning_records(project_name)

        print("✅ 学習記録分析完了!")
        print(f"   最近の進捗: {learning_records.get('recent_progress', 'なし')}")
        print(f"   弱点分野: {learning_records.get('weak_areas', 'なし')}")

        print()

        # 5. キーワード抽出テスト
        print("🔍 5. キーワード抽出テスト...")
        if pages and len(pages) > 0:
            test_page = pages[0]
            title = test_page.get("title", "")
            content = await service.get_page_text(project_name, title)

            if content:
                learning_keywords = service._extract_learning_keywords(title, content)
                weakness_keywords = service._extract_weakness_keywords(title, content)

                print(f"   学習キーワード: {learning_keywords}")
                print(f"   弱点キーワード: {weakness_keywords}")
            else:
                print("   ⚠️ ページ内容が取得できないため、キーワード抽出をスキップ")

        print()
        print("🎉 すべてのテストが完了しました!")

    except Exception as e:
        print(f"❌ エラーが発生しました: {e}")
        import traceback

        traceback.print_exc()


def get_project_name() -> Optional[str]:
    """
    標準入力からプロジェクト名を取得する

    Returns:
        プロジェクト名またはNone（キャンセル時）
    """
    try:
        print("Scrapbox APIテストツール")
        print("=" * 30)
        print("テストしたいScrapboxプロジェクト名を入力してください。")
        print("例: pnasi, help-jp, programming-memo など")
        print("(Ctrl+C で終了)")
        print()

        project_name = input("プロジェクト名: ").strip()

        if not project_name:
            print("❌ プロジェクト名が入力されていません")
            return None

        # 簡単なバリデーション
        if " " in project_name or "/" in project_name:
            print("⚠️  プロジェクト名にスペースやスラッシュが含まれています")
            confirm = input("このまま続行しますか？ (y/N): ")
            if confirm.lower() != "y":
                return None

        return project_name

    except KeyboardInterrupt:
        print("\n\n👋 テストを終了します")
        return None
    except Exception as e:
        print(f"❌ 入力エラー: {e}")
        return None


async def main():
    """メイン関数"""
    # コマンドライン引数からプロジェクト名を取得
    if len(sys.argv) > 1:
        project_name = sys.argv[1]
        print(f"📌 コマンドライン引数でプロジェクト名を指定: {project_name}")
    else:
        # 標準入力から取得
        project_name = get_project_name()

    if not project_name:
        return

    print(f"\n🔄 テスト開始...")
    await test_scrapbox_service(project_name)


if __name__ == "__main__":
    asyncio.run(main())
