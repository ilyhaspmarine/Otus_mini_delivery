from pydantic import BaseModel, Field
from decimal import Decimal
from uuid import UUID
from datetime import datetime
from typing import Optional

class ID(BaseModel):
    id: UUID

# _________________________________________________________

class CourierBase(BaseModel):
    first_name: str
    last_name: str  
    phone: str = Field(..., min_length=12, max_length=12)

class CourierCreate(CourierBase):
    pass

class CourierReturn(ID, CourierBase):
    pass
    class Config:
        from_attributes = True

# _________________________________________________________


class DeliveryBase(BaseModel):
    order_id: UUID
    address: str

class DeliveryCreate(DeliveryBase):
    pass

class DeliveryReturn(ID, DeliveryBase):
    courier_id: UUID
    courier_name: str
    status: str
    created_at: datetime
    last_changed: datetime
    class Config:
        from_attributes = True