
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
db_id = os.getenv("NOTION_DATABASE_ID")

client = Client(auth=api_key)

print(f"Target Database: {db_id}")

# define property to add
prop_name = "Date"
prop_config = {"date": {}}

print(f"Attempting to add property '{prop_name}'...")
try:
    client.databases.update(
        database_id=db_id,
        properties={prop_name: prop_config}
    )
    print("✅ Success!")
except Exception as e:
    print(f"❌ Failed: {e}")

# Check result
print("Checking properties...")
db = client.databases.retrieve(db_id)
print(f"Properties: {list(db['properties'].keys())}")
