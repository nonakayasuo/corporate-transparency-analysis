#!/usr/bin/env python3
"""
name-variant-searchツール統合モジュール

Bellingcatのname-variant-searchツールを使用して名前のバリエーションを生成します。
"""

import json
import re
import subprocess
from pathlib import Path
from typing import Optional

# プロジェクトルートをパスに追加
project_root = Path(__file__).parent.parent.parent
name_variant_path = project_root / "tools" / "name-variant-search"


# JavaScriptベースのツールなので、Node.jsが必要
def check_node_available() -> bool:
    """Node.jsが利用可能かチェック"""
    try:
        result = subprocess.run(
            ["node", "--version"], check=False, capture_output=True, text=True, timeout=5
        )
    except (subprocess.TimeoutExpired, FileNotFoundError):
        return False
    else:
        return result.returncode == 0


def generate_name_variants(name: str) -> list[str]:
    """
    名前のバリエーションを生成

    Args:
        name: 元の名前

    Returns:
        名前のバリエーションのリスト
    """
    # 基本的なバリエーションを生成(Python実装)
    variants = set()

    # 元の名前
    variants.add(name)

    # 大文字・小文字のバリエーション
    variants.add(name.upper())
    variants.add(name.lower())
    variants.add(name.title())
    variants.add(name.capitalize())

    # スペースの処理
    if " " in name:
        parts = name.split()
        # 各単語の頭文字
        initials = "".join([p[0].upper() for p in parts if p])
        if initials:
            variants.add(initials)
        # 最初の単語のみ
        variants.add(parts[0])
        # 最後の単語のみ
        variants.add(parts[-1])
        # スペースなし
        variants.add("".join(parts))
        # アンダースコア区切り
        variants.add("_".join(parts))
        # ハイフン区切り
        variants.add("-".join(parts))

    # カンマの処理(姓, 名 の形式)
    if "," in name:
        parts = [p.strip() for p in name.split(",")]
        if len(parts) >= 2:
            # 名 姓 の形式
            variants.add(f"{parts[1]} {parts[0]}")
            variants.add(f"{parts[1]}, {parts[0]}")

    # 括弧内の情報を除去
    name_no_paren = re.sub(r"\([^)]*\)", "", name).strip()
    if name_no_paren != name:
        variants.add(name_no_paren)
        # 括弧内の情報のみ
        paren_content = re.findall(r"\(([^)]*)\)", name)
        for content in paren_content:
            variants.add(content)

    # 重複を除去してソート
    return sorted(variants)


def generate_name_variants_js(name: str) -> Optional[list[str]]:
    """
    JavaScript版のname-variant-searchツールを使用(Node.jsが必要)

    Args:
        name: 元の名前

    Returns:
        名前のバリエーションのリスト、またはNone
    """
    if not check_node_available():
        return None

    try:
        # name-variant-searchツールのJavaScript実装を呼び出す
        # 実際の実装はツールの構造に依存
        script_path = name_variant_path / "src" / "index.js"

        if not script_path.exists():
            return None

        # Node.jsスクリプトを実行
        result = subprocess.run(
            ["node", str(script_path), name],
            check=False,
            capture_output=True,
            text=True,
            timeout=10,
            cwd=str(name_variant_path),
        )

        if result.returncode == 0:
            try:
                variants = json.loads(result.stdout)
            except json.JSONDecodeError:
                # JSONでない場合は行ごとに分割
                variants = [line.strip() for line in result.stdout.split("\n") if line.strip()]
            return variants
        else:
            return None

    except Exception as e:
        print(f"JavaScript版name-variant-searchエラー: {e}")
        return None


if __name__ == "__main__":
    # テスト
    test_name = "John Smith"
    variants = generate_name_variants(test_name)
    print(f"名前: {test_name}")
    print(f"バリエーション: {variants}")

    # JavaScript版も試す
    js_variants = generate_name_variants_js(test_name)
    if js_variants:
        print(f"JavaScript版バリエーション: {js_variants}")
