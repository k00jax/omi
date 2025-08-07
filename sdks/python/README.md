# 🎧 Omi Python SDK

**Real-time speech processing with live transcript display and memory creation**

## ✨ New: Real-time Transcript UI

The SDK now includes a **native desktop window** that displays live transcriptions from your Omi device!

### 🖥️ UI Features

- **📝 Live Transcripts** - See your speech transcribed in real-time
- **🧠 Memory Notifications** - Visual alerts when memories are created  
- **📊 Status Display** - Connection status and memory count
- **🎨 Dark Theme** - Easy-on-the-eyes dark interface
- **💾 Save Transcripts** - Export transcription sessions to text files
- **🔍 Font Controls** - Adjustable text size (A+ / A-)
- **🗑️ Clear Function** - Reset the transcript display

### 🚀 Quick Start with UI

1. **Install and setup** (follow the main installation steps)
2. **Run with UI:**
   ```bash
   python main.py
   ```
   This automatically opens the transcript window alongside the audio processing!

3. **Demo the UI:**
   ```bash
   python demo_ui.py
   ```
   See the transcript window in action with sample data.

4. **Showcase the UI:**
   ```bash
   python showcase_ui.py
   ```
   Simple demonstration of the transcript window features.

### 📱 UI Screenshots

The transcript window shows:
- **Timestamps** for each transcription
- **Live text** as you speak to your Omi device  
- **Memory alerts** when hot phrases are detected
- **Status updates** showing connection state

## 🏗️ Core Features  

- 🔵 **Bluetooth LE Connection** - Seamless connection to Omi wearable devices
- 🎵 **Real-time Audio Processing** - Opus codec decoding with fallback support  
- 🎤 **Live Speech Transcription** - Powered by Deepgram's WebSocket API
- 🖥️ **Real-time Transcript UI** - Native desktop window showing live transcriptions
- 🧠 **Intelligent Memory Creation** - Automatic detection of important phrases
- 💾 **Dual Storage System** - Cloud MCP API + local file backup
- 🔄 **Robust Error Handling** - Graceful fallbacks and recovery mechanisms
- 🚀 **Easy Setup** - Automated installation and configuration

## 🧠 Memory System

The system automatically detects "hot phrases" and creates memories:

| Phrase | Memory Type | Example |
|--------|-------------|---------|
| "note this", "remember this" | 📝 Note | "Note this meeting location" |
| "important", "crucial" | ⚡ Important | "This is important for the project" |
| "idea", "what if" | 💡 Idea | "I have an idea about the design" |
| "todo", "need to" | ✅ Todo | "Add this to my todo list" |

## 📋 Commands

| Command | Description |
|---------|-------------|
| `python main.py` | Start with real-time transcript UI |
| `python demo_ui.py` | Demo the transcript window (async) |
| `python showcase_ui.py` | Simple UI showcase (sync) |
| `python test.py` | Run system tests |
| `python setup.py` | Interactive setup wizard |

## 🔧 Installation

```bash
# Clone the repository
git clone https://github.com/BasedHardware/omi.git
cd omi/sdks/python

# Create virtual environment
python -m venv venv
venv\Scripts\activate  # Windows
# source venv/bin/activate  # macOS/Linux

# Install dependencies
pip install -r requirements.txt

# Windows: Install audio DLL
python install_opus_dll.py

# Setup configuration
python setup.py
```

## 🎯 Usage

1. **Configure your device MAC** in `.env` or `main.py`
2. **Add your Deepgram API key** to `.env`
3. **Run the system:**
   ```bash
   python main.py
   ```

The transcript window will open automatically and show:
- ✅ Real-time transcriptions as you speak
- 🧠 Memory creation notifications  
- 📊 Connection status and statistics

## 🐛 Troubleshooting

- **UI not showing?** Make sure tkinter is installed (`pip install tkinter` may be needed on some systems)
- **Connection issues?** Check your Omi device MAC address in the configuration
- **Audio problems?** Run `python install_opus_dll.py` on Windows

---

**Built with ❤️ for the Omi community**
