"use client";

import { Building2, Link2, Loader2, TrendingUp, Users } from "lucide-react";
import { useState } from "react";
import { EdgarTimeline } from "@/components/EdgarTimeline";
import { EntityTypeChart } from "@/components/EntityTypeChart";
import { NetworkGraph } from "@/components/NetworkGraph";
import { PoliticalContributionsChart } from "@/components/PoliticalContributionsChart";
import { SourceReferences } from "@/components/SourceReferences";
import { Button } from "@/components/ui/button";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

interface AnalysisResult {
  company_name: string;
  analysis_date: string;
  data_sources: {
    edgar: boolean;
    sugartrail: boolean;
    japan_corporate: boolean;
  };
  edgar_data: {
    filings?: Array<{
      form_name: string;
      filed_at: string;
      root_form?: string;
      [key: string]: unknown;
    }>;
    [key: string]: unknown;
  } | null;
  sugartrail_data: unknown;
  japan_data: {
    financial_data?: {
      net_income?: number;
    };
    [key: string]: unknown;
  } | null;
  political_contributions_data?: {
    total_contributions?: number;
    total_amount?: number;
    recipients?: Record<string, { count: number; amount: number }>;
    contributions?: unknown[];
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
  source_references?: Array<{
    name: string;
    url?: string;
    description?: string;
    type: "api" | "website" | "document" | "database";
    timestamp?: string;
  }>;
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
      <div className="container mx-auto px-4 py-8 max-w-7xl">
        <div className="mb-8">
          <h1 className="text-4xl font-bold text-slate-900 dark:text-slate-50 mb-2">
            企業・金融の透明性分析
          </h1>
          <p className="text-slate-600 dark:text-slate-400">
            EDGAR、sugartrail、name-variant-searchを統合した包括的な企業分析ツール
          </p>
        </div>

        <div className="grid gap-6 lg:grid-cols-3">
          {/* 入力フォーム */}
          <Card className="lg:col-span-1">
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
                  <label htmlFor="website" className="text-sm font-medium">
                    ウェブサイトURL（オプション）
                  </label>
                  <Input
                    id="website"
                    placeholder="例: https://example.com"
                    value={website}
                    onChange={(e) => setWebsite(e.target.value)}
                    disabled={loading}
                  />
                </div>
              )}

              <div className="space-y-2">
                <label htmlFor="officer" className="text-sm font-medium">
                  役員名（オプション）
                </label>
                <Input
                  id="officer"
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
          <div className="lg:col-span-2 space-y-6">
            {result ? (
              <>
                {/* サマリーカード */}
                <Card>
                  <CardHeader>
                    <CardTitle>分析結果サマリー</CardTitle>
                    <CardDescription>
                      {result.company_name} の分析結果
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                      <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
                        <div className="flex items-center gap-2 mb-2">
                          <Building2 className="h-4 w-4 text-blue-600 dark:text-blue-400" />
                          <p className="text-xs font-medium text-blue-600 dark:text-blue-400">
                            エンティティ
                          </p>
                        </div>
                        <p className="text-3xl font-bold text-blue-900 dark:text-blue-100">
                          {result.summary.total_entities}
                        </p>
                      </div>
                      <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
                        <div className="flex items-center gap-2 mb-2">
                          <Link2 className="h-4 w-4 text-green-600 dark:text-green-400" />
                          <p className="text-xs font-medium text-green-600 dark:text-green-400">
                            関係
                          </p>
                        </div>
                        <p className="text-3xl font-bold text-green-900 dark:text-green-100">
                          {result.summary.total_relationships}
                        </p>
                      </div>
                      <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
                        <div className="flex items-center gap-2 mb-2">
                          <Users className="h-4 w-4 text-purple-600 dark:text-purple-400" />
                          <p className="text-xs font-medium text-purple-600 dark:text-purple-400">
                            データソース
                          </p>
                        </div>
                        <div className="flex gap-1 flex-wrap">
                          {result.data_sources.edgar && (
                            <span className="px-2 py-0.5 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs">
                              EDGAR
                            </span>
                          )}
                          {result.data_sources.sugartrail && (
                            <span className="px-2 py-0.5 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs">
                              sugartrail
                            </span>
                          )}
                          {result.data_sources.japan_corporate && (
                            <span className="px-2 py-0.5 bg-purple-100 dark:bg-purple-900 text-purple-800 dark:text-purple-200 rounded text-xs">
                              日本
                            </span>
                          )}
                        </div>
                      </div>
                      <div className="p-4 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700">
                        <div className="flex items-center gap-2 mb-2">
                          <TrendingUp className="h-4 w-4 text-slate-600 dark:text-slate-400" />
                          <p className="text-xs font-medium text-slate-600 dark:text-slate-400">
                            分析日時
                          </p>
                        </div>
                        <p className="text-sm font-medium text-slate-900 dark:text-slate-100">
                          {new Date(result.analysis_date).toLocaleDateString(
                            "ja-JP"
                          )}
                        </p>
                        <p className="text-xs text-slate-500 dark:text-slate-400">
                          {new Date(result.analysis_date).toLocaleTimeString(
                            "ja-JP"
                          )}
                        </p>
                      </div>
                    </div>

                    {result.japan_data?.financial_data?.net_income && (
                      <div className="mt-4 p-4 bg-amber-50 dark:bg-amber-900/20 rounded-lg border border-amber-200 dark:border-amber-800">
                        <h3 className="font-semibold text-amber-900 dark:text-amber-100 mb-1">
                          純利益
                        </h3>
                        <p className="text-2xl font-bold text-amber-900 dark:text-amber-100">
                          {result.japan_data.financial_data.net_income.toLocaleString(
                            "ja-JP"
                          )}
                          円
                        </p>
                      </div>
                    )}
                  </CardContent>
                </Card>

                {/* ネットワークグラフ */}
                <NetworkGraph
                  entities={result.network_analysis.entities}
                  relationships={result.network_analysis.relationships}
                />

                {/* EDGARタイムライン */}
                {result.edgar_data?.filings &&
                  result.edgar_data.filings.length > 0 && (
                    <EdgarTimeline filings={result.edgar_data.filings} />
                  )}

                {/* エンティティタイプチャート */}
                <EntityTypeChart
                  entities={result.network_analysis.entities}
                  relationships={result.network_analysis.relationships}
                />

                {/* 政治献金チャート */}
                {result.political_contributions_data && (
                  <PoliticalContributionsChart
                    data={result.political_contributions_data}
                  />
                )}

                {/* ソース参照先 */}
                {result.source_references &&
                  result.source_references.length > 0 && (
                    <SourceReferences sources={result.source_references} />
                  )}

                {/* 詳細データタブ */}
                <Card>
                  <CardHeader>
                    <CardTitle>詳細データ</CardTitle>
                    <CardDescription>
                      分析結果の詳細情報を確認できます
                    </CardDescription>
                  </CardHeader>
                  <CardContent>
                    <Tabs defaultValue="entities" className="w-full">
                      <TabsList className="grid w-full grid-cols-3">
                        <TabsTrigger value="entities">
                          エンティティ (
                          {result.network_analysis.entities.length})
                        </TabsTrigger>
                        <TabsTrigger value="relationships">
                          関係 ({result.network_analysis.relationships.length})
                        </TabsTrigger>
                        <TabsTrigger value="raw">JSON</TabsTrigger>
                      </TabsList>

                      <TabsContent value="entities" className="space-y-2 mt-4">
                        <div className="max-h-96 overflow-y-auto space-y-2">
                          {result.network_analysis.entities.map((entity) => (
                            <div
                              key={`${entity.name}-${entity.type}-${entity.source}`}
                              className="p-3 bg-slate-100 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700"
                            >
                              <div className="flex items-center justify-between">
                                <span className="font-medium text-slate-900 dark:text-slate-100">
                                  {entity.name}
                                </span>
                                <div className="flex gap-2">
                                  <span className="px-2 py-1 bg-blue-100 dark:bg-blue-900 text-blue-800 dark:text-blue-200 rounded text-xs">
                                    {entity.type}
                                  </span>
                                  <span className="px-2 py-1 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded text-xs">
                                    {entity.source}
                                  </span>
                                </div>
                              </div>
                            </div>
                          ))}
                        </div>
                      </TabsContent>

                      <TabsContent
                        value="relationships"
                        className="space-y-2 mt-4"
                      >
                        <div className="max-h-96 overflow-y-auto space-y-2">
                          {result.network_analysis.relationships.map(
                            (rel, idx) => (
                              <div
                                key={`${rel.from}-${rel.to}-${rel.type}-${idx}`}
                                className="p-3 bg-slate-100 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700"
                              >
                                <div className="flex items-center gap-2">
                                  <span className="font-medium text-slate-900 dark:text-slate-100">
                                    {rel.from}
                                  </span>
                                  <span className="text-slate-500">→</span>
                                  <span className="font-medium text-slate-900 dark:text-slate-100">
                                    {rel.to}
                                  </span>
                                  <span className="ml-auto px-2 py-1 bg-green-100 dark:bg-green-900 text-green-800 dark:text-green-200 rounded text-xs">
                                    {rel.type}
                                  </span>
                                </div>
                              </div>
                            )
                          )}
                        </div>
                      </TabsContent>

                      <TabsContent value="raw" className="mt-4">
                        <div className="max-h-96 overflow-y-auto">
                          <pre className="text-xs bg-slate-100 dark:bg-slate-800 p-4 rounded-lg overflow-x-auto border border-slate-200 dark:border-slate-700">
                            {JSON.stringify(result, null, 2)}
                          </pre>
                        </div>
                      </TabsContent>
                    </Tabs>
                  </CardContent>
                </Card>
              </>
            ) : (
              <Card>
                <CardHeader>
                  <CardTitle>分析結果</CardTitle>
                  <CardDescription>
                    分析結果がここに表示されます
                  </CardDescription>
                </CardHeader>
                <CardContent>
                  <div className="text-center py-12 text-slate-500 dark:text-slate-400">
                    <Building2 className="h-12 w-12 mx-auto mb-4 opacity-50" />
                    <p>分析を実行すると、結果がここに表示されます</p>
                  </div>
                </CardContent>
              </Card>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
