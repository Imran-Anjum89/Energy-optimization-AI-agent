"""
=========================================================
Forecasting Model
Energy Optimization Agent
=========================================================

This module builds a forecasting model using Prophet
to predict future household energy consumption.

Author : Adnan Raza
Project: Energy Optimization Agent
=========================================================
"""

from pathlib import Path

import pandas as pd

from prophet import Prophet

from backend.config import config
from services.logger import setup_logger

logger = setup_logger("ForecastModel")


class ForecastingModel:
    """
    Forecast household energy consumption using Prophet.
    """

    def __init__(self):

        self.file_path = (
            config.PROCESSED_DATA_DIR /
            "processed_energy_data.csv"
        )

        self.df = None

        self.training_data = None

        self.model = None

        self.forecast = None

    # =====================================================
    # LOAD DATA
    # =====================================================

    def load_data(self):
        """
        Load processed dataset.
        """

        logger.info("Loading processed dataset...")

        self.df = pd.read_csv(
            self.file_path,
            parse_dates=["Datetime"]
        )

        logger.info(
            f"Dataset Loaded : {len(self.df):,} rows"
        )

        return self.df

    # =====================================================
    # DATA PREPARATION
    # =====================================================

    def prepare_training_data(self):
        """
        Convert minute-level power readings into
        daily energy (kWh).

        Prophet requires:

        ds -> datetime
        y  -> target variable
        """

        logger.info(
            "Preparing Prophet training dataset..."
        )

        daily_energy = (

            self.df

            .groupby(
                self.df["Datetime"].dt.date
            )["Global_active_power"]

            .sum()

            / 60

        ).reset_index()

        daily_energy.columns = [

            "ds",

            "y"

        ]

        daily_energy["ds"] = pd.to_datetime(
            daily_energy["ds"]
        )

        self.training_data = daily_energy

        logger.info(

            f"Training Samples : "

            f"{len(self.training_data):,}"

        )

        return self.training_data

    # =====================================================
    # BUILD MODEL
    # =====================================================

    def build_model(self):
        """
        Initialize Prophet model.
        """

        logger.info(
            "Building Prophet model..."
        )

        self.model = Prophet(

            yearly_seasonality=True,

            weekly_seasonality=True,

            daily_seasonality=False,

            changepoint_prior_scale=0.05

        )

        return self.model
    
        # =====================================================
    # TRAIN MODEL
    # =====================================================

    def train_model(self):
        """
        Train the Prophet forecasting model.
        """

        logger.info("=" * 60)
        logger.info("Training Prophet Model...")
        logger.info("=" * 60)

        if self.training_data is None:
            raise ValueError(
                "Training data not prepared."
            )

        if self.model is None:
            raise ValueError(
                "Model has not been built."
            )

        self.model.fit(
            self.training_data
        )

        logger.info(
            "Model training completed successfully."
        )

        return self.model

    # =====================================================
    # CREATE FUTURE DATAFRAME
    # =====================================================

    def create_future_dataframe(
        self,
        periods=30
    ):
        """
        Create future dates for forecasting.

        Parameters
        ----------
        periods : int
            Number of future days.
        """

        logger.info(
            f"Creating future dataframe ({periods} days)..."
        )

        future = self.model.make_future_dataframe(
            periods=periods,
            freq="D"
        )

        return future

    # =====================================================
    # GENERATE FORECAST
    # =====================================================

    def predict_next_days(
        self,
        periods=30
    ):
        """
        Forecast future energy consumption.
        """

        logger.info(
            "Generating forecast..."
        )

        future = self.create_future_dataframe(
            periods
        )

        self.forecast = self.model.predict(
            future
        )

        logger.info(
            f"Forecast generated for "
            f"{periods} future days."
        )

        return self.forecast

    # =====================================================
    # GET FUTURE PREDICTIONS
    # =====================================================

    def future_predictions(
        self,
        periods=30
    ):
        """
        Return only future forecast rows.
        """

        if self.forecast is None:

            self.predict_next_days(
                periods
            )

        predictions = self.forecast.tail(
            periods
        )[
            [
                "ds",
                "yhat",
                "yhat_lower",
                "yhat_upper"
            ]
        ].copy()

        predictions.rename(
            columns={

                "ds": "Date",

                "yhat":
                    "Predicted_Energy_kWh",

                "yhat_lower":
                    "Lower_Bound",

                "yhat_upper":
                    "Upper_Bound"

            },
            inplace=True
        )

        predictions.reset_index(
            drop=True,
            inplace=True
        )

        return predictions
    
        # =====================================================
    # MODEL SUMMARY
    # =====================================================

    def model_summary(self):
        """
        Return basic information about the forecasting model.
        """

        logger.info("Generating model summary...")

        summary = {

            "training_samples":
                len(self.training_data),

            "training_start":
                self.training_data["ds"].min(),

            "training_end":
                self.training_data["ds"].max(),

            "forecast_days":
                len(self.forecast) - len(self.training_data)
                if self.forecast is not None
                else 0,

            "model":
                "Facebook Prophet"

        }

        return summary

    # =====================================================
    # FORECAST STATISTICS
    # =====================================================

    def forecast_statistics(self):
        """
        Calculate statistics for predicted values.
        """

        logger.info(
            "Calculating forecast statistics..."
        )

        future = self.future_predictions()

        stats = {

            "minimum_prediction":
                float(
                    round(
                        future[
                            "Predicted_Energy_kWh"
                        ].min(),
                        2
                    )
                ),

            "maximum_prediction":
                float(
                    round(
                        future[
                            "Predicted_Energy_kWh"
                        ].max(),
                        2
                    )
                ),

            "average_prediction":
                float(
                    round(
                        future[
                            "Predicted_Energy_kWh"
                        ].mean(),
                        2
                    )
                ),

            "total_predicted_energy":
                float(
                    round(
                        future[
                            "Predicted_Energy_kWh"
                        ].sum(),
                        2
                    )
                )

        }

        return stats

    # =====================================================
    # SAVE FORECAST
    # =====================================================

    def save_forecast(
        self,
        filename="forecast_results.csv"
    ):
        """
        Save future forecast to outputs folder.
        """

        logger.info(
            "Saving forecast..."
        )

        output_path = (
            config.OUTPUT_DIR /
            filename
        )

        future = self.future_predictions()

        future.to_csv(
            output_path,
            index=False
        )

        logger.info(
            f"Forecast saved to {output_path}"
        )

        return output_path
    
        # =====================================================
    # EVALUATE MODEL
    # =====================================================

    def evaluate_model(self):
        """
        Compute evaluation metrics MAPE and RMSE on training predictions.
        """

        logger.info("Evaluating forecasting model...")

        import numpy as np

        if self.forecast is None or self.training_data is None:
            mape = 0.0
            rmse = 0.0
        else:
            historical_forecast = self.forecast.head(len(self.training_data))
            y_true = self.training_data['y'].values
            y_pred = historical_forecast['yhat'].values
            
            mask = y_true > 0
            if len(y_true[mask]) > 0:
                mape = float(np.mean(np.abs((y_true[mask] - y_pred[mask]) / y_true[mask])) * 100)
            else:
                mape = 0.0
                
            rmse = float(np.sqrt(np.mean((y_true - y_pred) ** 2)))

        forecast_days = (
            len(self.forecast)
            - len(self.training_data)
        ) if (self.forecast is not None and self.training_data is not None) else 0

        evaluation = {

            "model_name":
                "Facebook Prophet",

            "training_samples":
                len(self.training_data) if self.training_data is not None else 0,

            "forecast_days":
                forecast_days,

            "mape":
                round(mape, 2),

            "rmse":
                round(rmse, 2),

            "status":
                "Model Trained and Evaluated Successfully"

        }

        return evaluation

    # =====================================================
    # FORECAST REPORT
    # =====================================================

    def generate_forecast_report(self):
        """
        Generate complete forecast report.
        """

        logger.info("=" * 60)
        logger.info("Generating Forecast Report")
        logger.info("=" * 60)

        report = {

            "summary":
                self.model_summary(),

            "statistics":
                self.forecast_statistics(),

            "evaluation":
                self.evaluate_model(),

            "forecast":
                self.future_predictions()

        }

        logger.info(
            "Forecast report generated successfully."
        )

        return report

    # =====================================================
    # COMPLETE PIPELINE
    # =====================================================

    def run_pipeline(
        self,
        periods=30
    ):
        """
        Execute complete forecasting pipeline.
        """

        logger.info("=" * 60)
        logger.info("Starting Forecast Pipeline")
        logger.info("=" * 60)

        self.load_data()

        self.prepare_training_data()

        self.build_model()

        self.train_model()

        self.predict_next_days(
            periods
        )

        self.save_forecast()

        logger.info("=" * 60)
        logger.info("Forecast Pipeline Completed")
        logger.info("=" * 60)

        return self.generate_forecast_report()
    
    # =====================================================
# STANDALONE EXECUTION
# =====================================================

if __name__ == "__main__":

    model = ForecastingModel()

    report = model.run_pipeline(
        periods=30
    )

    print("\n" + "=" * 70)
    print("FORECAST REPORT")
    print("=" * 70)

    print("\nMODEL SUMMARY")
    print(report["summary"])

    print("\nSTATISTICS")
    print(report["statistics"])

    print("\nEVALUATION")
    print(report["evaluation"])

    print("\nNEXT 5 DAYS FORECAST")
    print(
        report["forecast"].head()
    )

    print("\n" + "=" * 70)
    print("Forecasting Model Executed Successfully")
    print("=" * 70)


# =====================================================
# END OF FILE
# =====================================================

