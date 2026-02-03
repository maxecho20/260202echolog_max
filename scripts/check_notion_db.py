"""查看 Data Source 属性"""
from notion_client import Client
import os
import json
from dotenv import load_dotenv

load_dotenv()

notion = Client(auth=os.getenv('NOTION_API_KEY'))

# 查看 data source 属性
try:
    ds = notion.databases.retrieve('adb8fbc1-0b74-4d98-a8de-0f88319a1e7f')
    print('Data Source 属性:')
    print('-' * 40)
    props = ds.get('properties', {})
    if props:
        for name, prop in props.items():
            prop_type = prop.get('type', 'unknown')
            print(f'  ✓ {name}: {prop_type}')
    else:
        print('  (没有属性)')
    print()
    print('完整结构:')
    print(json.dumps(ds, indent=2, ensure_ascii=False, default=str))
except Exception as e:
    print(f'Error: {e}')
