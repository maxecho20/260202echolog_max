"""
EchoLog Notion Integration Module
================================
提供与 Notion API 的完整集成，包括 Database 操作、Page 创建和 Block 内容构建。
"""

from .client import NotionClient, get_notion_client
from .database import NotionDatabase
