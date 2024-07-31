from fastapi import APIRouter, Depends, HTTPException, status, Response
from sqlalchemy.orm import Session
from typing import List
import pandas as pd
from io import StringIO

from app.db import DBConnectionDep
from license_plates import schemas as lp_schemas
from license_plates.models import Visit, LicensePlate 
from paymets.models import Parking, Rate, Limit, Price
from paymets.dependencies import PaymentsControllerDep
from license_plates.routers import visit_router
from app.services.auth import AuthDep
from sqlalchemy import func

payments_router = APIRouter(prefix="/payments", tags=['payments'])

@visit_router.get("/{plate_ident}/total_duration", response_model=lp_schemas.TotalCostResponse)
async def calculate_total_duration(plate_ident, controller: PaymentsControllerDep, db: DBConnectionDep):
    """
    The calculate_total_duration function calculates the total duration of visits for a specific license plate.
    It uses the SUM function to calculate the total number of hours the license plate was registered.
    """
    result = db.query(
    Visit.license_plate_id,
    func.sum(func.extract('epoch', Visit.out_at - Visit.in_at) / 3600).label('total_hours')
    ).filter(Visit.license_plate_id == plate_ident).group_by(Visit.license_plate_id).first()
    
    if result is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Number not found")

    return lp_schemas.TotalCostResponse(license_plate_id=result.license_plate_id, total_cost=float(result.total_hours))


@payments_router.get("/{plate_ident}/total_cost", response_model=lp_schemas.TotalCostResponse)
async def calculate_total_cost(plate_ident, controller: PaymentsControllerDep, db: DBConnectionDep):
    """
    The calculate_total_cost function calculates the total cost of visits for a specific license plate.
    It multiplies the total duration of visits by the price per hour to calculate the total cost.
    """
    result = (
        db.query(
            Visit.license_plate_id,
            func.sum(func.extract('epoch', Visit.out_at - Visit.in_at) / 3600 * db.query(Price).filter(Price.hours == 1).first().price).label('total_cost')
        )
        .filter(Visit.license_plate_id == plate_ident)
        .group_by(Visit.license_plate_id).first()
    )
    print(result)
    return lp_schemas.TotalCostResponse(license_plate_id=result.license_plate_id, total_cost=float(result.total_cost))


# @payments_router.get("/exceeded_limit", response_model=List[lp_schemas.ExceededLimitResponse])
# async def check_exceeded_limit(db: Session = Depends(get_db)):
#     subquery = db.query(
#     Parking.license_plate,
#     func.sum(func.extract('epoch', Parking.end_time - Parking.start_time) / 3600 * Rate.rate_per_hour).label('total_cost')
#     ).join(Rate).group_by(Parking.license_plate).subquery()

#     result = db.query(
#         subquery.c.license_plate,
#         subquery.c.total_cost,
#         Limit.limit_amount
#     ).join(Limit, subquery.c.license_plate == Limit.license_plate).filter(subquery.c.total_cost > Limit.limit_amount).all()

#     return [lp_schemas.ExceededLimitResponse(
#                 license_plate=r.license_plate,
#                 total_cost=r.total_cost,
#                 limit_amount=r.limit_amount
#             ) for r in result]

@payments_router.get("/report/csv")
async def generate_csv_report(db: DBConnectionDep):
    """
    The generate_csv_report function generates a CSV report of total costs for all license plates.
    It calculates the total cost of visits for each license plate and exports the data to a CSV file.
    """
    result = db.query(
    Visit.license_plate_id,
    func.sum(func.extract('epoch', Visit.in_at - Visit.out_at) / 3600 * db.query(Price).filter(Price.hours == 1).first().price).label('total_cost')
    ).group_by(Visit.license_plate_id,).all()

    df = pd.DataFrame(result, columns=['license_plate', 'total_cost'])
    csv_data = df.to_csv(index=False)

    return Response(content=csv_data, media_type='text/csv', headers={"Content-Disposition": "attachment; filename=report.csv"})