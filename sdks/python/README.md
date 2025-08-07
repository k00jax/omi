<!-- This file is auto-generated from docs/doc/developer/sdk/python.md# Get a free API key from https://deepgram.com, then:
# Option 1: Set environment variable
export DEEPGRAM_API_KEY=your_actual_deepgram_key

# Option 2: Add to .env file (recommended)
echo "DEEPGRAM_API_KEY=your_actual_deepgram_key" >> .env

6. Find Omi's MAC Addresso not edit manually. -->
# 🎧 Omi Python SDK 

This SDK connects to an **Omi wearable device** over **Bluetooth**, decodes the **Opus-encoded audio**, and transcribes it in **real time using Deepgram**.


## 🚀 Quick Start

### 1. Clone the repo

```bash
git clone https://github.com/BasedHardware/omi.git
cd sdks/python

### 2. Set up Python environment
python3 -m venv venv
source venv/bin/activate


### 3. Install dependencies
```bash
pip install -r requirements.txt
```

### 📦 Windows Setup (Required for Windows users)
**Windows users need to install `libopus-0.dll` for audio decoding:**

```cmd
python install_opus_dll.py
```

Or simply double-click `install_opus_dll.bat`

This will:
- Download the required `libopus-0.dll` library
- Place it in the current directory
- Verify that opuslib can successfully load it

### 🧠 4. Memory Integration Setup (Optional)
**Set up automatic memory creation from speech:**

The SDK can automatically detect "hot phrases" in your speech and create memories via the MCP (Model Context Protocol) API.

1. **Copy environment template:**
```bash
copy .env.example .env
```

2. **Edit `.env` file with your API keys:**
```ini
# Required for speech-to-text
DEEPGRAM_API_KEY=your_deepgram_api_key

# Optional for MCP memory storage
OMI_API_KEY=your_omi_api_key
OMI_USER_ID=your_user_id
```

3. **Hot phrases that trigger memory creation:**
   - "note this" → Creates a note
   - "remember this" → Creates a note
   - "important" → Creates important memory
   - "idea" → Creates idea memory
   - "todo" → Creates todo memory

**Without OMI_API_KEY:** Memories are stored locally in `omi_memories.txt`
**With OMI_API_KEY:** Memories are sent to MCP API and also stored locally as backup

### ⚙️ 5. Configuration Set your Deepgram API key

# Get a free API key from https://deepgram.com, then run:
export DEEPGRAM_API_KEY=your_actual_deepgram_key

5. Find Omi’s MAC Address
To connect to your specific Omi device, you need its Bluetooth MAC address.

🔍 Scan for Nearby Bluetooth Devices
Run this command:
python -c "from omi.bluetooth import print_devices; print_devices()"
Look for a device named Omi, like this:

0. Omi [7F52EC55-50C9-D1B9-E8D7-19B83217C97D]
Copy the MAC address inside the brackets and paste it into main.py:

python
Copy code
OMI_MAC = "7F52EC55-50C9-D1B9-E8D7-19B83217C97D"


### 6. Confirm Omi Audio Characteristic (Optional)
You can verify the audio characteristic UUID by running:

python omi/discover_characteristics.py
You should see something like:


Characteristic UUID: 19B10001-E8F2-537E-4F6C-D104768A1214
This UUID is already used in the code by default.

### 🎯 Quick Setup (All-in-One)
**Run the automated setup wizard:**
```bash
python setup.py
```
This will check all requirements, setup your environment, and guide you through configuration.

🏃 Run the SDK
Once configured, start the main script:
python main.py
✅ You should see:
Connected to Deepgram WebSocket
Connected to [Omi MAC Address]
DATA FROM OMI: ...
Transcript: hello world


### 🧩 Troubleshooting
✅ Make sure Omi is powered on and near your computer

✅ You must be using Python 3.10+

✅ If you see extra_headers error from websockets, fix it with:


pip install websockets==11.0.3


### 🪪 License
MIT License — this is an unofficial SDK built by the community, not affiliated with Omi.

### 🙌 Credits
Built by [Your Name] using Omi hardware and Deepgram’s transcription engine.
