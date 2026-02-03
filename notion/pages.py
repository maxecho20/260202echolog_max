"""
Notion Page Service
===================
处理 Notion 页面的创建和内容写入。
"""

import logging
from typing import Dict, Any, List, Optional
from .client import get_notion_client
from .blocks import BlockBuilder

class NotionPageService:
    """Notion 页面管理服务"""
    
    def __init__(self):
        self.client = get_notion_client()
        self.logger = logging.getLogger("EchoLog.NotionPage")
        
    def create_page_in_database(
        self, 
        database_id: str, 
        properties: Dict[str, Any],
        children: Optional[List[Dict[str, Any]]] = None
    ) -> Optional[Dict[str, Any]]:
        """在指定 Database 中创建新页面"""
        
        if not self.client:
            self.logger.error("Notion 客户端未连接")
            return None
            
        payload = {
            "parent": {"database_id": database_id},
            "properties": properties,
        }
            
        if children:
            # Notion API 限制每次最多 100 个 block
            # 如果超过限制，需要分批追加（这里先简单处理前100个，实际场景可能需要优化）
            payload["children"] = children[:100]
            
        response = self.client.pages.create(**payload)
        self.logger.info(f"成功创建页面: {response['id']}")
        
        # 如果还有剩余的 block，分批追加
        if children and len(children) > 100:
            self._append_remaining_blocks(response['id'], children[100:])
            
        return response

    def _append_remaining_blocks(self, block_id: str, blocks: List[Dict[str, Any]]):
        """分批追加剩余的 blocks"""
        batch_size = 100
        for i in range(0, len(blocks), batch_size):
            batch = blocks[i : i + batch_size]
            try:
                self.client.blocks.children.append(block_id=block_id, children=batch)
                self.logger.info(f"追加 {len(batch)} 个 blocks 从索引 {i}")
            except Exception as e:
                self.logger.error(f"追加 blocks 失败: {e}")

    def construct_page_content(self, ai_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        根据 AI 分析结果构建页面的 Block 内容
        ai_data 结构预期包含: summary, action_items, risks, inspirations, outline
        """
        blocks = []
        
        # 1. 摘要部分 (Callout)
        if ai_data.get('summary'):
            blocks.append(BlockBuilder.heading_2("📝 此刻摘要"))
            blocks.append(BlockBuilder.paragraph(ai_data['summary']))
            blocks.append(BlockBuilder.divider())

        # 2. 待办事项 (To-Do List)
        if ai_data.get('action_items'):
            blocks.append(BlockBuilder.heading_2("✅ 待办事项"))
            for item in ai_data['action_items']:
                blocks.append(BlockBuilder.to_do(item))
            blocks.append(BlockBuilder.divider())

        # 3. 灵感与想法 (Bullet List)
        if ai_data.get('inspirations'):
            blocks.append(BlockBuilder.heading_2("💡 灵感与想法"))
            for item in ai_data['inspirations']:
                blocks.append(BlockBuilder.bulleted_list_item(item))
            blocks.append(BlockBuilder.divider())

        # 4. 风险提示 (Callout - Red/Warning)
        if ai_data.get('risks'):
            blocks.append(BlockBuilder.heading_2("⚠️ 风险提示"))
            for item in ai_data['risks']:
                blocks.append(BlockBuilder.callout(item, "⚠️"))
            blocks.append(BlockBuilder.divider())
            
        # 5. 原始内容/大纲
        if ai_data.get('content'):
            blocks.append(BlockBuilder.heading_2("📄 原始内容"))
            # 简单处理：将内容作为段落，或者按行分割
            # 更好的做法是如果 content 是长文本，按段落分割
            paragraphs = ai_data['content'].split('\n\n')
            for p in paragraphs:
                if p.strip():
                    blocks.append(BlockBuilder.paragraph(p.strip()))
                    
        return blocks
