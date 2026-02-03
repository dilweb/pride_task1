from decimal import Decimal
from pydantic import BaseModel, Field
from uuid import UUID
from typing import Literal
from datetime import datetime

class OrderItem(BaseModel):
    product_id: int
    name: str
    price: Decimal = Field(..., gt=0)
    quantity: int = Field(..., gt=0)

class OrderCreate(BaseModel):
    user_id: int
    items: list[OrderItem]
    amount: Decimal = Field(..., gt=0)

class OrderPayload(OrderCreate):
    created_at: datetime
    currency: Literal["USD", "KZT", "UAH", "RUB"]
    total: Decimal = Field(..., gt=0)

class OrderEvent(BaseModel):
    event_type: Literal["order.created"]
    order_id: UUID
    saga_id: UUID
    message_id: UUID
    payload: OrderPayload

class OrderAccepted(BaseModel):
    order_id: UUID
    saga_id: UUID
    message_id: UUID
    status: Literal["accepted"] = "accepted"
