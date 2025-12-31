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
- Node.js 18以上（フロントエンド用）

## セットアップ手順

### ステップ1: リポジトリの準備

#### オプションA: リポジトリをフォークする場合

1. GitHubアカウントにログイン
2. 以下のリポジトリをフォーク：
   - https://github.com/bellingcat/EDGAR
   - https://github.com/bellingcat/sugartrail
   - https://github.com/bellingcat/name-variant-search

#### オプションB: 直接クローンする場合

```bash
mkdir -p tools
cd tools

# 各リポジトリをクローン
git clone https://github.com/bellingcat/EDGAR.git
git clone https://github.com/bellingcat/sugartrail.git
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
# プロジェクトルートに移動（自分のプロジェクトディレクトリに置き換えてください）
cd /path/to/corporate-transparency-analysis

# uvを使用してプロジェクトを初期化（既にpyproject.tomlがある場合はスキップ）
uv init

# 依存関係をインストール（pyproject.tomlから自動的に読み込まれる）
uv sync

# または、開発用依存関係も含めてインストール
uv sync --dev
```

#### 仮想環境のアクティベート

```bash
# uvが自動的に作成した仮想環境をアクティベート
source .venv/bin/activate  # macOS/Linux
# または
# .venv\Scripts\activate  # Windows

# または、uv runを使用して直接コマンドを実行（仮想環境の管理が不要）
uv run python scripts/basic_analysis.py --company "Company Name"
```

### ステップ4: 各ツールの個別セットアップ

#### EDGARのセットアップ

```bash
cd tools/EDGAR

# READMEを確認
cat README.md

# 一般的なセットアップ（ツールによって異なる場合があります）
# pip install edgartools  # またはツール固有のパッケージ
```

**EDGARの主な機能:**
- SEC EDGARデータベースからの企業データ取得
- 財務報告書のダウンロード
- 企業情報の検索

#### sugartrailのセットアップ

```bash
cd tools/sugartrail

# READMEを確認
cat README.md

# 一般的なセットアップ
# pip install -r requirements.txt
```

**sugartrailの主な機能:**
- Companies Houseデータの取得
- 企業ネットワークの可視化
- 役員・住所の関係性分析

#### name-variant-searchのセットアップ

```bash
cd tools/name-variant-search

# READMEを確認
cat README.md

# 一般的なセットアップ
# npm install  # JavaScriptベースの場合
# または
# pip install -r requirements.txt  # Pythonベースの場合
```

**name-variant-searchの主な機能:**
- 人名のバリエーション生成
- 異なる表記の検索
- 同一人物の特定支援

### ステップ5: データディレクトリの作成

```bash
# プロジェクトルートに移動（自分のプロジェクトディレクトリに置き換えてください）
cd /path/to/corporate-transparency-analysis

# データ保存用ディレクトリを作成
mkdir -p data/edgar
mkdir -p data/sugartrail
mkdir -p data/name_variants
mkdir -p data/output
```

### ステップ6: APIキーの設定

`.env.example`をコピーして`.env`ファイルを作成し、必要なAPIキーを設定：

```bash
cp .env.example .env
```

必要なAPIキー：
- `HOUJIN_BANGOU_API_ID`: 法人番号システムAPI（日本の企業情報用）
- `COMPANIES_HOUSE_USERNAME`, `COMPANIES_HOUSE_PASSWORD`: Companies House API（英国企業情報用）
- `GBIZINFO_API_KEY`: gBizINFO API（財務データ用、オプション）

### ステップ7: 動作確認

```bash
# プロジェクトルートに戻る（自分のプロジェクトディレクトリに置き換えてください）
cd /path/to/corporate-transparency-analysis

# 基本的な動作確認
uv run python -c "import pandas, numpy, matplotlib; print('基本パッケージ OK')"

# スクリプトの動作確認
uv run python scripts/basic_analysis.py --help

# EDGARの動作確認
cd tools/EDGAR
uv run python -c "import sys; print('EDGAR setup OK')"  # またはツール固有のテスト
cd ../..

# sugartrailの動作確認
cd tools/sugartrail
uv run python -c "import sys; print('sugartrail setup OK')"  # またはツール固有のテスト
cd ../..

# name-variant-searchの動作確認
cd tools/name-variant-search
# ツール固有のテストコマンドを実行
cd ../..
```

## 使用方法

### コマンドライン

```bash
# 日本の企業分析
uv run python scripts/integrated_analysis.py --company "BMSG" --country JP --website "https://bmsg.tokyo/"

# 米国企業分析
uv run python scripts/integrated_analysis.py --company "Apple Inc." --country US

# 英国企業分析
uv run python scripts/integrated_analysis.py --company "Company Name" --country UK
```

### Web UI

```bash
# フロントエンドの起動
cd frontend
npm install
npm run dev
```

ブラウザで `http://localhost:3000` にアクセスして使用できます。

## ディレクトリ構造

```
corporate-transparency-analysis/
├── README.md                 # このファイル
├── pyproject.toml            # Python依存関係
├── frontend/                 # Next.jsフロントエンド
├── scripts/                  # 統合分析用スクリプト
│   ├── basic_analysis.py
│   ├── integrated_analysis.py
│   ├── japan_corporate_fetcher.py
│   ├── financial_data_fetcher.py
│   ├── edgar_integration.py
│   ├── sugartrail_integration.py
│   └── name_variant_integration.py
├── tools/                    # 各ツールのリポジトリ
│   ├── EDGAR/
│   ├── sugartrail/
│   └── name-variant-search/
├── data/                     # 分析データの保存先
│   ├── edgar/
│   ├── sugartrail/
│   ├── name_variants/
│   └── output/
└── docs/                     # ドキュメント
```

## APIキーの取得方法

### 法人番号システムAPI（日本）

1. [法人番号公表サイト](https://www.houjin-bangou.nta.go.jp/)でアプリケーションIDを申請
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

各ツールのリポジトリが正しくクローンされているか確認：

```bash
ls -la tools/EDGAR
ls -la tools/sugartrail
ls -la tools/name-variant-search
```

### APIキーが設定されていない場合

各ツールはAPIキーが未設定の場合、警告を表示して仮データを返します。実際のデータを取得するには、適切なAPIキーを設定してください。

### よくある問題

1. **依存関係のエラー**
   - 各ツールのREADMEを確認
   - Pythonのバージョンを確認（3.9以上が必要）
   - `uv sync`を再実行して依存関係を再インストール

2. **パスの問題**
   - 絶対パスを使用することを推奨
   - 環境変数PATHを確認
   - `uv run`を使用することで、仮想環境のパス問題を回避可能

3. **APIキーや認証情報**
   - 各ツールで必要な認証情報を確認
   - `.env`ファイルを使用して管理

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
