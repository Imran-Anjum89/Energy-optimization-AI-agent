from fastapi import APIRouter, HTTPException
from analytics.usage_analysis import UsageAnalyzer
from models.forecasting import ForecastingModel
from models.anomaly_detection import AnomalyDetectionModel
from services.recommendation_engine import RecommendationEngine
from agents.insight_agent import InsightAgent
from schemas.api_schemas import InsightReportSchema
from backend.cache import CacheManager
from utils.helpers import convert_numpy_types
import logging

logger = logging.getLogger("InsightsRoute")

router = APIRouter(
    prefix="/insights",
    tags=["Insights"]
)


@router.get("/", response_model=InsightReportSchema)
def get_insights():
    try:
        # Check cache
        cached_data = CacheManager.get("insight")
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

        recommendation = CacheManager.get("recommendations")
        if not recommendation:
            engine = RecommendationEngine(usage, forecast, anomaly)
            recommendation = convert_numpy_types(engine.run_pipeline())
            CacheManager.set("recommendations", recommendation)

        # Run the reasoning agent
        agent = InsightAgent()
        report = agent.execute({
            "usage": usage,
            "forecast": forecast,
            "anomaly": anomaly,
            "recommendation": recommendation,
        })

        # Save cache
        CacheManager.set("insight", report)
        return report
    except Exception as e:
        logger.error(f"Error generating AI insight: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
