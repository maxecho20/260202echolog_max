"""
飞书 API 连接测试脚本
=====================
验证凭据并尝试操作多维表格
"""

import os
import requests
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 配置
APP_ID = os.getenv("FEISHU_APP_ID")
APP_SECRET = os.getenv("FEISHU_APP_SECRET")
BITABLE_APP_TOKEN = os.getenv("FEISHU_BITABLE_APP_TOKEN")
BITABLE_TABLE_ID = os.getenv("FEISHU_BITABLE_TABLE_ID")


def get_tenant_access_token():
    """获取 tenant_access_token"""
    url = "https://open.feishu.cn/open-apis/auth/v3/tenant_access_token/internal"
    payload = {
        "app_id": APP_ID,
        "app_secret": APP_SECRET
    }
    response = requests.post(url, json=payload)
    data = response.json()
    
    if data.get("code") == 0:
        print(f"✅ 获取 access_token 成功！")
        print(f"   Token: {data['tenant_access_token'][:20]}...")
        print(f"   有效期: {data['expire']} 秒")
        return data["tenant_access_token"]
    else:
        print(f"❌ 获取 access_token 失败: {data}")
        return None


def get_bitable_meta(token):
    """获取多维表格元信息"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if data.get("code") == 0:
        app_info = data["data"]["app"]
        print(f"\n✅ 多维表格信息:")
        print(f"   名称: {app_info.get('name')}")
        print(f"   App Token: {BITABLE_APP_TOKEN}")
        return True
    else:
        print(f"❌ 获取多维表格信息失败: {data}")
        return False


def get_table_fields(token):
    """获取数据表字段"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{BITABLE_TABLE_ID}/fields"
    headers = {"Authorization": f"Bearer {token}"}
    response = requests.get(url, headers=headers)
    data = response.json()
    
    if data.get("code") == 0:
        fields = data["data"]["items"]
        print(f"\n✅ 当前表格字段 ({len(fields)} 个):")
        for field in fields:
            print(f"   - {field['field_name']} ({field['type']})")
        return fields
    else:
        print(f"❌ 获取字段失败: {data}")
        return None


def create_fields(token):
    """创建 EchoLog 所需字段"""
    url = f"https://open.feishu.cn/open-apis/bitable/v1/apps/{BITABLE_APP_TOKEN}/tables/{BITABLE_TABLE_ID}/fields"
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # 定义需要创建的字段
    fields_to_create = [
        {
            "field_name": "日期",
            "type": 5,  # 日期
        },
        {
            "field_name": "标题",
            "type": 1,  # 文本
        },
        {
            "field_name": "摘要",
            "type": 1,  # 文本
        },
        {
            "field_name": "云文档链接",
            "type": 15,  # 链接
        },
        {
            "field_name": "待办数量",
            "type": 2,  # 数字
        },
        {
            "field_name": "关键词",
            "type": 4,  # 多选
            "property": {
                "options": [
                    {"name": "会议"},
                    {"name": "待办"},
                    {"name": "灵感"},
                    {"name": "风险"},
                    {"name": "项目"},
                ]
            }
        },
        {
            "field_name": "类型",
            "type": 3,  # 单选
            "property": {
                "options": [
                    {"name": "日报"},
                    {"name": "周报"},
                    {"name": "月报"},
                ]
            }
        },
        {
            "field_name": "状态",
            "type": 3,  # 单选
            "property": {
                "options": [
                    {"name": "待处理"},
                    {"name": "已处理"},
                ]
            }
        },
    ]
    
    print(f"\n📝 开始创建字段...")
    
    created_count = 0
    for field in fields_to_create:
        response = requests.post(url, headers=headers, json=field)
        data = response.json()
        
        if data.get("code") == 0:
            print(f"   ✅ 创建字段: {field['field_name']}")
            created_count += 1
        else:
            error_msg = data.get("msg", "未知错误")
            if "already exist" in error_msg.lower() or "1254007" in str(data.get("code")):
                print(f"   ⏭️ 字段已存在: {field['field_name']}")
            else:
                print(f"   ❌ 创建失败: {field['field_name']} - {data}")
    
    print(f"\n✅ 创建完成！新增 {created_count} 个字段")
    return created_count


def main():
    print("=" * 50)
    print("飞书 API 连接测试")
    print("=" * 50)
    
    print(f"\n📋 配置信息:")
    print(f"   App ID: {APP_ID}")
    print(f"   Bitable App Token: {BITABLE_APP_TOKEN}")
    print(f"   Table ID: {BITABLE_TABLE_ID}")
    
    # 1. 获取 access_token
    print(f"\n{'='*50}")
    print("步骤 1: 获取 access_token")
    print("=" * 50)
    token = get_tenant_access_token()
    if not token:
        return
    
    # 2. 获取多维表格信息
    print(f"\n{'='*50}")
    print("步骤 2: 验证多维表格访问权限")
    print("=" * 50)
    if not get_bitable_meta(token):
        print("\n⚠️ 可能需要在飞书开放平台配置应用权限")
        return
    
    # 3. 获取当前字段
    print(f"\n{'='*50}")
    print("步骤 3: 获取当前表格字段")
    print("=" * 50)
    fields = get_table_fields(token)
    
    # 4. 创建新字段
    print(f"\n{'='*50}")
    print("步骤 4: 创建 EchoLog 所需字段")
    print("=" * 50)
    
    user_input = input("\n是否创建新字段？(y/n): ")
    if user_input.lower() == 'y':
        create_fields(token)
        
        # 再次获取字段验证
        print(f"\n{'='*50}")
        print("验证: 获取更新后的字段")
        print("=" * 50)
        get_table_fields(token)
    else:
        print("跳过字段创建")
    
    print(f"\n{'='*50}")
    print("✅ 测试完成！")
    print("=" * 50)


if __name__ == "__main__":
    main()
