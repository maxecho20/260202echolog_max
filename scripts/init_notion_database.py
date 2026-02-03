"""
重新创建 EchoLog Database（包含所有属性）
"""
from notion_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv('NOTION_API_KEY'))
PARENT_PAGE_ID = os.getenv('NOTION_PARENT_PAGE_ID')

print("正在创建带完整属性的 EchoLog Database...")

try:
    new_database = notion.databases.create(
        parent={'type': 'page_id', 'page_id': PARENT_PAGE_ID},
        title=[{'type': 'text', 'text': {'content': '📊 EchoLog Daily Reports'}}],
        icon={'type': 'emoji', 'emoji': '📊'},
        properties={
            'Title': {'title': {}},
            'Date': {'date': {}},
            'Summary': {'rich_text': {}},
            'Content': {'rich_text': {}},
            'Todo Count': {'number': {'format': 'number'}},
            'Keywords': {
                'multi_select': {
                    'options': [
                        {'name': '会议', 'color': 'blue'},
                        {'name': '待办', 'color': 'red'},
                        {'name': '灵感', 'color': 'yellow'},
                        {'name': '风险', 'color': 'orange'},
                        {'name': '笔记', 'color': 'green'},
                    ]
                }
            },
            'Type': {
                'select': {
                    'options': [
                        {'name': '日报', 'color': 'blue'},
                        {'name': '周报', 'color': 'purple'},
                        {'name': '月报', 'color': 'pink'},
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
    )
    
    db_id = new_database.get('id')
    url = new_database.get('url')
    
    print(f"\n✅ Database 创建成功！")
    print(f"   Database ID: {db_id}")
    print(f"   URL: {url}")
    
    # 列出属性
    print(f"\n📝 Database 属性：")
    for name, prop in new_database.get('properties', {}).items():
        print(f"   ✓ {name}: {prop.get('type')}")
    
    print(f"\n📋 请更新 .env 文件：")
    print(f"   NOTION_DATABASE_ID={db_id}")
    
except Exception as e:
    print(f"❌ 创建失败: {e}")
