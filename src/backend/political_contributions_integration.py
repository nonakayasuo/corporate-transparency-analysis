#!/usr/bin/env python3
"""
政治献金・政治資金統合モジュール

企業と政治家の関係、政治献金データを取得します。
- FEC (Federal Election Commission) API - 米国の連邦選挙の政治献金データ
- 日本の政治資金収支報告書データ（将来実装）

注意: OpenSecrets APIは2025年4月15日に廃止されました。
"""

import os
import sys
from pathlib import Path
from typing import Optional
from datetime import datetime, timedelta

import requests
from dotenv import load_dotenv

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 環境変数を読み込む
load_dotenv(project_root / ".env")


def search_fec_contributions(company_name: str, cik: Optional[str] = None) -> Optional[dict]:
    """
    FEC APIを使用して企業の政治献金を検索

    Args:
        company_name: 企業名
        cik: CIKコード（オプション）

    Returns:
        政治献金データの辞書、またはNone
    """
    print(f"  → FEC APIから政治献金データを検索: {company_name}")

    try:
        # FEC APIのエンドポイント
        # 注意: FEC APIは無料で利用可能だが、レート制限がある
        base_url = "https://api.open.fec.gov/v1"
        api_key = os.getenv("FEC_API_KEY")

        if not api_key:
            print("  → 警告: FEC_API_KEYが設定されていません。")
            print("  → ヒント: https://api.open.fec.gov/developers/ でAPIキーを取得してください")
            return None

        # 企業名で検索（committee_nameまたはcontributor_nameで検索）
        contributions = []

        # 過去5年間のデータを取得
        # 注意: two_year_transaction_periodは偶数年（選挙年）のみ有効
        # 例: 2020, 2022, 2024など
        current_year = datetime.now().year
        # 偶数年に調整（最新の選挙年を取得）
        latest_election_year = current_year if current_year % 2 == 0 else current_year - 1

        # 過去5回の選挙年を取得（偶数年のみ）
        election_years = []
        for i in range(6):  # 最大6年分（3回の選挙周期）
            year = latest_election_year - (i * 2)
            if year >= 2020:  # 2020年以降のみ
                election_years.append(year)

        for year in election_years:
            try:
                # 寄付者（contributor）として検索
                params = {
                    "api_key": api_key,
                    "contributor_name": company_name,
                    "two_year_transaction_period": year,
                    "per_page": 100,
                    "page": 1,
                }

                response = requests.get(
                    f"{base_url}/schedules/schedule_a",
                    params=params,
                    timeout=10,
                )
                response.raise_for_status()
                data = response.json()

                if data.get("results"):
                    contributions.extend(data["results"])
                    print(f"    → {year}年のデータ: {len(data['results'])}件の寄付を発見")

            except requests.exceptions.HTTPError as e:
                # 422エラーは無効な選挙年を指定した場合に発生（既に偶数年のみを指定しているが、念のため）
                if e.response and e.response.status_code == 422:
                    print(f"    → {year}年のデータ取得エラー: 無効な選挙年（422エラー）")
                else:
                    print(f"    → {year}年のデータ取得エラー: {e}")
                continue
            except requests.exceptions.RequestException as e:
                print(f"    → {year}年のデータ取得エラー: {e}")
                continue

        if contributions:
            # データを整理
            result = {
                "company_name": company_name,
                "cik": cik,
                "contributions": contributions,
                "total_contributions": len(contributions),
                "total_amount": sum(
                    float(c.get("contribution_receipt_amount", 0) or 0) for c in contributions
                ),
                "recipients": {},
                "timestamp": datetime.now().isoformat(),
                "source": "FEC",
            }

            # 受取人別に集計
            for contrib in contributions:
                recipient = contrib.get("recipient_name") or contrib.get(
                    "committee_name", "Unknown"
                )
                amount = float(contrib.get("contribution_receipt_amount", 0) or 0)
                if recipient not in result["recipients"]:
                    result["recipients"][recipient] = {"count": 0, "amount": 0.0}
                result["recipients"][recipient]["count"] += 1
                result["recipients"][recipient]["amount"] += amount

            print(f"  → FECから {len(contributions)} 件の政治献金を発見")
            print(f"  → 総額: ${result['total_amount']:,.2f}")
            return result
        else:
            print("  → FECから政治献金データが見つかりませんでした")
            return None

    except Exception as e:
        print(f"  → FEC APIエラー: {e}")
        import traceback

        traceback.print_exc()
        return None


def search_opensecrets_contributions(
    company_name: str, cik: Optional[str] = None
) -> Optional[dict]:
    """
    OpenSecrets APIを使用して企業の政治献金とロビー活動を検索

    注意: OpenSecrets APIは2025年4月15日に廃止されました。
    この関数は互換性のために残されていますが、常にNoneを返します。

    Args:
        company_name: 企業名
        cik: CIKコード（オプション）

    Returns:
        None（APIが廃止されたため）
    """
    print(f"  → OpenSecrets APIは2025年4月15日に廃止されました")
    print(
        f"  → カスタムデータソリューションが必要な場合は commercial@opensecrets.org に連絡してください"
    )
    return None


def search_japan_political_contributions(company_name: str) -> Optional[dict]:
    """
    日本の政治資金収支報告書から企業の政治献金を検索

    Args:
        company_name: 企業名

    Returns:
        政治献金データの辞書、またはNone
    """
    print(f"  → 日本の政治資金データを検索: {company_name}")

    # 注意: 日本の政治資金データは、総務省や各都道府県選挙管理委員会が公開しているが、
    # 統一されたAPIは存在しない。将来的にスクレイピングやデータベース化が必要。

    print("  → 警告: 日本の政治資金データの自動取得は未実装です")
    print("  → ヒント: 総務省の政治資金収支報告書データベースを参照してください")
    print("    https://www.soumu.go.jp/senkyo/seiji_s/seijishikin/")

    return None


def search_political_contributions(
    company_name: str, country: str = "US", cik: Optional[str] = None
) -> Optional[dict]:
    """
    政治献金データを検索（複数のソースから試行）

    Args:
        company_name: 企業名
        country: 国（US, JP）
        cik: CIKコード（US企業の場合）

    Returns:
        政治献金データの辞書、またはNone
    """
    if country == "US":
        # FEC APIから検索
        fec_data = search_fec_contributions(company_name, cik)
        if fec_data:
            return fec_data

        # OpenSecrets APIから検索
        opensecrets_data = search_opensecrets_contributions(company_name, cik)
        if opensecrets_data:
            return opensecrets_data

    elif country == "JP":
        # 日本の政治資金データを検索
        japan_data = search_japan_political_contributions(company_name)
        if japan_data:
            return japan_data

    return None


if __name__ == "__main__":
    # テスト
    result = search_political_contributions("Apple Inc.", "US", "0000320193")
    if result:
        print(f"\n結果: {result}")
    else:
        print("\n結果が見つかりませんでした")
