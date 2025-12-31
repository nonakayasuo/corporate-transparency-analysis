import { NextRequest, NextResponse } from "next/server";

// FastAPIサーバーのURL（環境変数から取得、デフォルトはlocalhost:8000）
const FASTAPI_URL = process.env.FASTAPI_URL || "http://localhost:8000";

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { company, country, website, officer } = body;

    if (!company || !country) {
      return NextResponse.json({ error: "企業名と国は必須です" }, { status: 400 });
    }

    // FastAPIサーバーにリクエストを送信
    let response: Response;
    try {
      response = await fetch(`${FASTAPI_URL}/analyze`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify({
          company,
          country,
          website: website || undefined,
          officer: officer || undefined,
        }),
      });
    } catch (fetchError) {
      console.error("FastAPIサーバーへの接続エラー:", fetchError);
      return NextResponse.json(
        {
          success: false,
          error: "FastAPIサーバーに接続できません。サーバーが起動しているか確認してください。",
          details: `接続先: ${FASTAPI_URL}`,
          fetchError: fetchError instanceof Error ? fetchError.message : String(fetchError),
        },
        { status: 503 }
      );
    }

    // レスポンスが404の場合
    if (response.status === 404) {
      return NextResponse.json(
        {
          success: false,
          error: "FastAPIサーバーのエンドポイントが見つかりません。",
          details: `エンドポイント: ${FASTAPI_URL}/analyze`,
          hint: "FastAPIサーバーが正しく起動しているか、エンドポイントが正しいか確認してください。",
        },
        { status: 503 }
      );
    }

    let data;
    try {
      data = await response.json();
    } catch (jsonError) {
      const text = await response.text();
      console.error("JSON解析エラー:", jsonError, "レスポンス:", text);
      return NextResponse.json(
        {
          success: false,
          error: "FastAPIサーバーからのレスポンスの解析に失敗しました。",
          details: text.substring(0, 500),
        },
        { status: 500 }
      );
    }

    if (!response.ok) {
      return NextResponse.json(
        {
          success: false,
          error: data.detail || "分析中にエラーが発生しました",
        },
        { status: response.status }
      );
    }

    return NextResponse.json({
      success: data.success,
      data: data.data,
      message: data.message,
    });
  } catch (error: unknown) {
    console.error("分析エラー:", error);
    const errorMessage = error instanceof Error ? error.message : "分析中にエラーが発生しました";

    // FastAPIサーバーに接続できない場合
    if (error instanceof TypeError && error.message.includes("fetch")) {
      return NextResponse.json(
        {
          success: false,
          error: "FastAPIサーバーに接続できません。サーバーが起動しているか確認してください。",
          details: `接続先: ${FASTAPI_URL}`,
        },
        { status: 503 }
      );
    }

    return NextResponse.json(
      {
        success: false,
        error: errorMessage,
      },
      { status: 500 }
    );
  }
}
