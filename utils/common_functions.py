import os
import pandas as pd
from src.logger import get_logger
from src.custom_exception import CustomException
import yaml

logger = get_logger(__name__)

def read_yaml(file_path: str) -> dict:
    try:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"YAML file not found in: {file_path}")
        with open(file_path, "r") as yaml_file:
            config = yaml.safe_load(yaml_file)
            logger.info("Successfully read the YAML file.")
            return config
    except Exception as e:
        logger.error(f"Error reading YAML file: {e}")
        raise CustomException("Failed to read YAML file", e)
    

def load_data(path):
    try:
        logger.info(f"Loading data")
        return pd.read_csv(path)
    except Exception as e:
        logger.error(f"Error loading the data {e}")
        raise CustomException(f"Fail to Load data", e)