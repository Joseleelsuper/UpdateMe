from dataclasses import dataclass
from bson import ObjectId

@dataclass
class PMPaypal:
    _id: ObjectId
    payment_method_id: ObjectId
    paypal_email: str
    paypal_customer_id: str
