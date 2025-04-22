from dataclasses import dataclass
from typing import Literal
from datetime import datetime
from bson import ObjectId

@dataclass
class Transaction:
    _id: ObjectId
    user_id: ObjectId
    payment_method: ObjectId
    amount: float
    currency: str  # e.g., "usd", "eur"
    status: Literal["successful", "failed", "pending"]
    provider_transacction_id: str
    created_at: datetime
