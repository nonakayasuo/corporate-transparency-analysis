#!/usr/bin/env python3
"""
ソース情報生成モジュール

分析結果にソース参照先の情報を追加します。
"""

from datetime import datetime
from typing import Optional, Dict, List, Any


def generate_edgar_source_info(edgar_data: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    EDGARデータからソース情報を生成

    Args:
        edgar_data: EDGARデータの辞書

    Returns:
        ソース情報のリスト
    """
    sources = []

    if not edgar_data:
        return sources

    company_name = edgar_data.get("company_name", "")
    cik = edgar_data.get("cik", "")

    # EDGARの企業ページ
    if cik and company_name:
        sources.append(
            {
                "name": "EDGAR - 企業情報",
                "url": f"https://www.sec.gov/cgi-bin/browse-edgar?CIK={cik}&owner=exclude&action=getcompany",
                "description": f"{company_name}のSEC提出書類一覧",
                "type": "database",
                "timestamp": edgar_data.get("timestamp"),
            }
        )

    # EDGARの検索ページ
    if company_name:
        sources.append(
            {
                "name": "EDGAR - 検索",
                "url": f"https://www.sec.gov/cgi-bin/browse-edgar?company={company_name.replace(' ', '+')}&owner=exclude&action=getcompany",
                "description": "EDGARデータベースでの企業検索",
                "type": "database",
            }
        )

    # 個別の書類へのリンク
    filings = edgar_data.get("filings", [])
    if filings:
        # 最新の書類へのリンクを追加
        latest_filing = filings[0] if filings else None
        if latest_filing and "accession_number" in latest_filing:
            accession = latest_filing["accession_number"]
            cik_str = cik.lstrip("0") if cik else ""
            if accession and cik_str:
                sources.append(
                    {
                        "name": "EDGAR - 最新書類",
                        "url": f"https://www.sec.gov/cgi-bin/viewer?action=view&cik={cik_str}&accession_number={accession}",
                        "description": f"最新の提出書類: {latest_filing.get('form_name', 'Unknown')}",
                        "type": "document",
                        "timestamp": latest_filing.get("filed_at"),
                    }
                )

    return sources


def generate_sugartrail_source_info(
    sugartrail_data: Optional[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """
    sugartrailデータからソース情報を生成

    Args:
        sugartrail_data: sugartrailデータの辞書

    Returns:
        ソース情報のリスト
    """
    sources = []

    if not sugartrail_data:
        return sources

    company_name = sugartrail_data.get("company_name", "")
    company_id = sugartrail_data.get("companies_house_id", "")

    # Companies Houseの企業ページ
    if company_id:
        sources.append(
            {
                "name": "Companies House - 企業情報",
                "url": f"https://find-and-update.company-information.service.gov.uk/company/{company_id}",
                "description": f"{company_name}のCompanies House企業情報",
                "type": "database",
                "timestamp": sugartrail_data.get("timestamp"),
            }
        )

    # Companies Houseの検索ページ
    if company_name:
        sources.append(
            {
                "name": "Companies House - 検索",
                "url": f"https://find-and-update.company-information.service.gov.uk/search?q={company_name.replace(' ', '+')}",
                "description": "Companies Houseでの企業検索",
                "type": "database",
            }
        )

    return sources


def generate_japan_source_info(japan_data: Optional[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    日本の企業データからソース情報を生成

    Args:
        japan_data: 日本の企業データの辞書

    Returns:
        ソース情報のリスト
    """
    sources = []

    if not japan_data:
        return sources

    company_name = japan_data.get("company_name", "")
    corporate_number = japan_data.get("corporate_number", "")

    # 法人番号システム
    if corporate_number:
        sources.append(
            {
                "name": "法人番号システム",
                "url": f"https://www.houjin-bangou.nta.go.jp/henkorireki-johoto.html?selHouzinNo={corporate_number}",
                "description": f"{company_name}の法人番号情報",
                "type": "database",
                "timestamp": japan_data.get("timestamp"),
            }
        )

    # 法人番号システムの検索ページ
    if company_name:
        sources.append(
            {
                "name": "法人番号システム - 検索",
                "url": "https://www.houjin-bangou.nta.go.jp/henkorireki-johoto.html",
                "description": "法人番号システムでの企業検索",
                "type": "database",
            }
        )

    # 企業ウェブサイト
    website_info = japan_data.get("website_info", {})
    website_url = website_info.get("website_url")
    if website_url:
        sources.append(
            {
                "name": "企業ウェブサイト",
                "url": website_url,
                "description": f"{company_name}の公式ウェブサイト",
                "type": "website",
                "timestamp": website_info.get("timestamp"),
            }
        )

    return sources


def generate_fec_source_info(
    political_data: Optional[Dict[str, Any]], company_name: str
) -> List[Dict[str, Any]]:
    """
    FECデータからソース情報を生成

    Args:
        political_data: 政治献金データの辞書
        company_name: 企業名

    Returns:
        ソース情報のリスト
    """
    sources = []

    if not political_data or political_data.get("source") != "FEC":
        return sources

    # FEC APIの検索ページ
    sources.append(
        {
            "name": "FEC API",
            "url": "https://api.open.fec.gov/developers/",
            "description": "米国連邦選挙委員会（FEC）のAPI",
            "type": "api",
            "timestamp": political_data.get("timestamp"),
        }
    )

    # FECの検索ページ
    if company_name:
        sources.append(
            {
                "name": "FEC - 企業検索",
                "url": f"https://www.fec.gov/data/receipts/individual-contributions/?contributor_name={company_name.replace(' ', '+')}",
                "description": f"{company_name}の政治献金データ",
                "type": "database",
            }
        )

    return sources


def generate_all_source_info(
    edgar_data: Optional[Dict[str, Any]] = None,
    sugartrail_data: Optional[Dict[str, Any]] = None,
    japan_data: Optional[Dict[str, Any]] = None,
    political_data: Optional[Dict[str, Any]] = None,
    company_name: str = "",
) -> List[Dict[str, Any]]:
    """
    すべてのデータソースからソース情報を生成

    Args:
        edgar_data: EDGARデータ
        sugartrail_data: sugartrailデータ
        japan_data: 日本の企業データ
        political_data: 政治献金データ
        company_name: 企業名

    Returns:
        ソース情報のリスト
    """
    sources = []

    # EDGARソース情報
    sources.extend(generate_edgar_source_info(edgar_data))

    # sugartrailソース情報
    sources.extend(generate_sugartrail_source_info(sugartrail_data))

    # 日本の企業ソース情報
    sources.extend(generate_japan_source_info(japan_data))

    # FECソース情報
    sources.extend(generate_fec_source_info(political_data, company_name))

    return sources
