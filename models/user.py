from dataclasses import dataclass, field
from typing import List, Optional, Literal
from datetime import datetime
from bson import ObjectId

@dataclass
class User:
    _id: ObjectId
    username: str
    email: str
    password: str  # hashed
    created_at: datetime
    role: Literal["free", "paid", "admin"]
    email_verified: bool
    account_status: Literal["active", "suspended"]
    billing_address: Optional[ObjectId]
    last_login: Optional[datetime]
    subscription: Optional[ObjectId]
    payment_methods: List[ObjectId] = field(default_factory=list)
