"""
Notion Block Generators
=======================
用于生成 Notion Block 结构的辅助工具函数。
"""

from typing import List, Dict, Any, Optional

class BlockBuilder:
    """Notion Block 构建器"""
    
    @staticmethod
    def paragraph(text: str) -> Dict[str, Any]:
        """创建段落块"""
        return {
            "object": "block",
            "type": "paragraph",
            "paragraph": {
                "rich_text": BlockBuilder.rich_text(text)
            }
        }
        
    @staticmethod
    def heading_1(text: str) -> Dict[str, Any]:
        """创建一级标题"""
        return {
            "object": "block",
            "type": "heading_1",
            "heading_1": {
                "rich_text": BlockBuilder.rich_text(text)
            }
        }
        
    @staticmethod
    def heading_2(text: str) -> Dict[str, Any]:
        """创建二级标题"""
        return {
            "object": "block",
            "type": "heading_2",
            "heading_2": {
                "rich_text": BlockBuilder.rich_text(text)
            }
        }
        
    @staticmethod
    def heading_3(text: str) -> Dict[str, Any]:
        """创建三级标题"""
        return {
            "object": "block",
            "type": "heading_3",
            "heading_3": {
                "rich_text": BlockBuilder.rich_text(text)
            }
        }
        
    @staticmethod
    def bulleted_list_item(text: str) -> Dict[str, Any]:
        """创建无序列表项"""
        return {
            "object": "block",
            "type": "bulleted_list_item",
            "bulleted_list_item": {
                "rich_text": BlockBuilder.rich_text(text)
            }
        }
        
    @staticmethod
    def to_do(text: str, checked: bool = False) -> Dict[str, Any]:
        """创建待办事项"""
        return {
            "object": "block",
            "type": "to_do",
            "to_do": {
                "rich_text": BlockBuilder.rich_text(text),
                "checked": checked
            }
        }
    
    @staticmethod
    def callout(text: str, emoji: str = "💡") -> Dict[str, Any]:
        """创建高亮块 (Callout)"""
        return {
            "object": "block",
            "type": "callout",
            "callout": {
                "rich_text": BlockBuilder.rich_text(text),
                "icon": {
                    "emoji": emoji
                }
            }
        }
        
    @staticmethod
    def quote(text: str) -> Dict[str, Any]:
        """创建引用块"""
        return {
            "object": "block",
            "type": "quote",
            "quote": {
                "rich_text": BlockBuilder.rich_text(text)
            }
        }
        
    @staticmethod
    def divider() -> Dict[str, Any]:
        """创建分割线"""
        return {
            "object": "block",
            "type": "divider",
            "divider": {}
        }
        
    @staticmethod
    def rich_text(content: str, link: Optional[str] = None) -> List[Dict[str, Any]]:
        """构建 rich_text 对象列表"""
        if not content:
            return []
            
        text_obj = {
            "type": "text",
            "text": {
                "content": content
            }
        }
        
        if link:
            text_obj["text"]["link"] = {"url": link}
            
        return [text_obj]
