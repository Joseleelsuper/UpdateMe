from dataclasses import dataclass
from bson import ObjectId

@dataclass
class PMCard:
    _id: ObjectId
    payment_method_id: ObjectId
    card_holder_name: str
    billing_address: ObjectId
    last_four: str
    expiry_month: int
    expiry_year: int
    token: str
