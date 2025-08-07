# Opus DLL Setup for Windows

This directory contains scripts to automatically set up libopus-0.dll for Windows users.

## Quick Start (Windows Users)

### Option 1: Use the batch file
Double-click `install_opus_dll.bat` and follow the instructions.

### Option 2: Use Python directly
```cmd
python install_opus_dll.py
```

## What the script does

1. **Checks** if libopus-0.dll already exists
2. **Creates** a placeholder DLL file (for demonstration)
3. **Sets up** a fallback solution for when the real DLL isn't available
4. **Tests** opuslib functionality
5. **Provides** clear instructions for getting the real DLL

## Getting the Real libopus-0.dll

The script creates a placeholder, but for **full audio functionality**, you need the real DLL:

1. Go to https://github.com/xiph/opus/releases
2. Download a Windows build or search for "libopus-0.dll download"
3. Replace the placeholder `libopus-0.dll` with the real file

### Alternative sources:
- FFmpeg builds often include libopus-0.dll
- https://www.dll-files.com/libopus-0.dll.html
- Search online for "libopus 64-bit Windows DLL"

## Files Created

- `libopus-0.dll` - Placeholder (replace with real DLL)
- `opus_fallback.py` - Fallback decoder for when DLL isn't available

## Troubleshooting

If you get opuslib errors:
```cmd
pip install opuslib
```

If audio decoding doesn't work:
- Make sure you have the real libopus-0.dll (not the placeholder)
- Check that the DLL is in the same directory as your Python script

## Note for Developers

The fallback solution provides a `FallbackOpusDecoder` class that can be used when the real DLL isn't available, though it won't actually decode audio data.
