import sqlite3
import logging

from app.entities.processed_agent_data import ProcessedAgentDataInDB

logger = logging.getLogger(__name__)

class SQLiteHubGateway:
    
    def __init__(self, db_path: str = "agent_data.db"):
        self.db_path = db_path
        self._initialize_database()

    def _initialize_database(self):
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS agent_data (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        road_state TEXT NOT NULL,
                        x REAL NOT NULL,
                        y REAL NOT NULL,
                        z REAL NOT NULL,
                        latitude REAL NOT NULL,
                        longitude REAL NOT NULL,
                        timestamp TEXT NOT NULL
                    )
                """)
                conn.commit()
                logger.info("Database initialized successfully")
        except sqlite3.Error as e:
            logger.error(f"Failed to initialize database: {e}")
            raise

    def save_data(self, processed_data: ProcessedAgentDataInDB) -> bool:
        """
        Save the processed agent data in the SQLite database.

        Parameters:
        processed_data (ProcessedAgentDataInDB): The processed agent data to be saved.

        Returns:
        bool: True if the data is successfully saved, False otherwise.
        """
        try:
            data_dict = processed_data.model_dump()
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute("""
                    INSERT OR REPLACE INTO agent_data (
                        id, road_state, x, y, z, latitude, longitude, timestamp
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    data_dict["id"],
                    data_dict["road_state"],
                    data_dict["x"],
                    data_dict["y"],
                    data_dict["z"],
                    data_dict["latitude"],
                    data_dict["longitude"],
                    data_dict["timestamp"].isoformat()
                ))
                conn.commit()
                logger.info(f"Successfully saved data with ID: {data_dict['id']}")
                return True
        except sqlite3.Error as e:
            logger.error(f"Failed to save data: {e}")
            return False
        except AttributeError as e:
            logger.error(f"Invalid ProcessedAgentDataInDB object: {e}")
            return False