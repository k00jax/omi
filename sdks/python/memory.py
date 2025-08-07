"""
Memory storage module for Omi Python SDK
Handles creating memories via MCP API and local storage
"""

import os
import httpx
import asyncio
from datetime import datetime
from typing import Optional, Dict, Any
from dataclasses import dataclass


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


async def process_transcript_for_memory(transcript: str, metadata: Optional[Dict[str, Any]] = None) -> bool:
    """
    Process transcript for hot phrases and create memory if detected
    
    Args:
        transcript: The transcript to process
        metadata: Optional metadata to include with memory
        
    Returns:
        bool: True if memory was created, False otherwise
    """
    category = detect_hot_phrase(transcript)
    
    if category:
        print(f"🔥 Hot phrase detected! Category: {category}")
        return await create_memory(transcript, category, metadata)
    
    return False
