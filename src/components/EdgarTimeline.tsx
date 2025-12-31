"use client";

import { useMemo } from "react";
import { Bar, BarChart, CartesianGrid, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

interface Filing {
  form_name: string;
  filed_at: string;
  root_form?: string;
  [key: string]: unknown;
}

interface EdgarTimelineProps {
  filings: Filing[];
}

export function EdgarTimeline({ filings }: EdgarTimelineProps) {
  const chartData = useMemo(() => {
    // 日付別に集計
    const dateMap = new Map<string, number>();

    filings.forEach((filing) => {
      const date = filing.filed_at;
      if (date) {
        dateMap.set(date, (dateMap.get(date) || 0) + 1);
      }
    });

    // ソートしてチャートデータに変換
    return Array.from(dateMap.entries())
      .map(([date, count]) => ({
        date,
        count,
      }))
      .sort((a, b) => a.date.localeCompare(b.date));
  }, [filings]);

  const formTypeData = useMemo(() => {
    const typeMap = new Map<string, number>();

    filings.forEach((filing) => {
      const formName = filing.form_name || "Unknown";
      typeMap.set(formName, (typeMap.get(formName) || 0) + 1);
    });

    return Array.from(typeMap.entries())
      .map(([name, count]) => ({
        name,
        count,
      }))
      .sort((a, b) => b.count - a.count);
  }, [filings]);

  if (filings.length === 0) {
    return null;
  }

  return (
    <div className="grid gap-6 md:grid-cols-2">
      <Card>
        <CardHeader>
          <CardTitle>EDGAR書類のタイムライン</CardTitle>
          <CardDescription>提出日別の書類数</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="date" angle={-45} textAnchor="end" height={80} />
              <YAxis />
              <Tooltip />
              <Bar dataKey="count" fill="#3b82f6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>書類タイプ別分布</CardTitle>
          <CardDescription>提出書類の種類</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={formTypeData} layout="vertical">
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis type="number" />
              <YAxis dataKey="name" type="category" width={150} />
              <Tooltip />
              <Bar dataKey="count" fill="#10b981" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>
    </div>
  );
}
