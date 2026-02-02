"""
飞书 API 客户端
===============
处理认证和基础 API 调用
"""

import os
import time
import requests
from typing import Optional, Dict, Any
from dotenv import load_dotenv

load_dotenv()


class FeishuClient:
    """飞书 API 客户端基类"""
    
    BASE_URL = "https://open.feishu.cn/open-apis"
    
    def __init__(self):
        self.app_id = os.getenv("FEISHU_APP_ID")
        self.app_secret = os.getenv("FEISHU_APP_SECRET")
        
        if not self.app_id or not self.app_secret:
            raise ValueError("请配置 FEISHU_APP_ID 和 FEISHU_APP_SECRET 环境变量")
        
        self._access_token: Optional[str] = None
        self._token_expire_time: float = 0
    
    @property
    def access_token(self) -> str:
        """获取 access_token，自动刷新过期的 token"""
        if self._access_token and time.time() < self._token_expire_time - 60:
            return self._access_token
        
        self._refresh_token()
        return self._access_token
    
    def _refresh_token(self):
        """刷新 tenant_access_token"""
        url = f"{self.BASE_URL}/auth/v3/tenant_access_token/internal"
        payload = {
            "app_id": self.app_id,
            "app_secret": self.app_secret
        }
        
        response = requests.post(url, json=payload, timeout=30)
        data = response.json()
        
        if data.get("code") != 0:
            raise Exception(f"获取 access_token 失败: {data}")
        
        self._access_token = data["tenant_access_token"]
        self._token_expire_time = time.time() + data["expire"]
    
    def _get_headers(self) -> Dict[str, str]:
        """获取请求头"""
        return {
            "Authorization": f"Bearer {self.access_token}",
            "Content-Type": "application/json"
        }
    
    def get(self, endpoint: str, params: Optional[Dict] = None) -> Dict[str, Any]:
        """发送 GET 请求"""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.get(url, headers=self._get_headers(), params=params, timeout=30)
        return response.json()
    
    def post(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """发送 POST 请求"""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.post(url, headers=self._get_headers(), json=data, timeout=30)
        return response.json()
    
    def put(self, endpoint: str, data: Optional[Dict] = None) -> Dict[str, Any]:
        """发送 PUT 请求"""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.put(url, headers=self._get_headers(), json=data, timeout=30)
        return response.json()
    
    def delete(self, endpoint: str) -> Dict[str, Any]:
        """发送 DELETE 请求"""
        url = f"{self.BASE_URL}/{endpoint}"
        response = requests.delete(url, headers=self._get_headers(), timeout=30)
        return response.json()
