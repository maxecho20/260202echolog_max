"""
Notion 同步服务
===============
负责将 EchoLog 的数据同步到 Notion Database。
"""

import os
import logging
from datetime import datetime
from typing import Dict, Any, Optional
from dotenv import load_dotenv

from .pages import NotionPageService

# 加载环境变量
load_dotenv()

class NotionSyncService:
    """Notion 同步服务"""
    
    def __init__(self):
        self.logger = logging.getLogger("EchoLog.NotionSync")
        self.page_service = NotionPageService()
        self.database_id = os.getenv("NOTION_DATABASE_ID")
        
    def sync_daily_report(self, report_data: Dict[str, Any]) -> bool:
        """
        同步日报到 Notion
        由于 Database 属性可能存在同步延迟或权限问题，
        我们将大部分元数据直接写入 Page 正文顶部。
        """
        if not self.database_id:
            self.logger.error("未配置 NOTION_DATABASE_ID，无法同步")
            return False
            
        self.logger.info("开始同步数据到 Notion...")
        
        # 1. 准备 Database Properties
        keywords = report_data.get("keywords", [])
        action_items = report_data.get("action_items", [])
        
        properties = {
            "Name": {
                "title": [{"text": {"content": report_data.get("title", f"EchoLog Report {datetime.now().strftime('%Y-%m-%d')}")}}]
            },
            "Date": {
                "date": {"start": datetime.now().strftime('%Y-%m-%d')}
            },
            "Type": {
                "select": {"name": report_data.get("type", "日报")}
            },
            "Summary": {
                "rich_text": [{"text": {"content": report_data.get("summary", "")[:2000]}}]  # Notion limit
            },
            "Keywords": {
                "multi_select": [{"name": kw[:100]} for kw in keywords[:10]]  # Max 10 tags
            },
            "Todo Count": {
                "number": len(action_items)
            },
            "Status": {
                "select": {"name": "已同步"}
            }
        }
        
        # 2. 准备页面内容 Blocks
        # 在顶部添加元数据信息块
        metadata_blocks = [
            {
                "object": "block",
                "type": "callout",
                "callout": {
                    "rich_text": [
                        {"type": "text", "text": {"content": f"📅 日期: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n"}},
                        {"type": "text", "text": {"content": f"🏷️ 类型: {report_data.get('type', '日报')}\n"}}, 
                        {"type": "text", "text": {"content": f"📌 关键词: {', '.join(report_data.get('keywords', []))}"}}
                    ],
                    "icon": {"emoji": "ℹ️"},
                    "color": "gray_background"
                }
            },
            {"object": "block", "type": "divider", "divider": {}}
        ]
        
        # 核心内容
        ai_data = {
            "summary": report_data.get("summary", ""),
            "content": report_data.get("text", ""),
            "action_items": report_data.get("action_items", []),
            "inspirations": report_data.get("inspirations", []),
            "risks": report_data.get("risks", [])
        }
        content_blocks = self.page_service.construct_page_content(ai_data)
        
        # 合并 Blocks
        all_blocks = metadata_blocks + content_blocks
        
        # 3. 创建页面
        try:
            result = self.page_service.create_page_in_database(
                database_id=self.database_id,
                properties=properties,
                children=all_blocks
            )
        except Exception as e:
            error_msg = str(e)
            if "property that exists" in error_msg or "validation" in error_msg.lower():
                self.logger.warning(f"完整属性同步失败 ({error_msg})，尝试仅同步标题和内容...")
                
                # Fallback: Use minimal properties (Just Title)
                # We assume "Name" is the title property name. 
                # If "Name" was also rejected, we might need to find the title key, but commonly it's Name or title.
                minimal_properties = {
                    "Name": properties.get("Name", {
                        "title": [{"text": {"content": report_data.get("title", "Untitled")}}]
                    })
                }
                
                result = self.page_service.create_page_in_database(
                    database_id=self.database_id,
                    properties=minimal_properties,
                    children=all_blocks
                )
            else:
                raise e
        
        if result:
            url = result.get('url')
            self.logger.info(f"✅ Notion 同步成功! URL: {url}")
            return url
        else:
            # If result is None, it means client is not connected (handled in page_service)
            raise Exception("Notion 客户端未连接或创建页面失败（无返回值）")

    def _build_properties(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """(Deprecated) 构建 Database 属性字段 - 保留以备未来恢复"""
        return {}

if __name__ == "__main__":
    # 简单测试代码
    logging.basicConfig(level=logging.INFO)
    service = NotionSyncService()
    
    test_data = {
        "title": "EchoLog 测试同步",
        "type": "日报",
        "summary": "这是一条由 EchoLog 自动同步的测试数据。",
        "text": "这里是完整的录音转写文本内容...\n\n第二段内容...",
        "action_items": ["测试 Notion API 连接", "验证 Block 构建器"],
        "keywords": ["测试", "API"],
        "risks": ["Token 可能过期"],
        "inspirations": ["增加 OAuth 支持"]
    }
    
    service.sync_daily_report(test_data)
