from sqlalchemy import Column, String, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import relationship
import uuid
from datetime import datetime
from enum import Enum


Base = declarative_base()

class DeliveryStatus(str, Enum):
    PLANNED = "planned"
    ONGOING = "ongoing"
    CANCELLED = "cancelled"
    DELIVERED = "delivered"


class Courier(Base):
    __tablename__ = 'couriers'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    first_name = Column(String(100), nullable=False)

    last_name = Column(String(100), nullable=False)

    phone = Column(String(12), nullable=False, unique=True, index=True)


class Delivery(Base):
    __tablename__ = 'deliveries'

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, nullable=False)

    courier_id = Column(UUID(as_uuid=True), ForeignKey('couriers.id'), index=True, nullable=False)

    order_id = Column(UUID(as_uuid=True), unique=True, index= True, nullable=False)

    address = Column(String(250), nullable=False)

    status = Column(SQLEnum(DeliveryStatus), nullable=False, default=DeliveryStatus.PLANNED)

    created_at = Column(DateTime, nullable=False, default=datetime.utcnow)

    last_changed = Column(DateTime, nullable=False, default=datetime.utcnow)