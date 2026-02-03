
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

load_dotenv(project_root / ".env")

api_key = os.getenv("NOTION_API_KEY")
parent_page_id = os.getenv("NOTION_PARENT_PAGE_ID")

if not api_key:
    print("❌ API Key missing.")
    sys.exit(1)

if not parent_page_id:
    print("❌ NOTION_PARENT_PAGE_ID missing. Cannot create database without a parent page.")
    # Try to find a parent page if not set?
    # For now, just exit.
    sys.exit(1)

client = Client(auth=api_key)

print(f"Creating new Daily Report Database under page: {parent_page_id}")

properties = {
    "Name": {"title": {}},
    "Date": {"date": {}},
    "Type": {
        "select": {
            "options": [
                {"name": "日报", "color": "blue"},
                {"name": "周报", "color": "purple"}
            ]
        }
    },
    "Summary": {"rich_text": {}},
    "Keywords": {
        "multi_select": {
            "options": []
        }
    },
    "Todo Count": {"number": {"format": "number"}},
    "Status": {
        "select": {
            "options": [
                {"name": "已同步", "color": "green"},
                {"name": "待同步", "color": "gray"}
            ]
        }
    }
}

try:
    new_db = client.databases.create(
        parent={"type": "page_id", "page_id": parent_page_id},
        title=[{"type": "text", "text": {"content": "EchoLog Debug DB"}}],
        properties={
            "Name": {"title": {}}
        }
    )
    
    import json
    print("DEBUG: Create Response:")
    print(json.dumps(new_db, indent=2, default=str))
    
    new_db_id = new_db["id"]
    print(f"\n✅ Successfully created new database!")
    print(f"ID: {new_db_id}")
    print(f"URL: {new_db['url']}")
    print(f"NOTION_DATABASE_ID={new_db_id}")
    
    # Optional: Auto-update .env?
    # confirm = input("Update .env now? (y/n): ")
    # if confirm.lower() == 'y':
    #     ...
    
except Exception as e:
    print(f"❌ Failed to create database: {e}")
    import traceback
    traceback.print_exc()
