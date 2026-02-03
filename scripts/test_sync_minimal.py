
import os
import sys
from pathlib import Path
from datetime import datetime
from notion_client import Client

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

api_key = os.getenv("NOTION_API_KEY")
db_id = os.getenv("NOTION_DATABASE_ID")

client = Client(auth=api_key)

print(f"Testing Minimal Sync to DB: {db_id}")

properties = {
    "Name": {
        "title": [{"text": {"content": "Minimal Sync Test"}}]
    }
}

try:
    client.pages.create(
        parent={"database_id": db_id},
        properties=properties
    )
    print("✅ Minimal sync (Title only) SUCCESS!")
except Exception as e:
    print(f"❌ Minimal sync failed: {e}")
    
    # Try with lowercase 'title' or 'Title'?
    print("Trying 'Title' as key...")
    properties2 = {
        "title": { # Using ID 'title' is risky, usually it's name
             "title": [{"text": {"content": "Minimal Sync Test 2"}}]
        }
    }
    # actually keys in properties dict are names or IDs.
    
    try:
        client.pages.create(
            parent={"database_id": db_id},
            properties={"Title": {"title": [{"text": {"content": "Test Title"}}]}}
        )
        print("✅ Sync with 'Title' SUCCESS!")
    except Exception as e2:
        print(f"❌ Sync with 'Title' failed: {e2}")

