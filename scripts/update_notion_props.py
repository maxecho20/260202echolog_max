"""更新 Notion Database 属性"""
from notion_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv('NOTION_API_KEY'))

DATABASE_ID = '8193023c-4ed6-4ea9-a6c6-62de1a722244'

print("正在更新 Database 属性...")

try:
    result = notion.databases.update(
        database_id=DATABASE_ID,
        properties={
            'Date': {'date': {}},
            'Summary': {'rich_text': {}},
            'Content': {'rich_text': {}},
            'Todo Count': {'number': {'format': 'number'}},
            'Keywords': {'multi_select': {}},
            'Type': {'select': {}},
            'Status': {'select': {}},
            'Page Link': {'url': {}},
        }
    )
    print("✅ 属性更新成功！")
    print(f"返回结果类型: {type(result)}")
    if isinstance(result, dict):
        props = result.get('properties', {})
        for name in props:
            print(f"  - {name}")
except Exception as e:
    print(f"❌ 更新失败: {e}")
