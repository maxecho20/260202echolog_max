"""
重新初始化 Notion Database
==========================
创建包含完整属性配置的 Database，并更新 .env
"""

from notion_client import Client
import os
import json
from dotenv import load_dotenv

load_dotenv()

# 初始化 Notion Client
notion = Client(auth=os.getenv('NOTION_API_KEY'))
parent_page_id = os.getenv('NOTION_PARENT_PAGE_ID')

print(f"Parent Page ID: {parent_page_id}")

try:
    # 1. 定义数据库结构
    db_schema = {
        "parent": {"type": "page_id", "page_id": parent_page_id},
        "title": [{"type": "text", "text": {"content": "EchoLog Daily Reports V2"}}],
        "icon": {"type": "emoji", "emoji": "🚀"},
        "properties": {
            "Name": {"title": {}}, # 必须包含一个 Title 类型的属性
            "Date": {"date": {}},
            "Type": {
                "select": {
                    "options": [
                        {"name": "日报", "color": "blue"},
                        {"name": "周报", "color": "purple"},
                        {"name": "月报", "color": "pink"}
                    ]
                }
            },
            "Status": {
                "select": {
                    "options": [
                        {"name": "待处理", "color": "yellow"},
                        {"name": "已处理", "color": "green"},
                        {"name": "归档", "color": "gray"}
                    ]
                }
            },
            "Summary": {"rich_text": {}},
            "Keywords": {
                "multi_select": {
                    "options": [
                        {"name": "会议", "color": "blue"},
                        {"name": "待办", "color": "red"},
                        {"name": "灵感", "color": "yellow"}
                    ]
                }
            },
            "Todo Count": {"number": {"format": "number"}},
            "Content": {"rich_text": {}} # 用于存储简略内容或链接
        }
    }

    # 2. 创建数据库
    print("正在创建新 Database...")
    new_db = notion.databases.create(**db_schema)
    
    new_db_id = new_db["id"]
    print(f"✅ Database 创建成功! ID: {new_db_id}")
    print(f"URL: {new_db['url']}")
    
    # 检查属性
    print("返回的属性列表:", list(new_db['properties'].keys()))
    
    # 3. 更新 .env
    env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.env')
    
    # 读取原始内容
    with open(env_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()
        
    # 写入新内容
    with open(env_path, 'w', encoding='utf-8') as f:
        for line in lines:
            if line.startswith('NOTION_DATABASE_ID='):
                continue # 跳过旧配置
            f.write(line)
        # 追加新配置
        if not line.endswith('\n'):
            f.write('\n')
        f.write(f"NOTION_DATABASE_ID={new_db_id}\n")
        
    print("✅ .env 文件已更新")

except Exception as e:
    print(f"❌ 创建失败: {e}")
    # 打印更详细的错误信息
    import traceback
    traceback.print_exc()
