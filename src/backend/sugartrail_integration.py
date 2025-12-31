#!/usr/bin/env python3
"""
sugartrailツール統合モジュール

Bellingcatのsugartrailツールを使用してCompanies Houseデータを取得します。
"""

import os
import sys
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sugartrail_path = project_root / "tools" / "sugartrail"
sys.path.insert(0, str(sugartrail_path))

# 環境変数を読み込む
load_dotenv(project_root / ".env")

try:
    from sugartrail.api import (
        get_appointments,
        get_company,
        get_company_officers,
        get_psc,
    )

    SUGARTRAIL_AVAILABLE = True
except ImportError:
    SUGARTRAIL_AVAILABLE = False
    print("警告: sugartrailツールが利用できません。tools/sugartrailを確認してください。")


def search_company_sugartrail(company_name: str) -> Optional[dict]:
    """
    sugartrailツールを使用して企業を検索

    Args:
        company_name: 検索する企業名

    Returns:
        企業情報の辞書、またはNone
    """
    if not SUGARTRAIL_AVAILABLE:
        return None

    # Companies House APIの認証情報を確認
    username = os.getenv("COMPANIES_HOUSE_USERNAME")
    password = os.getenv("COMPANIES_HOUSE_PASSWORD")

    if not username or not password:
        print("警告: Companies House APIの認証情報が設定されていません。")
        print(
            "ヒント: .envファイルにCOMPANIES_HOUSE_USERNAMEとCOMPANIES_HOUSE_PASSWORDを設定してください。"
        )
        return None

    try:
        # 企業IDを取得(実際の実装では検索APIを使用)
        # ここでは簡易的な実装
        company_id = None  # 実際には検索結果から取得

        if company_id:
            company_data = get_company(company_id)
            officers = get_company_officers(company_id)
            psc = get_psc(company_id)

            return {
                "company_name": company_name,
                "company_id": company_id,
                "company_data": company_data,
                "officers": officers,
                "psc": psc,
                "source": "sugartrail",
            }
        else:
            return None

    except Exception as e:
        print(f"sugartrail検索エラー: {e}")
        return None


def get_officer_network(officer_id: str) -> Optional[dict]:
    """
    役員のネットワークを取得

    Args:
        officer_id: 役員ID

    Returns:
        ネットワーク情報の辞書、またはNone
    """
    if not SUGARTRAIL_AVAILABLE:
        return None

    try:
        appointments = get_appointments(officer_id)
    except Exception as e:
        print(f"役員ネットワーク取得エラー: {e}")
        return None
    else:
        return {
            "officer_id": officer_id,
            "appointments": appointments,
            "source": "sugartrail",
        }
        print(f"役員ネットワーク取得エラー: {e}")
        return None


if __name__ == "__main__":
    # テスト
    if SUGARTRAIL_AVAILABLE:
        result = search_company_sugartrail("Example Company")
        print(result)
    else:
        print("sugartrailツールが利用できません")
