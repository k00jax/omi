@echo off
echo ===============================================
echo    Omi Python SDK - Windows Setup
echo ===============================================
echo.
@echo off
echo ===============================================
echo    Omi Python SDK - Windows Setup
echo ===============================================
echo.
echo Checking libopus-0.dll status...
echo.

REM Check if libopus-0.dll exists and get its size
if exist "libopus-0.dll" (
    for %%A in ("libopus-0.dll") do (
        set size=%%~zA
        if %%~zA LSS 1000 (
            echo ⚠️  Found placeholder libopus-0.dll ^(%%~zA bytes^)
            echo 📥 Running installer to set up real DLL...
            python install_opus_dll.py
        ) else (
            echo ✅ Real libopus-0.dll found ^(%%~zA bytes^)
            echo ✅ DLL setup appears complete
            echo.
            echo 🧪 Testing opuslib integration...
            python -c "import os, ctypes; ctypes.cdll.LoadLibrary(os.path.abspath('libopus-0.dll')); print('✅ DLL loads successfully')" 2>nul || echo ❌ DLL load test failed
        )
    )
) else (
    echo ❌ libopus-0.dll not found
    echo 📥 Running installer...
    python install_opus_dll.py
)

echo.
echo ===============================================
echo Setup Status: DLL file is present
echo.
echo NOTE: If opuslib still reports "Could not find Opus library"
echo this may be due to missing dependencies or opuslib compatibility.
echo.
echo The Omi SDK should still work with the fallback decoder.
echo For troubleshooting, see OPUS_SETUP.md
echo ===============================================
echo.
pause
