"""极简写入测试：使用默认属性名"""
from notion_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv('NOTION_API_KEY'))
db_id = os.getenv('NOTION_DATABASE_ID')

print(f"尝试向 Database {db_id} 写入...")

try:
    # 尝试使用最基础的 'Name' 属性
    new_page = notion.pages.create(
        parent={"database_id": db_id},
        properties={
            "Name": {
                "title": [{"text": {"content": "Test Page 1"}}]
            }
        }
    )
    print(f"✅ 使用 'Name' 写入成功! Page ID: {new_page['id']}")
except Exception as e:
    print(f"❌ 使用 'Name' 写入失败: {e}")

try:
    # 尝试使用 'Title' 属性
    new_page_2 = notion.pages.create(
        parent={"database_id": db_id},
        properties={
            "Title": {
                "title": [{"text": {"content": "Test Page 2"}}]
            }
        }
    )
    print(f"✅ 使用 'Title' 写入成功! Page ID: {new_page_2['id']}")
except Exception as e1:
    print(f"❌ 使用 'Title' 写入失败: {e1}")
