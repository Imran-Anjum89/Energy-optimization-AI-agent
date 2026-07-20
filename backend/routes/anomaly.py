from fastapi import APIRouter, HTTPException
from models.anomaly_detection import AnomalyDetectionModel
from schemas.api_schemas import AnomalyReportSchema
from backend.cache import CacheManager
from utils.helpers import convert_numpy_types
import logging

logger = logging.getLogger("AnomalyRoute")

router = APIRouter(
    prefix="/anomaly",
    tags=["Anomaly Detection"]
)


@router.get("/", response_model=AnomalyReportSchema)
def get_anomaly():
    try:
        # Check cache (caching anomalies for up to 12 hours)
        cached_data = CacheManager.get("anomaly", max_age_seconds=43200)
        if cached_data:
            return cached_data

        # Compute
        model = AnomalyDetectionModel()
        report = convert_numpy_types(model.run_pipeline())
        
        # Save cache
        CacheManager.set("anomaly", report)
        return report
    except Exception as e:
        logger.error(f"Error generating anomaly report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))