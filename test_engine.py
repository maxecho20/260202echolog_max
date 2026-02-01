"""
EchoLog Audio Engine Test Script
================================
Run this script to test the transcription engine.
Press Ctrl+C to stop recording.
"""

import asyncio
import signal
import sys
from audio_engine import TranscriptionEngine
from config import DeepgramConfig, validate_config


async def main():
    """Main test function."""
    
    print("=" * 60)
    print("  EchoLog 音频引擎测试")
    print("=" * 60)
    print()
    
    # Validate configuration
    print("[检查配置...]")
    if not DeepgramConfig.API_KEY or DeepgramConfig.API_KEY == "your_deepgram_api_key_here":
        print("\033[91m错误: 请先在 .env 文件中设置 DEEPGRAM_API_KEY\033[0m")
        print("获取 API Key: https://console.deepgram.com/")
        sys.exit(1)
    
    print(f"  ✓ API Key 已配置")
    print(f"  ✓ 模型: {DeepgramConfig.MODEL}")
    print(f"  ✓ 语言: {DeepgramConfig.LANGUAGE}")
    print()
    
    # Create engine instance
    engine = TranscriptionEngine()
    
    # Handle Ctrl+C gracefully
    stop_event = asyncio.Event()
    
    def signal_handler():
        print("\n\033[93m[接收到停止信号...]\033[0m")
        stop_event.set()
    
    # Set up signal handler for Windows compatibility
    if sys.platform == "win32":
        # Windows needs special handling
        loop = asyncio.get_event_loop()
        
        def win_handler(sig, frame):
            loop.call_soon_threadsafe(stop_event.set)
        
        signal.signal(signal.SIGINT, win_handler)
    else:
        loop = asyncio.get_event_loop()
        loop.add_signal_handler(signal.SIGINT, signal_handler)
    
    print("按 Ctrl+C 停止录音")
    print("-" * 60)
    print()
    
    # Start engine
    success = await engine.start()
    
    if not success:
        print("\033[91m启动失败!\033[0m")
        sys.exit(1)
    
    # Wait for stop signal
    try:
        await stop_event.wait()
    except KeyboardInterrupt:
        pass
    
    # Stop engine
    await engine.stop()
    
    print()
    print("=" * 60)
    print("  测试结束")
    print("=" * 60)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n程序已退出")
