"use client";

import { CheckCircle2, XCircle, Info, AlertCircle } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface LogEntry {
  timestamp: string;
  level: "info" | "success" | "warning" | "error";
  message: string;
  details?: string;
}

interface AnalysisLogProps {
  logs: LogEntry[];
}

const getLogIcon = (level: LogEntry["level"]) => {
  switch (level) {
    case "success":
      return (
        <CheckCircle2 className="h-4 w-4 text-green-600 dark:text-green-400" />
      );
    case "error":
      return <XCircle className="h-4 w-4 text-red-600 dark:text-red-400" />;
    case "warning":
      return (
        <AlertCircle className="h-4 w-4 text-yellow-600 dark:text-yellow-400" />
      );
    case "info":
    default:
      return <Info className="h-4 w-4 text-blue-600 dark:text-blue-400" />;
  }
};

const getLogColor = (level: LogEntry["level"]) => {
  switch (level) {
    case "success":
      return "border-green-200 dark:border-green-800 bg-green-50 dark:bg-green-900/20";
    case "error":
      return "border-red-200 dark:border-red-800 bg-red-50 dark:bg-red-900/20";
    case "warning":
      return "border-yellow-200 dark:border-yellow-800 bg-yellow-50 dark:bg-yellow-900/20";
    case "info":
    default:
      return "border-blue-200 dark:border-blue-800 bg-blue-50 dark:bg-blue-900/20";
  }
};

export function AnalysisLog({ logs }: AnalysisLogProps) {
  if (logs.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>分析プロセスログ</CardTitle>
        <CardDescription>分析の各ステップの実行状況を表示</CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-2 max-h-96 overflow-y-auto">
          {logs.map((log, index) => (
            <div
              key={index}
              className={`flex items-start gap-3 p-3 rounded-lg border ${getLogColor(
                log.level
              )}`}
            >
              <div className="mt-0.5 shrink-0">{getLogIcon(log.level)}</div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2 mb-1">
                  <span className="text-sm font-medium text-slate-900 dark:text-slate-100">
                    {log.message}
                  </span>
                  <span className="text-xs text-slate-500 dark:text-slate-400">
                    {new Date(log.timestamp).toLocaleTimeString("ja-JP")}
                  </span>
                </div>
                {log.details && (
                  <p className="text-xs text-slate-600 dark:text-slate-400 whitespace-pre-wrap">
                    {log.details}
                  </p>
                )}
              </div>
            </div>
          ))}
        </div>
      </CardContent>
    </Card>
  );
}
