"""更新 Notion Database 属性 (从 .env 读取 ID)"""
from notion_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv('NOTION_API_KEY'))
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

print(f"正在更新 Database: {DATABASE_ID}")

try:
    # 1. 先检查现在的属性
    db = notion.databases.retrieve(DATABASE_ID)
    print(f"当前属性: {list(db['properties'].keys())}")
    
    # 2. 如果只有默认属性，进行重命名
    # 默认的 Title 属性通常叫 "Name" 或 "标题"
    current_title_prop = None
    for name, prop in db['properties'].items():
        if prop['type'] == 'title':
            current_title_prop = name
            break
            
    properties_payload = {
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
    
    # 如果当前标题不是 'Title'，我们要重命名它
    if current_title_prop and current_title_prop != 'Title':
        print(f"  重命名标题属性: '{current_title_prop}' -> 'Title'")
        properties_payload[current_title_prop] = {'name': 'Title'}

    result = notion.databases.update(
        database_id=DATABASE_ID,
        properties=properties_payload
    )
    print("✅ 属性更新成功！")
    print(f"当前属性列表: {list(result['properties'].keys())}")

except Exception as e:
    print(f"❌ 更新失败: {e}")
