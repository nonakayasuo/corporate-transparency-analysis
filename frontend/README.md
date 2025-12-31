# フロントエンド

企業・金融の透明性分析ツールのWeb UIです。

## 技術スタック

- **Next.js 16** - Reactフレームワーク
- **TypeScript** - 型安全性
- **Tailwind CSS** - スタイリング
- **shadcn/ui** - UIコンポーネント
- **Lucide React** - アイコン

## セットアップ

```bash
# 依存関係のインストール
npm install

# 開発サーバーの起動
npm run dev
```

ブラウザで `http://localhost:3000` にアクセスします。

## ビルド

```bash
# プロダクションビルド
npm run build

# プロダクションサーバーの起動
npm start
```

## 機能

- 企業名、所在国、ウェブサイトURL、役員名の入力
- リアルタイム分析実行
- 分析結果の可視化（サマリー、ネットワーク、詳細データ）
- レスポンシブデザイン

## APIエンドポイント

### POST /api/analyze

企業分析を実行します。

**リクエストボディ:**
```json
{
  "company": "企業名",
  "country": "US" | "UK" | "JP",
  "website": "https://example.com" (オプション、JPの場合),
  "officer": "役員名" (オプション)
}
```

**レスポンス:**
```json
{
  "success": true,
  "data": {
    "company_name": "企業名",
    "analysis_date": "2024-01-01T00:00:00",
    "data_sources": {...},
    "network_analysis": {...},
    "summary": {...}
  }
}
```
