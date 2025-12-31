#!/usr/bin/env python3
"""
分析ログ生成モジュール

分析プロセスのログを構造化して生成します。
"""

from datetime import datetime
from typing import List, Dict, Any, Optional


class AnalysisLogger:
    """分析プロセスのログを管理するクラス"""

    def __init__(self):
        self.logs: List[Dict[str, Any]] = []

    def info(self, message: str, details: Optional[str] = None):
        """情報ログを追加"""
        self._add_log("info", message, details)

    def success(self, message: str, details: Optional[str] = None):
        """成功ログを追加"""
        self._add_log("success", message, details)

    def warning(self, message: str, details: Optional[str] = None):
        """警告ログを追加"""
        self._add_log("warning", message, details)

    def error(self, message: str, details: Optional[str] = None):
        """エラーログを追加"""
        self._add_log("error", message, details)

    def _add_log(self, level: str, message: str, details: Optional[str] = None):
        """ログを追加"""
        self.logs.append(
            {
                "timestamp": datetime.now().isoformat(),
                "level": level,
                "message": message,
                "details": details,
            }
        )
        # コンソールにも出力（既存のprint()との互換性のため）
        prefix = {
            "info": "  →",
            "success": "  ✓",
            "warning": "  ⚠",
            "error": "  ✗",
        }.get(level, "  →")
        print(f"{prefix} {message}")
        if details:
            print(f"     {details}")

    def get_logs(self) -> List[Dict[str, Any]]:
        """ログのリストを取得"""
        return self.logs

    def clear(self):
        """ログをクリア"""
        self.logs = []
