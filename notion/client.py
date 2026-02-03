"""
Notion API Client Wrapper
=========================
封装 notion-client，提供单例访问和配置管理。
"""

import os
import logging
from typing import Optional
from notion_client import Client
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

class NotionClient:
    """Notion API 客户端包装器 (单例模式)"""
    
    _instance: Optional['NotionClient'] = None
    _client: Optional[Client] = None
    
    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(NotionClient, cls).__new__(cls)
        return cls._instance
    
    def __init__(self):
        """初始化 Notion 客户端，如果未初始化过"""
        if self._client is None:
            self._logger = logging.getLogger("EchoLog.Notion")
            self._init_client()
            
    def _init_client(self):
        """从环境变量初始化 notion-client"""
        api_key = os.getenv("NOTION_API_KEY")
        
        if not api_key:
            self._logger.warning("未检测到 NOTION_API_KEY，Notion 集成模式: 离线/不可用")
            return
            
        try:
            self._client = Client(auth=api_key)
            self._logger.info("Notion 客户端初始化成功")
        except Exception as e:
            self._logger.error(f"Notion 客户端初始化失败: {e}")
            self._client = None

    @property
    def client(self) -> Optional[Client]:
        """获取原始 notion-client 实例"""
        return self._client
        
    @property
    def is_connected(self) -> bool:
        """检查连接状态"""
        return self._client is not None
        
    def test_connection(self) -> bool:
        """测试 API 连接有效性"""
        if not self.is_connected:
            return False
        try:
            self._client.users.me()
            return True
        except Exception as e:
            self._logger.error(f"Notion 连接测试失败: {e}")
            return False

# 全局单例获取函数
def get_notion_client() -> Optional[Client]:
    """获取全局 Notion Client 实例 (快捷方式)"""
    wrapper = NotionClient()
    return wrapper.client
