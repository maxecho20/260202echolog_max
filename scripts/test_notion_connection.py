import os
import sys
from pathlib import Path

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

import logging
logging.basicConfig(level=logging.INFO)

print("Checking Notion Environment Variables...")
api_key = os.getenv("NOTION_API_KEY")
db_id = os.getenv("NOTION_DATABASE_ID")

if not api_key:
    print("❌ NOTION_API_KEY is missing!")
else:
    print(f"✅ NOTION_API_KEY found: {api_key[:4]}...{api_key[-4:]}")

if not db_id:
    print("❌ NOTION_DATABASE_ID is missing!")
else:
    print(f"✅ NOTION_DATABASE_ID found: {db_id}")

if not api_key:
    sys.exit(1)

print("\nTesting Notion Client Connection...")
try:
    from notion_client import Client
    client = Client(auth=api_key)
    me = client.users.me()
    print(f"✅ Successfully connected as: {me.get('name')} ({me.get('type')})")
except Exception as e:
    print(f"❌ Connection failed: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\nTesting Database Access...")
if db_id:
    try:
        db = client.databases.retrieve(database_id=db_id)
        print(f"✅ Database accessed: {db.get('title', [{}])[0].get('plain_text', 'Untitled')}")
        print("Database Properties Schema:")
        for name, prop in db.get('properties', {}).items():
            print(f"  - {name}: {prop['type']}")
    except Exception as e:
        print(f"❌ Database access failed: {e}")
        import traceback
        traceback.print_exc()
