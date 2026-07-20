import requests
import streamlit as st
from analytics.usage_analysis import UsageAnalyzer
from models.forecasting import ForecastingModel
from models.anomaly_detection import AnomalyDetectionModel
from services.recommendation_engine import RecommendationEngine
from services.report_generator import ReportGenerator
from agents.insight_agent import InsightAgent
from services.chat_service import ChatService
from backend.cache import CacheManager
from utils.helpers import convert_numpy_types

API_BASE_URL = "http://127.0.0.1:8000"

@st.cache_data(ttl=3600)
def load_usage_data():
    try:
        response = requests.get(f"{API_BASE_URL}/usage", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    
    # Fallback to direct calculation
    cached = CacheManager.get("usage")
    if cached:
        return cached
    analyzer = UsageAnalyzer()
    report = convert_numpy_types(analyzer.generate_report())
    CacheManager.set("usage", report)
    return report

@st.cache_data(ttl=3600)
def load_forecast_data():
    try:
        response = requests.get(f"{API_BASE_URL}/forecast", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    
    # Fallback to direct calculation
    cached = CacheManager.get("forecast")
    if cached:
        return cached
    model = ForecastingModel()
    report = convert_numpy_types(model.run_pipeline())
    CacheManager.set("forecast", report)
    return report

@st.cache_data(ttl=3600)
def load_anomaly_data():
    try:
        response = requests.get(f"{API_BASE_URL}/anomaly", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    
    # Fallback to direct calculation
    cached = CacheManager.get("anomaly")
    if cached:
        return cached
    model = AnomalyDetectionModel()
    report = convert_numpy_types(model.run_pipeline())
    CacheManager.set("anomaly", report)
    return report

@st.cache_data(ttl=3600)
def load_recommendation_data():
    try:
        response = requests.get(f"{API_BASE_URL}/recommendations", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    
    # Fallback to direct calculation
    cached = CacheManager.get("recommendations")
    if cached:
        return cached
    usage = load_usage_data()
    forecast = load_forecast_data()
    anomaly = load_anomaly_data()
    engine = RecommendationEngine(usage, forecast, anomaly)
    report = convert_numpy_types(engine.run_pipeline())
    CacheManager.set("recommendations", report)
    return report

@st.cache_data(ttl=3600)
def load_insight_data():
    try:
        response = requests.get(f"{API_BASE_URL}/insights", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    # Fallback to direct calculation
    cached = CacheManager.get("insight")
    if cached:
        return cached
    data = {
        "usage": load_usage_data(),
        "forecast": load_forecast_data(),
        "anomaly": load_anomaly_data(),
        "recommendation": load_recommendation_data()
    }
    report = InsightAgent().execute(data)
    CacheManager.set("insight", report)
    return report

@st.cache_data(ttl=3600)
def load_reports_data():
    try:
        response = requests.get(f"{API_BASE_URL}/reports", timeout=3)
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass
    
    # Fallback to direct calculation
    cached = CacheManager.get("report")
    if cached:
        return cached
    data = {
        "usage": load_usage_data(),
        "forecast": load_forecast_data(),
        "anomaly": load_anomaly_data(),
        "recommendation": load_recommendation_data(),
        "insight": load_insight_data()
    }
    generator = ReportGenerator(data)
    report = convert_numpy_types(generator.generate_report())
    CacheManager.set("report", report)
    return report


def send_chat_message(message: str, history: list) -> dict:
    """
    NOT cached with @st.cache_data - every message is a fresh real-time
    exchange, not a repeatable/idempotent lookup.
    """
    try:
        response = requests.post(
            f"{API_BASE_URL}/chat/",
            json={"message": message, "history": history},
            timeout=15,
        )
        if response.status_code == 200:
            return response.json()
    except Exception:
        pass

    # Fallback to direct in-process call (e.g. API server not running)
    reports = {
        "usage": load_usage_data(),
        "forecast": load_forecast_data(),
        "anomaly": load_anomaly_data(),
        "recommendation": load_recommendation_data(),
        "insight": load_insight_data(),
    }
    return ChatService().answer(message, history, reports)
