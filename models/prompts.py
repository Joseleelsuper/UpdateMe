from dataclasses import dataclass
from typing import Optional, Dict, Any
from bson import ObjectId

@dataclass
class Prompts:
    _id: ObjectId
    openai_prompt: Optional[str] = None
    groq_prompt: Optional[str] = None
    deepseek_prompt: Optional[str] = None
    tavily_prompt: Optional[str] = None 
    serpapi_prompt: Optional[str] = None
    tavily_config: Optional[Dict[str, Any]] = None
    serpapi_config: Optional[Dict[str, Any]] = None