"""
Configuration module for the Aeropredict flight delay predictor.
Centralizes file paths and application settings.
"""
import os
from pathlib import Path
from typing import List

# Base directory paths
BASE_DIR = Path(__file__).parent
DATA_DIR = BASE_DIR.parent / "data"
INTERIM_DIR = DATA_DIR / "interim"
MODELS_DIR = BASE_DIR.parent / "models"

# Data file paths
FLIGHTS_DATA_PATH = BASE_DIR / "Combined_Flights_2021_streamlit.parquet"
MODEL_PATH = BASE_DIR / "best_model_xgb_subsample_1.0_n_estimators_200_max_depth_10_learning_rate_0.2_gamma_0.1_colsample_bytree_0.8.pkl"

# Required columns for the application
REQUIRED_COLUMNS: List[str] = [
    "Airline", "Origin", "Dest", "OriginCityName", "DestCityName",
    "OriginStateName", "DestStateName"
]

# Encoder file names
ENCODER_FILES: List[str] = [
    "enc_Airline", "enc_Origin", "enc_Dest", 
    "enc_OriginCityName", "enc_DestCityName", 
    "enc_OriginStateName", "enc_DestStateName"
]

# Application settings
DEFAULT_DEPARTURE_HOUR = 9
DEFAULT_DEPARTURE_MINUTE = 0
DEFAULT_ARRIVAL_HOUR = 16
DEFAULT_ARRIVAL_MINUTE = 30
DEFAULT_DISTANCE = 2500
MIN_DISTANCE = 100
MAX_DISTANCE = 5000

# UI Configuration
APP_TITLE = "Predicción de Retrasos en Vuelos"
SIDEBAR_HEADER = "Introducir características del vuelo"

def get_encoder_path(encoder_name: str) -> Path:
    """Get the full path for an encoder file."""
    return INTERIM_DIR / f"{encoder_name}.json"

def validate_paths() -> bool:
    """Validate that all required files exist."""
    required_paths = [
        FLIGHTS_DATA_PATH,
        MODEL_PATH,
        INTERIM_DIR
    ]
    
    for path in required_paths:
        if not path.exists():
            return False
    
    # Check encoder files
    for encoder in ENCODER_FILES:
        if not get_encoder_path(encoder).exists():
            return False
    
    return True