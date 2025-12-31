import { NextRequest, NextResponse } from "next/server";
import { exec } from "child_process";
import { promisify } from "util";
import path from "path";

const execAsync = promisify(exec);

export async function POST(request: NextRequest) {
  try {
    const body = await request.json();
    const { company, country, website, officer } = body;

    if (!company || !country) {
      return NextResponse.json(
        { error: "企業名と国は必須です" },
        { status: 400 }
      );
    }

    // プロジェクトルートのパスを取得
    const projectRoot = path.join(process.cwd(), "..");

    // 統合分析スクリプトを実行
    let command = `cd "${projectRoot}" && uv run python scripts/integrated_analysis.py --company "${company}" --country ${country}`;

    if (website) {
      command += ` --website "${website}"`;
    }

    if (officer) {
      command += ` --officer "${officer}"`;
    }

    const { stdout, stderr } = await execAsync(command, {
      maxBuffer: 10 * 1024 * 1024, // 10MB
      timeout: 300000, // 5分
    });

    // 出力からJSONファイルのパスを抽出
    const outputMatch = stdout.match(/data\/output\/([^\s]+\.json)/);

    if (outputMatch) {
      const fs = await import("fs/promises");
      const jsonPath = path.join(projectRoot, "data", "output", outputMatch[1]);
      const jsonContent = await fs.readFile(jsonPath, "utf-8");
      const analysisResult = JSON.parse(jsonContent);

      return NextResponse.json({
        success: true,
        data: analysisResult,
        output: stdout,
      });
    }

    // JSONファイルが見つからない場合でも、stdoutを返す
    return NextResponse.json({
      success: true,
      data: null,
      output: stdout,
      error: stderr,
    });
  } catch (error: unknown) {
    console.error("分析エラー:", error);
    const errorMessage =
      error instanceof Error ? error.message : "分析中にエラーが発生しました";
    const errorDetails =
      error instanceof Error && "stderr" in error
        ? (error as { stderr?: string; stdout?: string }).stderr
        : undefined;

    return NextResponse.json(
      {
        success: false,
        error: errorMessage,
        details: errorDetails,
      },
      { status: 500 }
    );
  }
}
