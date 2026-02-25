from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy.exc import IntegrityError
from prometheus_fastapi_instrumentator import Instrumentator
from datetime import datetime
from db import _get_db
from uuid import UUID
from typing import List
from models import CourierCreate, CourierReturn, DeliveryCreate, DeliveryReturn
import utils


app = FastAPI(title="Order Service", version="1.0.0")


@app.get('/health', summary='HealthCheck EndPoint', tags=['Health Check'])
def healthcheck():
    return {'status': 'OK'}


@app.post('/couriers', summary = 'Create new courier', tags=['Couriers'], response_model = CourierReturn, status_code = status.HTTP_201_CREATED)
async def create_new_courier(
    courier_data: CourierCreate,
    db = Depends(_get_db)
):
    courier_created = await utils.create_new_courier(courier_data, db)
    return courier_created


@app.get('/couriers/{courier_id}', summary = 'Get courier by id', tags=['Couriers'], response_model = CourierReturn)
async def get_courier_by_courier_id(
    courier_id: UUID,
    db = Depends(_get_db)
):
    courier = await utils.get_courier_by_courier_id(courier_id, db)
    return courier


@app.post('/deliveries', summary = 'Create new delivery', tags=['Deliveries'], response_model = DeliveryReturn, status_code = status.HTTP_201_CREATED)
async def create_new_delivery(
    delivery_data: DeliveryCreate,
    db = Depends(_get_db)
):
    delivery_created = await utils.create_new_delivery(delivery_data, db)
    return delivery_created


@app.get('/deliveries/{order_id}', summary = 'Get delivery for order id', response_model = DeliveryReturn, tags=['Deliveries'])
async def get_delivery_for_order_id(
    order_id: UUID,
    db = Depends(_get_db)
):
    delivery = await utils.get_delivery_by_order_id(order_id, db)
    return delivery


@app.put('/deliveries/cancel/{order_id}', summary = 'Cancel delivery for order id', response_model = DeliveryReturn, tags=['Deliveries'])
async def cancel_delivery_for_order_id(
    order_id: UUID,
    db = Depends(_get_db)
):
    delivery_canceled = await utils.cancel_delivery_by_order_id(order_id, db)
    return delivery_canceled


# if __name__ == "__main__":
#     import uvicorn
#     # Запускаем приложение на localhost:8000
#     uvicorn.run(
#         "main:app",
#         host="127.0.0.1",
#         port=8000,
#         reload=True,  # Автоперезагрузка при изменении кода (только для разработки)
#         log_level="info"
#     )