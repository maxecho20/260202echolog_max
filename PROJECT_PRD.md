# 项目名称：EchoLog - 桌面智能听写助手 (Desktop AI Dictation MVP)

## 1. 项目背景与目标
**背景**：用户需要在办公环境（PC + 有线麦克风）下，进行长时间、全天候的语音记录。
**痛点**：现有的云端会议软件（如飞书）有额度限制，且无法导出实时流数据；传统录音笔需要二次导出，流程繁琐。
**目标**：开发一款基于 Python 的桌面端 MVP（最小可行性产品），利用 Deepgram API 实现高精度的实时语音转文字，并自动保存到本地 Markdown 文件中。

## 2. 核心功能 (MVP Scope)
1.  **实时听写**：点击“开始”后，实时捕获麦克风音频，通过 WebSocket 发送给 Deepgram，返回文字并显示在界面上。
2.  **即时上屏**：文字需要流式（Streaming）显示，区分“正在输入（Interim）”和“已确认（Final）”的状态。
3.  **自动归档**：
    - 每次启动或点击开始，自动生成一个新的 Markdown 文件（以时间戳命名）。
    - 所有的识别结果实时写入该文件，防止程序崩溃丢失数据。
4.  **极简 GUI**：
    - 一个“开始/停止”按钮。
    - 一个状态指示灯（录音中/空闲）。
    - 一个大的文本显示区域（Text Area）。

## 3. 技术栈规范 (Tech Stack)
- **编程语言**：Python 3.10+
- **GUI 框架**：Tkinter (利用 CustomTkinter 美化) 或 PySide6 (如 AI 推荐，优先选简单的 CustomTkinter)
- **核心逻辑库**：
    - `asyncio` (异步控制)
    - `websockets` (连接 Deepgram)
    - `sounddevice` (音频采集)
    - `numpy` (音频流处理)
- **API 服务**：Deepgram Nova-2 Model (Chinese)

## 4. 详细业务逻辑
### 4.1 音频流处理
- 采样率：16000 Hz
- 通道：1 (Mono)
- 格式：Linear16 (Int16)
- 传输方式：通过 WebSocket 实时推流。

### 4.2 文本处理逻辑
- 接收 Deepgram 返回的 JSON。
- **Interim 结果**：在 UI 上以灰色或斜体显示（表示正在修正）。
- **Final 结果**：
    1. 在 UI 上转为正文黑色显示，并换行。
    2. 立即追加写入（Append）到当前的本地 `.md` 文件中。
    3. 加上时间戳（可选，例如 `[10:05:23] 文本内容`）。

## 5. 交付物要求
- 完整的 Python 源代码（模块化结构）。
- `requirements.txt` 依赖列表。
- `.env` 文件模板（用于存放 API Key）。