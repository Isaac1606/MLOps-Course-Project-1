import os 
import pandas as pd
import numpy as np
from src.logger import get_logger
from src.custom_exception import CustomException
from config.paths_config import *
from utils.common_functions import read_yaml, load_data
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE

logger = get_logger(__name__)


class DataProcessor:
    """
    DataProcessor is a class for handling data preprocessing tasks in a machine learning pipeline.
    Attributes:
        train_path (str): Path to the training data file.
        test_path (str): Path to the test data file.
        processed_dir (str): Directory where processed data will be saved.
        config (dict): Configuration parameters loaded from a YAML file.
    Methods:
        preprocess_data(df):
            Cleans and preprocesses the input DataFrame by dropping unnecessary columns, removing duplicates,
            encoding categorical variables, and handling skewness in numerical features.
        balance_data(df):
            Balances the dataset using SMOTE to address class imbalance in the target variable.
        select_features(df):
            Selects the most important features using a RandomForestClassifier based on feature importance scores.
        save_data(df, file_path):
            Saves the processed DataFrame to the specified file path as a CSV file.
    """
    def __init__(self, train_path, test_path, processed_dir, config_path):
        self.train_path = train_path
        self.test_path = test_path
        self.processed_dir = processed_dir
        self.config = read_yaml(config_path)

        if not os.path.exists(self.processed_dir):
            os.makedirs(self.processed_dir)


    def preprocess_data(self, df):
        try:
            logger.info("Starting our Data Processing step")
            logger.info("Dropping the columns")
            df.drop(columns=['Unnamed: 0', 'Booking_ID'], inplace=True)
            df.drop_duplicates(inplace=True)
            cat_cols = self.config["data_processing"]["categorical_columns"]
            num_cols = self.config["data_processing"]["numerical_columns"]
            logger.info("Applying Label Encoding")

            label_encoder = LabelEncoder()
            mappings = {}
            for col in cat_cols:
                df[col] = label_encoder.fit_transform(df[col])
                mappings[col] = dict(zip(label_encoder.classes_, label_encoder.transform(label_encoder.classes_)))
            logger.info(f"Label Encoding Mappings")
            for col, mapping in mappings.items():
                logger.info(f"{col}: {mapping}")

            logger.info("Doing skewness handling")
            skew_threshold = self.config["data_processing"]["skewness_threshold"]
            skewness = df[num_cols].apply(lambda x: x.skew())

            for col in skewness[skewness>skew_threshold].index:
                df[col] = np.log1p(df[col])

            return df
        
        except Exception as e:
            logger.error(f"Error during preprocess step: {e}")
            raise CustomException("Error occurred during data preprocessing", e)


    def balance_data(self, df):
        try:
            logger.info("Starting data balancing")
            X = df.drop(columns=['booking_status'])
            y = df['booking_status']

            smote = SMOTE(random_state=42)
            X_resampled, y_resampled = smote.fit_resample(X, y)

            balanced_df = pd.DataFrame(X_resampled, columns=X.columns)
            balanced_df["booking_status"] = y_resampled

            logger.info("Data balancing completed")
            
            return balanced_df

        except Exception as e:
            logger.error(f"Error during balance step: {e}")
            raise CustomException("Error occurred during data balancing", e)


    def select_features(self, df):
        try:
            logger.info("Starting feature selection")

            X = df.drop(columns=['booking_status'])
            y = df['booking_status']

            model = RandomForestClassifier(random_state=42)
            model.fit(X, y)

            feature_importance_df = pd.DataFrame({
                'feature': X.columns,
                'importance': model.feature_importances_
            })

            top_features_importance_df = feature_importance_df.sort_values(by="importance", ascending=False)

            num_features_to_select = self.config['data_processing']['no_of_features']

            top_n_features = top_features_importance_df["feature"].head(num_features_to_select).values

            logger.info(f"Top {num_features_to_select} Features: {top_n_features}")

            top_n_df = df[top_n_features.tolist() + ['booking_status']]

            logger.info(f"Feature selection completed successfully")

            return top_n_df

        except Exception as e:
            logger.error(f"Error during feature selection: {e}")
            raise CustomException("Error occurred during feature selection", e)
        

    def save_data(self, df, file_path):
        try:
            logger.info("Saving our data in processed folder")
            df.to_csv(file_path, index=False)
            logger.info("Data saved successfully")
        except Exception as e:
            logger.error(f"Error during save step: {e}")
            raise CustomException("Error occurred during data saving", e)
        
    def process(self):
        try:
            logger.info("Loading data from RAW directory")

            train_df = load_data(self.train_path)
            test_df = load_data(self.test_path)

            # Preprocess the data
            train_df = self.preprocess_data(train_df)
            test_df = self.preprocess_data(test_df)

            # Balance the data
            train_df = self.balance_data(train_df)

            # Feature selection
            train_df = self.select_features(train_df)
            test_df = test_df[train_df.columns]

            # Save the processed data
            self.save_data(train_df, PROCESSED_TRAIN_DATA_PATH)
            self.save_data(test_df, PROCESSED_TEST_DATA_PATH)

            logger.info("Data processing completed successfully")

        except Exception as e:
            logger.error(f"Error during preprocessing pipeline: {e}")
            raise CustomException("Error occurred during data preprocessing pipeline", e)


if __name__ == "__main__":
    processor = DataProcessor(TRAIN_FILE_PATH, TEST_FILE_PATH, PROCESSED_DIR, CONFIG_PATH)
    processor.process()
    