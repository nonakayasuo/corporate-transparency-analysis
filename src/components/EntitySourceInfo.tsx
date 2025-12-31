"use client";

import { ExternalLink, Info } from "lucide-react";
import { useState } from "react";

interface EntitySourceInfoProps {
  entity: {
    name: string;
    type: string;
    source: string;
    sourceUrl?: string;
    sourceDescription?: string;
  };
}

const getSourceUrl = (
  source: string,
  entityName: string
): string | undefined => {
  // ソースに応じたURLを生成
  switch (source) {
    case "EDGAR":
      // EDGARの企業検索ページ
      return `https://www.sec.gov/cgi-bin/browse-edgar?company=${encodeURIComponent(
        entityName
      )}&owner=exclude&action=getcompany`;
    case "sugartrail":
      // Companies Houseの検索ページ
      return `https://find-and-update.company-information.service.gov.uk/search?q=${encodeURIComponent(
        entityName
      )}`;
    case "japan_corporate":
      // 法人番号システムの検索ページ
      return `https://www.houjin-bangou.nta.go.jp/henkorireki-johoto.html?selHouzinNo=${encodeURIComponent(
        entityName
      )}`;
    case "FEC":
      // FECの検索ページ
      return `https://www.fec.gov/data/`;
    default:
      return undefined;
  }
};

const getSourceDescription = (source: string): string => {
  switch (source) {
    case "EDGAR":
      return "米国証券取引委員会（SEC）のEDGARデータベース";
    case "sugartrail":
      return "英国Companies Houseの企業情報データベース";
    case "japan_corporate":
      return "日本の法人番号システム";
    case "FEC":
      return "米国連邦選挙委員会（FEC）の政治献金データ";
    default:
      return "不明なデータソース";
  }
};

export function EntitySourceInfo({ entity }: EntitySourceInfoProps) {
  const [showDetails, setShowDetails] = useState(false);
  const sourceUrl =
    entity.sourceUrl || getSourceUrl(entity.source, entity.name);
  const sourceDescription =
    entity.sourceDescription || getSourceDescription(entity.source);

  return (
    <div className="flex items-center gap-2">
      <span className="px-2 py-1 bg-slate-200 dark:bg-slate-700 text-slate-700 dark:text-slate-300 rounded text-xs">
        {entity.source}
      </span>
      {sourceUrl && (
        <a
          href={sourceUrl}
          target="_blank"
          rel="noopener noreferrer"
          className="text-blue-600 dark:text-blue-400 hover:underline flex items-center gap-1 text-xs"
          title={sourceDescription}
        >
          <ExternalLink className="h-3 w-3" />
        </a>
      )}
      <button
        onClick={() => setShowDetails(!showDetails)}
        className="text-slate-500 hover:text-slate-700 dark:text-slate-400 dark:hover:text-slate-200"
        title="ソース情報を表示"
      >
        <Info className="h-3 w-3" />
      </button>
      {showDetails && (
        <div className="absolute z-10 mt-2 p-2 bg-white dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded shadow-lg text-xs">
          <p className="font-medium text-slate-900 dark:text-slate-100 mb-1">
            {entity.source}
          </p>
          <p className="text-slate-600 dark:text-slate-400">
            {sourceDescription}
          </p>
          {sourceUrl && (
            <a
              href={sourceUrl}
              target="_blank"
              rel="noopener noreferrer"
              className="text-blue-600 dark:text-blue-400 hover:underline mt-1 flex items-center gap-1"
            >
              <ExternalLink className="h-3 w-3" />
              参照先を開く
            </a>
          )}
        </div>
      )}
    </div>
  );
}
