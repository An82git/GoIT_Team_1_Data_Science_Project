from fastapi import APIRouter
from paymets.dependencies import PaymentsControllerDep

payments_router = APIRouter(prefix="/payments", tags=['payments'])
