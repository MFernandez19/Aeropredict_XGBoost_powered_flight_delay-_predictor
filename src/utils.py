"""
Utility functions for data loading, model operations, and encoders.
"""
import json
import pickle
import pandas as pd
import streamlit as st
from pathlib import Path
from typing import Dict, List, Tuple, Any, Optional
import logging

from config import (
    FLIGHTS_DATA_PATH, MODEL_PATH, REQUIRED_COLUMNS, 
    ENCODER_FILES, get_encoder_path
)

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class DataLoadingError(Exception):
    """Custom exception for data loading errors."""
    pass

class ModelLoadingError(Exception):
    """Custom exception for model loading errors."""
    pass

class EncoderLoadingError(Exception):
    """Custom exception for encoder loading errors."""
    pass

@st.cache_resource
def load_and_prepare_data(file_path: Path = FLIGHTS_DATA_PATH) -> pd.DataFrame:
    """
    Load and prepare the flights dataset.
    
    Args:
        file_path: Path to the parquet file
        
    Returns:
        Cleaned DataFrame with required columns
        
    Raises:
        DataLoadingError: If file cannot be loaded or processed
    """
    try:
        logger.info(f"Loading data from {file_path}")
        df = pd.read_parquet(file_path)
        
        # Check if required columns exist
        missing_columns = [col for col in REQUIRED_COLUMNS if col not in df.columns]
        if missing_columns:
            raise DataLoadingError(f"Missing required columns: {missing_columns}")
        
        # Select and clean data
        df = df[REQUIRED_COLUMNS].drop_duplicates().dropna()
        logger.info(f"Data loaded successfully. Shape: {df.shape}")
        return df
        
    except FileNotFoundError:
        raise DataLoadingError(f"Data file not found: {file_path}")
    except Exception as e:
        raise DataLoadingError(f"Error loading data: {str(e)}")

@st.cache_resource
def load_encoders() -> Dict[str, Dict[str, int]]:
    """
    Load all label encoders from JSON files.
    
    Returns:
        Dictionary mapping encoder names to their label mappings
        
    Raises:
        EncoderLoadingError: If encoders cannot be loaded
    """
    encoders = {}
    
    try:
        for encoder_file in ENCODER_FILES:
            encoder_path = get_encoder_path(encoder_file)
            
            if not encoder_path.exists():
                raise EncoderLoadingError(f"Encoder file not found: {encoder_path}")
            
            with open(encoder_path, "r") as f:
                encoder_data = json.load(f)
                # Extract the actual encoder name (remove 'enc_' prefix)
                encoder_name = encoder_file.split("_", 1)[1]
                encoders[encoder_name] = encoder_data
                
        logger.info(f"Loaded {len(encoders)} encoders successfully")
        return encoders
        
    except json.JSONDecodeError as e:
        raise EncoderLoadingError(f"Invalid JSON in encoder file: {str(e)}")
    except Exception as e:
        raise EncoderLoadingError(f"Error loading encoders: {str(e)}")

@st.cache_resource
def load_model(model_path: Path = MODEL_PATH) -> Any:
    """
    Load the trained XGBoost model.
    
    Args:
        model_path: Path to the pickle model file
        
    Returns:
        Loaded model object
        
    Raises:
        ModelLoadingError: If model cannot be loaded
    """
    try:
        logger.info(f"Loading model from {model_path}")
        
        if not model_path.exists():
            raise ModelLoadingError(f"Model file not found: {model_path}")
        
        with open(model_path, "rb") as file:
            model = pickle.load(file)
            
        logger.info("Model loaded successfully")
        return model
        
    except Exception as e:
        raise ModelLoadingError(f"Error loading model: {str(e)}")

@st.cache_resource
def create_mappings(data: pd.DataFrame) -> Tuple[Dict[str, List[str]], ...]:
    """
    Create dynamic mappings for cascading dropdown selections.
    
    Args:
        data: DataFrame containing flight data
        
    Returns:
        Tuple of mapping dictionaries for UI selections
    """
    try:
        state_to_city_mapping = data.groupby("OriginStateName")["OriginCityName"].apply(
            lambda x: sorted(list(set(x)))
        ).to_dict()
        
        city_to_airport_mapping = data.groupby("OriginCityName")["Origin"].apply(
            lambda x: sorted(list(set(x)))
        ).to_dict()
        
        dest_state_to_city_mapping = data.groupby("DestStateName")["DestCityName"].apply(
            lambda x: sorted(list(set(x)))
        ).to_dict()
        
        dest_city_to_airport_mapping = data.groupby("DestCityName")["Dest"].apply(
            lambda x: sorted(list(set(x)))
        ).to_dict()
        
        logger.info("Mappings created successfully")
        return (
            state_to_city_mapping,
            city_to_airport_mapping,
            dest_state_to_city_mapping,
            dest_city_to_airport_mapping
        )
        
    except Exception as e:
        logger.error(f"Error creating mappings: {str(e)}")
        raise DataLoadingError(f"Error creating mappings: {str(e)}")

def encode_categorical_features(
    encoders: Dict[str, Dict[str, int]],
    airline: str,
    origin_airport: str,
    dest_airport: str,
    origin_city: str,
    dest_city: str,
    origin_state: str,
    dest_state: str
) -> Dict[str, int]:
    """
    Encode categorical features using the loaded encoders.
    
    Args:
        encoders: Dictionary of encoder mappings
        airline, origin_airport, dest_airport, origin_city, 
        dest_city, origin_state, dest_state: Categorical values to encode
        
    Returns:
        Dictionary of encoded values
        
    Raises:
        ValueError: If encoding fails for any feature
    """
    try:
        encoded_values = {
            "Airline": encoders["Airline"].get(airline, -1),
            "Origin": encoders["Origin"].get(origin_airport, -1),
            "Dest": encoders["Dest"].get(dest_airport, -1),
            "OriginCityName": encoders["OriginCityName"].get(origin_city, -1),
            "DestCityName": encoders["DestCityName"].get(dest_city, -1),
            "OriginStateName": encoders["OriginStateName"].get(origin_state, -1),
            "DestStateName": encoders["DestStateName"].get(dest_state, -1),
        }
        
        # Check for any failed encodings
        failed_encodings = [k for k, v in encoded_values.items() if v == -1]
        if failed_encodings:
            logger.warning(f"Failed to encode: {failed_encodings}")
        
        return encoded_values
        
    except Exception as e:
        raise ValueError(f"Error encoding categorical features: {str(e)}")

def prepare_prediction_data(
    encoded_categorical: Dict[str, int],
    crs_dep_time: int,
    crs_arr_time: int,
    distance: int,
    quarter: int,
    month: int,
    day_of_month: int,
    day_of_week: int
) -> pd.DataFrame:
    """
    Prepare the input data for model prediction.
    
    Args:
        encoded_categorical: Encoded categorical features
        crs_dep_time, crs_arr_time: Scheduled departure and arrival times
        distance: Flight distance
        quarter, month, day_of_month, day_of_week: Date features
        
    Returns:
        DataFrame ready for model prediction
    """
    input_data = {
        **encoded_categorical,
        "CRSDepTime": crs_dep_time,
        "CRSArrTime": crs_arr_time,
        "Distance": distance,
        "Quarter": quarter,
        "Month": month,
        "DayofMonth": day_of_month,
        "DayOfWeek": day_of_week,
    }
    
    return pd.DataFrame([input_data])

def make_prediction(model: Any, input_data: pd.DataFrame) -> int:
    """
    Make a delay prediction using the trained model.
    
    Args:
        model: Trained ML model
        input_data: DataFrame with features for prediction
        
    Returns:
        Prediction result (0 = no delay, 1 = delay)
        
    Raises:
        ValueError: If prediction fails
    """
    try:
        prediction = model.predict(input_data)
        return int(prediction[0])
    except Exception as e:
        raise ValueError(f"Error making prediction: {str(e)}")