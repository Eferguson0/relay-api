import logging
from datetime import datetime
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.heart_rate import HourlyHeartRate
from app.models.user import User
from app.schemas.heart_rate import HeartRateIngestRequest, HeartRateIngestResponse
from app.services.auth_service import get_current_active_user

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api", tags=["heart-rate"])


@router.post("/ingest-heart-rate", response_model=HeartRateIngestResponse)
async def ingest_heart_rate_data(
    request: HeartRateIngestRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Ingest heart rate data from request body and store in hourly_heart_rate table"""
    try:
        # Use the authenticated user
        user = current_user

        # Process the heart rate data from request body
        inserted_records = 0
        processed_metrics = []

        # Extract metrics from the request
        metrics = request.record.data.metrics

        for metric in metrics:
            metric_name = metric.name
            metric_data = metric.data

            logger.info(
                f"Processing metric: {metric_name} with {len(metric_data)} data points"
            )

            # Process each heart rate data point
            for data_point in metric_data:
                date_str = data_point.date
                min_hr = data_point.Min
                avg_hr = data_point.Avg
                max_hr = data_point.Max
                source = data_point.source

                # Parse the date string (format: "2025-08-31 19:00:00 -0400")
                try:
                    # Parse the full datetime
                    activity_datetime = datetime.strptime(
                        date_str, "%Y-%m-%d %H:%M:%S %z"
                    )
                    # Convert to UTC if needed, or keep as is
                    if activity_datetime.tzinfo:
                        activity_datetime = activity_datetime.replace(tzinfo=None)
                except ValueError as e:
                    logger.warning(f"Invalid date format: {date_str}, error: {e}")
                    continue

                # Validate required fields
                if not source:
                    logger.warning(f"Missing source for data point: {data_point}")
                    continue

                # Validate heart rate values
                if min_hr is not None and (min_hr < 0 or min_hr > 300):
                    logger.warning(f"Invalid min_hr value: {min_hr}")
                    min_hr = None

                if avg_hr is not None and (avg_hr < 0 or avg_hr > 300):
                    logger.warning(f"Invalid avg_hr value: {avg_hr}")
                    avg_hr = None

                if max_hr is not None and (max_hr < 0 or max_hr > 300):
                    logger.warning(f"Invalid max_hr value: {max_hr}")
                    max_hr = None

                # Check if record already exists for this datetime, user, and source
                existing_record = (
                    db.query(HourlyHeartRate)
                    .filter(
                        HourlyHeartRate.user_id == user.id,
                        HourlyHeartRate.date == activity_datetime,
                        HourlyHeartRate.source == source,
                    )
                    .first()
                )

                if existing_record:
                    # Update existing record
                    existing_record.min_hr = (
                        min_hr if min_hr is not None else existing_record.min_hr
                    )
                    existing_record.avg_hr = (
                        avg_hr if avg_hr is not None else existing_record.avg_hr
                    )
                    existing_record.max_hr = (
                        max_hr if max_hr is not None else existing_record.max_hr
                    )
                    existing_record.updated_at = datetime.now()
                    logger.info(
                        f"Updated existing heart rate record for {activity_datetime}"
                    )
                else:
                    # Create new record
                    new_record = HourlyHeartRate(
                        user_id=user.id,
                        date=activity_datetime,
                        min_hr=min_hr,
                        avg_hr=avg_hr,
                        max_hr=max_hr,
                        source=source,
                    )
                    db.add(new_record)
                    logger.info(
                        f"Created new heart rate record for {activity_datetime}"
                    )

                inserted_records += 1

            processed_metrics.append(metric_name)

        # Commit all changes
        db.commit()

        logger.info(f"Successfully ingested {inserted_records} heart rate records")

        return HeartRateIngestResponse(
            message="Heart rate data ingested successfully",
            records_processed=inserted_records,
            metrics_processed=processed_metrics,
            user_id=user.id,
            source="POST request",
        )

    except Exception as e:
        logger.error(f"Error ingesting heart rate data: {str(e)}")
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error ingesting data: {str(e)}",
        )


@router.get("/heart-rate")
async def get_heart_rate_data(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_active_user),
):
    """Get hourly heart rate records with optional filtering"""
    try:
        # Only show data for the authenticated user (security)
        query = db.query(HourlyHeartRate).filter(
            HourlyHeartRate.user_id == current_user.id
        )

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
                    "user_id": record.user_id,
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
