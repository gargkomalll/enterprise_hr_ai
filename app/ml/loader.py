import os
import joblib
from app.utils.config import settings
from app.utils.logger import logger

class ModelLoader:
    _instance = None
    _pipeline = None

    @classmethod
    def get_pipeline(cls):
        if cls._pipeline is None:
            model_path = os.path.abspath(settings.MODEL_PATH)
            if not os.path.exists(model_path):
                logger.error(f"Model file not found at: {model_path}")
                raise FileNotFoundError(f"Model file not found at {model_path}")
            cls._pipeline = joblib.load(model_path)
            logger.info(f"Loaded ML model pipeline successfully from {model_path}")
        return cls._pipeline
