"""
Database Utility Layer
Energy Optimization Agent
"""

import sqlite3
import pandas as pd
from backend.config import config
from services.logger import setup_logger

logger = setup_logger("Database")


class DatabaseManager:
    """
    Manages SQLite database connections, schema initialization,
    and data storage/retrieval for energy consumption data.
    """

    @staticmethod
    def get_connection():
        """Get a connection to the SQLite database."""
        # Ensure parent directory exists
        config.DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)
        return sqlite3.connect(str(config.DATABASE_PATH))

    @staticmethod
    def initialize_db():
        """Create the energy_data table and index if they do not exist."""
        logger.info("Initializing database schema...")
        conn = DatabaseManager.get_connection()
        cursor = conn.cursor()
        try:
            # We define the schema. We store Datetime as TEXT for SQLite.
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS energy_data (
                    Datetime TEXT PRIMARY KEY,
                    Global_active_power REAL,
                    Global_reactive_power REAL,
                    Voltage REAL,
                    Global_intensity REAL,
                    Sub_metering_1 REAL,
                    Sub_metering_2 REAL,
                    Sub_metering_3 REAL,
                    Hour INTEGER,
                    Day INTEGER,
                    Month INTEGER,
                    Weekday TEXT,
                    Is_Weekend INTEGER
                )
            """)
            # Create an index on Datetime to speed up lookups
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_datetime ON energy_data(Datetime)")
            conn.commit()
            logger.info("Database initialized successfully.")
        except Exception as e:
            logger.error(f"Error initializing database: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def save_data(df: pd.DataFrame):
        """
        Save the processed Pandas DataFrame to the SQLite database.
        """
        logger.info(f"Saving {len(df):,} records to database...")
        conn = DatabaseManager.get_connection()
        try:
            # Ensure Datetime is stored as string in ISO format
            df_to_save = df.copy()
            if pd.api.types.is_datetime64_any_dtype(df_to_save["Datetime"]):
                df_to_save["Datetime"] = df_to_save["Datetime"].dt.strftime("%Y-%m-%d %H:%M:%S")

            # Write DataFrame to SQLite using pandas to_sql
            df_to_save.to_sql("energy_data", conn, if_exists="replace", index=False)
            
            # Since to_sql with if_exists="replace" drops the table, we re-initialize the indexes
            cursor = conn.cursor()
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_datetime ON energy_data(Datetime)")
            conn.commit()
            logger.info("Data saved and index recreated successfully.")
        except Exception as e:
            logger.error(f"Error saving data to database: {e}")
            raise e
        finally:
            conn.close()

    @staticmethod
    def get_data() -> pd.DataFrame:
        """
        Retrieve all energy data from the SQLite database as a Pandas DataFrame.
        """
        logger.info("Retrieving energy data from database...")
        conn = DatabaseManager.get_connection()
        try:
            df = pd.read_sql_query("SELECT * FROM energy_data", conn, parse_dates=["Datetime"])
            logger.info(f"Retrieved {len(df):,} records from database.")
            return df
        except Exception as e:
            logger.error(f"Error retrieving data from database: {e}")
            raise e
        finally:
            conn.close()
