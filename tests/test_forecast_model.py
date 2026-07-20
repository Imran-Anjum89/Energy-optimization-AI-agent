"""
Test Forecast Model
Energy Optimization Agent
"""

from models.forecasting import ForecastingModel


def test_forecast_report_structure(forecast_report):
    report = forecast_report

    assert "summary" in report
    assert "statistics" in report
    assert "evaluation" in report
    assert "forecast" in report


def test_forecast_evaluation_metrics(forecast_report):
    evaluation = forecast_report["evaluation"]

    assert evaluation["model_name"] == "Facebook Prophet"
    assert evaluation["status"] == "Model Trained and Evaluated Successfully"
    assert "mape" in evaluation
    assert "rmse" in evaluation
    assert evaluation["mape"] >= 0
    assert evaluation["rmse"] >= 0


def test_forecast_prediction_rows(forecast_report):
    forecast_rows = forecast_report["forecast"]

    # Forecast rows are serialized as a list of records via convert_numpy_types
    assert len(forecast_rows) == 30

    first_row = forecast_rows[0]
    assert "Date" in first_row
    assert "Predicted_Energy_kWh" in first_row


def test_forecasting_model_class_importable():
    # Regression check: the class must be named ForecastingModel
    model = ForecastingModel()
    assert model is not None
