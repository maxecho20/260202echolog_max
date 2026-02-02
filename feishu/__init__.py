"""
飞书集成模块
============
提供与飞书 Open API 的集成功能
"""

from .client import FeishuClient
from .bitable import BitableClient
from .docs import DocsClient
from .summary import DailySummaryService, get_daily_summary_service
from .sync import FeishuSyncService, get_feishu_sync_service
from .ai_processor import AIProcessor, get_ai_processor

__all__ = [
    "FeishuClient",
    "BitableClient",
    "DocsClient",
    "DailySummaryService",
    "get_daily_summary_service",
    "FeishuSyncService",
    "get_feishu_sync_service",
    "AIProcessor",
    "get_ai_processor"
]
