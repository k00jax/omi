# 🎧 Omi Python SDK - Complete System Overview

## 📁 Project Structure

```text
omi-python-sdk/
├── main.py                     # 🎯 Entry point: BLE + Deepgram + memory hook
├── memory.py                   # 🧠 Memory storage (MCP API + local fallback)
├── env_config.py               # ⚙️  Environment configuration loader
├── setup.py                    # 🚀 Complete setup wizard
├── test.py                     # 🧪 Test suite for all functionality
├── install_opus_dll.py         # 🔊 Windows Opus DLL installer
├── install_opus_dll.bat        # 📋 Windows batch helper
├── .env.example                # 📝 Environment template
├── .env                        # 🔐 User secrets (auto-created)
├── omi_memories.txt            # 💾 Local memory storage
├── requirements.txt            # 📦 Python dependencies
├── README.md                   # 📖 Main documentation
├── OPUS_SETUP.md              # 🔊 Opus DLL setup guide
├── libopus-0.dll              # 🎵 Native audio decoder (Windows)
├── opus_fallback.py           # 🔄 Fallback when DLL unavailable
└── omi/                       # 📂 Core SDK modules
    ├── bluetooth.py           #    🔵 BLE connection to Omi device
    ├── decoder.py            #    🎵 Opus audio packet decoding
    ├── transcribe.py         #    🎤 Deepgram WebSocket streaming
    └── ...
```

## 🔁 Complete Runtime Flow

```mermaid
graph TD
    A[Omi Wearable Device] -->|BLE Audio| B[omi.bluetooth]
    B --> C[omi.decoder - Opus]
    C -->|PCM Audio| D[omi.transcribe - Deepgram]
    D -->|Text Transcript| E[Hot Phrase Detection]
    E -->|"note this", "remember", etc.| F[memory.py]
    F -->|Try MCP API| G[Remote Storage]
    F -->|Fallback| H[Local omi_memories.txt]
    E -->|Console| I[Live Output]
```

## 🚀 Quick Start

### Option 1: Automated Setup
```bash
python setup.py    # Complete guided setup
python test.py     # Verify everything works
python main.py     # Start the system
```

### Option 2: Manual Setup
```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Windows only: Setup Opus DLL
python install_opus_dll.py

# 3. Configure environment
cp .env.example .env
# Edit .env with your API keys

# 4. Update MAC address in main.py
# 5. Run
python main.py
```

## 🧠 Memory System Features

### Hot Phrase Detection
| Phrase | Category | Action |
|--------|----------|--------|
| "note this" | note | Creates memory |
| "remember this" | note | Creates memory |
| "important" | important | Creates memory |
| "idea" | idea | Creates memory |
| "todo" | todo | Creates memory |
| "remind me" | reminder | Creates memory |

### Dual Storage Strategy
1. **Primary**: MCP API (with OMI_API_KEY)
2. **Fallback**: Local file (omi_memories.txt)
3. **Backup**: Both systems store data for reliability

## ⚙️ Configuration (.env)

```ini
# Required
DEEPGRAM_API_KEY=your_deepgram_key     # Speech-to-text

# Optional  
OMI_API_KEY=your_omi_key               # MCP memory storage
OMI_USER_ID=your_user_id               # User identification
MCP_BASE_URL=https://api.omi.com/mcp   # MCP endpoint
MEMORY_FILE=omi_memories.txt           # Local storage file
```

## 🛠️ System Components

### Core Modules
- **main.py**: Orchestrates everything, async event loop
- **memory.py**: Memory creation, MCP integration, hot phrase detection
- **env_config.py**: Environment variable management

### Omi SDK Modules
- **omi.bluetooth**: BLE device connection and data streaming
- **omi.decoder**: Opus audio packet decoding to PCM
- **omi.transcribe**: Real-time speech-to-text via Deepgram

### Utility Scripts
- **setup.py**: Complete setup wizard with validation
- **test.py**: Comprehensive test suite
- **install_opus_dll.py**: Windows audio codec setup

## 🔧 Windows-Specific Setup

Windows requires `libopus-0.dll` for audio decoding:

```bash
# Automated (recommended)
python install_opus_dll.py

# Manual
# 1. Download libopus-0.dll from https://github.com/xiph/opus/releases
# 2. Place in same directory as main.py
```

## 🧪 Testing & Validation

```bash
python test.py    # Full system test
```

Tests:
- ✅ Import validation
- ✅ Environment configuration  
- ✅ Memory system functionality
- ✅ Hot phrase detection
- ✅ Local storage fallback

## 📊 Memory Storage Format

### MCP API Payload
```json
{
  "text": "transcript content",
  "user_id": "user123",
  "text_source": "audio_transcript",
  "text_source_spec": "omi_sdk_note",
  "started_at": "2025-08-07T13:55:17.585284",
  "finished_at": "2025-08-07T13:55:17.585284"
}
```

### Local Storage Format
```text
--- Memory Entry ---
Timestamp: 2025-08-07T13:55:17.585284
Category: note
Text: Remember this important information
Metadata: {"location": {"lat": 40.7128, "lng": -74.0060}}
--- End Entry ---
```

## 🚨 Error Handling

The system gracefully handles:
- **Missing DLL**: Falls back to placeholder, provides instructions
- **No API Keys**: Uses local storage only
- **Network Issues**: Automatic fallback to local storage
- **BLE Disconnection**: Continues processing queued audio
- **Import Errors**: Clear error messages with solutions

## 🔮 Future Enhancements

- [ ] Voice activity detection (reduce noise)
- [ ] Custom hot phrase patterns via config
- [ ] Memory categorization via AI
- [ ] Real-time transcript editing
- [ ] Multiple device support
- [ ] Cloud sync for local memories
- [ ] Advanced metadata extraction (location, context)

## 🤝 Integration Points

### MCP (Model Context Protocol)
- Direct integration with Claude via MCP servers
- Structured memory storage with metadata
- Category-based organization
- Search and retrieval capabilities

### Local System
- File-based backup storage
- Offline operation capability
- Debug and audit trail
- Manual memory review

This system provides both real-time speech processing and long-term memory storage, enabling powerful AI assistance workflows.
