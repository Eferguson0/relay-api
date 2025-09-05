import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.heart_rate import HourlyHeartRate

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["export"])


@router.get("/heart-rate")
async def get_heart_rate_data(
    user_email: Optional[str] = None,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
):
    """Get hourly heart rate records with optional filtering"""
    try:
        query = db.query(HourlyHeartRate)

        # Filter by user_email if provided
        if user_email:
            query = query.filter(HourlyHeartRate.user_email == user_email)

        # Filter by date range if provided
        if start_date:
            query = query.filter(HourlyHeartRate.date >= start_date)
        if end_date:
            query = query.filter(HourlyHeartRate.date <= end_date)

        # Order by date descending
        query = query.order_by(HourlyHeartRate.date.desc())

        records = query.all()

        return {
            "records": [
                {
                    "user_email": record.user_email,
                    "date": record.date.isoformat(),
                    "min_hr": record.min_hr,
                    "avg_hr": float(record.avg_hr) if record.avg_hr else None,
                    "max_hr": record.max_hr,
                    "source": record.source,
                    "created_at": record.created_at.isoformat(),
                    "updated_at": (
                        record.updated_at.isoformat() if record.updated_at else None
                    ),
                }
                for record in records
            ],
            "total_count": len(records),
        }

    except Exception as e:
        logger.error(f"Error fetching heart rate records: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error fetching data: {str(e)}",
        )
