# 企業・金融の透明性分析ツール

Bellingcatの3つのツール（EDGAR、sugartrail、name-variant-search）を統合して、企業・金融の透明性を分析するためのリポジトリです。

## 概要

このリポジトリは、以下の3つのツールを組み合わせて使用します：

1. **EDGAR**: 米国証券取引委員会（SEC）のEDGARデータベースから企業や金融データを取得
2. **sugartrail**: 英国Companies Houseを通じて企業、役員、住所のネットワークを可視化
3. **name-variant-search**: 人名のバリエーションを検索し、同一人物の異なる表記を特定

## 前提条件

- Python 3.9以上
- Git
- uv（高速なPythonパッケージマネージャー）
- Node.js 18以上、pnpm（フロントエンド用）

## セットアップ手順

### ステップ1: 必要なツールリポジトリの準備

**注意**: 以下のツールリポジトリは、対応する機能を使用する場合にのみ必要です。

#### EDGAR（米国企業分析用 - 必須）

```bash
mkdir -p tools
cd tools
git clone https://github.com/bellingcat/EDGAR.git
cd ..
```

#### sugartrail（英国企業分析用 - オプション）

```bash
cd tools
git clone https://github.com/bellingcat/sugartrail.git
cd ..
# インストール
uv pip install -e tools/sugartrail
```

#### name-variant-search（オプション）

このツールはPython実装で代替されているため、クローンは不要です。
より高度な機能が必要な場合のみ、以下のコマンドでクローンできます：

```bash
cd tools
git clone https://github.com/bellingcat/name-variant-search.git
cd ..
```

### ステップ2: uvのインストール

#### uvとは

uvは、Rustで書かれた高速なPythonパッケージマネージャーです。pipやpoetryの代替として使用できます。

#### インストール方法

```bash
# macOS/Linux
curl -LsSf https://astral.sh/uv/install.sh | sh

# またはHomebrewを使用（macOS）
brew install uv

# Windows
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# インストール後、シェルを再起動するか、PATHを更新
export PATH="$HOME/.cargo/bin:$PATH"  # macOS/Linux
```

#### インストールの確認

```bash
uv --version
```

### ステップ3: Python環境のセットアップ

#### プロジェクトの初期化

```bash
# プロジェクトルートに移動
cd corporate-transparency-analysis

# 依存関係をインストール（pyproject.tomlから自動的に読み込まれる）
uv sync
```

#### 仮想環境のアクティベート

```bash
# uvが自動的に作成した仮想環境をアクティベート
source .venv/bin/activate  # macOS/Linux
# または
# .venv\Scripts\activate  # Windows
```

### ステップ4: EDGARツールの依存関係をインストール

```bash
# プロジェクトルートで実行
uv add typer pydantic jsonlines tenacity xmltodict click python-dateutil
```

### ステップ5: フロントエンドのセットアップ

```bash
# プロジェクトルートで実行
pnpm install
```

### ステップ6: データディレクトリの作成

```bash
# プロジェクトルートで実行
# データ保存用ディレクトリを作成
mkdir -p data/edgar
mkdir -p data/sugartrail
mkdir -p data/name_variants
mkdir -p data/output
```

### ステップ7: APIキーの設定

`.env.example`をコピーして`.env`ファイルを作成し、必要なAPIキーを設定：

```bash
cp .env.example .env
```

必要なAPIキー：
- `HOUJIN_BANGOU_API_ID`: 法人番号システムAPI（日本の企業情報用）
- `COMPANIES_HOUSE_USERNAME`, `COMPANIES_HOUSE_PASSWORD`: Companies House API（英国企業情報用）
- `GBIZINFO_API_KEY`: gBizINFO API（財務データ用、オプション）
- `FEC_API_KEY`: FEC (Federal Election Commission) API（米国の政治献金データ用、オプション）

注意: OpenSecrets APIは2025年4月15日に廃止されました。

### ステップ8: 動作確認

FastAPIサーバーを起動して動作確認を行います：

```bash
# バックエンドサーバーを起動
pnpm dev:api

# 別のターミナルでヘルスチェック
curl http://localhost:8000/health
```

正常に動作していれば、`{"status":"healthy","timestamp":"..."}` が返されます。

## 使用方法

### 開発サーバーの起動

```bash
# プロジェクトルートで実行
pnpm dev:all
```

これにより、FastAPIサーバー（ポート8000）とNext.js開発サーバー（ポート3000）が同時に起動します。

### APIエンドポイント

FastAPIサーバーが起動すると、以下のエンドポイントが利用可能になります：

- **APIドキュメント**: http://localhost:8000/docs (Swagger UI)
- **ReDoc**: http://localhost:8000/redoc
- **ヘルスチェック**: GET http://localhost:8000/health
- **統合分析**: POST http://localhost:8000/analyze
- **基本分析**: POST http://localhost:8000/basic-analysis
- **日本の企業情報**: POST http://localhost:8000/japan-company
- **財務データ**: POST http://localhost:8000/financial-data
- **PDF生成**: POST http://localhost:8000/generate-pdf

### Web UI

ブラウザで `http://localhost:3000` にアクセスして使用できます。

## コード品質管理

### Lintとフォーマット

```bash
# Lintチェック（エラーのみ表示）
pnpm lint

# Lintエラーを自動修正
pnpm lint:fix

# フォーマットチェック
pnpm format

# コードチェック（Lint + フォーマット）
pnpm check

# コードチェックと自動修正
pnpm check:fix
```

## ディレクトリ構造

```
corporate-transparency-analysis/
├── README.md                 # このファイル
├── package.json              # Node.js依存関係
├── pyproject.toml            # Python依存関係
├── pnpm-lock.yaml            # pnpmロックファイル
├── uv.lock                   # uvロックファイル
├── tsconfig.json             # TypeScript設定
├── next.config.ts            # Next.js設定
├── biome.json                # Biome（Lint/フォーマット）設定
├── components.json           # shadcn/ui設定
├── eslint.config.mjs         # ESLint設定
├── postcss.config.mjs        # PostCSS設定
├── .env.example              # 環境変数テンプレート
├── src/
│   ├── app/                  # Next.jsアプリケーション
│   │   ├── api/              # APIルート
│   │   │   └── analyze/
│   │   │       └── route.ts   # 分析APIルート
│   │   ├── layout.tsx        # レイアウト
│   │   ├── page.tsx          # メインページ
│   │   ├── globals.css       # グローバルスタイル
│   │   └── favicon.ico       # ファビコン
│   ├── backend/              # バックエンド処理
│   │   ├── api_server.py     # FastAPIサーバー
│   │   ├── integrated_analysis.py      # 統合分析
│   │   ├── basic_analysis.py            # 基本分析
│   │   ├── japan_corporate_fetcher.py   # 日本の企業情報取得
│   │   ├── financial_data_fetcher.py    # 財務データ取得
│   │   ├── edgar_integration.py         # EDGAR統合
│   │   ├── sugartrail_integration.py    # sugartrail統合
│   │   ├── name_variant_integration.py  # 名前バリエーション統合
│   │   ├── political_contributions_integration.py  # 政治献金統合
│   │   └── generate_usage_purpose_pdf.py           # PDF生成
│   ├── components/           # Reactコンポーネント
│   │   ├── NetworkGraph.tsx  # ネットワークグラフ
│   │   └── ui/               # shadcn/uiコンポーネント
│   │       ├── button.tsx
│   │       ├── card.tsx
│   │       ├── input.tsx
│   │       ├── select.tsx
│   │       └── tabs.tsx
│   └── lib/                  # ユーティリティ
│       └── utils.ts
├── tools/                    # 各ツールのリポジトリ（オプション）
│   ├── EDGAR/                # EDGARツール（米国企業分析用）
│   ├── sugartrail/           # sugartrailツール（英国企業分析用）
│   └── name-variant-search/  # name-variant-searchツール（オプション）
├── data/                     # 分析データの保存先
│   ├── edgar/                # EDGARデータ
│   ├── sugartrail/           # sugartrailデータ
│   ├── name_variants/        # 名前バリエーションデータ
│   └── output/               # 分析結果JSONファイル
├── public/                   # 静的ファイル
│   ├── file.svg
│   ├── globe.svg
│   ├── next.svg
│   ├── vercel.svg
│   └── window.svg
└── docs/                     # ドキュメント
```

## APIキーの取得方法

### 法人番号システムAPI（日本）

1. [法人番号公表サイト](https://www.houjin-bangou.nta.go.jp/)でアプリケーションIDを申請

### FEC API（米国の政治献金データ）

1. [FEC API Developer Portal](https://api.open.fec.gov/developers/)でアカウントを作成
2. APIキーを取得して`.env`ファイルに`FEC_API_KEY`として設定
3. 注意: FEC APIは無料で利用可能だが、レート制限があります

### OpenSecrets API（廃止済み）

**注意**: OpenSecrets APIは2025年4月15日に廃止されました。
カスタムデータソリューションが必要な場合は、commercial@opensecrets.org に連絡してください。
2. `.env`に`HOUJIN_BANGOU_API_ID`を設定

詳細: `docs/japan_corporate_api_setup.md`

### Companies House API（英国）

1. [Companies House Developer](https://developer.company-information.service.gov.uk/)でアカウント作成
2. `.env`に`COMPANIES_HOUSE_USERNAME`と`COMPANIES_HOUSE_PASSWORD`を設定

### gBizINFO API（財務データ、オプション）

1. [gBizINFO API](https://info.gbiz.go.jp/api/index.html)で利用申請
2. `.env`に`GBIZINFO_API_KEY`を設定

## トラブルシューティング

### 依存関係のエラー

```bash
uv sync --reinstall
```

### モジュールのインポートエラー

使用するツールのリポジトリが正しくクローンされているか確認：

```bash
# EDGARを使用する場合
ls -la tools/EDGAR

# sugartrailを使用する場合
ls -la tools/sugartrail
uv pip list | grep sugartrail
```

## 参考リンク

- [EDGAR リポジトリ](https://github.com/bellingcat/EDGAR)
- [sugartrail リポジトリ](https://github.com/bellingcat/sugartrail)
- [name-variant-search リポジトリ](https://github.com/bellingcat/name-variant-search)
- [Bellingcat GitHub Organization](https://github.com/orgs/bellingcat/repositories)
- [法人番号システム Web-API](https://www.houjin-bangou.nta.go.jp/webapi/index.html)
- [gBizINFO API](https://info.gbiz.go.jp/api/index.html)

## 注意事項

- 各ツールの使用に際しては、関連する法令や規制を遵守してください
- データの取得や分析を行う際は、適切な方法で情報を取り扱ってください
- 個人情報の取り扱いには特に注意してください

## ライセンス

このプロジェクトは **GNU General Public License v3.0 (GPL-3.0)** の下で公開されています。

### 使用しているツールのライセンス

このプロジェクトは以下のBellingcatのツールを統合して使用しています：

1. **EDGAR** - GNU General Public License v3.0
   - リポジトリ: https://github.com/bellingcat/EDGAR
   - このプロジェクトはEDGARのコードを直接使用しているため、GPL v3.0のコピーレフト条項により、プロジェクト全体もGPL v3.0で公開されています。

2. **name-variant-search** - MIT License
   - リポジトリ: https://github.com/bellingcat/name-variant-search
   - Copyright (c) 2021 Stichting Bellingcat

3. **sugartrail** - MIT License
   - リポジトリ: https://github.com/bellingcat/sugartrail
   - Copyright (c) 2022 Sean Greaves

### ライセンスの詳細

GPL v3.0はコピーレフトライセンスです。このライセンスの下で、あなたは以下を行うことができます：

- ✅ ソフトウェアを使用する
- ✅ ソフトウェアを研究する
- ✅ ソフトウェアを修正する
- ✅ ソフトウェアを配布する

ただし、配布する場合は、同じライセンス（GPL v3.0）の下でソースコードも公開する必要があります。

詳細については、`LICENSE`ファイルを参照してください。
