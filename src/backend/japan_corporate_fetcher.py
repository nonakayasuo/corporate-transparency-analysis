#!/usr/bin/env python3
"""
日本の企業情報取得スクリプト

日本の企業情報を取得するためのツールです。
- 国税庁法人番号システムAPI
- 官報決算データベース
- 企業の公式ウェブサイト情報
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# 条件付きインポート
try:
    from src.backend.financial_data_fetcher import get_financial_data
except ImportError:
    get_financial_data = None

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 環境変数を読み込む
load_dotenv(project_root / ".env")


def fetch_corporate_number(company_name: str) -> Optional[dict]:
    """
    国税庁法人番号システムAPIから企業情報を取得

    注意: 実際のAPIを使用するには、法人番号システムの利用登録が必要です
    """
    print(f"  → 法人番号システムから企業情報を取得: {company_name}")

    # アプリケーションIDを環境変数から取得
    api_id = os.getenv("HOUJIN_BANGOU_API_ID")

    if not api_id:
        print("  → 警告: HOUJIN_BANGOU_API_IDが設定されていません。")
        print("  → ヒント: .envファイルにHOUJIN_BANGOU_API_IDを設定してください。")
        return None

    # 法人番号システムAPIのエンドポイント
    api_url = "https://api.houjin-bangou.nta.go.jp/4/name"

    try:
        params = {"id": api_id, "name": company_name, "type": "12", "format": "json"}  # 法人番号

        response = requests.get(api_url, params=params, timeout=10)
        response.raise_for_status()

        result = response.json()

        # APIレスポンスをパース
        if "count" in result and result["count"] > 0:
            # 最初の結果を使用
            company_data = result.get("corporations", [{}])[0]

            data = {
                "company_name": company_data.get("name", company_name),
                "corporate_number": company_data.get("corporate_number", ""),
                "address": company_data.get("address", ""),
                "post_code": company_data.get("post_code", ""),
                "establishment_date": company_data.get("update_date", ""),
                "status": "active",
                "timestamp": datetime.now().isoformat(),
                "source": "houjin_bangou_api",
            }

            print(f"  → 取得成功: 法人番号 {data.get('corporate_number')}")
            return data
        else:
            print("  → 警告: 企業が見つかりませんでした。")
            return None

    except requests.exceptions.RequestException as e:
        print(f"  → エラー: APIリクエストに失敗しました - {e}")
        return None
    except (KeyError, ValueError, json.JSONDecodeError) as e:
        print(f"  → エラー: APIレスポンスの解析に失敗しました - {e}")
        return None


def fetch_company_website_info(
    company_name: str, website_url: Optional[str] = None
) -> Optional[dict]:
    """
    企業の公式ウェブサイトから情報を取得
    """
    if not website_url:
        # 一般的なドメインパターンを試す
        possible_domains = [
            f"https://{company_name.lower()}.co.jp",
            f"https://{company_name.lower()}.com",
            f"https://www.{company_name.lower()}.co.jp",
            f"https://www.{company_name.lower()}.com",
        ]
    else:
        possible_domains = [website_url]

    print(f"  → 企業ウェブサイトから情報を取得: {company_name}")

    # 各ドメインを試行
    for url in possible_domains:
        try:
            # User-Agentを設定してリクエスト
            user_agent = (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/91.0.4472.124 Safari/537.36"
            )
            headers = {"User-Agent": user_agent}
            response = requests.get(url, headers=headers, timeout=10, allow_redirects=True)
            response.raise_for_status()

            # HTMLをパース
            soup = BeautifulSoup(response.content, "html.parser")

            # 基本情報を抽出
            data = {
                "company_name": company_name,
                "website_url": response.url,  # リダイレクト後のURL
                "timestamp": datetime.now().isoformat(),
            }

            # メタタグから情報を取得
            # description
            meta_desc = soup.find("meta", attrs={"name": "description"}) or soup.find(
                "meta", attrs={"property": "og:description"}
            )
            if meta_desc:
                data["description"] = meta_desc.get("content", "")

            # title
            title_tag = soup.find("title")
            if title_tag:
                data["title"] = title_tag.get_text(strip=True)

            # 構造化データ(JSON-LD)から情報を取得
            json_ld_scripts = soup.find_all("script", type="application/ld+json")
            for script in json_ld_scripts:
                try:
                    json_data = json.loads(script.string)
                    if isinstance(json_data, dict) and json_data.get("@type") == "Organization":
                        if "name" in json_data:
                            data["structured_name"] = json_data["name"]
                        if "description" in json_data:
                            data["description"] = (
                                data.get("description") or json_data["description"]
                            )
                        if "address" in json_data:
                            addr = json_data["address"]
                            if isinstance(addr, dict):
                                data["location"] = addr.get("addressLocality", "")
                            elif isinstance(addr, str):
                                data["location"] = addr
                        if "foundingDate" in json_data:
                            data["established"] = json_data["foundingDate"]
                        if "founder" in json_data:
                            data["founder"] = json_data["founder"]
                except (json.JSONDecodeError, KeyError):
                    continue

            # HTMLから直接情報を抽出(フォールバック)
            # 会社概要、企業情報などのセクションを探す
            about_sections = soup.find_all(
                ["div", "section"],
                class_=re.compile(r"about|company|corporate|企業|会社", re.I),
            )
            for section in about_sections:
                text = section.get_text(strip=True)
                if len(text) > 50 and not data.get("description"):
                    # 最初の長いテキストを説明として使用
                    data["description"] = text[:500]  # 最初の500文字
                    break

            # 住所パターンを検索
            address_pattern = re.compile(
                r"([都道府県][^都道府県]*?[市区町村][^都道府県]*?[0-9\-]+[番号]*[^都道府県]*)"
            )
            page_text = soup.get_text()
            address_match = address_pattern.search(page_text)
            if address_match and not data.get("location"):
                data["location"] = address_match.group(1).strip()

            # 設立年月日パターンを検索
            date_pattern = re.compile(r"(19|20)\d{2}[年/\-](0?[1-9]|1[0-2])[月/\-]")
            date_match = date_pattern.search(page_text)
            if date_match and not data.get("established"):
                data["established"] = date_match.group(0)

            print(f"  → 取得成功: {data.get('website_url')}")
            return data

        except requests.exceptions.RequestException as e:
            print(f"  → {url} へのアクセスに失敗: {e}")
            continue
        except Exception as e:
            print(f"  → {url} の解析中にエラー: {e}")
            continue

    print("  → 警告: ウェブサイト情報を取得できませんでした")
    return None


def fetch_financial_data(
    company_name: str, corporate_number: Optional[str] = None
) -> Optional[dict]:
    """
    財務データを取得(官報決算データベースなどから)

    注意: 実際のデータ取得には、各データベースへのアクセス権限が必要です
    """
    print(f"  → 財務データを取得: {company_name}")

    # 財務データ取得モジュールを使用
    if get_financial_data is not None:
        financial_data = get_financial_data(company_name, corporate_number)

        if financial_data:
            # タイムスタンプを追加
            financial_data["timestamp"] = datetime.now().isoformat()
            return financial_data
        else:
            print("  → 警告: 財務データが見つかりませんでした")
            return None
    else:
        print("  → 警告: 財務データ取得モジュールが利用できません")
        return None


def analyze_japanese_company(company_name: str, website_url: Optional[str] = None) -> dict:
    """
    日本の企業情報を包括的に分析
    """
    print(f"\n[日本の企業情報分析] {company_name}")
    print("=" * 60)

    # 1. 法人番号情報を取得
    corporate_info = fetch_corporate_number(company_name)

    # 2. ウェブサイト情報を取得
    website_info = fetch_company_website_info(company_name, website_url)

    # 3. 財務データを取得
    corporate_number = corporate_info.get("corporate_number") if corporate_info else None
    financial_data = fetch_financial_data(company_name, corporate_number)

    # 結果を統合
    result = {
        "company_name": company_name,
        "analysis_date": datetime.now().isoformat(),
        "country": "JP",
        "corporate_info": corporate_info,
        "website_info": website_info,
        "financial_data": financial_data,
        "sources": {
            "corporate_number_api": corporate_info is not None,
            "website": website_info is not None,
            "financial_data": financial_data is not None,
        },
    }

    return result


def main():
    parser = argparse.ArgumentParser(description="日本の企業情報を取得")
    parser.add_argument("--company", required=True, help="分析する企業名")
    parser.add_argument("--website", help="企業のウェブサイトURL(オプション)")
    parser.add_argument("--output", help="出力ファイルパス(オプション)")

    args = parser.parse_args()

    # 分析を実行
    result = analyze_japanese_company(args.company, args.website)

    # 結果を保存
    if args.output:
        output_file = Path(args.output)
    else:
        output_dir = project_root / "data" / "output"
        output_dir.mkdir(parents=True, exist_ok=True)
        safe_company_name = args.company.replace(" ", "_").replace("/", "_")
        output_file = (
            output_dir
            / f"{safe_company_name}_japan_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )

    output_path = Path(output_file)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print("\n" + "=" * 60)
    print("分析結果サマリー")
    print("=" * 60)
    print(f"企業名: {result['company_name']}")
    print(f"法人番号情報: {'取得済み' if result['sources']['corporate_number_api'] else '未取得'}")
    print(f"ウェブサイト情報: {'取得済み' if result['sources']['website'] else '未取得'}")
    print(f"財務データ: {'取得済み' if result['sources']['financial_data'] else '未取得'}")
    if result.get("financial_data", {}).get("net_income"):
        print(f"純利益: {result['financial_data']['net_income']:,}円")
    print(f"\n結果を保存: {output_file}")
    print("=" * 60)


if __name__ == "__main__":
    main()
