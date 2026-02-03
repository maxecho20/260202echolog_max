
import os
import sys
from pathlib import Path
from notion_client import Client
from dotenv import load_dotenv

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

load_dotenv(project_root / ".env")

api_key = os.getenv("NOTION_API_KEY")
db_id = os.getenv("NOTION_DATABASE_ID")

client = Client(auth=api_key)

new_title = "EchoLog Minutes"

print(f"Renaming database {db_id} to '{new_title}'...")

try:
    client.databases.update(
        database_id=db_id,
        title=[{"text": {"content": new_title}}]
    )
    print("✅ Database renamed successfully!")
except Exception as e:
    print(f"❌ Failed to rename database: {e}")
