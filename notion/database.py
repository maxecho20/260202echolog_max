"""
Notion Database Service
=======================
处理 Notion Database 的查询和操作。
"""

import logging
from typing import Dict, Any, List, Optional
from .client import get_notion_client

class NotionDatabase:
    """Notion Database 管理服务"""
    
    def __init__(self):
        self.client = get_notion_client()
        self.logger = logging.getLogger("EchoLog.NotionDB")
        
    def query_database(
        self, 
        database_id: str, 
        filter_criteria: Optional[Dict[str, Any]] = None,
        sorts: Optional[List[Dict[str, Any]]] = None
    ) -> List[Dict[str, Any]]:
        """查询 Database"""
        
        if not self.client:
            return []
            
        try:
            payload = {"database_id": database_id}
            if filter_criteria:
                payload["filter"] = filter_criteria
            if sorts:
                payload["sorts"] = sorts
                
            response = self.client.databases.query(**payload)
            return response.get("results", [])
            
        except Exception as e:
            self.logger.error(f"查询 Database 失败: {e}")
            return []

    def get_database_info(self, database_id: str) -> Optional[Dict[str, Any]]:
        """获取 Database 元数据"""
        if not self.client:
            return None
        try:
            return self.client.databases.retrieve(database_id=database_id)
        except Exception as e:
            self.logger.error(f"获取 Database 信息失败: {e}")
            return None
