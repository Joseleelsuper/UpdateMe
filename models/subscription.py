from dataclasses import dataclass
from typing import Literal
from datetime import datetime
from bson import ObjectId

@dataclass
class Subscription:
    _id: ObjectId
    status: Literal["active", "canceled"]
    start_date: datetime
    end_date: datetime
    renewal_date: datetime
    payment_method_id: ObjectId
    price: float
    interval: Literal["monthly", "yearly"]
