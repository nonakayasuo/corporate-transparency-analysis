#!/usr/bin/env python3
"""
EDGARツール統合モジュール

BellingcatのEDGARツールを使用してSECデータを取得します。
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
edgar_path = project_root / "tools" / "EDGAR" / "src"
sys.path.insert(0, str(edgar_path))

try:
    from edgar_tool.search_params import SearchParams
    from edgar_tool.text_search import search as edgar_search

    EDGAR_AVAILABLE = True
except ImportError as e:
    EDGAR_AVAILABLE = False
    import_error = str(e)
    if "typer" in import_error.lower():
        print("警告: EDGARツールの依存関係がインストールされていません。")
        print("  以下のコマンドでインストールしてください:")
        print("  cd tools/EDGAR && poetry install")
        print("  または")
        print("  uv pip install -e tools/EDGAR")
    else:
        print(f"警告: EDGARツールが利用できません: {import_error}")
        print("  tools/EDGARを確認してください。")


def search_company_edgar(company_name: str, max_results: int = 10) -> Optional[dict]:
    """
    EDGARツールを使用して企業を検索

    Args:
        company_name: 検索する企業名
        max_results: 最大結果数

    Returns:
        企業情報の辞書、またはNone
    """
    if not EDGAR_AVAILABLE:
        return None

    try:
        # EDGARのテキスト検索を使用
        # まずentityパラメータで企業名を検索（より正確）
        print(f"  → EDGAR検索を実行中: {company_name}")

        # 方法1: entityパラメータを使用（企業名として検索）
        try:
            search_params = SearchParams(entity=company_name, date_range_select="5y")
            search_results = edgar_search(search_params=search_params, max_results=max_results)

            if search_results and len(search_results) > 0:
                print("  → entity検索で結果を取得")
        except Exception as e1:
            print(f"  → entity検索でエラー: {e1}")
            search_results = None

        # 方法2: keywordsパラメータを使用（フォールバック）
        if not search_results or len(search_results) == 0:
            try:
                print("  → keywords検索を試行中...")
                search_params = SearchParams(keywords=[company_name], date_range_select="5y")
                search_results = edgar_search(search_params=search_params, max_results=max_results)

                if search_results and len(search_results) > 0:
                    print("  → keywords検索で結果を取得")
            except Exception as e2:
                print(f"  → keywords検索でエラー: {e2}")
                search_results = None

        if not search_results or len(search_results) == 0:
            print(f"  → 警告: {company_name} の検索結果が見つかりませんでした")
            return None

        # 最初の結果から企業情報を抽出
        first_result = search_results[0] if search_results else None
        cik = None
        if first_result:
            # CIKを取得（複数ある場合は最初のものを使用）
            cik_list = first_result.get("company_cik", [])
            if cik_list:
                cik = cik_list[0] if isinstance(cik_list, list) else cik_list

        # 結果を整理
        results = {
            "company_name": company_name,
            "cik": cik or "0000000000",
            "search_method": "edgar_text_search",
            "results_count": len(search_results),
            "filings": search_results,
            "timestamp": datetime.now().isoformat(),
        }

        print(f"  → 検索成功: {len(search_results)}件の結果を取得")
        if cik:
            print(f"  → CIK: {cik}")

        return results

    except Exception as e:
        print(f"  → EDGAR検索エラー: {e}")
        import traceback

        traceback.print_exc()
        return None


def get_company_filings(cik: str, form_type: Optional[str] = None) -> list[dict]:
    """
    企業の提出書類を取得

    Args:
        cik: CIKコード
        form_type: 書類タイプ（例: "10-K", "10-Q"）

    Returns:
        提出書類のリスト
    """
    if not EDGAR_AVAILABLE:
        return []

    try:
        # 実際の実装はEDGARツールのAPIに依存
        filings = []
        return filings

    except Exception as e:
        print(f"提出書類取得エラー: {e}")
        return []


if __name__ == "__main__":
    # テスト
    if EDGAR_AVAILABLE:
        result = search_company_edgar("Apple Inc.")
        print(result)
    else:
        print("EDGARツールが利用できません")
