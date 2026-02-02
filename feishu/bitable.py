"""
飞书多维表格 API
================
提供多维表格的 CRUD 操作
"""

import os
from typing import Optional, Dict, Any, List
from datetime import datetime
from .client import FeishuClient


class BitableClient(FeishuClient):
    """飞书多维表格客户端"""
    
    def __init__(self):
        super().__init__()
        self.app_token = os.getenv("FEISHU_BITABLE_APP_TOKEN")
        self.table_id = os.getenv("FEISHU_BITABLE_TABLE_ID")
        
        if not self.app_token or not self.table_id:
            raise ValueError("请配置 FEISHU_BITABLE_APP_TOKEN 和 FEISHU_BITABLE_TABLE_ID")
    
    def _get_base_endpoint(self) -> str:
        """获取多维表格基础端点"""
        return f"bitable/v1/apps/{self.app_token}/tables/{self.table_id}"
    
    def create_record(self, fields: Dict[str, Any]) -> Dict[str, Any]:
        """创建单条记录"""
        endpoint = f"{self._get_base_endpoint()}/records"
        data = {"fields": fields}
        result = self.post(endpoint, data)
        
        if result.get("code") != 0:
            raise Exception(f"创建记录失败: {result}")
        
        return result.get("data", {}).get("record", {})
    
    def batch_create_records(self, records: List[Dict[str, Any]]) -> List[Dict]:
        """批量创建记录（最多 500 条）"""
        if len(records) > 500:
            raise ValueError("批量创建最多支持 500 条记录")
        
        endpoint = f"{self._get_base_endpoint()}/records/batch_create"
        data = {"records": [{"fields": r} if "fields" not in r else r for r in records]}
        result = self.post(endpoint, data)
        
        if result.get("code") != 0:
            raise Exception(f"批量创建记录失败: {result}")
        
        return result.get("data", {}).get("records", [])
    
    def get_record(self, record_id: str) -> Dict[str, Any]:
        """获取单条记录"""
        endpoint = f"{self._get_base_endpoint()}/records/{record_id}"
        result = self.get(endpoint)
        
        if result.get("code") != 0:
            raise Exception(f"获取记录失败: {result}")
        
        return result.get("data", {}).get("record", {})
    
    def list_records(self, page_size: int = 100) -> Dict[str, Any]:
        """获取记录列表"""
        endpoint = f"{self._get_base_endpoint()}/records"
        params = {"page_size": min(page_size, 500)}
        result = self.get(endpoint, params)
        
        if result.get("code") != 0:
            raise Exception(f"获取记录列表失败: {result}")
        
        return {
            "records": result.get("data", {}).get("items", []),
            "has_more": result.get("data", {}).get("has_more", False)
        }
    
    def update_record(self, record_id: str, fields: Dict[str, Any]) -> Dict:
        """更新单条记录"""
        endpoint = f"{self._get_base_endpoint()}/records/{record_id}"
        data = {"fields": fields}
        result = self.put(endpoint, data)
        
        if result.get("code") != 0:
            raise Exception(f"更新记录失败: {result}")
        
        return result.get("data", {}).get("record", {})
    
    def delete_record(self, record_id: str) -> bool:
        """删除单条记录"""
        endpoint = f"{self._get_base_endpoint()}/records/{record_id}"
        result = self.delete(endpoint)
        
        if result.get("code") != 0:
            raise Exception(f"删除记录失败: {result}")
        
        return True
    
    # ==================== 便捷方法 ====================
    
    def create_daily_report(
        self,
        date: datetime,
        title: str,
        summary: str,
        doc_url: Optional[str] = None,
        todo_count: int = 0,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """创建日报记录"""
        fields = {
            "日期": int(date.timestamp() * 1000),
            "标题": title,
            "摘要": summary,
            "类型": "日报",
            "状态": "待处理",
            "待办数量": todo_count,
        }
        
        if doc_url:
            fields["云文档链接"] = {"link": doc_url, "text": "查看详情"}
        
        if keywords:
            fields["关键词"] = keywords
        
        return self.create_record(fields)
    
    def create_weekly_report(
        self,
        date: datetime,
        title: str,
        summary: str,
        doc_url: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """创建周报记录"""
        fields = {
            "日期": int(date.timestamp() * 1000),
            "标题": title,
            "摘要": summary,
            "类型": "周报",
            "状态": "待处理",
        }
        
        if doc_url:
            fields["云文档链接"] = {"link": doc_url, "text": "查看详情"}
        
        if keywords:
            fields["关键词"] = keywords
        
        return self.create_record(fields)
    
    def create_monthly_report(
        self,
        date: datetime,
        title: str,
        summary: str,
        doc_url: Optional[str] = None,
        keywords: Optional[List[str]] = None
    ) -> Dict[str, Any]:
        """创建月报记录"""
        fields = {
            "日期": int(date.timestamp() * 1000),
            "标题": title,
            "摘要": summary,
            "类型": "月报",
            "状态": "待处理",
        }
        
        if doc_url:
            fields["云文档链接"] = {"link": doc_url, "text": "查看详情"}
        
        if keywords:
            fields["关键词"] = keywords
        
        return self.create_record(fields)
