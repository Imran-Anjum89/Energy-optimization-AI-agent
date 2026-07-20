from fastapi import APIRouter, HTTPException
from analytics.usage_analysis import UsageAnalyzer
from schemas.api_schemas import UsageReportSchema
from backend.cache import CacheManager
from utils.helpers import convert_numpy_types
import logging

logger = logging.getLogger("UsageRoute")

router = APIRouter(
    prefix="/usage",
    tags=["Usage Analytics"]
)


@router.get("/", response_model=UsageReportSchema)
def get_usage():
    try:
        # Check cache
        cached_data = CacheManager.get("usage")
        if cached_data:
            return cached_data

        # Compute
        analyzer = UsageAnalyzer()
        report = convert_numpy_types(analyzer.generate_report())
        
        # Save cache
        CacheManager.set("usage", report)
        return report
    except Exception as e:
        logger.error(f"Error generating usage report: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))