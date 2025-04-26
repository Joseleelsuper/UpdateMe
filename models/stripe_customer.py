from dataclasses import dataclass
from typing import Optional
from bson import ObjectId

@dataclass
class StripeCustomer:
    """Model representing a customer in Stripe."""
    _id: ObjectId
    user_id: ObjectId
    stripe_customer_id: str
    stripe_subscription_id: Optional[str] = None
    default_payment_method: Optional[str] = None