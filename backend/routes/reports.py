from fastapi import APIRouter, HTTPException
from services.report_generator import ReportGenerator
from schemas.api_schemas import ReportingResponseSchema
from backend.cache import CacheManager
from analytics.usage_analysis import UsageAnalyzer
from models.forecasting import ForecastingModel
from models.anomaly_detection import AnomalyDetectionModel
from services.recommendation_engine import RecommendationEngine
from agents.insight_agent import InsightAgent
from utils.helpers import convert_numpy_types
import logging

logger = logging.getLogger("ReportsRoute")

router = APIRouter(
    prefix="/reports",
    tags=["Reports"]
)


@router.get("/", response_model=ReportingResponseSchema)
def get_reports():
    try:
        # Check cache
        cached_data = CacheManager.get("report")
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

        insight = CacheManager.get("insight")
        if not insight:
            insight = InsightAgent().execute({
                "usage": usage,
                "forecast": forecast,
                "anomaly": anomaly,
                "recommendation": recommendation
            })
            CacheManager.set("insight", insight)

        # Generate report
        data = {
            "usage": usage,
            "forecast": forecast,
            "anomaly": anomaly,
            "recommendation": recommendation,
            "insight": insight
        }

        generator = ReportGenerator(data)
        report = convert_numpy_types(generator.generate_report())

        # Save cache
        CacheManager.set("report", report)
        return report
    except Exception as e:
        logger.error(f"Error generating intelligence report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
