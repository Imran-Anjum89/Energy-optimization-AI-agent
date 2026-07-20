"""
=========================================================
FastAPI Backend
Energy Optimization Agent
=========================================================
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes import (
    usage,
    forecast,
    anomaly,
    recommendation,
    insights,
    chat,
    reports,
    auth,
    datasets,
)

app = FastAPI(
    title="Energy Optimization Agent",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def home():
    return {
        "project": "Energy Optimization Agent",
        "status": "Running",
        "version": "1.0.0"
    }


# Include Routers
app.include_router(auth.router)
app.include_router(datasets.router)
app.include_router(usage.router)
app.include_router(forecast.router)
app.include_router(anomaly.router)
app.include_router(recommendation.router)
app.include_router(insights.router)
app.include_router(chat.router)
app.include_router(reports.router)