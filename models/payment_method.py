from dataclasses import dataclass
from typing import Literal
from bson import ObjectId

@dataclass
class PaymentMethod:
    _id: ObjectId
    user_id: ObjectId
    payment_type: Literal["credit_card", "debit_card", "paypal"]
    is_default: bool
    provider: str  # e.g., "visa", "mastercard", "paypal", etc.
