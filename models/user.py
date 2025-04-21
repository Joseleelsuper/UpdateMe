from dataclasses import dataclass, field
from typing import List, Optional, Literal
from datetime import datetime
from bson import ObjectId

@dataclass
class User:
    _id: ObjectId
    username: str   
    email: str
    created_at: datetime
    role: Literal["free", "paid", "admin"]
    email_verified: bool
    account_status: Literal["active", "suspended"]
    language: str = "es" 
    search_provider: Literal["serpapi", "tavily"] = "tavily"  # Proveedor de búsqueda web por defecto
    ai_provider: Literal["openai", "deepseek", "groq"] = "groq"  # Proveedor de IA por defecto
    password: Optional[str] = None
    billing_address: Optional[ObjectId] = None
    last_login: Optional[datetime] = None
    subscription: Optional[ObjectId] = None
    payment_methods: List[ObjectId] = field(default_factory=list)
    prompts: Optional[ObjectId] = None  # Reference to user's custom prompts
