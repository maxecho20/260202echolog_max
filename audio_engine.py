"""
EchoLog Audio Engine Module
===========================
Core audio capture and transcription engine using Deepgram WebSocket API.
"""

import asyncio
import json
import numpy as np
import sounddevice as sd
import websockets
from datetime import datetime
from typing import Callable, Optional
from config import AudioConfig, DeepgramConfig, OutputConfig


class TranscriptionEngine:
    """
    Real-time audio transcription engine.
    
    Captures audio from microphone and streams to Deepgram for transcription.
    Supports interim (in-progress) and final (confirmed) results.
    """
    
    def __init__(
        self,
        on_interim: Optional[Callable[[str], None]] = None,
        on_final: Optional[Callable[[str], None]] = None,
        on_error: Optional[Callable[[Exception], None]] = None,
        on_status_change: Optional[Callable[[str], None]] = None,
    ):
        """
        Initialize the transcription engine.
        
        Args:
            on_interim: Callback for interim (in-progress) transcription results
            on_final: Callback for final (confirmed) transcription results
            on_error: Callback for error handling
            on_status_change: Callback for status changes (idle, connecting, recording, etc.)
        """
        self._on_interim = on_interim or self._default_interim_handler
        self._on_final = on_final or self._default_final_handler
        self._on_error = on_error or self._default_error_handler
        self._on_status_change = on_status_change or (lambda s: None)
        
        self._is_running = False
        self._websocket = None  # websockets.ClientConnection
        self._audio_queue: asyncio.Queue = asyncio.Queue()
        self._tasks: list[asyncio.Task] = []
        
        # Output file handling
        self._output_file: Optional[str] = None
        
    @property
    def is_running(self) -> bool:
        """Check if the engine is currently running."""
        return self._is_running
    
    # ========================================
    # Default Handlers
    # ========================================
    
    def _default_interim_handler(self, text: str) -> None:
        """Default handler for interim results - print in gray."""
        print(f"\033[90m[interim] {text}\033[0m", end="\r")
    
    def _default_final_handler(self, text: str) -> None:
        """Default handler for final results - print and save."""
        timestamp = datetime.now().strftime(OutputConfig.CONTENT_TIME_FORMAT)
        if OutputConfig.INCLUDE_TIMESTAMPS:
            print(f"\033[92m[final]\033[0m {timestamp} {text}")
        else:
            print(f"\033[92m[final]\033[0m {text}")
        
        # Write to file
        self._write_to_file(text, timestamp)
    
    def _default_error_handler(self, error: Exception) -> None:
        """Default error handler."""
        print(f"\033[91m[error] {error}\033[0m")
    
    # ========================================
    # File Output
    # ========================================
    
    def _init_output_file(self) -> str:
        """Initialize a new output file for this session."""
        OutputConfig.ensure_output_dir()
        
        timestamp = datetime.now().strftime(OutputConfig.FILENAME_TIME_FORMAT)
        filename = f"{OutputConfig.FILE_PREFIX}_{timestamp}{OutputConfig.FILE_EXTENSION}"
        filepath = OutputConfig.OUTPUT_DIR / filename
        
        # Write header
        with open(filepath, "w", encoding="utf-8") as f:
            f.write(f"# EchoLog 听写记录\n")
            f.write(f"> 创建时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n")
            f.write("---\n\n")
        
        self._output_file = str(filepath)
        print(f"\033[94m[info] 输出文件: {filepath}\033[0m")
        return self._output_file
    
    def _write_to_file(self, text: str, timestamp: str) -> None:
        """Append text to the output file."""
        if not self._output_file:
            return
        
        try:
            with open(self._output_file, "a", encoding="utf-8") as f:
                if OutputConfig.INCLUDE_TIMESTAMPS:
                    f.write(f"{timestamp} {text}\n\n")
                else:
                    f.write(f"{text}\n\n")
        except Exception as e:
            self._on_error(e)
    
    # ========================================
    # Audio Capture
    # ========================================
    
    def _audio_callback(self, indata: np.ndarray, frames: int, time_info, status) -> None:
        """Callback for sounddevice audio stream."""
        if status:
            print(f"\033[93m[audio warning] {status}\033[0m")
        
        # Convert to bytes and put in queue
        audio_data = indata.copy().tobytes()
        
        try:
            self._audio_queue.put_nowait(audio_data)
        except asyncio.QueueFull:
            pass  # Drop frames if queue is full
    
    async def _capture_audio(self) -> None:
        """Capture audio from microphone and put into queue."""
        loop = asyncio.get_event_loop()
        
        with sd.InputStream(
            samplerate=AudioConfig.SAMPLE_RATE,
            channels=AudioConfig.CHANNELS,
            dtype=AudioConfig.DTYPE,
            blocksize=AudioConfig.BLOCK_SIZE,
            callback=self._audio_callback,
        ):
            print(f"\033[94m[info] 麦克风已启动 (采样率: {AudioConfig.SAMPLE_RATE}Hz)\033[0m")
            
            # Keep the stream running
            while self._is_running:
                await asyncio.sleep(0.1)
    
    # ========================================
    # WebSocket Communication
    # ========================================
    
    async def _send_audio(self) -> None:
        """Send audio data to Deepgram via WebSocket."""
        while self._is_running:
            try:
                # Get audio data from queue
                audio_data = await asyncio.wait_for(
                    self._audio_queue.get(), 
                    timeout=0.5
                )
                
                if self._websocket:
                    try:
                        await self._websocket.send(audio_data)
                    except websockets.ConnectionClosed:
                        break
                    
            except asyncio.TimeoutError:
                continue
            except Exception as e:
                if self._is_running:
                    self._on_error(e)
                break
    
    async def _receive_transcription(self) -> None:
        """Receive transcription results from Deepgram."""
        while self._is_running:
            try:
                if not self._websocket:
                    await asyncio.sleep(0.1)
                    continue
                
                message = await asyncio.wait_for(
                    self._websocket.recv(),
                    timeout=1.0
                )
                
                # Parse JSON response
                data = json.loads(message)
                
                # Extract transcription
                if "channel" in data:
                    channel = data["channel"]
                    alternatives = channel.get("alternatives", [])
                    
                    if alternatives:
                        transcript = alternatives[0].get("transcript", "")
                        is_final = data.get("is_final", False)
                        
                        if transcript.strip():
                            if is_final:
                                self._on_final(transcript)
                            else:
                                self._on_interim(transcript)
                
            except asyncio.TimeoutError:
                continue
            except websockets.ConnectionClosed:
                if self._is_running:
                    print("\033[93m[warning] WebSocket 连接已关闭\033[0m")
                break
            except Exception as e:
                if self._is_running:
                    self._on_error(e)
    
    async def _connect_websocket(self) -> bool:
        """Connect to Deepgram WebSocket API."""
        try:
            ws_url = DeepgramConfig.get_ws_url()
            headers = {
                "Authorization": f"Token {DeepgramConfig.API_KEY}"
            }
            
            print(f"\033[94m[info] 正在连接 Deepgram...\033[0m")
            
            self._websocket = await websockets.connect(
                ws_url,
                additional_headers=headers,
                ping_interval=20,
                ping_timeout=10,
            )
            
            print(f"\033[92m[success] Deepgram 连接成功!\033[0m")
            return True
            
        except Exception as e:
            self._on_error(Exception(f"连接失败: {e}"))
            return False
    
    async def _disconnect_websocket(self) -> None:
        """Disconnect from Deepgram WebSocket."""
        if self._websocket:
            try:
                # Send close message
                await self._websocket.send(json.dumps({"type": "CloseStream"}))
                await self._websocket.close()
            except Exception:
                pass
            finally:
                self._websocket = None
    
    # ========================================
    # Public Methods
    # ========================================
    
    async def start(self) -> bool:
        """
        Start the transcription engine.
        
        Returns:
            True if started successfully, False otherwise.
        """
        if self._is_running:
            print("\033[93m[warning] 引擎已在运行中\033[0m")
            return False
        
        self._on_status_change("connecting")
        
        # Initialize output file
        self._init_output_file()
        
        # Connect to Deepgram
        if not await self._connect_websocket():
            self._on_status_change("error")
            return False
        
        self._is_running = True
        self._on_status_change("recording")
        
        # Clear audio queue
        while not self._audio_queue.empty():
            try:
                self._audio_queue.get_nowait()
            except asyncio.QueueEmpty:
                break
        
        # Start tasks
        self._tasks = [
            asyncio.create_task(self._capture_audio()),
            asyncio.create_task(self._send_audio()),
            asyncio.create_task(self._receive_transcription()),
        ]
        
        print("\033[92m[success] 开始录音...\033[0m")
        print("-" * 50)
        
        return True
    
    async def stop(self) -> None:
        """Stop the transcription engine."""
        if not self._is_running:
            return
        
        print("\n" + "-" * 50)
        print("\033[94m[info] 正在停止...\033[0m")
        
        self._is_running = False
        self._on_status_change("stopping")
        
        # Cancel all tasks
        for task in self._tasks:
            task.cancel()
            try:
                await task
            except asyncio.CancelledError:
                pass
        
        self._tasks.clear()
        
        # Disconnect WebSocket
        await self._disconnect_websocket()
        
        self._on_status_change("idle")
        
        if self._output_file:
            print(f"\033[92m[success] 录音已保存至: {self._output_file}\033[0m")
    
    async def run_until_stopped(self) -> None:
        """Run the engine until manually stopped or interrupted."""
        await self.start()
        
        try:
            # Wait for all tasks to complete
            await asyncio.gather(*self._tasks, return_exceptions=True)
        except asyncio.CancelledError:
            pass
        finally:
            await self.stop()
