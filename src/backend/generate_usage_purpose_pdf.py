#!/usr/bin/env python3
"""
利用目的書PDF生成スクリプト

法人番号システムWeb-API申請用の利用目的書をPDF形式で生成します。
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import mm
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.cidfonts import UnicodeCIDFont
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import Paragraph, SimpleDocTemplate, Spacer
except ImportError:
    print("エラー: reportlabがインストールされていません。")
    print("以下のコマンドでインストールしてください:")
    print("  uv add reportlab")
    sys.exit(1)

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent


def register_japanese_font():
    """
    日本語フォントを登録
    reportlabのUnicodeCIDFontを使用して日本語を表示
    """
    # UnicodeCIDFontを使用（reportlabに標準で含まれる日本語フォント）
    # HeiseiKakuGo-W3: 平成角ゴシック体W3
    # HeiseiMin-W3: 平成明朝体W3
    try:
        pdfmetrics.registerFont(UnicodeCIDFont("HeiseiKakuGo-W3"))
        print("✓ 日本語フォント(HeiseiKakuGo-W3)を登録しました")
    except Exception as e1:
        print(f"警告: HeiseiKakuGo-W3の登録に失敗: {e1}")
        try:
            pdfmetrics.registerFont(UnicodeCIDFont("HeiseiMin-W3"))
            print("✓ 日本語フォント(HeiseiMin-W3)を登録しました")
        except Exception as e2:
            print(f"警告: HeiseiMin-W3の登録に失敗: {e2}")
            # 最後の手段として、システムフォントを試す
            font_paths = [
                "/System/Library/Fonts/AppleGothic.ttf",
                "/System/Library/Fonts/STHeiti Light.ttc",
            ]
            for font_path in font_paths:
                if Path(font_path).exists():
                    try:
                        if font_path.endswith(".ttc"):
                            # TTCファイルはサポートされていない可能性が高い
                            continue
                        pdfmetrics.registerFont(TTFont("JapaneseFont", font_path))
                        print(f"✓ システムフォントを使用: {font_path}")
                        return "JapaneseFont"
                    except Exception:
                        continue
            print("警告: 日本語フォントの登録に失敗しました。デフォルトフォントを使用します。")
            return "Helvetica"
        else:
            return "HeiseiMin-W3"
    else:
        return "HeiseiKakuGo-W3"


def create_usage_purpose_pdf(
    output_path: Path,
    applicant_name: str = "[申請者の氏名または名称]",
    email: str = "[メールアドレス]",
    application_date: Optional[str] = None,
):
    """
    利用目的書PDFを作成

    Args:
        output_path: 出力PDFファイルのパス
        applicant_name: 申請者名
        email: 連絡先メールアドレス
    """
    # 日本語フォントを登録
    japanese_font = register_japanese_font()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        rightMargin=20 * mm,
        leftMargin=20 * mm,
        topMargin=20 * mm,
        bottomMargin=20 * mm,
    )

    # スタイルの設定(日本語フォントを使用)
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        "CustomTitle",
        parent=styles["Heading1"],
        fontName=japanese_font,
        fontSize=16,
        textColor="black",
        spaceAfter=12,
        alignment=1,  # 中央揃え
    )
    heading_style = ParagraphStyle(
        "CustomHeading",
        parent=styles["Heading2"],
        fontName=japanese_font,
        fontSize=14,
        textColor="black",
        spaceAfter=10,
        spaceBefore=10,
    )
    subheading_style = ParagraphStyle(
        "CustomSubHeading",
        parent=styles["Heading3"],
        fontName=japanese_font,
        fontSize=12,
        textColor="black",
        spaceAfter=8,
        spaceBefore=8,
    )
    normal_style = ParagraphStyle(
        "CustomNormal",
        parent=styles["Normal"],
        fontName=japanese_font,
        fontSize=11,
        textColor="black",
        spaceAfter=6,
        leading=16,
    )

    # コンテンツの構築
    story = []

    # タイトル
    story.append(Paragraph("法人番号システムWeb-API利用目的書", title_style))
    story.append(Spacer(1, 12 * mm))

    # 申請日の設定
    if application_date:
        try:
            # YYYY/MM/DD形式を解析
            date_obj = datetime.strptime(application_date, "%Y/%m/%d")
            date_str = date_obj.strftime("%Y年%m月%d日")
        except ValueError:
            date_str = application_date
    else:
        date_str = datetime.now().strftime("%Y年%m月%d日")

    # 1. 申請者情報
    story.append(Paragraph("1. 申請者情報", heading_style))
    story.append(Paragraph(f"申請者名: {applicant_name}", normal_style))
    story.append(Paragraph(f"申請日: {date_str}", normal_style))
    story.append(Paragraph(f"連絡先メールアドレス: {email}", normal_style))
    story.append(Spacer(1, 6 * mm))

    # 2. プログラムの名称
    story.append(Paragraph("2. プログラムの名称", heading_style))
    story.append(
        Paragraph(
            "企業・金融の透明性分析ツール(Corporate Transparency Analysis Tool)", normal_style
        )
    )
    story.append(Spacer(1, 6 * mm))

    # 3. 利用目的
    story.append(Paragraph("3. 利用目的", heading_style))

    story.append(Paragraph("3.1 プログラムの概要", subheading_style))
    story.append(
        Paragraph(
            "本プログラムは、企業・金融の透明性を分析するための統合ツールです。"
            "法人番号システムWeb-APIを使用して、日本の企業情報(法人番号、商号、所在地、法人種別など)を取得し、企業分析に活用します。",
            normal_style,
        )
    )
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("3.2 法人番号システムWeb-APIの利用目的", subheading_style))
    story.append(Paragraph("(1) 企業情報の検索・取得", normal_style))
    story.append(Paragraph("・法人名による企業情報の検索", normal_style))
    story.append(Paragraph("・法人番号による企業情報の取得", normal_style))
    story.append(Paragraph("・企業の基本3情報(商号、所在地、法人番号)の取得", normal_style))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("(2) 企業分析・可視化", normal_style))
    story.append(Paragraph("・取得した企業情報を用いた企業分析", normal_style))
    story.append(Paragraph("・企業情報の可視化・レポート作成", normal_style))
    story.append(Paragraph("・企業間の関係性分析とネットワーク可視化", normal_style))
    story.append(Spacer(1, 3 * mm))

    story.append(Paragraph("(3) 研究・教育目的", normal_style))
    story.append(Paragraph("・企業情報の分析手法の研究", normal_style))
    story.append(Paragraph("・データ分析の教育・学習目的", normal_style))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("3.3 利用方法", subheading_style))
    story.append(Paragraph("コマンドライン実行:", normal_style))
    story.append(
        Paragraph(
            'uv run python scripts/japan_corporate_fetcher.py --company "企業名" --website "https://example.com"',
            normal_style,
        )
    )
    story.append(Spacer(1, 3 * mm))
    story.append(Paragraph("Web UI経由:", normal_style))
    story.append(Paragraph("1. フロントエンドアプリケーション(Next.js)を起動", normal_style))
    story.append(Paragraph("2. ブラウザから企業名、所在国、ウェブサイトURL等を入力", normal_style))
    story.append(Paragraph("3. 分析実行ボタンをクリック", normal_style))
    story.append(Paragraph("4. 取得した企業情報を表示・可視化", normal_style))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("3.4 取得するデータ項目", subheading_style))
    story.append(
        Paragraph("法人番号システムWeb-APIから以下のデータ項目を取得します:", normal_style)
    )
    story.append(Paragraph("・法人番号", normal_style))
    story.append(Paragraph("・商号又は名称", normal_style))
    story.append(Paragraph("・本店又は主たる事務所の所在地", normal_style))
    story.append(Paragraph("・法人種別", normal_style))
    story.append(
        Paragraph(
            "・その他、法人番号システムWeb-APIで提供される基本3情報および付随情報", normal_style
        )
    )
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("3.5 データの利用範囲", subheading_style))
    story.append(Paragraph("・企業分析・調査のための内部利用", normal_style))
    story.append(Paragraph("・企業情報の可視化・レポート作成", normal_style))
    story.append(Paragraph("・企業間の関係性分析", normal_style))
    story.append(Paragraph("・研究・教育目的での利用", normal_style))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("3.6 データの取り扱い", subheading_style))
    story.append(
        Paragraph(
            "・取得したデータは適切に管理し、関連する法令や規制を遵守して取り扱います", normal_style
        )
    )
    story.append(Paragraph("・個人情報の取り扱いには特に注意を払います", normal_style))
    story.append(
        Paragraph(
            "・取得元の明示を行います(「このサービスは、国税庁法人番号システムのWeb-API機能を利用して取得した情報をもとに作成しているが、サービスの内容は国税庁によって保証されたものではない」)",
            normal_style,
        )
    )
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("3.7 技術仕様", subheading_style))
    story.append(Paragraph("・開発言語: Python 3.9以上", normal_style))
    story.append(
        Paragraph("・API利用方式: REST API(法人番号システムWeb-API Ver.4.0)", normal_style)
    )
    story.append(Paragraph("・実行環境: ローカル環境またはサーバー環境", normal_style))
    story.append(Paragraph("・データ形式: JSON形式でのデータ取得", normal_style))
    story.append(Spacer(1, 4 * mm))

    story.append(Paragraph("3.8 利用頻度", subheading_style))
    story.append(Paragraph("・開発・テスト段階: 1日あたり数回〜数十回程度", normal_style))
    story.append(
        Paragraph(
            "・本番利用: 必要に応じて適度な頻度で利用(過度なリクエストは行いません)", normal_style
        )
    )
    story.append(Spacer(1, 6 * mm))

    # 4. その他
    story.append(Paragraph("4. その他", heading_style))
    story.append(
        Paragraph(
            "本プログラムは、企業情報の適切な取得・分析を目的としており、法令を遵守して利用いたします。",
            normal_style,
        )
    )
    story.append(Spacer(1, 12 * mm))

    # 申請者署名
    story.append(Paragraph("申請者署名", subheading_style))
    story.append(Spacer(1, 8 * mm))
    story.append(Paragraph(applicant_name, normal_style))
    story.append(Paragraph(date_str, normal_style))

    # PDFの生成
    doc.build(story)
    print(f"✓ 利用目的書PDFを作成しました: {output_path}")


def main():
    parser = argparse.ArgumentParser(description="利用目的書PDFを生成")
    parser.add_argument("--applicant-name", default="[申請者の氏名または名称]", help="申請者名")
    parser.add_argument("--email", default="[メールアドレス]", help="連絡先メールアドレス")
    parser.add_argument(
        "--output", default=None, help="出力PDFファイルのパス(デフォルト: docs/利用目的書.pdf)"
    )
    parser.add_argument(
        "--application-date", default=None, help="申請日(YYYY/MM/DD形式、例: 2025/12/31)"
    )

    args = parser.parse_args()

    output_path = Path(args.output) if args.output else project_root / "docs" / "利用目的書.pdf"

    # 出力ディレクトリを作成
    output_path.parent.mkdir(parents=True, exist_ok=True)

    create_usage_purpose_pdf(
        output_path,
        applicant_name=args.applicant_name,
        email=args.email,
        application_date=args.application_date,
    )


if __name__ == "__main__":
    main()
