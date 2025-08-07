"""
Environment configuration loader for Omi Python SDK
"""

import os
from pathlib import Path


def load_env_file(env_path: str = ".env") -> bool:
    """
    Load environment variables from a .env file
    
    Args:
        env_path: Path to the .env file
        
    Returns:
        bool: True if file was loaded successfully
    """
    env_file = Path(env_path)
    
    if not env_file.exists():
        print(f"⚠️  Environment file {env_path} not found")
        return False
    
    try:
        with open(env_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                
                # Skip empty lines and comments
                if not line or line.startswith('#'):
                    continue
                
                # Parse KEY=VALUE format
                if '=' in line:
                    key, value = line.split('=', 1)
                    key = key.strip()
                    value = value.strip()
                    
                    # Remove quotes if present
                    if value.startswith('"') and value.endswith('"'):
                        value = value[1:-1]
                    elif value.startswith("'") and value.endswith("'"):
                        value = value[1:-1]
                    
                    # Only set if not already in environment
                    if key and not os.getenv(key):
                        os.environ[key] = value
        
        print(f"✅ Loaded environment from {env_path}")
        return True
        
    except Exception as e:
        print(f"❌ Error loading {env_path}: {e}")
        return False


def check_required_env_vars() -> bool:
    """
    Check if all required environment variables are set
    
    Returns:
        bool: True if all required vars are present
    """
    required_vars = ["DEEPGRAM_API_KEY"]
    optional_vars = ["OMI_API_KEY", "OMI_USER_ID", "MCP_BASE_URL", "MEMORY_FILE"]
    
    missing_required = []
    missing_optional = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_required.append(var)
    
    for var in optional_vars:
        if not os.getenv(var):
            missing_optional.append(var)
    
    if missing_required:
        print("❌ Missing required environment variables:")
        for var in missing_required:
            print(f"   - {var}")
        return False
    
    if missing_optional:
        print("⚠️  Optional environment variables not set:")
        for var in missing_optional:
            print(f"   - {var} (will use defaults)")
    
    print("✅ Environment configuration OK")
    return True


def setup_environment() -> bool:
    """
    Complete environment setup - load .env and validate
    
    Returns:
        bool: True if setup successful
    """
    # Try to load .env file
    load_env_file()
    
    # Check configuration
    return check_required_env_vars()
