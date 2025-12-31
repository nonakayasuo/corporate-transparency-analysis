"use client";

import { DollarSign } from "lucide-react";
import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Legend,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface PoliticalContributionsData {
  total_contributions?: number;
  total_amount?: number;
  recipients?: Record<string, { count: number; amount: number }>;
  contributions?: unknown[];
}

interface PoliticalContributionsChartProps {
  data: PoliticalContributionsData | null | undefined;
}

const _COLORS = ["#3b82f6", "#10b981", "#8b5cf6", "#f59e0b", "#ef4444"];

export function PoliticalContributionsChart({ data }: PoliticalContributionsChartProps) {
  const chartData = useMemo(() => {
    if (!data || !data.recipients) {
      return [];
    }

    return Object.entries(data.recipients)
      .map(([name, info]) => ({
        name: name.length > 30 ? `${name.substring(0, 30)}...` : name,
        fullName: name,
        count: info.count,
        amount: info.amount,
      }))
      .sort((a, b) => b.amount - a.amount)
      .slice(0, 10); // 上位10件
  }, [data]);

  if (!data || !data.recipients || Object.keys(data.recipients).length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>政治献金データ</CardTitle>
        <CardDescription>企業から政治家への献金情報</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="grid gap-6 md:grid-cols-3 mb-6">
          <div className="p-4 bg-blue-50 dark:bg-blue-900/20 rounded-lg border border-blue-200 dark:border-blue-800">
            <div className="flex items-center gap-2 mb-2">
              <DollarSign className="h-4 w-4 text-blue-600 dark:text-blue-400" />
              <p className="text-xs font-medium text-blue-600 dark:text-blue-400">総額</p>
            </div>
            <p className="text-2xl font-bold text-blue-900 dark:text-blue-100">
              $
              {data.total_amount?.toLocaleString("en-US", {
                minimumFractionDigits: 2,
                maximumFractionDigits: 2,
              }) || "0.00"}
            </p>
          </div>
          <div className="p-4 bg-green-50 dark:bg-green-900/20 rounded-lg border border-green-200 dark:border-green-800">
            <div className="flex items-center gap-2 mb-2">
              <p className="text-xs font-medium text-green-600 dark:text-green-400">寄付件数</p>
            </div>
            <p className="text-2xl font-bold text-green-900 dark:text-green-100">
              {data.total_contributions || 0}
            </p>
          </div>
          <div className="p-4 bg-purple-50 dark:bg-purple-900/20 rounded-lg border border-purple-200 dark:border-purple-800">
            <div className="flex items-center gap-2 mb-2">
              <p className="text-xs font-medium text-purple-600 dark:text-purple-400">受取人数</p>
            </div>
            <p className="text-2xl font-bold text-purple-900 dark:text-purple-100">
              {Object.keys(data.recipients || {}).length}
            </p>
          </div>
        </div>

        {chartData.length > 0 && (
          <div className="mt-6">
            <h3 className="text-sm font-semibold mb-4">受取人別献金額（上位10件）</h3>
            <ResponsiveContainer width="100%" height={400}>
              <BarChart data={chartData} layout="vertical">
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis type="number" />
                <YAxis dataKey="name" type="category" width={200} />
                <Tooltip
                  formatter={(value: number, name: string) => {
                    if (name === "amount") {
                      return [
                        `$${value.toLocaleString("en-US", {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        })}`,
                        "金額",
                      ];
                    }
                    return [value, "件数"];
                  }}
                />
                <Legend />
                <Bar dataKey="amount" fill="#3b82f6" name="金額 ($)" />
                <Bar dataKey="count" fill="#10b981" name="件数" />
              </BarChart>
            </ResponsiveContainer>
          </div>
        )}
      </CardContent>
    </Card>
  );
}
