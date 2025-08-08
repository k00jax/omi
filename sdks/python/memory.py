"""
Memory storage module for Omi Python SDK
Handles creating memories via MCP API and local storage
"""

import os
import sys
import subprocess
import httpx
import asyncio
import logging
import numpy as np
import time
from datetime import datetime
from typing import Optional, Dict, Any, List, Callable
from dataclasses import dataclass

# Command execution cooldown tracking
_last_command_time = {}
COMMAND_COOLDOWN = 3.0  # 3 seconds between identical commands

# Import semantic matching dependencies
try:
    from sentence_transformers import SentenceTransformer
    from sklearn.metrics.pairwise import cosine_similarity
    SEMANTIC_MATCHING_AVAILABLE = True
    print("✅ Semantic intent matching available")
except ImportError as e:
    print(f"⚠️  Semantic matching not available: {e}")
    print("🔄 Falling back to string-based matching")
    SEMANTIC_MATCHING_AVAILABLE = False

# Set up logging for intent matching
logger = logging.getLogger(__name__)

# Initialize the sentence transformer model (only if available)
_model = None
_model_loading = False


@dataclass
class MemoryConfig:
    """Configuration for memory storage"""
    omi_api_key: str
    user_id: str = "default_user"
    mcp_base_url: str = "https://api.omi.com/mcp"  # Replace with actual MCP endpoint
    local_storage: bool = True
    memory_file: str = "omi_memories.txt"


class MemoryStorage:
    """Handles memory creation and storage via MCP API"""
    
    def __init__(self, config: MemoryConfig):
        self.config = config
        self.client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Authorization": f"Bearer {config.omi_api_key}",
                "Content-Type": "application/json"
            }
        )
    
    async def create_memory(self, transcript: str, category: str = "conversation", 
                           metadata: Optional[Dict[str, Any]] = None) -> bool:
        """
        Create a memory from transcript text
        
        Args:
            transcript: The transcribed text to store as memory
            category: Category/tag for the memory (e.g., "note", "conversation", "idea")
            metadata: Optional metadata (location, timestamp, etc.)
        
        Returns:
            bool: True if memory was created successfully
        """
        timestamp = datetime.now().isoformat()
        
        # Prepare memory data
        memory_data = {
            "text": transcript,
            "user_id": self.config.user_id,
            "text_source": "audio_transcript",
            "category": category,
            "created_at": timestamp,
            "metadata": metadata or {}
        }
        
        print(f"🧠 Creating memory: {transcript[:50]}...")
        
        # Try MCP API first
        mcp_success = await self._create_via_mcp(memory_data)
        
        # Fallback to local storage if MCP fails
        if not mcp_success and self.config.local_storage:
            print("⚠️  MCP failed, storing locally...")
            local_success = await self._store_locally(memory_data)
            return local_success
        
        return mcp_success
    
    async def _create_via_mcp(self, memory_data: Dict[str, Any]) -> bool:
        """Create memory via MCP API"""
        try:
            # Using the MCP memories endpoint structure
            mcp_payload = {
                "text": memory_data["text"],
                "user_id": memory_data["user_id"],
                "text_source": memory_data["text_source"],
                "text_source_spec": f"omi_sdk_{memory_data['category']}",
                "started_at": memory_data["created_at"],
                "finished_at": memory_data["created_at"]
            }
            
            # Add geolocation if available in metadata
            if "location" in memory_data.get("metadata", {}):
                location = memory_data["metadata"]["location"]
                if "latitude" in location and "longitude" in location:
                    mcp_payload["geolocation"] = {
                        "latitude": location["latitude"],
                        "longitude": location["longitude"]
                    }
            
            response = await self.client.post(
                f"{self.config.mcp_base_url}/create_omi_conversation",
                json=mcp_payload
            )
            
            if response.status_code == 200:
                result = response.json()
                print(f"✅ Memory created via MCP: ID {result.get('id', 'unknown')}")
                return True
            else:
                print(f"❌ MCP API error: {response.status_code} - {response.text}")
                return False
                
        except Exception as e:
            print(f"❌ MCP connection error: {e}")
            return False
    
    async def _store_locally(self, memory_data: Dict[str, Any]) -> bool:
        """Store memory locally as fallback"""
        try:
            memory_entry = (
                f"\n--- Memory Entry ---\n"
                f"Timestamp: {memory_data['created_at']}\n"
                f"Category: {memory_data['category']}\n"
                f"Text: {memory_data['text']}\n"
                f"Metadata: {memory_data['metadata']}\n"
                f"--- End Entry ---\n"
            )
            
            with open(self.config.memory_file, "a", encoding="utf-8") as f:
                f.write(memory_entry)
            
            print(f"💾 Memory stored locally in {self.config.memory_file}")
            return True
            
        except Exception as e:
            print(f"❌ Local storage error: {e}")
            return False
    
    async def close(self):
        """Clean up resources"""
        await self.client.aclose()


# Global memory storage instance
_memory_storage: Optional[MemoryStorage] = None


def init_memory_storage(omi_api_key: str, user_id: str = "default_user") -> MemoryStorage:
    """Initialize the global memory storage instance"""
    global _memory_storage
    
    config = MemoryConfig(
        omi_api_key=omi_api_key,
        user_id=user_id,
        mcp_base_url=os.getenv("MCP_BASE_URL", "https://api.omi.com/mcp"),
        local_storage=True,
        memory_file=os.getenv("MEMORY_FILE", "omi_memories.txt")
    )
    
    _memory_storage = MemoryStorage(config)
    return _memory_storage


async def create_memory(transcript: str, category: str = "note", 
                       metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    Convenience function to create a memory
    
    Args:
        transcript: The text to store as memory
        category: Memory category ("note", "idea", "conversation", etc.)
        metadata: Optional metadata dict
    
    Returns:
        bool: Success status
    """
    if _memory_storage is None:
        print("❌ Memory storage not initialized! Call init_memory_storage() first.")
        return False
    
    return await _memory_storage.create_memory(transcript, category, metadata)


async def cleanup_memory_storage():
    """Cleanup memory storage resources"""
    global _memory_storage
    if _memory_storage:
        await _memory_storage.close()
        _memory_storage = None


# Hot phrase patterns and their corresponding categories
HOT_PHRASES = {
    "note this": "note",
    "remember this": "note", 
    "important": "important",
    "idea": "idea",
    "todo": "todo",
    "remind me": "reminder",
    "save this": "note"
}

# Semantic intent command registry
INTENT_COMMANDS = {
    "open_notepad": {
        "examples": [
            "hey omi open notepad",
            "omi, start notepad",
            "open notes",
            "launch notepad now",
            "can you open notepad",
            "hey omi launch notepad",
            "open the notepad application",
            "start up notepad for me"
        ],
        "action": lambda: _execute_system_command(["notepad.exe"], "Opening Notepad..."),
        "description": "Open Windows Notepad",
        "embeddings": None  # Will be computed when model loads
    },
    # Add more intents here as needed
    # "open_calculator": {
    #     "examples": [
    #         "hey omi open calculator",
    #         "omi, start calc",
    #         "open the calculator",
    #         "launch calculator app"
    #     ],
    #     "action": lambda: _execute_system_command(["calc.exe"], "Opening Calculator..."),
    #     "description": "Open Windows Calculator",
    #     "embeddings": None
    # },
}


def _get_model():
    """Lazy load the sentence transformer model"""
    global _model, _model_loading
    
    if not SEMANTIC_MATCHING_AVAILABLE:
        return None
        
    if _model is not None:
        return _model
        
    if _model_loading:
        return None
        
    try:
        _model_loading = True
        print("🤖 Loading semantic intent model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")  # ~100MB, fast and accurate
        
        # Precompute embeddings for all command examples
        _precompute_embeddings()
        
        print("✅ Semantic intent model loaded successfully")
        return _model
    except Exception as e:
        print(f"❌ Failed to load semantic model: {e}")
        return None
    finally:
        _model_loading = False


def _precompute_embeddings():
    """Precompute embeddings for all command examples"""
    global _model
    if _model is None:
        return
        
    try:
        for intent_name, intent_data in INTENT_COMMANDS.items():
            if intent_data["embeddings"] is None:
                logger.debug(f"Computing embeddings for intent: {intent_name}")
                intent_data["embeddings"] = _model.encode(intent_data["examples"])
                print(f"🧠 Computed embeddings for '{intent_name}' ({len(intent_data['examples'])} examples)")
    except Exception as e:
        print(f"❌ Error precomputing embeddings: {e}")


def match_semantic_intent(transcript: str, threshold: float = 0.8) -> Optional[str]:
    """
    Match transcript to semantic intents using embedding similarity
    
    Args:
        transcript: The transcript text to match
        threshold: Minimum similarity score (0.0-1.0) to trigger intent
        
    Returns:
        Optional[str]: Intent name if match found above threshold, None otherwise
    """
    model = _get_model()
    if model is None:
        return None
        
    try:
        # Encode the input transcript
        input_embedding = model.encode([transcript])
        
        best_match = None
        best_score = 0.0
        
        # Compare against all intents
        for intent_name, intent_data in INTENT_COMMANDS.items():
            if intent_data["embeddings"] is None:
                continue
                
            # Calculate cosine similarity with all examples
            similarities = cosine_similarity(input_embedding, intent_data["embeddings"])
            max_similarity = similarities.max()
            
            logger.debug(f"Intent '{intent_name}': max similarity = {max_similarity:.3f}")
            
            if max_similarity > best_score:
                best_score = max_similarity
                best_match = intent_name
        
        # Check if best match exceeds threshold
        if best_score >= threshold:
            print(f"🎯 Semantic intent matched: '{best_match}' (confidence: {best_score:.3f})")
            return best_match
        elif best_score >= 0.7:  # Close match - provide feedback
            print(f"🤔 Close match: '{best_match}' (confidence: {best_score:.3f}) - did you mean to trigger this?")
            
        return None
        
    except Exception as e:
        logger.error(f"Error in semantic intent matching: {e}")
        return None


def _execute_system_command(command_list: list, description: str) -> bool:
    """
    Execute a system command safely with error handling and cooldown
    
    Args:
        command_list: List of command and arguments to execute
        description: User-friendly description of what's being executed
        
    Returns:
        bool: True if command executed successfully, False otherwise
    """
    global _last_command_time
    
    # Check cooldown to prevent rapid duplicate executions
    command_key = " ".join(command_list)
    current_time = time.time()
    
    if command_key in _last_command_time:
        time_since_last = current_time - _last_command_time[command_key]
        if time_since_last < COMMAND_COOLDOWN:
            print(f"⏳ Command '{description}' on cooldown ({COMMAND_COOLDOWN - time_since_last:.1f}s remaining)")
            return False
    
    try:
        # Only run on Windows for now
        if sys.platform != "win32":
            print(f"⚠️  Command '{description}' is currently Windows-only")
            return False
            
        print(f"🚀 {description}")
        subprocess.Popen(command_list, shell=False)
        _last_command_time[command_key] = current_time
        return True
    except FileNotFoundError:
        print(f"❌ Command not found: {command_list[0]}")
        return False
    except Exception as e:
        print(f"❌ Error executing command '{description}': {e}")
        return False


def detect_hot_command(transcript: str) -> Optional[str]:
    """
    Detect hot commands using semantic intent matching or fallback string matching
    
    Args:
        transcript: The transcript text to analyze
        
    Returns:
        Optional[str]: Command description if executed, None otherwise
    """
    transcript_lower = transcript.lower().strip()
    print(f"🔍 Checking hot command for: '{transcript_lower}'")  # Debug
    
    # First try semantic intent matching if available
    if SEMANTIC_MATCHING_AVAILABLE:
        print("🤖 Trying semantic intent matching...")  # Debug
        intent_name = match_semantic_intent(transcript)
        if intent_name and intent_name in INTENT_COMMANDS:
            intent_data = INTENT_COMMANDS[intent_name]
            try:
                success = intent_data["action"]()
                if success:
                    return f"Executed: {intent_data['description']}"
            except Exception as e:
                logger.error(f"Error executing intent '{intent_name}': {e}")
                return None
    else:
        print("⚠️  Semantic matching not available, using string matching")  # Debug
    
    # Enhanced fallback string matching with better pattern recognition
    # Look for "omi" variations (hey omi, oh me, army, o m i, etc.)
    omi_triggers = ["hey omi", "oh me", "omi", "army", "o m i", "hey army", "on me", "only"]
    has_trigger = any(trigger in transcript_lower for trigger in omi_triggers)
    print(f"🔍 Checking triggers {omi_triggers} in '{transcript_lower}': {has_trigger}")  # Debug
    
    if not has_trigger:
        print("❌ No omi trigger found")  # Debug
        return None
    
    # Enhanced notepad detection patterns
    notepad_patterns = [
        "open notepad", "notepad", "open notes", "launch notepad", 
        "start notepad", "open the notepad", "notepad please"
    ]
    
    # Look for notepad command
    for pattern in notepad_patterns:
        if pattern in transcript_lower:
            print(f"✅ Found notepad pattern: '{pattern}'")  # Debug
            success = _execute_system_command(["notepad.exe"], "Opening Notepad...")
            if success:
                return f"Executed: open notepad"
    
    print("❌ No notepad patterns found")  # Debug
    return None


def detect_hot_phrase(transcript: str) -> Optional[str]:
    """
    Detect hot phrases in transcript and return appropriate category
    
    Args:
        transcript: The transcript text to analyze
        
    Returns:
        Optional[str]: Category if hot phrase detected, None otherwise
    """
    transcript_lower = transcript.lower()
    
    for phrase, category in HOT_PHRASES.items():
        if phrase in transcript_lower:
            return category
    
    return None


async def process_transcript_for_memory(transcript: str, metadata: Optional[Dict[str, Any]] = None) -> tuple[bool, Optional[str]]:
    """
    Process transcript for hot phrases and commands
    
    Args:
        transcript: The transcript to process
        metadata: Optional metadata to include with memory
        
    Returns:
        tuple[bool, Optional[str]]: (True if memory was created or command executed, category/command if detected)
    """
    # Check for hot commands first (like "hey omi... open notepad")
    command_result = detect_hot_command(transcript)
    if command_result:
        print(f"🎯 Hot command executed: {command_result}")
        return True, f"command: {command_result}"
    
    # Check for memory-creating hot phrases
    category = detect_hot_phrase(transcript)
    if category:
        print(f"🔥 Hot phrase detected! Category: {category}")
        success = await create_memory(transcript, category, metadata)
        return success, category
    
    return False, None
