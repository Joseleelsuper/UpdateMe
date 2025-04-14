from dataclasses import dataclass
from bson import ObjectId

@dataclass
class BillingAddress:
    _id: ObjectId
    billing_address: str
