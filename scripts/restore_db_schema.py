
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

if not api_key or not db_id:
    print("❌ API Key or Database ID missing.")
    sys.exit(1)

client = Client(auth=api_key)

import json

print(f"Checking Database: {db_id}")
try:
    db = client.databases.retrieve(db_id)
    print("DEBUG: Database Object:")
    print(json.dumps(db, indent=2, default=str))
    
    current_props = db.get("properties", {})
    if current_props is None:
        print("⚠️ 'properties' key is missing from response. Assuming empty or write-only access.")
        current_props = {}
        
    print(f"Current Properties Keys: {list(current_props.keys())}")
    
    # Identify Title property
    title_prop_name = None
    if current_props:
        for name, prop in current_props.items():
            if prop["type"] == "title":
                title_prop_name = name
                break
    else:
        # Blindly assume "Name" might effectively be the title if we can't see it
        # But for safety, let's just proceed with adding other fields.
        pass
    
    # ... (logic to define properties_to_update) ...
    properties_to_update = {}
    
    # Force Name if missing
    if not title_prop_name and "Name" not in current_props:
         # Note: You can't usually ADD a title property, you rename existing.
         # If we can't see existing, we can't rename.
         # So we hope the DB was created with "Name" (which my debug script did).
         pass

    # 2. Add missing properties
    # Always add them if we can't see them (idempotent-ish if types match, but might error if exists with different type)
    # Safer to just try adding.
    
    target_props = ["Date", "Type", "Summary", "Keywords", "Todo Count", "Status"]
    
    for prop in target_props:
        if prop not in current_props:
            if prop == "Date": properties_to_update["Date"] = {"date": {}}
            if prop == "Type": properties_to_update["Type"] = {"select": {"options": [{"name": "日报", "color": "blue"}, {"name": "周报", "color": "purple"}]}}
            if prop == "Summary": properties_to_update["Summary"] = {"rich_text": {}}
            if prop == "Keywords": properties_to_update["Keywords"] = {"multi_select": {"options": []}}
            if prop == "Todo Count": properties_to_update["Todo Count"] = {"number": {"format": "number"}}
            if prop == "Status": properties_to_update["Status"] = {"select": {"options": [{"name": "已同步", "color": "green"}, {"name": "待同步", "color": "gray"}]}}

    if properties_to_update:
        print(f"Updating database with properties: {list(properties_to_update.keys())}")
        try:
            client.databases.update(database_id=db_id, properties=properties_to_update)
            print("✅ Database schema updated command sent successfully.")
        except Exception as update_e:
             print(f"❌ Update failed: {update_e}")
             
    else:
        print("✅ No updates needed (according to visible schema).")

except Exception as e:
    print(f"❌ Error updating database: {e}")
    import traceback
    traceback.print_exc()
