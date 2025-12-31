"use client";

import dynamic from "next/dynamic";
import { useMemo } from "react";
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from "@/components/ui/card";

// 動的インポート（SSRを無効化）
const ForceGraph2D = dynamic(() => import("react-force-graph-2d"), {
  ssr: false,
});

interface Entity {
  type: string;
  name: string;
  source: string;
}

interface Relationship {
  from: string;
  to: string;
  type: string;
}

interface NetworkGraphProps {
  entities: Entity[];
  relationships: Relationship[];
}

export function NetworkGraph({ entities, relationships }: NetworkGraphProps) {
  const graphData = useMemo(() => {
    // エンティティをノードに変換
    const nodesMap = new Map<
      string,
      { id: string; name: string; type: string; source: string; group: number }
    >();

    entities.forEach((entity) => {
      if (!nodesMap.has(entity.name)) {
        // タイプに応じてグループを設定
        let group = 1; // デフォルト
        if (entity.type === "company") {
          group = 1;
        } else if (entity.type === "officer") {
          group = 2;
        } else {
          group = 3;
        }

        nodesMap.set(entity.name, {
          id: entity.name,
          name: entity.name,
          type: entity.type,
          source: entity.source,
          group,
        });
      }
    });

    // 関係をリンクに変換
    const links = relationships.map((rel) => ({
      source: rel.from,
      target: rel.to,
      type: rel.type,
    }));

    // リンクに含まれるノードを追加（孤立ノードも表示）
    links.forEach((link) => {
      if (!nodesMap.has(link.source)) {
        nodesMap.set(link.source, {
          id: link.source,
          name: link.source,
          type: "unknown",
          source: "unknown",
          group: 0,
        });
      }
      if (!nodesMap.has(link.target)) {
        nodesMap.set(link.target, {
          id: link.target,
          name: link.target,
          type: "unknown",
          source: "unknown",
          group: 0,
        });
      }
    });

    return {
      nodes: Array.from(nodesMap.values()),
      links,
    };
  }, [entities, relationships]);

  // グループに応じた色を返す
  const getNodeColor = (node: { type?: string; [key: string]: unknown }) => {
    const nodeType = node.type || "unknown";
    if (nodeType === "company") {
      return "#3b82f6"; // 青
    } else if (nodeType === "officer") {
      return "#10b981"; // 緑
    } else {
      return "#8b5cf6"; // 紫
    }
  };

  if (graphData.nodes.length === 0) {
    return (
      <Card>
        <CardHeader>
          <CardTitle>ネットワークグラフ</CardTitle>
          <CardDescription>エンティティと関係性を視覚化</CardDescription>
        </CardHeader>
        <CardContent>
          <div className="flex items-center justify-center h-96 text-slate-500 dark:text-slate-400">
            <p>表示するデータがありません</p>
          </div>
        </CardContent>
      </Card>
    );
  }

  return (
    <Card>
      <CardHeader>
        <CardTitle>ネットワークグラフ</CardTitle>
        <CardDescription>
          {graphData.nodes.length}個のエンティティと{graphData.links.length}
          個の関係
        </CardDescription>
      </CardHeader>
      <CardContent>
        <div className="w-full h-[600px] border rounded-lg overflow-hidden bg-slate-50 dark:bg-slate-900">
          <ForceGraph2D
            graphData={graphData}
            nodeLabel={(node) => `${node.name} (${node.type})`}
            nodeColor={getNodeColor}
            nodeVal={(node) => {
              // ノードのサイズを関係の数に基づいて設定
              const linkCount = graphData.links.filter(
                (link) => link.source === node.id || link.target === node.id
              ).length;
              return Math.max(5, Math.min(20, 5 + linkCount * 2));
            }}
            linkColor={() => "rgba(148, 163, 184, 0.6)"}
            linkWidth={2}
            linkDirectionalArrowLength={6}
            linkDirectionalArrowRelPos={1}
            linkCurvature={0.2}
            cooldownTicks={100}
            onEngineStop={() => {
              // アニメーション停止時に再レンダリングを防ぐ
            }}
          />
        </div>
        <div className="mt-4 flex gap-4 flex-wrap">
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-blue-500"></div>
            <span className="text-sm text-slate-600 dark:text-slate-400">企業</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-green-500"></div>
            <span className="text-sm text-slate-600 dark:text-slate-400">役員</span>
          </div>
          <div className="flex items-center gap-2">
            <div className="w-4 h-4 rounded-full bg-purple-500"></div>
            <span className="text-sm text-slate-600 dark:text-slate-400">その他</span>
          </div>
        </div>
      </CardContent>
    </Card>
  );
}
