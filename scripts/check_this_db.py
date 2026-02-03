"""完整打印当前 Database JSON"""
from notion_client import Client
import os
import json
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv('NOTION_API_KEY'))
db_id = os.getenv('NOTION_DATABASE_ID')

print(f"检查 Database ID: {db_id}")

try:
    db = notion.databases.retrieve(db_id)
    print("\n完整 JSON:")
    print(json.dumps(db, indent=2, ensure_ascii=False))
        
except Exception as e:
    print(f"Error: {e}")
