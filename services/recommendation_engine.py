"""
=========================================================
Recommendation Engine
Energy Optimization Agent
=========================================================
"""

from services.logger import setup_logger
from backend.database import DatabaseManager

logger = setup_logger("RecommendationEngine")


class RecommendationEngine:
    """
    Generates intelligent energy-saving recommendations
    using analytics, forecasting and anomaly detection.
    """

    def __init__(
        self,
        usage_report,
        forecast_report,
        anomaly_report,
        dataset_id: int = None
    ):

        import pandas as pd

        self.usage = usage_report
        self.forecast = forecast_report
        if isinstance(self.forecast, dict) and "forecast" in self.forecast:
            if isinstance(self.forecast["forecast"], list):
                self.forecast["forecast"] = pd.DataFrame(self.forecast["forecast"])
        self.anomaly = anomaly_report
        self.dataset_id = dataset_id

        self.recommendations = []

    # =====================================================
    # PEAK USAGE
    # =====================================================

    def peak_hour_recommendations(self):
        """
        Generate recommendations based on peak usage.
        """

        logger.info(
            "Analyzing peak hour usage..."
        )

        peak_hour = (
            self.usage["peak_usage"]["peak_hour"]
        )

        peak_power = (
            self.usage["peak_usage"][
                "peak_hour_average_kw"
            ]
        )

        self.recommendations.append({

            "category":
                "Peak Usage",

            "priority":
                "High",

            "recommendation":
                f"Reduce appliance usage around "
                f"{peak_hour}:00 when average "
                f"consumption reaches "
                f"{peak_power:.2f} kW.",

            "estimated_saving_percent":
                8

        })

        return self.recommendations

    # =====================================================
    # WEEKEND USAGE
    # =====================================================

    def weekend_recommendations(self):
        """
        Weekend usage recommendations.
        """

        logger.info(
            "Analyzing weekend usage..."
        )

        difference = (
            self.usage["weekday_weekend"][
                "difference_kw"
            ]
        )

        if difference > 0:

            self.recommendations.append({

                "category":
                    "Weekend Usage",

                "priority":
                    "Medium",

                "recommendation":
                    "Weekend consumption is higher "
                    "than weekday usage. Shift "
                    "heavy appliances to off-peak "
                    "hours whenever possible.",

                "estimated_saving_percent":
                    5

            })

        return self.recommendations
    
        # =====================================================
    # FORECAST RECOMMENDATIONS
    # =====================================================

    def forecast_recommendations(self):
        """
        Generate recommendations using forecast results.
        """

        logger.info(
            "Analyzing forecast..."
        )

        forecast_df = self.forecast["forecast"]

        average_forecast = round(
            forecast_df["Predicted_Energy_kWh"].mean(),
            2
        )

        historical_average = (
            self.usage["consumption"][
                "average_daily_energy_kwh"
            ]
        )

        if average_forecast > historical_average:

            increase = round(

                (
                    average_forecast
                    -
                    historical_average
                )
                /
                historical_average
                * 100,

                2

            )

            self.recommendations.append({

                "category":
                    "Forecast",

                "priority":
                    "High",

                "recommendation":
                    f"Forecasted daily energy "
                    f"consumption is expected to "
                    f"increase by {increase}% "
                    f"compared to historical "
                    f"usage. Reduce unnecessary "
                    f"loads during peak periods.",

                "estimated_saving_percent":
                    10

            })

        return self.recommendations

    # =====================================================
    # ANOMALY RECOMMENDATIONS
    # =====================================================

    def anomaly_recommendations(self):
        """
        Generate recommendations from anomalies.
        """

        logger.info(
            "Analyzing anomalies..."
        )

        anomaly_percent = (
            self.anomaly["statistics"][
                "anomaly_percentage"
            ]
        )

        if anomaly_percent > 0.5:

            self.recommendations.append({

                "category":
                    "Anomaly",

                "priority":
                    "High",

                "recommendation":
                    "Abnormal energy usage has "
                    "been detected. Inspect "
                    "electrical appliances for "
                    "faults or unnecessary "
                    "standby power consumption.",

                "estimated_saving_percent":
                    12

            })

        return self.recommendations

    # =====================================================
    # GENERAL RECOMMENDATIONS
    # =====================================================

    def general_recommendations(self):
        """
        Add generic energy-saving tips.
        """

        logger.info(
            "Adding general recommendations..."
        )

        tips = [

            "Replace incandescent bulbs with LED lighting.",

            "Turn off appliances when they are not in use.",

            "Use energy-efficient appliances whenever possible.",

            "Run washing machines and dishwashers during off-peak hours.",

            "Service HVAC equipment regularly for better efficiency."

        ]

        for tip in tips:

            self.recommendations.append({

                "category":
                    "General",

                "priority":
                    "Low",

                "recommendation":
                    tip,

                "estimated_saving_percent":
                    2

            })

        return self.recommendations
    
        # =====================================================
    # ESTIMATE SAVINGS
    # =====================================================

    def estimate_savings(self):
        """
        Estimate possible energy savings.
        """

        logger.info(
            "Estimating energy savings..."
        )

        saving_percent = sum(

            recommendation[
                "estimated_saving_percent"
            ]

            for recommendation
            in self.recommendations

        )

        average_daily = (
            self.usage["consumption"][
                "average_daily_energy_kwh"
            ]
        )

        from services.savings_calculator import SavingsCalculator
        return SavingsCalculator.calculate_savings(saving_percent, average_daily)

    # =====================================================
    # CO2 REDUCTION
    # =====================================================

    def estimate_co2_reduction(self):
        """
        Estimate yearly and monthly CO₂ reduction.
        """

        logger.info(
            "Estimating CO₂ reduction..."
        )

        savings = self.estimate_savings()
        yearly_saving_kwh = savings["yearly_saving_kwh"]

        from services.savings_calculator import SavingsCalculator
        return SavingsCalculator.calculate_co2_reduction(yearly_saving_kwh)

    # =====================================================
    # GENERATE REPORT
    # =====================================================

    def generate_report(self):
        """
        Generate recommendation report.
        """

        logger.info("=" * 60)
        logger.info(
            "Generating Recommendation Report"
        )
        logger.info("=" * 60)

        report = {

            "recommendations":
                self.recommendations,

            "savings":
                self.estimate_savings(),

            "co2":
                self.estimate_co2_reduction()

        }

        logger.info(
            "Recommendation report generated."
        )

        return report

    # =====================================================
    # COMPLETE PIPELINE
    # =====================================================

    def save_recommendations_to_db(self):
        """Save recommendations into SQLite recommendations table."""
        if not self.recommendations or self.dataset_id is None:
            return
        logger.info(f"Saving recommendations to database for dataset {self.dataset_id}...")
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM recommendations WHERE dataset_id = ?", (self.dataset_id,))
            conn.commit()
            
            for rec in self.recommendations:
                cursor.execute(
                    """
                    INSERT INTO recommendations (dataset_id, category, priority, recommendation, estimated_saving_percent)
                    VALUES (?, ?, ?, ?, ?)
                    """,
                    (
                        self.dataset_id,
                        rec["category"],
                        rec["priority"],
                        rec["recommendation"],
                        float(rec["estimated_saving_percent"])
                    )
                )
            conn.commit()
            logger.info("Recommendations saved to database successfully.")
        except Exception as e:
            conn.rollback()
            logger.error(f"Failed to save recommendations to database: {e}")
        finally:
            conn.close()

    def run_pipeline(self):
        """
        Execute complete recommendation pipeline.
        """

        logger.info("=" * 60)
        logger.info(
            "Starting Recommendation Engine"
        )
        logger.info("=" * 60)

        self.peak_hour_recommendations()

        self.weekend_recommendations()

        self.forecast_recommendations()

        self.anomaly_recommendations()

        self.general_recommendations()

        report = self.generate_report()

        self.save_recommendations_to_db()

        logger.info("=" * 60)
        logger.info(
            "Recommendation Engine Completed"
        )
        logger.info("=" * 60)

        return report


# =====================================================
# STANDALONE EXECUTION
# =====================================================

if __name__ == "__main__":

    print(
        "Recommendation Engine module loaded successfully."
    )