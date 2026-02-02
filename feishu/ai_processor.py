"""
AI 内容处理模块
===============
使用 DeepSeek API 对录音转写内容进行智能提炼
"""

import os
import json
import requests
from typing import Dict, Any, List, Optional
from dotenv import load_dotenv

load_dotenv()


class AIProcessor:
    """AI 内容处理器"""
    
    SYSTEM_PROMPT = """你是一个专业的工作日报助手。你的任务是将用户一天的录音转写内容进行结构化处理。

请分析输入的原始录音内容，提取并生成以下结构化信息：

1. **今日摘要**：用1-2句话概括今天的主要工作内容（50-100字)
2. **待办事项**：提取所有需要完成的任务、承诺、计划（按优先级排序）
3. **灵感/想法**：提取有价值的创意、灵感、思考
4. **风险/问题**：提取提到的问题、担忧、风险点
5. **关键词**：提取3-5个核心关键词/标签
6. **要点大纲**：将内容按主题整理成层级大纲

输出要求：
- 使用 JSON 格式返回
- 内容要精炼、可执行
- 待办事项要具体、可操作
- 去除口语化表达和重复内容
- 如果某类内容不存在，返回空数组

JSON 格式示例：
{
    "summary": "今日主要进行了 EchoLog 与飞书集成的开发工作，完成了 API 对接和 GUI 集成。",
    "todos": [
        "完成 AI 提炼功能开发",
        "测试午夜自动同步",
        "更新项目文档"
    ],
    "ideas": [
        "可以添加 Magic Word 标记重要内容",
        "考虑支持多语言识别"
    ],
    "risks": [
        "飞书 API 创建文档有时较慢，需要优化"
    ],
    "keywords": ["飞书集成", "API开发", "日报"],
    "outline": "1. 飞书集成开发\\n   - API 权限配置\\n   - 多维表格字段设计\\n2. GUI 界面优化\\n   - 添加同步按钮\\n   - 状态显示"
}"""

    def __init__(self):
        self.api_key = os.getenv("DEEPSEEK_API_KEY")
        self.api_url = os.getenv("DEEPSEEK_API_URL", "https://api.deepseek.com")
        self.model = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
        
        if not self.api_key:
            raise ValueError("请配置 DEEPSEEK_API_KEY 环境变量")
    
    def process_content(self, raw_content: str) -> Dict[str, Any]:
        """
        处理原始录音内容，提取结构化信息
        
        Args:
            raw_content: 原始录音转写文本
            
        Returns:
            结构化数据字典
        """
        if not raw_content or len(raw_content.strip()) < 50:
            return self._empty_result("内容过短，无法处理")
        
        try:
            # 调用 DeepSeek API
            response = self._call_api(raw_content)
            
            # 解析响应
            result = self._parse_response(response)
            return result
            
        except Exception as e:
            print(f"AI 处理失败: {e}")
            return self._empty_result(str(e))
    
    def _call_api(self, content: str) -> str:
        """调用 DeepSeek API"""
        url = f"{self.api_url}/v1/chat/completions"
        
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # 限制内容长度（避免超长）
        max_chars = 50000  # 约 12k tokens
        if len(content) > max_chars:
            content = content[:max_chars] + "\n\n[内容已截断...]"
        
        data = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": f"请分析以下录音转写内容，提取结构化信息：\n\n{content}"}
            ],
            "temperature": 0.3,
            "max_tokens": 2000,
            "response_format": {"type": "json_object"}
        }
        
        response = requests.post(url, headers=headers, json=data, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result["choices"][0]["message"]["content"]
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """解析 API 响应"""
        try:
            data = json.loads(response)
            
            return {
                "success": True,
                "summary": data.get("summary", ""),
                "todos": data.get("todos", []),
                "ideas": data.get("ideas", []),
                "risks": data.get("risks", []),
                "keywords": data.get("keywords", []),
                "outline": data.get("outline", ""),
            }
        except json.JSONDecodeError as e:
            print(f"JSON 解析失败: {e}")
            print(f"原始响应: {response}")
            return self._empty_result("AI 响应格式错误")
    
    def _empty_result(self, error: str = "") -> Dict[str, Any]:
        """返回空结果"""
        return {
            "success": False,
            "error": error,
            "summary": "",
            "todos": [],
            "ideas": [],
            "risks": [],
            "keywords": [],
            "outline": "",
        }
    
    def generate_markdown_report(self, ai_result: Dict[str, Any], raw_content: str = "") -> str:
        """
        根据 AI 处理结果生成 Markdown 格式日报
        
        Args:
            ai_result: AI 处理结果
            raw_content: 原始内容（可选，用于附录）
        """
        lines = []
        
        # 摘要
        if ai_result.get("summary"):
            lines.append("## 📊 今日摘要")
            lines.append(f"> {ai_result['summary']}")
            lines.append("")
        
        # 待办事项
        if ai_result.get("todos"):
            lines.append("## ✅ 待办事项")
            for todo in ai_result["todos"]:
                lines.append(f"- [ ] {todo}")
            lines.append("")
        
        # 灵感/想法
        if ai_result.get("ideas"):
            lines.append("## 💡 灵感/想法")
            for idea in ai_result["ideas"]:
                lines.append(f"- {idea}")
            lines.append("")
        
        # 风险/问题
        if ai_result.get("risks"):
            lines.append("## ⚠️ 风险/问题")
            for risk in ai_result["risks"]:
                lines.append(f"- {risk}")
            lines.append("")
        
        # 要点大纲
        if ai_result.get("outline"):
            lines.append("## 🗺️ 要点大纲")
            lines.append(ai_result["outline"])
            lines.append("")
        
        # 原始记录（折叠）
        if raw_content:
            lines.append("## 📋 原始记录")
            lines.append("<details>")
            lines.append("<summary>点击展开原始录音转写</summary>")
            lines.append("")
            lines.append(raw_content)
            lines.append("")
            lines.append("</details>")
        
        return "\n".join(lines)


# 单例
_ai_processor = None

def get_ai_processor() -> AIProcessor:
    """获取 AI 处理器单例"""
    global _ai_processor
    if _ai_processor is None:
        _ai_processor = AIProcessor()
    return _ai_processor


# 测试代码
if __name__ == "__main__":
    # 测试 AI 处理
    test_content = """
    [01:13:18] 哈喽哈喽
    [01:13:20] 很高兴能够录音尝试一下看一下效果怎么样
    [01:13:25] 真的有字产得出来
    [01:13:25] 这个的话是血压水泵的吗
    [01:13:28] 还是怎么样来去走
    [01:13:32] 唉你这个录音效果还挺快的
    [01:15:00] 今天主要讨论了飞书集成的开发
    [01:15:10] 需要完成 API 对接
    [01:15:20] 明天要测试一下午夜自动同步功能
    [01:16:00] 有个想法，可以添加 Magic Word 功能
    [01:16:30] 担心飞书 API 有时候会比较慢
    """
    
    processor = get_ai_processor()
    result = processor.process_content(test_content)
    
    print("=" * 50)
    print("AI 处理结果:")
    print("=" * 50)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    if result["success"]:
        print("\n" + "=" * 50)
        print("生成的 Markdown:")
        print("=" * 50)
        markdown = processor.generate_markdown_report(result, test_content)
        print(markdown)
