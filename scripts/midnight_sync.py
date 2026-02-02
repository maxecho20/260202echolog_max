"""
EchoLog 午夜自动同步脚本
========================
此脚本通过 Windows 任务计划在每天午夜自动执行，
将前一天的录音内容经 AI 处理后同步到飞书。

使用方法：
1. 直接运行测试：python scripts/midnight_sync.py
2. 安装 Windows 任务：python scripts/midnight_sync.py --install
3. 卸载 Windows 任务：python scripts/midnight_sync.py --uninstall
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

# 加载环境变量
from dotenv import load_dotenv
load_dotenv(project_root / ".env")


def sync_yesterday():
    """同步昨天的日报"""
    from feishu import get_feishu_sync_service
    
    yesterday = datetime.now() - timedelta(days=1)
    
    print(f"=" * 50)
    print(f"EchoLog 午夜自动同步")
    print(f"执行时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"同步日期: {yesterday.strftime('%Y-%m-%d')}")
    print(f"=" * 50)
    
    try:
        service = get_feishu_sync_service()
        result = service.sync_daily_report(yesterday, use_ai=True)
        
        if result.get("success"):
            print(f"\n✅ 同步成功！")
            print(f"   - 文件数量: {result.get('file_count', 0)}")
            print(f"   - 字数统计: {result.get('total_words', 0)}")
            print(f"   - AI 处理: {'是' if result.get('ai_processed') else '否'}")
            if result.get("doc_url"):
                print(f"   - 云文档: {result.get('doc_url')}")
        else:
            print(f"\n❌ 同步失败: {result.get('error', '未知错误')}")
            
        return result.get("success", False)
        
    except Exception as e:
        print(f"\n❌ 发生异常: {e}")
        import traceback
        traceback.print_exc()
        return False


def install_task():
    """安装 Windows 任务计划"""
    import subprocess
    
    # 获取 Python 和脚本路径
    python_exe = sys.executable
    script_path = Path(__file__).resolve()
    
    # 任务名称
    task_name = "EchoLog_MidnightSync"
    
    # 创建 XML 任务定义
    xml_content = f'''<?xml version="1.0" encoding="UTF-16"?>
<Task version="1.4" xmlns="http://schemas.microsoft.com/windows/2004/02/mit/task">
  <RegistrationInfo>
    <Description>EchoLog 午夜自动同步 - 每天 00:05 将前一天录音同步到飞书</Description>
    <Author>EchoLog</Author>
  </RegistrationInfo>
  <Triggers>
    <CalendarTrigger>
      <StartBoundary>2026-01-01T00:05:00</StartBoundary>
      <Enabled>true</Enabled>
      <ScheduleByDay>
        <DaysInterval>1</DaysInterval>
      </ScheduleByDay>
    </CalendarTrigger>
  </Triggers>
  <Principals>
    <Principal id="Author">
      <LogonType>InteractiveToken</LogonType>
      <RunLevel>LeastPrivilege</RunLevel>
    </Principal>
  </Principals>
  <Settings>
    <MultipleInstancesPolicy>IgnoreNew</MultipleInstancesPolicy>
    <DisallowStartIfOnBatteries>false</DisallowStartIfOnBatteries>
    <StopIfGoingOnBatteries>false</StopIfGoingOnBatteries>
    <AllowHardTerminate>true</AllowHardTerminate>
    <StartWhenAvailable>true</StartWhenAvailable>
    <RunOnlyIfNetworkAvailable>true</RunOnlyIfNetworkAvailable>
    <AllowStartOnDemand>true</AllowStartOnDemand>
    <Enabled>true</Enabled>
    <Hidden>false</Hidden>
    <RunOnlyIfIdle>false</RunOnlyIfIdle>
    <WakeToRun>false</WakeToRun>
    <ExecutionTimeLimit>PT1H</ExecutionTimeLimit>
    <Priority>7</Priority>
  </Settings>
  <Actions Context="Author">
    <Exec>
      <Command>{python_exe}</Command>
      <Arguments>"{script_path}"</Arguments>
      <WorkingDirectory>{project_root}</WorkingDirectory>
    </Exec>
  </Actions>
</Task>'''
    
    # 保存 XML 文件
    xml_path = project_root / "scripts" / "midnight_sync_task.xml"
    xml_path.write_text(xml_content, encoding="utf-16")
    
    # 注册任务
    try:
        # 先尝试删除已有任务
        subprocess.run(
            ["schtasks", "/delete", "/tn", task_name, "/f"],
            capture_output=True
        )
        
        # 创建新任务
        result = subprocess.run(
            ["schtasks", "/create", "/tn", task_name, "/xml", str(xml_path)],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Windows 任务计划已安装!")
            print(f"   - 任务名称: {task_name}")
            print(f"   - 执行时间: 每天 00:05")
            print(f"   - 脚本路径: {script_path}")
            print(f"\n💡 提示:")
            print(f"   - 可在「任务计划程序」中查看和管理")
            print(f"   - 运行 'python {script_path} --uninstall' 卸载")
            return True
        else:
            print(f"❌ 安装失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 安装失败: {e}")
        return False


def uninstall_task():
    """卸载 Windows 任务计划"""
    import subprocess
    
    task_name = "EchoLog_MidnightSync"
    
    try:
        result = subprocess.run(
            ["schtasks", "/delete", "/tn", task_name, "/f"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print(f"✅ Windows 任务计划已卸载: {task_name}")
            return True
        else:
            print(f"❌ 卸载失败: {result.stderr}")
            return False
            
    except Exception as e:
        print(f"❌ 卸载失败: {e}")
        return False


def main():
    """主入口"""
    if len(sys.argv) > 1:
        if sys.argv[1] == "--install":
            install_task()
        elif sys.argv[1] == "--uninstall":
            uninstall_task()
        elif sys.argv[1] == "--help":
            print(__doc__)
        else:
            print(f"未知参数: {sys.argv[1]}")
            print("使用 --help 查看帮助")
    else:
        # 直接执行同步
        sync_yesterday()


if __name__ == "__main__":
    main()
