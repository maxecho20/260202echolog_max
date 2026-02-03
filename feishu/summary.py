"""
每日汇总服务
============
负责聚合当天的录音记录，生成日报并同步到飞书
"""

import os
from pathlib import Path
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from config import OutputConfig


class DailySummaryService:
    """每日汇总服务"""
    
    def __init__(self):
        self.output_dir = OutputConfig.OUTPUT_DIR
    
    def get_today_files(self) -> List[Path]:
        """获取今天的所有录音文件"""
        today = datetime.now().date()
        files = []
        
        for ext in ["*.md", "*.txt"]:
            for filepath in self.output_dir.glob(ext):
                try:
                    mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)
                    if mod_time.date() == today:
                        files.append(filepath)
                except:
                    continue
        
        return sorted(files, key=lambda x: x.stat().st_mtime)
    
    def get_files_by_date(self, date: datetime) -> List[Path]:
        """获取指定日期的所有文件"""
        target_date = date.date()
        files = []
        
        for ext in ["*.md", "*.txt"]:
            for filepath in self.output_dir.glob(ext):
                try:
                    mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)
                    if mod_time.date() == target_date:
                        files.append(filepath)
                except:
                    continue
        
        return sorted(files, key=lambda x: x.stat().st_mtime)
    
    def read_file_content(self, filepath: Path) -> str:
        """读取文件内容"""
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return f.read()
        except:
            return ""

    def aggregate_weekly_content(self, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """聚合一周的内容 (从周一到指定日期/今天)"""
        if end_date is None:
            end_date = datetime.now()
        
        # Calculate start of the week (Monday)
        start_date = end_date - timedelta(days=end_date.weekday())
        start_date = start_date.replace(hour=0, minute=0, second=0, microsecond=0)
        
        all_contents = []
        total_words = 0
        file_count = 0
        all_files = []
        
        # Iterate through each day of the week up to end_date
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            if current_date.date() > end_date.date():
                break
            
            data = self.aggregate_daily_content(current_date)
            if data["contents"]:
                 # Add a separator/header for the day
                 all_contents.append({
                     "filename": f"📅 {current_date.strftime('%Y-%m-%d %A')}", 
                     "time": "", 
                     "content": f"=== {current_date.strftime('%Y-%m-%d')} Summary ===",
                     "words": 0
                 })
                 all_contents.extend(data["contents"])
                 all_files.extend(data["files"])
                 total_words += data["total_words"]
                 file_count += data["file_count"]
        
        return {
            "date": end_date,
            "start_date": start_date,
            "end_date": end_date,
            "files": all_files,
            "contents": all_contents,
            "total_words": total_words,
            "file_count": file_count
        }

    def aggregate_daily_content(self, date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        聚合一天的所有内容
        
        Returns:
            包含 files, contents, total_words 的字典
        """
        if date is None:
            date = datetime.now()
        
        files = self.get_files_by_date(date)
        contents = []
        total_words = 0
        
        for filepath in files:
            content = self.read_file_content(filepath)
            if content:
                mod_time = datetime.fromtimestamp(filepath.stat().st_mtime)
                contents.append({
                    "filename": filepath.name,
                    "time": mod_time.strftime("%H:%M"),
                    "content": content,
                    "words": len(content)
                })
                total_words += len(content)
        
        return {
            "date": date,
            "files": files,
            "contents": contents,
            "total_words": total_words,
            "file_count": len(files)
        }
    
    def generate_daily_markdown(self, date: Optional[datetime] = None) -> str:
        """
        生成每日汇总的 Markdown 内容
        
        这是一个简单版本，后续会接入 LLM 进行智能处理
        """
        data = self.aggregate_daily_content(date)
        
        if not data["contents"]:
            return f"# 📅 {data['date'].strftime('%Y-%m-%d')} 工作日报\n\n暂无记录"
        
        lines = []
        lines.append(f"# 📅 {data['date'].strftime('%Y-%m-%d')} 工作日报")
        lines.append("")
        lines.append(f"> 共 {data['file_count']} 条记录，{data['total_words']} 字")
        lines.append("")
        
        # 摘要（简单版本：取前 200 字）
        lines.append("## 📝 今日摘要")
        all_content = " ".join([c["content"] for c in data["contents"]])
        summary = all_content[:200] + "..." if len(all_content) > 200 else all_content
        lines.append(f"> {summary}")
        lines.append("")
        
        # 详细记录
        lines.append("## 📋 详细记录")
        lines.append("")
        
        for item in data["contents"]:
            lines.append(f"### {item['time']} - {item['filename']}")
            lines.append("")
            lines.append(item["content"])
            lines.append("")
            lines.append("---")
            lines.append("")
        
        return "\n".join(lines)
    
    def generate_weekly_markdown(self, end_date: Optional[datetime] = None) -> str:
        """生成周报 Markdown"""
        if end_date is None:
            end_date = datetime.now()
        
        # 获取本周一到周日的数据
        start_date = end_date - timedelta(days=end_date.weekday())
        
        lines = []
        lines.append(f"# 📊 {start_date.strftime('%Y-%m-%d')} ~ {end_date.strftime('%Y-%m-%d')} 周报")
        lines.append("")
        
        total_files = 0
        total_words = 0
        daily_summaries = []
        
        for i in range(7):
            current_date = start_date + timedelta(days=i)
            if current_date > end_date:
                break
            
            data = self.aggregate_daily_content(current_date)
            total_files += data["file_count"]
            total_words += data["total_words"]
            
            if data["file_count"] > 0:
                daily_summaries.append({
                    "date": current_date,
                    "file_count": data["file_count"],
                    "words": data["total_words"]
                })
        
        lines.append(f"> 本周共 {total_files} 条记录，{total_words} 字")
        lines.append("")
        
        lines.append("## 📅 每日统计")
        for day in daily_summaries:
            lines.append(f"- **{day['date'].strftime('%m-%d %A')}**: {day['file_count']} 条记录, {day['words']} 字")
        
        lines.append("")
        
        return "\n".join(lines)
    
    def generate_monthly_markdown(self, date: Optional[datetime] = None) -> str:
        """生成月报 Markdown"""
        if date is None:
            date = datetime.now()
        
        # 获取本月第一天和最后一天
        first_day = date.replace(day=1)
        if date.month == 12:
            last_day = date.replace(year=date.year + 1, month=1, day=1) - timedelta(days=1)
        else:
            last_day = date.replace(month=date.month + 1, day=1) - timedelta(days=1)
        
        lines = []
        lines.append(f"# 📈 {date.strftime('%Y年%m月')} 月报")
        lines.append("")
        
        total_files = 0
        total_words = 0
        
        current = first_day
        while current <= min(last_day, date):
            data = self.aggregate_daily_content(current)
            total_files += data["file_count"]
            total_words += data["total_words"]
            current += timedelta(days=1)
        
        lines.append(f"> 本月共 {total_files} 条记录，{total_words} 字")
        lines.append("")
        
        return "\n".join(lines)


# 单例
_daily_summary_service = None

def get_daily_summary_service() -> DailySummaryService:
    """获取每日汇总服务单例"""
    global _daily_summary_service
    if _daily_summary_service is None:
        _daily_summary_service = DailySummaryService()
    return _daily_summary_service
