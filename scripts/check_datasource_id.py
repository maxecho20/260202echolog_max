
import os
import sys
from pathlib import Path
from dotenv import load_dotenv
from notion_client import Client
import json

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

load_dotenv(project_root / ".env")

api_key = os.getenv("NOTION_API_KEY")
# The ID found in data_sources from previous run
target_id = "51e55372-8601-4b09-8f9d-417de52d95d0"

client = Client(auth=api_key)

print(f"Checking potential REAL Database ID: {target_id}")
try:
    db = client.databases.retrieve(target_id)
    print("DEBUG: Database Object:")
    print(json.dumps(db, indent=2, default=str))
    
    current_props = db.get("properties", {})
    print(f"Properties Keys: {list(current_props.keys())}")
except Exception as e:
    print(f"❌ Failed: {e}")
