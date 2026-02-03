"""逐个添加属性"""
from notion_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv('NOTION_API_KEY'))
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

properties_to_add = {
    'Date': {'date': {}},
    'Summary': {'rich_text': {}},
    'Content': {'rich_text': {}},
    'Todo Count': {'number': {'format': 'number'}},
    'Keywords': {
        'multi_select': {
            'options': [
                {'name': '会议', 'color': 'blue'},
                {'name': '待办', 'color': 'red'},
            ]
        }
    },
    'Type': {
        'select': {
            'options': [
                {'name': '日报', 'color': 'blue'},
                {'name': '周报', 'color': 'purple'},
            ]
        }
    },
    'Status': {
        'select': {
            'options': [
                {'name': '待处理', 'color': 'yellow'},
                {'name': '已处理', 'color': 'green'},
            ]
        }
    },
    'Page Link': {'url': {}},
}

print(f"正在向 {DATABASE_ID} 添加属性...")

for name, config in properties_to_add.items():
    print(f"尝试添加 [{name}]...", end="")
    try:
        notion.databases.update(
            database_id=DATABASE_ID,
            properties={name: config}
        )
        print(" ✅ 成功")
    except Exception as e:
        print(f" ❌ 失败: {e}")
