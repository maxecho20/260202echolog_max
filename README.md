# 🎙️ EchoLog - 桌面智能听写助手

> Desktop AI Dictation MVP - 基于 Deepgram API 的实时语音转文字工具

## ✨ 功能特性

- **实时听写**：捕获麦克风音频，通过 WebSocket 连接 Deepgram 实时转写
- **即时上屏**：流式显示识别结果，区分"正在输入"和"已确认"状态
- **自动归档**：识别结果实时写入 Markdown 文件，防止数据丢失
- **历史管理**：支持导入 MD/TXT 文件，删除历史记录
- **跨平台支持**：提供 Windows 和 macOS 两个版本
- **极简 GUI**：CustomTkinter 构建的现代化界面

## �️ 平台支持

### Windows 版本
- 使用 Microsoft YaHei 字体
- 支持 `os.startfile()` 打开文件
- 启动脚本: `platforms/windows/run_echolog.bat`

### macOS 版本
- 使用 PingFang SC 字体
- 自动请求麦克风权限
- 使用 `subprocess.run(["open", ...])` 打开文件
- 启动脚本: `platforms/macos/run_echolog.sh`

## �🛠️ 技术栈

- Python 3.10+
- CustomTkinter (GUI)
- websockets (WebSocket 连接)
- sounddevice (音频采集)
- numpy (音频处理)
- Deepgram Nova-2 Model (中文语音识别)

## 📦 安装

### Windows

```bash
# 1. 创建并激活虚拟环境
python -m venv venv
.\venv\Scripts\activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
copy .env.example .env
# 编辑 .env 文件，填入你的 Deepgram API Key
```

### macOS

```bash
# 1. 创建并激活虚拟环境
python3 -m venv venv
source venv/bin/activate

# 2. 安装依赖
pip install -r requirements.txt

# 3. 配置环境变量
cp .env.example .env
# 编辑 .env 文件，填入你的 Deepgram API Key

# 4. 首次运行时，系统会提示授权麦克风权限
# 请在「系统偏好设置」→「隐私与安全性」→「麦克风」中授权
```

## ⚙️ 配置

编辑 `.env` 文件：

```env
DEEPGRAM_API_KEY=your_deepgram_api_key_here
ENVIRONMENT=dev
```

获取 API Key：[Deepgram Console](https://console.deepgram.com/)

## 🚀 运行

### Windows
```bash
# 方式一：直接运行
python main_gui.py

# 方式二：使用启动脚本
platforms\windows\run_echolog.bat
```

### macOS
```bash
# 方式一：直接运行
python platforms/macos/main_gui_macos.py

# 方式二：使用启动脚本
chmod +x platforms/macos/run_echolog.sh
./platforms/macos/run_echolog.sh
```

## 📁 项目结构

```
echolog/
├── main_gui.py           # Windows 主程序入口
├── audio_engine.py       # 音频引擎
├── config.py             # 配置管理
├── requirements.txt      # 依赖列表
├── .env                  # 环境变量（不提交）
├── .env.example          # 环境变量模板
├── output/               # 输出的 Markdown 文件
├── platforms/
│   ├── windows/          # Windows 专用文件
│   │   ├── main_gui_windows.py
│   │   └── run_echolog.bat
│   └── macos/            # macOS 专用文件
│       ├── main_gui_macos.py
│       └── run_echolog.sh
└── PROJECT_PRD.md        # 产品需求文档
```

## 🔧 macOS 权限说明

在 macOS 上首次运行时，需要授予麦克风权限：

1. 打开「系统偏好设置」
2. 选择「隐私与安全性」
3. 选择「麦克风」
4. 勾选 Python 或终端应用
5. 重新启动应用程序

## 📄 License

MIT License
