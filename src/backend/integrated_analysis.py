#!/usr/bin/env python3
"""
統合分析スクリプト

このスクリプトは、EDGAR、sugartrail、name-variant-searchの3つのツールを
組み合わせて包括的な企業・金融の透明性分析を実行します。
"""

import argparse
import json
import sys
from datetime import datetime
from pathlib import Path

# プロジェクトルートをパスに追加（インポート前に設定）
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "tools" / "EDGAR"))
sys.path.insert(0, str(project_root / "tools" / "sugartrail"))
sys.path.insert(0, str(project_root / "tools" / "name-variant-search"))

# 条件付きインポート
try:
    from src.backend.name_variant_integration import generate_name_variants
except ImportError:
    generate_name_variants = None

try:
    from src.backend.edgar_integration import search_company_edgar

    # 関数が存在するか確認
    if search_company_edgar is None:
        search_company_edgar = None
except (ImportError, AttributeError) as e:
    print(f"  → 警告: EDGAR統合モジュールのインポートに失敗: {e}")
    search_company_edgar = None

try:
    from src.backend.sugartrail_integration import search_company_sugartrail
except ImportError:
    search_company_sugartrail = None

try:
    from src.backend.japan_corporate_fetcher import analyze_japanese_company
except ImportError:
    analyze_japanese_company = None


def setup_directories():
    """必要なディレクトリを作成"""
    data_dir = project_root / "data"
    for subdir in ["edgar", "sugartrail", "name_variants", "output"]:
        (data_dir / subdir).mkdir(exist_ok=True)


def get_name_variants(name):
    """
    name-variant-searchを使用して名前のバリエーションを取得
    """
    print(f"  → 名前のバリエーションを検索: {name}")

    # name-variant-search統合モジュールを使用
    if generate_name_variants is not None:
        variants = generate_name_variants(name)
        print(f"  → {len(variants)}個のバリエーションを生成")
        return variants
    else:
        # フォールバック: 基本的なバリエーション
        variants = [name, name.upper(), name.lower(), name.title()]
        return variants


def fetch_edgar_data(company_name, country="US"):
    """
    EDGARを使用してSECデータを取得(米国企業の場合)
    """
    if country != "US":
        print("  → EDGARは米国企業のみ対応。スキップします。")
        return None

    print(f"  → EDGARからSECデータを取得: {company_name}")

    # EDGAR統合モジュールを使用
    if search_company_edgar is not None:
        try:
            edgar_result = search_company_edgar(company_name)

            if edgar_result:
                data = {
                    "company_name": company_name,
                    "cik": edgar_result.get("cik", "0000000000"),
                    "filings": edgar_result.get("filings", []),
                    "search_results": edgar_result,
                    "timestamp": datetime.now().isoformat(),
                    "source": "edgar_tool",
                }
                return data
            else:
                print("  → 警告: EDGAR検索結果が取得できませんでした")
                return None
        except Exception as e:
            print(f"  → エラー: EDGARデータ取得中にエラーが発生しました - {e}")
            return None
    else:
        print("  → 警告: EDGAR統合モジュールが利用できません")
        print("  → ヒント: EDGARツールの依存関係をインストールしてください")
        print("    cd tools/EDGAR && poetry install")
        return None


def fetch_sugartrail_data(company_name, country="UK"):
    """
    sugartrailを使用してCompanies Houseデータを取得(英国企業の場合)
    """
    if country != "UK":
        print("  → sugartrailは英国企業のみ対応。スキップします。")
        return None

    print(f"  → sugartrailからCompanies Houseデータを取得: {company_name}")

    # sugartrail統合モジュールを使用
    if search_company_sugartrail is not None:
        sugartrail_result = search_company_sugartrail(company_name)

        if sugartrail_result:
            data = {
                "company_name": company_name,
                "companies_house_id": sugartrail_result.get("company_id", "00000000"),
                "officers": sugartrail_result.get("officers", {}).get("items", []),
                "addresses": [],
                "network": {},
                "company_data": sugartrail_result.get("company_data"),
                "timestamp": datetime.now().isoformat(),
                "source": "sugartrail",
            }
            return data

    # フォールバック: 仮データ
    data = {
        "company_name": company_name,
        "companies_house_id": "00000000",
        "officers": [],
        "addresses": [],
        "network": {},
        "timestamp": datetime.now().isoformat(),
        "note": "sugartrail統合準備中",
    }

    return data


def fetch_japan_corporate_data(company_name, website_url=None):
    """
    日本の企業情報を取得
    """
    print(f"  → 日本の企業情報を取得: {company_name}")

    # japan_corporate_fetcherモジュールをインポート
    if analyze_japanese_company is not None:
        result = analyze_japanese_company(company_name, website_url)
        return result
    else:
        print("  → 警告: japan_corporate_fetcherモジュールが見つかりません")
        return None


def analyze_network(edgar_data, sugartrail_data, japan_data, name_variants):
    """
    取得したデータを統合してネットワーク分析を実行
    """
    print("\n[ステップ4] ネットワーク分析を実行")

    network = {"entities": [], "relationships": [], "analysis": {}}

    # EDGARデータからエンティティを抽出
    if edgar_data:
        network["entities"].append(
            {
                "type": "company",
                "name": edgar_data.get("company_name"),
                "source": "EDGAR",
            }
        )

    # sugartrailデータからエンティティと関係を抽出
    if sugartrail_data:
        network["entities"].append(
            {
                "type": "company",
                "name": sugartrail_data.get("company_name"),
                "source": "sugartrail",
            }
        )

        # 役員情報を追加
        for officer in sugartrail_data.get("officers", []):
            network["entities"].append({"type": "officer", "name": officer, "source": "sugartrail"})
            network["relationships"].append(
                {
                    "from": sugartrail_data.get("company_name"),
                    "to": officer,
                    "type": "officer_of",
                }
            )

    # 日本の企業データからエンティティと関係を抽出
    if japan_data:
        network["entities"].append(
            {
                "type": "company",
                "name": japan_data.get("company_name"),
                "source": "japan_corporate",
            }
        )

        # CEO情報を追加
        if japan_data.get("website_info", {}).get("ceo"):
            ceo_name = japan_data["website_info"]["ceo"]
            network["entities"].append(
                {"type": "officer", "name": ceo_name, "source": "japan_corporate"}
            )
            network["relationships"].append(
                {
                    "from": japan_data.get("company_name"),
                    "to": ceo_name,
                    "type": "ceo_of",
                }
            )

    # 名前のバリエーションを考慮
    if name_variants:
        network["analysis"]["name_variants"] = name_variants

    return network


def generate_report(company_name, edgar_data, sugartrail_data, japan_data, network, output_file):
    """
    分析レポートを生成
    """
    report = {
        "company_name": company_name,
        "analysis_date": datetime.now().isoformat(),
        "data_sources": {
            "edgar": edgar_data is not None,
            "sugartrail": sugartrail_data is not None,
            "japan_corporate": japan_data is not None,
        },
        "edgar_data": edgar_data,
        "sugartrail_data": sugartrail_data,
        "japan_data": japan_data,
        "network_analysis": network,
        "summary": {
            "total_entities": len(network.get("entities", [])),
            "total_relationships": len(network.get("relationships", [])),
        },
    }

    # JSONファイルに保存
    output_path = Path(output_file)
    with output_path.open("w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)

    print(f"\n[結果] レポートを保存: {output_file}")

    return report


def main():
    parser = argparse.ArgumentParser(description="統合分析を実行")
    parser.add_argument("--company", required=True, help="分析する企業名")
    parser.add_argument(
        "--country",
        default="US",
        choices=["US", "UK", "JP"],
        help="企業の所在国(US, UK, JP)",
    )
    parser.add_argument("--officer", help="分析する役員名(オプション)")
    parser.add_argument("--website", help="企業のウェブサイトURL(オプション、JPの場合に有効)")

    args = parser.parse_args()

    # ディレクトリのセットアップ
    setup_directories()

    print("=" * 60)
    print("企業・金融の透明性分析 - 統合分析")
    print("=" * 60)
    print(f"企業名: {args.company}")
    print(f"所在国: {args.country}")
    if args.officer:
        print(f"役員名: {args.officer}")
    print("=" * 60)

    print("\n[ステップ1] 名前のバリエーションを検索")
    company_variants = get_name_variants(args.company)
    officer_variants = []
    if args.officer:
        officer_variants = get_name_variants(args.officer)

    # ステップ2: EDGARデータを取得(米国企業の場合)
    print("\n[ステップ2] SECデータを取得")
    edgar_data = None
    if args.country == "US":
        for variant in company_variants:
            try:
                edgar_data = fetch_edgar_data(variant, args.country)
                if edgar_data:
                    break
            except Exception as e:
                print(f"  → エラー: {variant} のデータ取得に失敗 - {e}")

    # ステップ3: sugartrailデータを取得(英国企業の場合)
    print("\n[ステップ3] Companies Houseデータを取得")
    sugartrail_data = None
    if args.country == "UK":
        for variant in company_variants:
            try:
                sugartrail_data = fetch_sugartrail_data(variant, args.country)
                if sugartrail_data:
                    break
            except Exception as e:
                print(f"  → エラー: {variant} のデータ取得に失敗 - {e}")

    # ステップ3.5: 日本の企業データを取得(日本企業の場合)
    japan_data = None
    if args.country == "JP":
        print("\n[ステップ3.5] 日本の企業情報を取得")
        try:
            japan_data = fetch_japan_corporate_data(args.company, args.website)
        except Exception as e:
            print(f"  → エラー: 日本の企業データ取得に失敗 - {e}")

    all_variants = company_variants + officer_variants
    network = analyze_network(edgar_data, sugartrail_data, japan_data, all_variants)

    output_file = (
        project_root
        / "data"
        / "output"
        / f"{args.company}_integrated_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
    )
    report = generate_report(
        args.company, edgar_data, sugartrail_data, japan_data, network, output_file
    )

    # 結果の表示
    print("\n" + "=" * 60)
    print("分析結果サマリー")
    print("=" * 60)
    print(f"企業名: {args.company}")
    print(f"見つかったエンティティ数: {report['summary']['total_entities']}")
    print(f"見つかった関係数: {report['summary']['total_relationships']}")
    print(f"EDGARデータ: {'取得済み' if edgar_data else '未取得'}")
    print(f"sugartrailデータ: {'取得済み' if sugartrail_data else '未取得'}")
    print(f"日本の企業データ: {'取得済み' if japan_data else '未取得'}")
    if japan_data and isinstance(japan_data, dict):
        financial_data = japan_data.get("financial_data")
        if financial_data and isinstance(financial_data, dict) and financial_data.get("net_income"):
            print(f"純利益: {financial_data['net_income']:,}円")
    print("=" * 60)


if __name__ == "__main__":
    main()
