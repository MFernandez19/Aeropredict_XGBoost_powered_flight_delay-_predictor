"""
Basic tests for the flight delay predictor modules.
"""
import unittest
import datetime
from pathlib import Path
import pandas as pd

# Import modules to test
import config
import validation
from utils import DataLoadingError, ModelLoadingError, EncoderLoadingError

class TestConfig(unittest.TestCase):
    """Test configuration module."""
    
    def test_paths_exist(self):
        """Test that all configured paths exist."""
        self.assertTrue(config.FLIGHTS_DATA_PATH.exists(), "Flights data file should exist")
        self.assertTrue(config.MODEL_PATH.exists(), "Model file should exist")
        self.assertTrue(config.INTERIM_DIR.exists(), "Interim directory should exist")
    
    def test_validate_paths(self):
        """Test path validation function."""
        self.assertTrue(config.validate_paths(), "All required paths should be valid")
    
    def test_encoder_paths(self):
        """Test encoder path generation."""
        for encoder in config.ENCODER_FILES:
            path = config.get_encoder_path(encoder)
            self.assertTrue(path.exists(), f"Encoder file {encoder} should exist")

class TestValidation(unittest.TestCase):
    """Test validation module."""
    
    def test_valid_time_input(self):
        """Test valid time inputs."""
        dep_time = datetime.time(9, 0)
        arr_time = datetime.time(16, 30)
        self.assertTrue(validation.validate_time_input(dep_time, arr_time))
    
    def test_invalid_time_input(self):
        """Test invalid time inputs."""
        # Same time
        dep_time = datetime.time(9, 0)
        arr_time = datetime.time(9, 0)
        with self.assertRaises(validation.ValidationError):
            validation.validate_time_input(dep_time, arr_time)
        
        # Too short flight
        dep_time = datetime.time(9, 0)
        arr_time = datetime.time(9, 15)
        with self.assertRaises(validation.ValidationError):
            validation.validate_time_input(dep_time, arr_time)
    
    def test_valid_distance(self):
        """Test valid distance inputs."""
        self.assertTrue(validation.validate_distance(500))
        self.assertTrue(validation.validate_distance(config.MIN_DISTANCE))
        self.assertTrue(validation.validate_distance(config.MAX_DISTANCE))
    
    def test_invalid_distance(self):
        """Test invalid distance inputs."""
        with self.assertRaises(validation.ValidationError):
            validation.validate_distance(config.MIN_DISTANCE - 1)
        
        with self.assertRaises(validation.ValidationError):
            validation.validate_distance(config.MAX_DISTANCE + 1)
    
    def test_valid_flight_date(self):
        """Test valid flight dates."""
        tomorrow = datetime.date.today() + datetime.timedelta(days=1)
        self.assertTrue(validation.validate_flight_date(tomorrow))
    
    def test_invalid_flight_date(self):
        """Test invalid flight dates."""
        # Past date
        yesterday = datetime.date.today() - datetime.timedelta(days=1)
        with self.assertRaises(validation.ValidationError):
            validation.validate_flight_date(yesterday)
        
        # Too far in future
        far_future = datetime.date.today() + datetime.timedelta(days=400)
        with self.assertRaises(validation.ValidationError):
            validation.validate_flight_date(far_future)
    
    def test_valid_route(self):
        """Test valid route inputs."""
        self.assertTrue(validation.validate_route(
            "California", "Los Angeles", "LAX",
            "New York", "New York", "JFK"
        ))
    
    def test_invalid_route(self):
        """Test invalid route inputs."""
        # Same airport
        with self.assertRaises(validation.ValidationError):
            validation.validate_route(
                "California", "Los Angeles", "LAX",
                "California", "Los Angeles", "LAX"
            )
        
        # Empty fields
        with self.assertRaises(validation.ValidationError):
            validation.validate_route(
                "", "Los Angeles", "LAX",
                "New York", "New York", "JFK"
            )

class TestUtils(unittest.TestCase):
    """Test utility functions."""
    
    def test_data_loading(self):
        """Test data loading functionality."""
        from utils import load_and_prepare_data
        try:
            data = load_and_prepare_data()
            self.assertIsInstance(data, pd.DataFrame)
            self.assertGreater(len(data), 0, "Data should not be empty")
            
            # Check required columns
            for col in config.REQUIRED_COLUMNS:
                self.assertIn(col, data.columns, f"Column {col} should be present")
        except DataLoadingError:
            self.fail("Data loading should not raise DataLoadingError with valid data")
    
    def test_encoders_loading(self):
        """Test encoder loading functionality."""
        from utils import load_encoders
        try:
            encoders = load_encoders()
            self.assertIsInstance(encoders, dict)
            self.assertGreater(len(encoders), 0, "Encoders should not be empty")
            
            # Check for expected encoder keys
            expected_keys = [name.split("_", 1)[1] for name in config.ENCODER_FILES]
            for key in expected_keys:
                self.assertIn(key, encoders, f"Encoder {key} should be present")
        except EncoderLoadingError:
            self.fail("Encoder loading should not raise EncoderLoadingError with valid encoders")
    
    def test_model_loading(self):
        """Test model loading functionality."""
        from utils import load_model
        try:
            model = load_model()
            self.assertIsNotNone(model, "Model should not be None")
            # Test that model has predict method
            self.assertTrue(hasattr(model, 'predict'), "Model should have predict method")
        except ModelLoadingError:
            self.fail("Model loading should not raise ModelLoadingError with valid model")

if __name__ == '__main__':
    # Run tests
    unittest.main(verbosity=2)