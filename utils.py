from models import CourierCreate, CourierReturn, DeliveryCreate, DeliveryReturn
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import exists, select, func, or_
from sqlalchemy.dialects.postgresql import insert
import uuid
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import selectinload
from fastapi import HTTPException, status
from config import settings
from db_schema import Courier as CourierSchema, Delivery as DeliverySchema, DeliveryStatus


async def create_new_courier(
    courier_data: CourierCreate,
    db: AsyncSession
):
    new_courier = CourierSchema(
        id = uuid.uuid4(),
        first_name = courier_data.first_name,
        last_name = courier_data.last_name,
        phone = courier_data.phone
    )
    
    db.add(new_courier)

    try:
        await db.commit()
    except IntegrityError:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Failed to create new courier')
    
    return new_courier


async def get_courier_by_courier_id(
    courier_id: uuid.UUID,
    db: AsyncSession
):
    
    print(courier_id)

    result = await db.execute(
        select(CourierSchema)
        .filter(CourierSchema.id == courier_id)
    )
    courier = result.scalar_one_or_none()

    if courier is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'No courier found'
        )
    
    return courier


async def create_new_delivery(
    delivery_data: DeliveryCreate,
    db: AsyncSession
):
    # Ищем первого попавшегося курьера свободного
    result = await db.execute(
        select(CourierSchema)
        .where(
            ~exists().where(
                (DeliverySchema.courier_id == CourierSchema.id)
                &
                (
                    or_(
                        DeliverySchema.status == DeliveryStatus.ONGOING,
                        DeliverySchema.status == DeliveryStatus.PLANNED
                    )
                )
            )
        )
        .order_by(CourierSchema.id)
        .limit(1)
        .with_for_update()
    )

    courier = result.scalar_one_or_none()

    if courier is None:
        raise HTTPException(
            status_code = status.HTTP_406_NOT_ACCEPTABLE,
            detail = 'All couriers are busy'
        )
    
    now = datetime.utcnow()

    delivery_new = DeliverySchema(
        id = uuid.uuid4(),
        courier_id = courier.id,
        order_id = delivery_data.order_id,
        address = delivery_data.address,
        status = DeliveryStatus.PLANNED,
        created_at = now,
        last_changed = now
    )

    db.add(delivery_new)

    try:
        await db.commit()
        await db.refresh(delivery_new)
    except IntegrityError:
        raise HTTPException(status_code = status.HTTP_400_BAD_REQUEST, detail = 'Failed to create new delivery')
    
    ret = await build_delivery_return(delivery_new, db)

    return ret


async def get_delivery_by_order_id(
    order_id: uuid.UUID,
    db: AsyncSession
):
    result = await db.execute(
        select(DeliverySchema)
        .filter(DeliverySchema.order_id == order_id)
    )

    delivery = result.scalar_one_or_none()

    if delivery is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'No courier found'
        )
    
    ret = await build_delivery_return(delivery, db)

    return ret


async def cancel_delivery_by_order_id(
    order_id: uuid.UUID,
    db: AsyncSession
):
    result = await db.execute(
        select(DeliverySchema)
        .filter(DeliverySchema.order_id == order_id)
        .with_for_update()
    )

    delivery = result.scalar_one_or_none()

    if delivery is None:
        raise HTTPException(
            status_code = status.HTTP_404_NOT_FOUND,
            detail = 'No courier found'
        )
    
    if delivery.status == DeliveryStatus.DELIVERED:
        raise HTTPException(
            status_code = status.HTTP_409_CONFLICT,
            detail = 'Unable to cancel finished delivery'
        )
    elif delivery.status == DeliveryStatus.ONGOING or delivery.status == DeliveryStatus.PLANNED:
        delivery.status = DeliveryStatus.CANCELLED
        delivery.last_changed = datetime.utcnow()

        try:
            await db.commit()
            await db.refresh(delivery)
        except Exception as e:
            await db.rollback()
            raise HTTPException(
                status_code = status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail = 'Failed to cancel reservation'
            )

    ret = await build_delivery_return(delivery, db)

    return ret



async def build_delivery_return(
    delivery: DeliverySchema,
    db: AsyncSession
):
    courier = await get_courier_by_courier_id(delivery.courier_id, db)

    return DeliveryReturn(
        id = delivery.id,
        order_id = delivery.order_id,
        courier_id = delivery.courier_id,
        courier_name = courier.first_name,
        address = delivery.address,
        status = delivery.status,
        created_at = delivery.created_at,
        last_changed = delivery.last_changed
    )