"""
Data Preprocessing Module
Energy Optimization Agent
"""

import pandas as pd

from backend.config import config
from services.logger import setup_logger

logger = setup_logger("Preprocessing")


class DataPreprocessor:
    """
    Handles loading, cleaning, feature engineering,
    and saving the energy consumption dataset.
    """

    def __init__(self):
        self.file_path = (
            config.RAW_DATA_DIR /
            "household_power_consumption.txt"
        )

    def load_data(self):
        """
        Load raw dataset.
        """
        logger.info("Loading dataset...")

        df = pd.read_csv(
            self.file_path,
            sep=";",
            low_memory=False,
            na_values=["?"]
        )

        logger.info(f"Rows Loaded: {len(df):,}")
        logger.info(f"Columns: {len(df.columns)}")

        return df

    def inspect_data(self, df):
        """
        Display basic dataset information.
        """
        logger.info("Inspecting dataset...")

        logger.info(f"Shape: {df.shape}")

        logger.info(f"Columns: {list(df.columns)}")

        logger.info(
            f"Missing Values:\n{df.isnull().sum()}"
        )

        return df

    def clean_data(self, df):
        """
        Remove rows with missing values.
        """
        logger.info("Cleaning dataset...")

        before = len(df)

        df = df.dropna()

        after = len(df)

        logger.info(f"Removed {before-after:,} rows")

        logger.info(f"Remaining rows: {after:,}")

        return df

    def create_datetime(self, df):
        """
        Combine Date and Time into Datetime.
        """
        logger.info("Creating Datetime column...")

        df["Datetime"] = pd.to_datetime(
            df["Date"] + " " + df["Time"],
            format="%d/%m/%Y %H:%M:%S"
        )

        logger.info("Datetime column created.")

        return df

    def engineer_features(self, df):
        """
        Create useful time-based features.
        """
        logger.info("Creating engineered features using FeatureEngineer...")

        from services.feature_engineering import FeatureEngineer
        df = FeatureEngineer.create_features(df)

        logger.info("Feature engineering completed.")

        return df

    def save_processed_data(self, df):
        """
        Save cleaned dataset.
        """
        output_path = (
            config.PROCESSED_DATA_DIR /
            "processed_energy_data.csv"
        )

        df.to_csv(output_path, index=False)

        logger.info(
            f"Processed dataset saved to:\n{output_path}"
        )

    def preprocess(self):
        """
        Complete preprocessing pipeline.
        """
        logger.info("=" * 60)
        logger.info("Starting Data Preprocessing Pipeline")
        logger.info("=" * 60)

        df = self.load_data()

        df = self.inspect_data(df)

        df = self.clean_data(df)

        df = self.create_datetime(df)

        df = self.engineer_features(df)

        self.save_processed_data(df)

        logger.info("=" * 60)
        logger.info("Data Preprocessing Completed Successfully")
        logger.info("=" * 60)

        return df