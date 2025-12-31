"use client";

import { useMemo } from "react";
import {
  Bar,
  BarChart,
  CartesianGrid,
  Cell,
  Pie,
  PieChart,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";
import {
  Card,
  CardContent,
  CardDescription,
  CardHeader,
  CardTitle,
} from "@/components/ui/card";

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

interface EntityTypeChartProps {
  entities: Entity[];
  relationships: Relationship[];
}

const COLORS = [
  "#3b82f6",
  "#10b981",
  "#8b5cf6",
  "#f59e0b",
  "#ef4444",
  "#06b6d4",
];

export function EntityTypeChart({
  entities,
  relationships,
}: EntityTypeChartProps) {
  const entityTypeData = useMemo(() => {
    const typeMap = new Map<string, number>();

    entities.forEach((entity) => {
      const type = entity.type || "unknown";
      typeMap.set(type, (typeMap.get(type) || 0) + 1);
    });

    return Array.from(typeMap.entries())
      .map(([name, value]) => ({
        name,
        value,
      }))
      .sort((a, b) => b.value - a.value);
  }, [entities]);

  const relationshipTypeData = useMemo(() => {
    const typeMap = new Map<string, number>();

    relationships.forEach((rel) => {
      const type = rel.type || "unknown";
      typeMap.set(type, (typeMap.get(type) || 0) + 1);
    });

    return Array.from(typeMap.entries())
      .map(([name, value]) => ({
        name,
        value,
      }))
      .sort((a, b) => b.value - a.value);
  }, [relationships]);

  const sourceData = useMemo(() => {
    const sourceMap = new Map<string, number>();

    entities.forEach((entity) => {
      const source = entity.source || "unknown";
      sourceMap.set(source, (sourceMap.get(source) || 0) + 1);
    });

    return Array.from(sourceMap.entries())
      .map(([name, value]) => ({
        name,
        value,
      }))
      .sort((a, b) => b.value - a.value);
  }, [entities]);

  if (entities.length === 0) {
    return null;
  }

  return (
    <div className="grid gap-6 md:grid-cols-3">
      <Card>
        <CardHeader>
          <CardTitle>エンティティタイプ</CardTitle>
          <CardDescription>エンティティの種類別分布</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={entityTypeData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) =>
                  `${name}: ${percent ? (percent * 100).toFixed(0) : 0}%`
                }
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {entityTypeData.map((entry, index) => (
                  <Cell
                    key={`cell-${entry.name}-${entry.value}`}
                    fill={COLORS[index % COLORS.length]}
                  />
                ))}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>データソース</CardTitle>
          <CardDescription>エンティティのデータソース別分布</CardDescription>
        </CardHeader>
        <CardContent>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={sourceData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip />
              <Bar dataKey="value" fill="#8b5cf6" />
            </BarChart>
          </ResponsiveContainer>
        </CardContent>
      </Card>

      <Card>
        <CardHeader>
          <CardTitle>関係性タイプ</CardTitle>
          <CardDescription>関係性の種類別分布</CardDescription>
        </CardHeader>
        <CardContent>
          {relationshipTypeData.length > 0 ? (
            <ResponsiveContainer width="100%" height={300}>
              <BarChart data={relationshipTypeData}>
                <CartesianGrid strokeDasharray="3 3" />
                <XAxis
                  dataKey="name"
                  angle={-45}
                  textAnchor="end"
                  height={100}
                />
                <YAxis />
                <Tooltip />
                <Bar dataKey="value" fill="#10b981" />
              </BarChart>
            </ResponsiveContainer>
          ) : (
            <div className="flex items-center justify-center h-[300px] text-slate-500 dark:text-slate-400">
              <p>関係性データがありません</p>
            </div>
          )}
        </CardContent>
      </Card>
    </div>
  );
}
