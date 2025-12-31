"use client";

import { useState } from "react";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { Loader2 } from "lucide-react";

interface AnalysisResult {
  company_name: string;
  analysis_date: string;
  data_sources: {
    edgar: boolean;
    sugartrail: boolean;
    japan_corporate: boolean;
  };
  edgar_data: unknown;
  sugartrail_data: unknown;
  japan_data: {
    financial_data?: {
      net_income?: number;
    };
    [key: string]: unknown;
  } | null;
  network_analysis: {
    entities: Array<{ type: string; name: string; source: string }>;
    relationships: Array<{ from: string; to: string; type: string }>;
    analysis: Record<string, unknown>;
  };
  summary: {
    total_entities: number;
    total_relationships: number;
  };
}

export default function Home() {
  const [company, setCompany] = useState("");
  const [country, setCountry] = useState<"US" | "UK" | "JP">("US");
  const [website, setWebsite] = useState("");
  const [officer, setOfficer] = useState("");
  const [loading, setLoading] = useState(false);
  const [result, setResult] = useState<AnalysisResult | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [debugOutput, setDebugOutput] = useState<string | null>(null);

  const handleAnalyze = async () => {
    if (!company.trim()) {
      setError("企業名を入力してください");
      return;
    }

    setLoading(true);
    setError(null);
    setResult(null);

    try {
      const response = await fetch("/api/analyze", {
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

      const data = await response.json();

      // デバッグ出力を保存
      if (data.output) {
        setDebugOutput(data.output);
      }

      if (!response.ok || !data.success) {
        const errorMsg = data.error || "分析に失敗しました";
        const details = data.details || data.output || "";
        throw new Error(`${errorMsg}\n${details ? `\n詳細:\n${details}` : ""}`);
      }

      if (data.data) {
        setResult(data.data);
        setError(null);
      } else {
        setError("結果データが見つかりませんでした");
        if (data.output) {
          setDebugOutput(data.output);
        }
      }
    } catch (err: unknown) {
      const errorMessage =
        err instanceof Error ? err.message : "分析中にエラーが発生しました";
      setError(errorMessage);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
      <div className="container mx-auto px-4 py-8 max-w-6xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-50 mb-2">
            企業・金融の透明性分析
          </h1>
        </div>

        <div className="grid gap-6 md:grid-cols-2">
          {/* 入力フォーム */}
          <Card>
            <CardHeader>
              <CardTitle>分析パラメータ</CardTitle>
              <CardDescription>
                分析する企業の情報を入力してください
              </CardDescription>
            </CardHeader>
            <CardContent className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-medium">企業名 *</label>
                <Input
                  placeholder="例: Apple Inc."
                  value={company}
                  onChange={(e) => setCompany(e.target.value)}
                  disabled={loading}
                />
              </div>

              <div className="space-y-2">
                <label className="text-sm font-medium">所在国 *</label>
                <Select
                  value={country}
                  onValueChange={(value: "US" | "UK" | "JP") =>
                    setCountry(value)
                  }
                  disabled={loading}
                >
                  <SelectTrigger>
                    <SelectValue />
                  </SelectTrigger>
                  <SelectContent>
                    <SelectItem value="US">米国 (US)</SelectItem>
                    <SelectItem value="UK">英国 (UK)</SelectItem>
                    <SelectItem value="JP">日本 (JP)</SelectItem>
                  </SelectContent>
                </Select>
              </div>

              {country === "JP" && (
                <div className="space-y-2">
                  <label className="text-sm font-medium">
                    ウェブサイトURL（オプション）
                  </label>
                  <Input
                    placeholder="例: https://example.com"
                    value={website}
                    onChange={(e) => setWebsite(e.target.value)}
                    disabled={loading}
                  />
                </div>
              )}

              <div className="space-y-2">
                <label className="text-sm font-medium">
                  役員名（オプション）
                </label>
                <Input
                  placeholder="例: Tim Cook"
                  value={officer}
                  onChange={(e) => setOfficer(e.target.value)}
                  disabled={loading}
                />
              </div>

              <Button
                onClick={handleAnalyze}
                disabled={loading || !company.trim()}
                className="w-full"
              >
                {loading ? (
                  <>
                    <Loader2 className="mr-2 h-4 w-4 animate-spin" />
                    分析中...
                  </>
                ) : (
                  "分析を実行"
                )}
              </Button>

              {error && (
                <div className="p-3 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-md">
                  <p className="text-sm text-red-800 dark:text-red-200 whitespace-pre-wrap">
                    {error}
                  </p>
                </div>
              )}
              {debugOutput && (
                <div className="p-3 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-md">
                  <p className="text-xs font-mono text-slate-600 dark:text-slate-400 whitespace-pre-wrap max-h-60 overflow-y-auto">
                    {debugOutput}
                  </p>
                </div>
              )}
            </CardContent>
          </Card>

          {/* 結果表示 */}
          <Card>
            <CardHeader>
              <CardTitle>分析結果</CardTitle>
              <CardDescription>
                {result ? "分析が完了しました" : "分析結果がここに表示されます"}
              </CardDescription>
            </CardHeader>
            <CardContent>
              {result ? (
                <Tabs defaultValue="summary" className="w-full">
                  <TabsList className="grid w-full grid-cols-3">
                    <TabsTrigger value="summary">サマリー</TabsTrigger>
                    <TabsTrigger value="network">ネットワーク</TabsTrigger>
                    <TabsTrigger value="raw">詳細データ</TabsTrigger>
                  </TabsList>

                  <TabsContent value="summary" className="space-y-4">
                    <div className="space-y-2">
                      <h3 className="font-semibold">企業名</h3>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        {result.company_name}
                      </p>
                    </div>

                    <div className="space-y-2">
                      <h3 className="font-semibold">分析日時</h3>
                      <p className="text-sm text-slate-600 dark:text-slate-400">
                        {new Date(result.analysis_date).toLocaleString("ja-JP")}
                      </p>
                    </div>

                    <div className="space-y-2">
                      <h3 className="font-semibold">データソース</h3>
                      <div className="flex gap-2 flex-wrap">
                        {result.data_sources.edgar && (
                          <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs">
                            EDGAR
                          </span>
                        )}
                        {result.data_sources.sugartrail && (
                          <span className="px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs">
                            sugartrail
                          </span>
                        )}
                        {result.data_sources.japan_corporate && (
                          <span className="px-2 py-1 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded text-xs">
                            日本企業情報
                          </span>
                        )}
                      </div>
                    </div>

                    <div className="grid grid-cols-2 gap-4">
                      <div className="p-3 bg-slate-100 dark:bg-slate-800 rounded">
                        <p className="text-xs text-slate-600 dark:text-slate-400">
                          エンティティ数
                        </p>
                        <p className="text-2xl font-bold">
                          {result.summary.total_entities}
                        </p>
                      </div>
                      <div className="p-3 bg-slate-100 dark:bg-slate-800 rounded">
                        <p className="text-xs text-slate-600 dark:text-slate-400">
                          関係数
                        </p>
                        <p className="text-2xl font-bold">
                          {result.summary.total_relationships}
                        </p>
                      </div>
                    </div>

                    {result.japan_data?.financial_data?.net_income && (
                      <div className="space-y-2">
                        <h3 className="font-semibold">純利益</h3>
                        <p className="text-sm text-slate-600 dark:text-slate-400">
                          {result.japan_data.financial_data.net_income.toLocaleString(
                            "ja-JP"
                          )}
                          円
                        </p>
                      </div>
                    )}
                  </TabsContent>

                  <TabsContent value="network" className="space-y-4">
                    <div className="space-y-2">
                      <h3 className="font-semibold">
                        エンティティ ({result.network_analysis.entities.length})
                      </h3>
                      <div className="max-h-60 overflow-y-auto space-y-1">
                        {result.network_analysis.entities.map((entity, idx) => (
                          <div
                            key={idx}
                            className="p-2 bg-slate-100 dark:bg-slate-800 rounded text-sm"
                          >
                            <span className="font-medium">{entity.name}</span>
                            <span className="text-xs text-slate-500 dark:text-slate-400 ml-2">
                              ({entity.type}) - {entity.source}
                            </span>
                          </div>
                        ))}
                      </div>
                    </div>

                    <div className="space-y-2">
                      <h3 className="font-semibold">
                        関係 ({result.network_analysis.relationships.length})
                      </h3>
                      <div className="max-h-60 overflow-y-auto space-y-1">
                        {result.network_analysis.relationships.map(
                          (rel, idx) => (
                            <div
                              key={idx}
                              className="p-2 bg-slate-100 dark:bg-slate-800 rounded text-sm"
                            >
                              <span className="font-medium">{rel.from}</span>
                              <span className="mx-2 text-slate-500">→</span>
                              <span className="font-medium">{rel.to}</span>
                              <span className="text-xs text-slate-500 dark:text-slate-400 ml-2">
                                ({rel.type})
                              </span>
                            </div>
                          )
                        )}
                      </div>
                    </div>
                  </TabsContent>

                  <TabsContent value="raw">
                    <div className="max-h-96 overflow-y-auto">
                      <pre className="text-xs bg-slate-100 dark:bg-slate-800 p-4 rounded overflow-x-auto">
                        {JSON.stringify(result, null, 2)}
                      </pre>
                    </div>
                  </TabsContent>
                </Tabs>
              ) : (
                <div className="text-center py-8 text-slate-500 dark:text-slate-400">
                  分析結果がありません
                </div>
              )}
            </CardContent>
          </Card>
        </div>
      </div>
    </div>
  );
}
