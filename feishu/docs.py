"""
飞书云文档 API
==============
提供云文档的创建和编辑功能
"""

import os
from typing import Optional, Dict, Any, List
from .client import FeishuClient


class DocsClient(FeishuClient):
    """飞书云文档客户端"""
    
    def __init__(self, folder_token: Optional[str] = None):
        super().__init__()
        self.folder_token = folder_token or os.getenv("FEISHU_FOLDER_TOKEN")
    
    def create_document(self, title: str) -> Dict[str, Any]:
        """创建新文档"""
        endpoint = "docx/v1/documents"
        data = {"title": title}
        
        if self.folder_token:
            data["folder_token"] = self.folder_token
        
        result = self.post(endpoint, data)
        
        if result.get("code") != 0:
            raise Exception(f"创建文档失败: {result}")
        
        doc_data = result.get("data", {}).get("document", {})
        doc_id = doc_data.get("document_id")
        
        return {
            "document_id": doc_id,
            "title": doc_data.get("title"),
            "url": f"https://xatc0v8uz5m.feishu.cn/docx/{doc_id}"
        }
    
    def create_block(self, document_id: str, block_type: int, content: Dict) -> Dict:
        """在文档中创建块"""
        endpoint = f"docx/v1/documents/{document_id}/blocks/{document_id}/children"
        data = {
            "children": [{
                "block_type": block_type,
                **content
            }],
            "index": -1
        }
        
        result = self.post(endpoint, data)
        if result.get("code") != 0:
            raise Exception(f"创建块失败: {result}")
        
        return result.get("data", {})
    
    def append_markdown(self, document_id: str, markdown_content: str) -> bool:
        """将 Markdown 内容追加到文档"""
        blocks = self._markdown_to_blocks(markdown_content)
        
        for block in blocks:
            try:
                self.create_block(document_id, block["type"], block["content"])
            except Exception as e:
                print(f"添加块失败: {e}")
        
        return True
    
    def _markdown_to_blocks(self, markdown: str) -> List[Dict[str, Any]]:
        """将 Markdown 转换为飞书文档块格式"""
        blocks = []
        lines = markdown.split("\n")
        
        for line in lines:
            line = line.strip()
            if not line:
                continue
            
            # 处理不同类型的 Markdown 元素
            if line.startswith("# "):
                # 一级标题 (block_type: 3)
                blocks.append({
                    "type": 3,
                    "content": {
                        "heading1": {
                            "elements": [{"text_run": {"content": line[2:], "text_element_style": {}}}]
                        }
                    }
                })
            elif line.startswith("## "):
                # 二级标题 (block_type: 4)
                blocks.append({
                    "type": 4,
                    "content": {
                        "heading2": {
                            "elements": [{"text_run": {"content": line[3:], "text_element_style": {}}}]
                        }
                    }
                })
            elif line.startswith("### "):
                # 三级标题 (block_type: 5)
                blocks.append({
                    "type": 5,
                    "content": {
                        "heading3": {
                            "elements": [{"text_run": {"content": line[4:], "text_element_style": {}}}]
                        }
                    }
                })
            elif line.startswith("- [ ] "):
                # 待办事项-未完成 (block_type: 17)
                blocks.append({
                    "type": 17,
                    "content": {
                        "todo": {
                            "elements": [{"text_run": {"content": line[6:], "text_element_style": {}}}],
                            "style": {"done": False}
                        }
                    }
                })
            elif line.startswith("- [x] ") or line.startswith("- [X] "):
                # 待办事项-已完成 (block_type: 17)
                blocks.append({
                    "type": 17,
                    "content": {
                        "todo": {
                            "elements": [{"text_run": {"content": line[6:], "text_element_style": {}}}],
                            "style": {"done": True}
                        }
                    }
                })
            elif line.startswith("- ") or line.startswith("* "):
                # 无序列表 (block_type: 12)
                blocks.append({
                    "type": 12,
                    "content": {
                        "bullet": {
                            "elements": [{"text_run": {"content": line[2:], "text_element_style": {}}}]
                        }
                    }
                })
            elif line.startswith("> "):
                # 引用块 (block_type: 14)
                # 引用块结构不同，需要使用 quote_container
                blocks.append({
                    "type": 2,  # 使用文本块代替引用块，避免结构问题
                    "content": {
                        "text": {
                            "elements": [{"text_run": {"content": f"📝 {line[2:]}", "text_element_style": {}}}]
                        }
                    }
                })
            else:
                # 普通文本段落 (block_type: 2)
                blocks.append({
                    "type": 2,
                    "content": {
                        "text": {
                            "elements": [{"text_run": {"content": line, "text_element_style": {}}}]
                        }
                    }
                })
        
        return blocks
    
    def create_daily_report_doc(
        self,
        title: str,
        summary: str,
        todos: List[str],
        ideas: List[str],
        risks: List[str],
        details: str,
        outline: str
    ) -> Dict[str, Any]:
        """创建日报文档"""
        doc = self.create_document(title)
        document_id = doc["document_id"]
        
        content_parts = []
        content_parts.append(f"## 📝 今日摘要\n> {summary}\n")
        
        if todos:
            content_parts.append("## ✅ 待办事项")
            for todo in todos:
                content_parts.append(f"- [ ] {todo}")
            content_parts.append("")
        
        if ideas:
            content_parts.append("## 💡 灵感/想法")
            for idea in ideas:
                content_parts.append(f"- {idea}")
            content_parts.append("")
        
        if risks:
            content_parts.append("## ⚠️ 风险/问题")
            for risk in risks:
                content_parts.append(f"- {risk}")
            content_parts.append("")
        
        if details:
            content_parts.append("## 📋 详细记录")
            content_parts.append(details)
            content_parts.append("")
        
        if outline:
            content_parts.append("## 🗺️ 要点大纲")
            content_parts.append(outline)
        
        self.append_markdown(document_id, "\n".join(content_parts))
        return doc
