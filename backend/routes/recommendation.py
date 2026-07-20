from fastapi import APIRouter, HTTPException
from analytics.usage_analysis import UsageAnalyzer
from models.forecasting import ForecastingModel
from models.anomaly_detection import AnomalyDetectionModel
from services.recommendation_engine import RecommendationEngine
from schemas.api_schemas import RecommendationReportSchema
from backend.cache import CacheManager
from utils.helpers import convert_numpy_types
import logging

logger = logging.getLogger("RecommendationRoute")

router = APIRouter(
    prefix="/recommendations",
    tags=["Recommendations"]
)


@router.get("/", response_model=RecommendationReportSchema)
def get_recommendations():
    try:
        # Check cache
        cached_data = CacheManager.get("recommendations")
        if cached_data:
            return cached_data

        # Load inputs from cache or compute them
        usage = CacheManager.get("usage")
        if not usage:
            usage = convert_numpy_types(UsageAnalyzer().generate_report())
            CacheManager.set("usage", usage)

        forecast = CacheManager.get("forecast")
        if not forecast:
            forecast = convert_numpy_types(ForecastingModel().run_pipeline())
            CacheManager.set("forecast", forecast)

        anomaly = CacheManager.get("anomaly")
        if not anomaly:
            anomaly = convert_numpy_types(AnomalyDetectionModel().run_pipeline())
            CacheManager.set("anomaly", anomaly)

        # Run engine
        engine = RecommendationEngine(usage, forecast, anomaly)
        report = convert_numpy_types(engine.run_pipeline())

        # Save cache
        CacheManager.set("recommendations", report)
        return report
    except Exception as e:
        logger.error(f"Error generating recommendation report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))