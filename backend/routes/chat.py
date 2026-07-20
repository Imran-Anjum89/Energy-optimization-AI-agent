from fastapi import APIRouter, HTTPException
from analytics.usage_analysis import UsageAnalyzer
from models.forecasting import ForecastingModel
from models.anomaly_detection import AnomalyDetectionModel
from services.recommendation_engine import RecommendationEngine
from agents.insight_agent import InsightAgent
from services.chat_service import ChatService
from schemas.api_schemas import ChatRequestSchema, ChatResponseSchema
from backend.cache import CacheManager
from utils.helpers import convert_numpy_types
import logging

logger = logging.getLogger("ChatRoute")

router = APIRouter(
    prefix="/chat",
    tags=["Chat"]
)

_chat_service = ChatService()


def _load_all_reports() -> dict:
    """
    Reuses whatever's already cached (usage/forecast/anomaly/recommendation/
    insight) and only computes what's missing - same pattern as every other
    route, so opening the chat never re-triggers a full Prophet/Isolation
    Forest refit if the dashboard already warmed the cache.
    """
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
            "recommendation": recommendation,
        })
        CacheManager.set("insight", insight)

    return {
        "usage": usage,
        "forecast": forecast,
        "anomaly": anomaly,
        "recommendation": recommendation,
        "insight": insight,
    }


@router.post("/", response_model=ChatResponseSchema)
def post_chat(request: ChatRequestSchema):
    try:
        reports = _load_all_reports()
        history = [turn.model_dump() for turn in request.history]

        result = _chat_service.answer(request.message, history, reports)
        return result
    except Exception as e:
        logger.error(f"Error handling chat message: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))
