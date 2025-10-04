import os 
import pandas as pd
from boto3.session import Session
import boto3
from sklearn.model_selection import train_test_split
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml

logger = get_logger(__name__)

class DataIngestion:
    def __init__(self, config):
        self.config = config["data_ingestion"]
        self.bucket_name = self.config["bucket_name"]
        self.file_name = self.config["bucket_file_name"]
        self.train_test_ratio = self.config["train_ratio"]

        os.makedirs(RAW_DIR, exist_ok=True)

        logger.info(f"Data Ingestion Started with {self.bucket_name} and file is {self.file_name}")

    
    def download_csv_from_s3(self):
        try:
            session = Session()
            s3_resource = session.resource('s3')
            s3_client = session.client('s3')

            # Quick head_object to verify existence & region/permissions
            try:
                s3_client.head_object(Bucket=self.bucket_name, Key=self.file_name)
                # If head_object succeeds, download the exact key
                s3_resource.Bucket(self.bucket_name).download_file(self.file_name, RAW_FILE_PATH)
                logger.info(f"File downloaded successfully from S3: {self.file_name} to {RAW_FILE_PATH}")
                return
            except Exception as head_exc:
                logger.error(f"HeadObject failed for s3://{self.bucket_name}/{self.file_name}: {head_exc}")
                # Try listing objects with the same prefix to help debugging and attempt matches
                prefix = os.path.dirname(self.file_name) if "/" in self.file_name else ""
                logger.info(f"Listing objects with prefix '{prefix}' to help debugging")
                objs = s3_resource.Bucket(self.bucket_name).objects.filter(Prefix=prefix)
                found = [o.key for o in objs]
                logger.info(f"Objects found (sample up to 50): {found[:50]}")

                # Attempt to find a close match: exact case-insensitive, spaces/underscores swapped
                target_lower = self.file_name.lower()
                matched = None
                for k in found:
                    if k.lower() == target_lower:
                        matched = k
                        break
                if not matched:
                    alt1 = self.file_name.replace("_", " ").lower()
                    alt2 = self.file_name.replace(" ", "_").lower()
                    for k in found:
                        kl = k.lower()
                        if kl == alt1 or kl == alt2:
                            matched = k
                            break

                if matched:
                    logger.info(f"Matched object key '{matched}' for requested '{self.file_name}'. Downloading matched key.")
                    s3_resource.Bucket(self.bucket_name).download_file(matched, RAW_FILE_PATH)
                    logger.info(f"File downloaded successfully from S3: {matched} to {RAW_FILE_PATH}")
                    return

                raise CustomException("S3 object not found or inaccessible", head_exc)

            # unreachable
        except CustomException:
            raise
        except Exception as e:
            logger.exception("Error while downloading file from S3")
            raise CustomException("Error while downloading file from S3", e)
    

    def split_data(self):
        try:
            logger.info(f"Starting the data split process")
            df = pd.read_csv(RAW_FILE_PATH)
            train_df, test_df = train_test_split(df, train_size=self.train_test_ratio, random_state=42)
            train_df.to_csv(TRAIN_FILE_PATH)
            test_df.to_csv(TEST_FILE_PATH)
            logger.info(f"Train data saved to {TRAIN_FILE_PATH}")
            logger.info(f"Test data saved to {TEST_FILE_PATH}")
        except Exception as e:
            logger.error(f"Error while splitting data: {e}")
            raise CustomException("Error while splitting data", e)
    
    def run(self):
        try:
            logger.info("Starting data ingestion process")
            self.download_csv_from_s3()
            self.split_data()
            logger.info("Data ingestion completed successfully")
        except CustomException as ce:
            logger.error(f"CustomException : {str(ce)}")
        finally:
            logger.info("Data ingestion completed")


if __name__ == "__main__":
    data_ingestion = DataIngestion(read_yaml(CONFIG_PATH))
    data_ingestion.run()