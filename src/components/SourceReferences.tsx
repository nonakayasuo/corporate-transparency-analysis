"use client";

import { ExternalLink, Database, Globe, FileText } from "lucide-react";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

interface SourceReference {
  name: string;
  url?: string;
  description?: string;
  type: "api" | "website" | "document" | "database";
  timestamp?: string;
}

interface SourceReferencesProps {
  sources: SourceReference[];
}

const getSourceIcon = (type: SourceReference["type"]) => {
  switch (type) {
    case "api":
      return <Database className="h-4 w-4" />;
    case "website":
      return <Globe className="h-4 w-4" />;
    case "document":
      return <FileText className="h-4 w-4" />;
    case "database":
      return <Database className="h-4 w-4" />;
    default:
      return <Globe className="h-4 w-4" />;
  }
};

const getSourceColor = (type: SourceReference["type"]) => {
  switch (type) {
    case "api":
      return "text-blue-600 dark:text-blue-400";
    case "website":
      return "text-green-600 dark:text-green-400";
    case "document":
      return "text-purple-600 dark:text-purple-400";
    case "database":
      return "text-orange-600 dark:text-orange-400";
    default:
      return "text-slate-600 dark:text-slate-400";
  }
};

export function SourceReferences({ sources }: SourceReferencesProps) {
  if (sources.length === 0) {
    return null;
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>データソース参照先</CardTitle>
        <CardDescription>
          この分析で使用されたデータソースへのリンク
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="space-y-3">
          {sources.map((source, index) => (
            <div
              key={index}
              className="flex items-start gap-3 p-3 bg-slate-50 dark:bg-slate-800 rounded-lg border border-slate-200 dark:border-slate-700 hover:bg-slate-100 dark:hover:bg-slate-700 transition-colors"
            >
              <div className={`mt-0.5 ${getSourceColor(source.type)}`}>
                {getSourceIcon(source.type)}
              </div>
              <div className="flex-1 min-w-0">
                <div className="flex items-center gap-2">
                  <span className="font-medium text-slate-900 dark:text-slate-100">
                    {source.name}
                  </span>
                  {source.url && (
                    <a
                      href={source.url}
                      target="_blank"
                      rel="noopener noreferrer"
                      className="text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1"
                    >
                      <ExternalLink className="h-3 w-3" />
                      <span className="text-xs">開く</span>
                    </a>
                  )}
                </div>
                {source.description && (
                  <p className="text-sm text-slate-600 dark:text-slate-400 mt-1">
                    {source.description}
                  </p>
                )}
                {source.timestamp && (
                  <p className="text-xs text-slate-500 dark:text-slate-500 mt-1">
                    取得日時:{" "}
                    {new Date(source.timestamp).toLocaleString("ja-JP")}
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
