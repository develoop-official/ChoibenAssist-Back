#!/usr/bin/env python3
"""
Scrapboxサービスの各関数を包括的にテストするスクリプト
実際のAPIを使用して各メソッドの動作を確認します
"""

import asyncio
import sys
import os
import json
from typing import Optional, Dict, Any, List
from datetime import datetime

# プロジェクトルートをパスに追加
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.services.scrapbox_service import ScrapboxService


class ScrapboxServiceTester:
    """Scrapboxサービスの包括的テストクラス"""
    
    def __init__(self, project_name: str):
        """
        テスターを初期化
        
        Args:
            project_name: テストするScrapboxプロジェクト名
        """
        self.project_name = project_name
        self.service = ScrapboxService(timeout=15.0)
        self.test_results: Dict[str, Dict[str, Any]] = {}
        self.test_data: Dict[str, Any] = {}
        
    async def run_all_tests(self):
        """すべてのテストを実行"""
        print(f"🚀 Scrapboxサービス包括テスト開始")
        print(f"📋 プロジェクト: {self.project_name}")
        print("=" * 60)
        
        # テスト実行順序
        test_methods = [
            ("get_pages_list", self.test_get_pages_list),
            ("get_page_text", self.test_get_page_text),
            ("get_recent_pages", self.test_get_recent_pages),
            ("get_learning_records", self.test_get_learning_records),
            ("_extract_learning_keywords", self.test_extract_learning_keywords),
            ("_extract_weakness_keywords", self.test_extract_weakness_keywords),
            ("_generate_recent_progress", self.test_generate_recent_progress),
            ("_generate_weak_areas", self.test_generate_weak_areas),
        ]
        
        for method_name, test_method in test_methods:
            print(f"\n📝 テスト実行: {method_name}")
            print("-" * 40)
            
            try:
                result = await test_method()
                self.test_results[method_name] = {
                    "status": "SUCCESS" if result else "FAILED",
                    "result": result
                }
                
                if result:
                    print(f"✅ {method_name}: テスト成功")
                else:
                    print(f"❌ {method_name}: テスト失敗")
                    
            except Exception as e:
                print(f"💥 {method_name}: 例外発生 - {e}")
                self.test_results[method_name] = {
                    "status": "ERROR", 
                    "error": str(e)
                }
        
        # 結果サマリー
        self.print_summary()
    
    async def test_get_pages_list(self) -> bool:
        """get_pages_listメソッドのテスト"""
        print("  🔍 ページ一覧取得をテスト中...")
        
        pages = await self.service.get_pages_list(self.project_name)
        
        # 基本検証
        if not isinstance(pages, list):
            print(f"  ❌ 戻り値がリストではありません: {type(pages)}")
            return False
        
        print(f"  📊 取得したページ数: {len(pages)}")
        
        if len(pages) == 0:
            print("  ⚠️  ページが0件です（プロジェクトが空または存在しない可能性）")
            return True  # 空のプロジェクトも有効
        
        # 最初のページの構造をチェック
        first_page = pages[0]
        required_fields = ['id', 'title', 'updated']
        
        for field in required_fields:
            if field not in first_page:
                print(f"  ❌ 必須フィールド '{field}' が見つかりません")
                return False
        
        print(f"  📄 最初のページ: {first_page.get('title', 'タイトルなし')}")
        print(f"  📅 最終更新: {datetime.fromtimestamp(first_page.get('updated', 0))}")
        
        # データをテスト用に保存
        self.test_data = {"pages": pages}
        
        return True
    
    async def test_get_page_text(self) -> bool:
        """get_page_textメソッドのテスト"""
        print("  🔍 ページ本文取得をテスト中...")
        
        # 前のテストでページが取得できていることを確認
        if not hasattr(self, 'test_data') or not self.test_data.get('pages'):
            print("  ❌ ページ一覧が取得できていないため、テストをスキップ")
            return False
        
        pages = self.test_data['pages']
        
        # 複数のページでテスト
        test_pages = pages[:3]  # 最初の3ページ
        success_count = 0
        
        for i, page in enumerate(test_pages):
            page_title = page.get('title', '')
            print(f"  📄 ページ {i+1}: '{page_title}' の本文取得中...")
            
            content = await self.service.get_page_text(self.project_name, page_title)
            
            if not isinstance(content, str):
                print(f"    ❌ 戻り値が文字列ではありません: {type(content)}")
                continue
            
            print(f"    📝 本文長: {len(content)}文字")
            
            if len(content) > 0:
                # 内容のプレビューを表示
                preview = content[:100].replace('\n', ' ') + "..." if len(content) > 100 else content
                print(f"    📖 内容プレビュー: {preview}")
                success_count += 1
            else:
                print("    ⚠️  空のページです")
                success_count += 1  # 空のページも有効
        
        # テスト結果の評価
        if success_count > 0:
            print(f"  ✅ {success_count}/{len(test_pages)} ページの本文取得に成功")
            return True
        else:
            print("  ❌ すべてのページで本文取得に失敗")
            return False
    
    async def test_get_recent_pages(self) -> bool:
        """get_recent_pagesメソッドのテスト"""
        print("  🔍 最近のページ取得をテスト中...")
        
        # 異なる期間でテスト
        test_periods = [7, 30, 90]
        
        for days in test_periods:
            print(f"  📅 {days}日以内のページを取得中...")
            
            recent_pages = await self.service.get_recent_pages(self.project_name, days)
            
            if not isinstance(recent_pages, list):
                print(f"    ❌ 戻り値がリストではありません: {type(recent_pages)}")
                return False
            
            print(f"    📊 取得ページ数: {len(recent_pages)}")
            
            # 最大20ページ制限の確認
            if len(recent_pages) > 20:
                print(f"    ❌ ページ数が制限を超えています: {len(recent_pages)} > 20")
                return False
            
            # 日付順ソートの確認
            if len(recent_pages) > 1:
                for i in range(len(recent_pages) - 1):
                    current_updated = recent_pages[i].get('updated', 0)
                    next_updated = recent_pages[i + 1].get('updated', 0)
                    
                    if current_updated < next_updated:
                        print(f"    ❌ ページが更新日時順にソートされていません")
                        return False
                
                print(f"    ✅ ページが正しく更新日時順にソートされています")
            
            # 期間フィルタリングの確認
            if recent_pages:
                cutoff_time = datetime.now().timestamp() - (days * 24 * 60 * 60)
                for page in recent_pages:
                    page_updated = page.get('updated', 0)
                    if page_updated <= cutoff_time:
                        print(f"    ❌ 期間外のページが含まれています")
                        return False
                
                print(f"    ✅ すべてのページが{days}日以内に更新されています")
        
        return True
    
    async def test_get_learning_records(self) -> bool:
        """get_learning_recordsメソッドのテスト"""
        print("  🔍 学習記録取得をテスト中...")
        
        learning_records = await self.service.get_learning_records(self.project_name)
        
        # 戻り値の構造チェック
        if not isinstance(learning_records, dict):
            print(f"  ❌ 戻り値が辞書ではありません: {type(learning_records)}")
            return False
        
        required_keys = ['recent_progress', 'weak_areas']
        for key in required_keys:
            if key not in learning_records:
                print(f"  ❌ 必須キー '{key}' が見つかりません")
                return False
            
            if not isinstance(learning_records[key], str):
                print(f"  ❌ キー '{key}' の値が文字列ではありません")
                return False
        
        print(f"  📈 最近の進捗: {learning_records['recent_progress']}")
        print(f"  ⚠️  弱点分野: {learning_records['weak_areas']}")
        
        # 内容の妥当性チェック
        if len(learning_records['recent_progress']) == 0:
            print("  ⚠️  最近の進捗が空です")
        
        if len(learning_records['weak_areas']) == 0:
            print("  ⚠️  弱点分野が空です")
        
        # テスト用データを保存
        if 'learning_records' not in self.test_data:
            self.test_data['learning_records'] = {}
        self.test_data['learning_records'] = learning_records
        
        return True
    
    async def test_extract_learning_keywords(self) -> bool:
        """_extract_learning_keywordsメソッドのテスト"""
        print("  🔍 学習キーワード抽出をテスト中...")
        
        # テストケース
        test_cases = [
            {
                "title": "Python学習記録",
                "content": "今日はPythonの基本文法を学習した。FastAPIを使って実装してみた。",
                "expected_keywords": ["Python", "FastAPI"]
            },
            {
                "title": "JavaScript勉強メモ",
                "content": "Reactフレームワークを習得中。TypeScriptも理解した。",
                "expected_keywords": ["JavaScript", "React", "TypeScript"]
            },
            {
                "title": "Docker実装完了",
                "content": "Kubernetesの学習も進めている。AWSの理解が深まった。",
                "expected_keywords": ["Docker", "Kubernetes", "AWS"]
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            title = str(test_case["title"])
            content = str(test_case["content"])
            expected_keywords = test_case["expected_keywords"]
            
            print(f"    テストケース {i+1}: {title}")
            
            keywords = self.service._extract_learning_keywords(title, content)
            
            if not isinstance(keywords, list):
                print(f"      ❌ 戻り値がリストではありません: {type(keywords)}")
                continue
            
            print(f"      📝 抽出されたキーワード: {keywords}")
            
            # 期待されるキーワードがあるかチェック
            found_expected = 0
            for expected in expected_keywords:
                if expected in keywords:
                    found_expected += 1
            
            if found_expected > 0:
                print(f"      ✅ 期待されるキーワードが {found_expected}/{len(expected_keywords)} 個見つかりました")
                success_count += 1
            else:
                print(f"      ⚠️  期待されるキーワードが見つかりませんでした")
        
        # 実際のページでもテスト
        if hasattr(self, 'test_data') and self.test_data.get('pages'):
            pages = self.test_data['pages']
            if pages:
                real_page = pages[0]
                title = real_page.get('title', '')
                content = await self.service.get_page_text(self.project_name, title)
                
                if content:
                    real_keywords = self.service._extract_learning_keywords(title, content)
                    print(f"    🔍 実際のページ '{title}' からのキーワード: {real_keywords}")
        
        return success_count > 0
    
    async def test_extract_weakness_keywords(self) -> bool:
        """_extract_weakness_keywordsメソッドのテスト"""
        print("  🔍 弱点キーワード抽出をテスト中...")
        
        # テストケース
        test_cases = [
            {
                "title": "学習の課題",
                "content": "Pythonが苦手で、非同期処理が難しい。SQLも問題がある。",
                "should_find_keywords": True
            },
            {
                "title": "エラー対処",
                "content": "Dockerでエラーが発生した。Reactがわからない部分がある。",
                "should_find_keywords": True
            },
            {
                "title": "成功報告",
                "content": "今日は順調に進んだ。すべて理解できた。",
                "should_find_keywords": False
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            title = str(test_case["title"])
            content = str(test_case["content"])
            should_find = bool(test_case["should_find_keywords"])
            
            print(f"    テストケース {i+1}: {title}")
            
            keywords = self.service._extract_weakness_keywords(title, content)
            
            if not isinstance(keywords, list):
                print(f"      ❌ 戻り値がリストではありません: {type(keywords)}")
                continue
            
            print(f"      📝 抽出されたキーワード: {keywords}")
            
            has_keywords = len(keywords) > 0
            expected = test_case['should_find_keywords']
            
            if has_keywords == expected:
                print(f"      ✅ 期待通りの結果です（キーワード{'あり' if expected else 'なし'}）")
                success_count += 1
            else:
                print(f"      ⚠️  期待と異なる結果です（期待: {'あり' if expected else 'なし'}, 実際: {'あり' if has_keywords else 'なし'}）")
        
        return success_count > 0
    
    async def test_generate_recent_progress(self) -> bool:
        """_generate_recent_progressメソッドのテスト"""
        print("  🔍 進捗生成をテスト中...")
        
        # テストケース
        test_cases = [
            {
                "pages": [],
                "expected_contains": "最近の学習記録が見つかりません"
            },
            {
                "pages": [
                    {
                        "title": "Python学習",
                        "content": "今日はPythonを学習した。基本文法を理解した。",
                        "updated": datetime.now().timestamp()
                    }
                ],
                "expected_contains": "Python学習"
            },
            {
                "pages": [
                    {
                        "title": "React実装",
                        "content": "コンポーネントを作成した。うまく動作している。",
                        "updated": datetime.now().timestamp()
                    },
                    {
                        "title": "Docker設定",
                        "content": "コンテナを実装した。問題なく完了した。",
                        "updated": datetime.now().timestamp() - 3600
                    }
                ],
                "expected_contains": "React実装"
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            # 型安全なアクセス
            if isinstance(test_case, dict):
                pages = test_case.get("pages", [])
                expected_contains = str(test_case.get("expected_contains", ""))
            else:
                print(f"      ❌ テストケースが辞書型ではありません")
                continue
            
            print(f"    テストケース {i+1}: {len(pages)}ページ")
            
            progress = self.service._generate_recent_progress(pages)
            
            if not isinstance(progress, str):
                print(f"      ❌ 戻り値が文字列ではありません: {type(progress)}")
                continue
            
            print(f"      📈 生成された進捗: {progress}")
            
            if expected_contains in progress:
                print(f"      ✅ 期待される内容が含まれています")
                success_count += 1
            else:
                print(f"      ⚠️  期待される内容が含まれていません")
        
        return success_count > 0
    
    async def test_generate_weak_areas(self) -> bool:
        """_generate_weak_areasメソッドのテスト"""
        print("  🔍 弱点分野生成をテスト中...")
        
        # テストケース
        test_cases = [
            {
                "keywords": [],
                "expected_contains": "特に弱点は見つかりませんでした"
            },
            {
                "keywords": ["Python", "SQL", "Docker"],
                "expected_contains": "Python"
            },
            {
                "keywords": ["非同期処理", "TypeScript", "React", "Vue"],
                "expected_length_limit": 3  # 最大3つまで
            }
        ]
        
        success_count = 0
        
        for i, test_case in enumerate(test_cases):
            # 型安全なアクセス
            if isinstance(test_case, dict):
                keywords = test_case.get("keywords", [])
                expected_contains = test_case.get("expected_contains")
                expected_length_limit = test_case.get("expected_length_limit")
            else:
                print(f"      ❌ テストケースが辞書型ではありません")
                continue
                
            print(f"    テストケース {i+1}: {len(keywords)}個のキーワード")
            
            weak_areas = self.service._generate_weak_areas(keywords)
            
            if not isinstance(weak_areas, str):
                print(f"      ❌ 戻り値が文字列ではありません: {type(weak_areas)}")
                continue
            
            print(f"      ⚠️  生成された弱点分野: {weak_areas}")
            
            # 期待される内容のチェック
            if expected_contains:
                if expected_contains in weak_areas:
                    print(f"      ✅ 期待される内容が含まれています")
                    success_count += 1
                else:
                    print(f"      ⚠️  期待される内容が含まれていません")
            
            # 長さ制限のチェック
            if expected_length_limit:
                split_areas = [area.strip() for area in weak_areas.split(',')]
                if len(split_areas) <= expected_length_limit:
                    print(f"      ✅ 長さ制限が守られています ({len(split_areas)} <= {expected_length_limit})")
                    success_count += 1
                else:
                    print(f"      ❌ 長さ制限を超えています ({len(split_areas)} > {expected_length_limit})")
        
        return success_count > 0
    
    def print_summary(self):
        """テスト結果のサマリーを表示"""
        print("\n" + "=" * 60)
        print("📊 テスト結果サマリー")
        print("=" * 60)
        
        total_tests = len(self.test_results)
        successful_tests = sum(1 for result in self.test_results.values() if result['status'] == 'SUCCESS')
        failed_tests = sum(1 for result in self.test_results.values() if result['status'] == 'FAILED')
        error_tests = sum(1 for result in self.test_results.values() if result['status'] == 'ERROR')
        
        print(f"📈 総テスト数: {total_tests}")
        print(f"✅ 成功: {successful_tests}")
        print(f"❌ 失敗: {failed_tests}")
        print(f"💥 エラー: {error_tests}")
        print(f"🎯 成功率: {(successful_tests/total_tests)*100:.1f}%")
        
        print("\n📋 詳細結果:")
        for method_name, result in self.test_results.items():
            status_icon = "✅" if result['status'] == 'SUCCESS' else "❌" if result['status'] == 'FAILED' else "💥"
            print(f"  {status_icon} {method_name}: {result['status']}")
            
            if result['status'] == 'ERROR':
                print(f"    エラー詳細: {result.get('error', 'Unknown error')}")
        
        print("\n" + "=" * 60)
        
        if successful_tests == total_tests:
            print("🎉 すべてのテストが成功しました！")
        elif successful_tests > total_tests // 2:
            print("😊 大部分のテストが成功しました。")
        else:
            print("😢 多くのテストが失敗しました。実装を確認してください。")


def get_project_name() -> Optional[str]:
    """標準入力からプロジェクト名を取得"""
    try:
        print("🧪 Scrapboxサービス包括テストツール")
        print("=" * 40)
        print("テストしたいScrapboxプロジェクト名を入力してください。")
        print("例: pnasi, help-jp, programming-memo など")
        print("(Ctrl+C で終了)")
        print()
        
        project_name = input("プロジェクト名: ").strip()
        
        if not project_name:
            print("❌ プロジェクト名が入力されていません")
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
    # コマンドライン引数またはstdin からプロジェクト名を取得
    if len(sys.argv) > 1:
        project_name = sys.argv[1]
        print(f"📌 コマンドライン引数でプロジェクト名を指定: {project_name}")
    else:
        project_name = get_project_name()
    
    if not project_name:
        return
    
    print(f"\n🔄 包括テスト開始...")
    
    # テスター作成・実行
    tester = ScrapboxServiceTester(project_name)
    await tester.run_all_tests()


if __name__ == "__main__":
    asyncio.run(main())
