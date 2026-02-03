
import os
import sys
from pathlib import Path
from datetime import datetime

# Add project root to sys.path
project_root = Path(__file__).resolve().parent.parent
sys.path.append(str(project_root))

from dotenv import load_dotenv
load_dotenv(project_root / ".env")

import logging
logging.basicConfig(level=logging.INFO)

print("Project Root:", project_root)

try:
    from notion.sync import NotionSyncService
    print("✅ Successfully imported NotionSyncService")
except ImportError as e:
    print(f"❌ Failed to import NotionSyncService: {e}")
    sys.exit(1)

service = NotionSyncService()

test_data = {
    "title": "EchoLog Test Report " + datetime.now().strftime('%H:%M:%S'),
    "type": "日报",
    "summary": "This is a test summary from the diagnostic script.",
    "text": "This is the full content of the test report.\nIt has multiple lines.\nAnd some *formatting*.",
    "action_items": ["Check Notion Sync", "Fix Error Handling"],
    "keywords": ["Test", "Debug"],
    "risks": ["None"],
    "inspirations": ["Better error messages"]
}

print("\nAttempting to sync test report...")
try:
    success = service.sync_daily_report(test_data)
    if success:
        print("✅ Sync returned True")
    else:
        print("❌ Sync returned False (unexpected if exceptions are propagated)")
except Exception as e:
    print(f"❌ Sync failed with Exception: {e}")
    import traceback
    traceback.print_exc()
