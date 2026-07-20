from fastapi import APIRouter, HTTPException
from models.forecasting import ForecastingModel
from schemas.api_schemas import ForecastReportSchema
from backend.cache import CacheManager
from utils.helpers import convert_numpy_types
import logging

logger = logging.getLogger("ForecastRoute")

router = APIRouter(
    prefix="/forecast",
    tags=["Forecasting"]
)


@router.get("/", response_model=ForecastReportSchema)
def get_forecast():
    try:
        # Check cache (caching forecast for up to 12 hours)
        cached_data = CacheManager.get("forecast", max_age_seconds=43200)
        if cached_data:
            return cached_data

        # Compute
        model = ForecastingModel()
        report = convert_numpy_types(model.run_pipeline())
        
        # Save cache
        CacheManager.set("forecast", report)
        return report
    except Exception as e:
        logger.error(f"Error generating forecast report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))