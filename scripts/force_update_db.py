"""暴力更新 Notion Database 属性"""
from notion_client import Client
import os
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv('NOTION_API_KEY'))
DATABASE_ID = os.getenv('NOTION_DATABASE_ID')

print(f"正在更新 Database: {DATABASE_ID}")

try:
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
        # 尝试重命名 'Name' -> 'Title'，如果失败也不应该影响其他属性添加
        'Name': {'name': 'Title'}
    }

    result = notion.databases.update(
        database_id=DATABASE_ID,
        properties=properties_payload
    )
    print("✅ 属性更新操作完成！")
    # print(result) # 避免打印过多

except Exception as e:
    print(f"❌ 更新失败: {e}")
