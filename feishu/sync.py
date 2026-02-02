"""
飞书同步服务
============
负责将每日汇总同步到飞书多维表格和云文档
"""

from datetime import datetime
from typing import Optional, Dict, Any
from .bitable import BitableClient
from .docs import DocsClient
from .summary import DailySummaryService, get_daily_summary_service


class FeishuSyncService:
    """飞书同步服务"""
    
    def __init__(self):
        self.bitable_client: Optional[BitableClient] = None
        self.docs_client: Optional[DocsClient] = None
        self.summary_service: DailySummaryService = get_daily_summary_service()
        self._initialized = False
    
    def initialize(self) -> bool:
        """初始化飞书客户端"""
        try:
            self.bitable_client = BitableClient()
            self.docs_client = DocsClient()
            self._initialized = True
            return True
        except Exception as e:
            print(f"初始化飞书客户端失败: {e}")
            return False
    
    @property
    def is_initialized(self) -> bool:
        return self._initialized
    
    def sync_daily_report(self, date: Optional[datetime] = None, use_ai: bool = True) -> Dict[str, Any]:
        """
        同步日报到飞书
        
        Args:
            date: 日期，默认为今天
            use_ai: 是否使用 AI 处理
            
        Returns:
            包含同步结果的字典
        """
        if not self._initialized:
            if not self.initialize():
                return {"success": False, "error": "初始化失败"}
        
        if date is None:
            date = datetime.now()
        
        try:
            # 1. 聚合当天内容
            data = self.summary_service.aggregate_daily_content(date)
            
            if not data["contents"]:
                return {
                    "success": True,
                    "message": "当天无记录",
                    "file_count": 0
                }
            
            # 2. 合并所有内容
            raw_content = "\n\n".join([
                f"### {c['time']} - {c['filename']}\n{c['content']}" 
                for c in data["contents"]
            ])
            
            title = f"📅 {date.strftime('%Y-%m-%d')} 工作日报"
            summary = ""
            todo_count = 0
            keywords = ["会议"]
            doc_url = None
            
            # 3. AI 处理（如果启用）
            if use_ai:
                try:
                    from .ai_processor import get_ai_processor
                    processor = get_ai_processor()
                    ai_result = processor.process_content(raw_content)
                    
                    if ai_result.get("success"):
                        summary = ai_result.get("summary", "")
                        todo_count = len(ai_result.get("todos", []))
                        keywords = ai_result.get("keywords", ["会议"])
                        
                        # 生成 Markdown 并创建云文档
                        markdown_content = processor.generate_markdown_report(ai_result, raw_content)
                        
                        try:
                            doc = self.docs_client.create_document(title)
                            self.docs_client.append_markdown(doc["document_id"], markdown_content)
                            doc_url = doc["url"]
                        except Exception as doc_error:
                            print(f"创建云文档失败: {doc_error}")
                    else:
                        # AI 处理失败，使用原始内容
                        summary = data["contents"][0]["content"][:100] + "..."
                except Exception as ai_error:
                    print(f"AI 处理失败: {ai_error}")
                    summary = data["contents"][0]["content"][:100] + "..."
            else:
                summary = data["contents"][0]["content"][:100] + "..."
            
            # 4. 在多维表格创建索引记录
            record = self.bitable_client.create_daily_report(
                date=date,
                title=title,
                summary=summary,
                doc_url=doc_url,
                todo_count=todo_count,
                keywords=keywords if keywords else ["会议"]
            )
            
            return {
                "success": True,
                "message": "同步成功" + ("（含 AI 处理）" if use_ai and doc_url else ""),
                "file_count": data["file_count"],
                "total_words": data["total_words"],
                "doc_url": doc_url,
                "record_id": record.get("record_id"),
                "ai_processed": use_ai and doc_url is not None
            }
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_weekly_report(self, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """同步周报到飞书"""
        if not self._initialized:
            if not self.initialize():
                return {"success": False, "error": "初始化失败"}
        
        if end_date is None:
            end_date = datetime.now()
        
        try:
            # 生成周报 Markdown
            markdown_content = self.summary_service.generate_weekly_markdown(end_date)
            
            # 创建云文档
            start_date = end_date
            while start_date.weekday() != 0:  # 找到本周一
                start_date = start_date.replace(day=start_date.day - 1)
            
            title = f"📊 {start_date.strftime('%m.%d')}-{end_date.strftime('%m.%d')} 周报"
            doc = self.docs_client.create_document(title)
            self.docs_client.append_markdown(doc["document_id"], markdown_content)
            
            # 在多维表格创建记录
            record = self.bitable_client.create_weekly_report(
                date=end_date,
                title=title,
                summary=f"本周工作汇总",
                doc_url=doc["url"]
            )
            
            return {
                "success": True,
                "message": "周报同步成功",
                "doc_url": doc["url"],
                "record_id": record.get("record_id")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }
    
    def sync_monthly_report(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """同步月报到飞书"""
        if not self._initialized:
            if not self.initialize():
                return {"success": False, "error": "初始化失败"}
        
        if date is None:
            date = datetime.now()
        
        try:
            # 生成月报 Markdown
            markdown_content = self.summary_service.generate_monthly_markdown(date)
            
            # 创建云文档
            title = f"📈 {date.strftime('%Y年%m月')} 月报"
            doc = self.docs_client.create_document(title)
            self.docs_client.append_markdown(doc["document_id"], markdown_content)
            
            # 在多维表格创建记录
            record = self.bitable_client.create_monthly_report(
                date=date,
                title=title,
                summary=f"{date.strftime('%Y年%m月')} 工作汇总",
                doc_url=doc["url"]
            )
            
            return {
                "success": True,
                "message": "月报同步成功",
                "doc_url": doc["url"],
                "record_id": record.get("record_id")
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }


# 单例
_feishu_sync_service = None

def get_feishu_sync_service() -> FeishuSyncService:
    """获取飞书同步服务单例"""
    global _feishu_sync_service
    if _feishu_sync_service is None:
        _feishu_sync_service = FeishuSyncService()
    return _feishu_sync_service
