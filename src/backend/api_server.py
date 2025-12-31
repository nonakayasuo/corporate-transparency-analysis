#!/usr/bin/env python3
"""
FastAPIサーバー

企業・金融の透明性分析APIを提供します。
"""

import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(project_root))

# 統合分析モジュールをインポート
from src.backend.integrated_analysis import (  # noqa: E402
    setup_directories,
    get_name_variants,
    fetch_edgar_data,
    fetch_sugartrail_data,
    fetch_japan_corporate_data,
    analyze_network,
    generate_report,
)

# 政治献金モジュールをインポート
try:
    from src.backend.political_contributions_integration import (
        search_political_contributions,
    )  # noqa: E402
except ImportError:
    search_political_contributions = None

# その他のモジュールをインポート
from src.backend.japan_corporate_fetcher import analyze_japanese_company  # noqa: E402
from src.backend.financial_data_fetcher import get_financial_data  # noqa: E402

app = FastAPI(
    title="企業・金融の透明性分析API",
    description="EDGAR、sugartrail、name-variant-searchを統合した包括的な企業分析API",
    version="1.0.0",
)

# CORS設定
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],  # Next.jsのデフォルトポート
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# リクエストモデル
class AnalysisRequest(BaseModel):
    company: str = Field(..., description="分析する企業名", example="Apple Inc.")
    country: str = Field(
        default="US", description="企業の所在国", example="US", pattern="^(US|UK|JP)$"
    )
    website: Optional[str] = Field(None, description="企業のウェブサイトURL（JPの場合に有効）")
    officer: Optional[str] = Field(None, description="分析する役員名（オプション）")


class BasicAnalysisRequest(BaseModel):
    company: str = Field(..., description="分析する企業名", example="Apple Inc.")
    officer: Optional[str] = Field(None, description="分析する役員名（オプション）")


class JapanCompanyRequest(BaseModel):
    company: str = Field(..., description="分析する企業名", example="トヨタ自動車")
    website: Optional[str] = Field(None, description="企業のウェブサイトURL（オプション）")


class FinancialDataRequest(BaseModel):
    company: str = Field(..., description="企業名", example="BMSG")
    corporate_number: Optional[str] = Field(None, description="法人番号（オプション）")


class GeneratePDFRequest(BaseModel):
    applicant_name: str = Field(..., description="申請者名", example="山田太郎")
    applicant_organization: Optional[str] = Field(None, description="申請者組織名（オプション）")
    usage_purpose: str = Field(
        ..., description="利用目的", example="企業分析のための法人番号情報の取得"
    )
    output_path: Optional[str] = Field(None, description="出力ファイルパス（オプション）")


# レスポンスモデル
class AnalysisResponse(BaseModel):
    success: bool
    data: Optional[dict] = None
    message: Optional[str] = None
    error: Optional[str] = None


@app.get("/")
async def root():
    """APIのルートエンドポイント"""
    return {
        "message": "企業・金融の透明性分析API",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "POST - 統合企業分析を実行",
            "/basic-analysis": "POST - 基本企業分析を実行",
            "/japan-company": "POST - 日本の企業情報を取得",
            "/financial-data": "POST - 財務データを取得",
            "/generate-pdf": "POST - 利用目的書PDFを生成",
            "/health": "GET - ヘルスチェック",
            "/docs": "GET - APIドキュメント（Swagger UI）",
        },
    }


@app.get("/health")
async def health_check():
    """ヘルスチェックエンドポイント"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}


@app.post("/analyze", response_model=AnalysisResponse)
async def analyze_company(request: AnalysisRequest):
    """
    企業分析を実行

    - **company**: 分析する企業名（必須）
    - **country**: 企業の所在国（US, UK, JP）- デフォルト: US
    - **website**: 企業のウェブサイトURL（JPの場合に有効、オプション）
    - **officer**: 分析する役員名（オプション）
    """
    try:
        # ディレクトリのセットアップ
        setup_directories()

        # 名前のバリエーションを取得
        company_variants = get_name_variants(request.company)
        officer_variants = []
        if request.officer:
            officer_variants = get_name_variants(request.officer)

        # EDGARデータを取得（米国企業の場合）
        edgar_data = None
        if request.country == "US":
            for variant in company_variants:
                try:
                    edgar_data = fetch_edgar_data(variant, request.country)
                    if edgar_data:
                        break
                except Exception as e:
                    print(f"  → エラー: {variant} のデータ取得に失敗 - {e}")

        # sugartrailデータを取得（英国企業の場合）
        sugartrail_data = None
        if request.country == "UK":
            for variant in company_variants:
                try:
                    sugartrail_data = fetch_sugartrail_data(variant, request.country)
                    if sugartrail_data:
                        break
                except Exception as e:
                    print(f"  → エラー: {variant} のデータ取得に失敗 - {e}")

        # 日本の企業データを取得（日本企業の場合）
        japan_data = None
        if request.country == "JP":
            try:
                japan_data = fetch_japan_corporate_data(request.company, request.website)
            except Exception as e:
                print(f"  → エラー: 日本の企業データ取得に失敗 - {e}")

        # 政治献金データを取得
        political_data = None
        if search_political_contributions is not None:
            try:
                cik = None
                if edgar_data:
                    cik = edgar_data.get("cik")
                political_data = search_political_contributions(
                    request.company, request.country, cik
                )
            except Exception as e:
                print(f"  → エラー: 政治献金データ取得に失敗 - {e}")

        # ネットワーク分析を実行
        all_variants = company_variants + officer_variants
        network = analyze_network(
            edgar_data, sugartrail_data, japan_data, all_variants, political_data
        )

        # レポートを生成（一時ファイルとして保存）
        output_file = (
            project_root
            / "data"
            / "output"
            / f"{request.company}_integrated_analysis_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        )
        report = generate_report(
            request.company,
            edgar_data,
            sugartrail_data,
            japan_data,
            network,
            output_file,
            political_data,
        )

        return AnalysisResponse(
            success=True,
            data=report,
            message="分析が正常に完了しました",
        )

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"分析エラー: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"分析中にエラーが発生しました: {str(e)}",
        )


@app.post("/basic-analysis", response_model=AnalysisResponse)
async def basic_analysis(request: BasicAnalysisRequest):
    """
    基本企業分析を実行

    - **company**: 分析する企業名（必須）
    - **officer**: 分析する役員名（オプション）
    """
    try:
        setup_directories()

        # 名前のバリエーションを取得
        company_variants = get_name_variants(request.company)
        officer_variants = []
        if request.officer:
            officer_variants = get_name_variants(request.officer)

        # EDGARデータを取得
        edgar_data_list = []
        for variant in company_variants:
            try:
                edgar_data = fetch_edgar_data(variant, "US")
                if edgar_data:
                    edgar_data_list.append(edgar_data)
            except Exception as e:
                print(f"  → エラー: {variant} のデータ取得に失敗 - {e}")

        result = {
            "company": request.company,
            "company_variants": company_variants,
            "officer_variants": officer_variants,
            "edgar_data": edgar_data_list,
            "timestamp": datetime.now().isoformat(),
        }

        return AnalysisResponse(
            success=True,
            data=result,
            message="基本分析が正常に完了しました",
        )

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"基本分析エラー: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"基本分析中にエラーが発生しました: {str(e)}",
        )


@app.post("/japan-company", response_model=AnalysisResponse)
async def japan_company_analysis(request: JapanCompanyRequest):
    """
    日本の企業情報を取得

    - **company**: 分析する企業名（必須）
    - **website**: 企業のウェブサイトURL（オプション）
    """
    try:
        result = analyze_japanese_company(request.company, request.website)

        return AnalysisResponse(
            success=True,
            data=result,
            message="日本の企業情報取得が正常に完了しました",
        )

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"日本の企業情報取得エラー: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"日本の企業情報取得中にエラーが発生しました: {str(e)}",
        )


@app.post("/financial-data", response_model=AnalysisResponse)
async def get_financial_data_api(request: FinancialDataRequest):
    """
    財務データを取得

    - **company**: 企業名（必須）
    - **corporate_number**: 法人番号（オプション）
    """
    try:
        result = get_financial_data(request.company, request.corporate_number)

        if result:
            return AnalysisResponse(
                success=True,
                data=result,
                message="財務データ取得が正常に完了しました",
            )
        else:
            return AnalysisResponse(
                success=False,
                data=None,
                message="財務データが見つかりませんでした",
            )

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"財務データ取得エラー: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"財務データ取得中にエラーが発生しました: {str(e)}",
        )


@app.post("/generate-pdf")
async def generate_pdf_api(request: GeneratePDFRequest):
    """
    利用目的書PDFを生成

    - **applicant_name**: 申請者名（必須）
    - **applicant_organization**: 申請者組織名（オプション）
    - **usage_purpose**: 利用目的（必須）
    - **output_path**: 出力ファイルパス（オプション）
    """
    try:
        from fastapi.responses import FileResponse

        output_path = request.output_path
        if not output_path:
            output_dir = project_root / "data" / "edgar"
            output_dir.mkdir(parents=True, exist_ok=True)
            safe_name = request.applicant_name.replace(" ", "_").replace("/", "_")
            output_path = (
                output_dir
                / f"利用目的書_{safe_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
            )

        pdf_path = generate_usage_purpose_pdf(
            applicant_name=request.applicant_name,
            applicant_organization=request.applicant_organization,
            usage_purpose=request.usage_purpose,
            output_path=str(output_path),
        )

        if pdf_path and Path(pdf_path).exists():
            return FileResponse(
                pdf_path,
                media_type="application/pdf",
                filename=Path(pdf_path).name,
            )
        else:
            raise HTTPException(
                status_code=500,
                detail="PDFファイルの生成に失敗しました",
            )

    except Exception as e:
        import traceback

        error_details = traceback.format_exc()
        print(f"PDF生成エラー: {error_details}")
        raise HTTPException(
            status_code=500,
            detail=f"PDF生成中にエラーが発生しました: {str(e)}",
        )


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
