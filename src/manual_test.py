"""
Manual test script to verify core functionality without Streamlit UI.
"""
import datetime
import sys
from pathlib import Path

# Add current directory to path for imports
sys.path.append(str(Path(__file__).parent))

from utils import (
    load_and_prepare_data, load_encoders, load_model, create_mappings,
    encode_categorical_features, prepare_prediction_data, make_prediction
)
from validation import validate_all_inputs

def test_full_prediction_workflow():
    """Test the complete prediction workflow."""
    print("🧪 Testing complete prediction workflow...")
    
    # Load resources
    print("📊 Loading data...")
    data = load_and_prepare_data()
    print(f"   ✅ Data loaded: {data.shape[0]} rows, {data.shape[1]} columns")
    
    print("🔧 Loading encoders...")
    encoders = load_encoders()
    print(f"   ✅ Encoders loaded: {len(encoders)} encoders")
    
    print("🤖 Loading model...")
    model = load_model()
    print("   ✅ Model loaded successfully")
    
    print("🗺️ Creating mappings...")
    mappings = create_mappings(data)
    print("   ✅ Mappings created successfully")
    
    # Test with sample data
    print("\n🎯 Testing prediction with sample data...")
    
    # Get sample values from the data
    sample_airline = data["Airline"].iloc[0]
    sample_origin_state = data["OriginStateName"].iloc[0]
    sample_origin_city = data["OriginCityName"].iloc[0]
    sample_origin_airport = data["Origin"].iloc[0]
    
    # Find a different destination
    different_dest_idx = 1
    while (data["Dest"].iloc[different_dest_idx] == sample_origin_airport and 
           different_dest_idx < len(data) - 1):
        different_dest_idx += 1
    
    sample_dest_state = data["DestStateName"].iloc[different_dest_idx]
    sample_dest_city = data["DestCityName"].iloc[different_dest_idx]
    sample_dest_airport = data["Dest"].iloc[different_dest_idx]
    
    # Test data
    departure_time = datetime.time(9, 0)
    arrival_time = datetime.time(16, 30)
    distance = 2500
    flight_date = datetime.date.today() + datetime.timedelta(days=1)
    
    print(f"   📍 Origin: {sample_origin_state}, {sample_origin_city}, {sample_origin_airport}")
    print(f"   📍 Destination: {sample_dest_state}, {sample_dest_city}, {sample_dest_airport}")
    print(f"   ✈️ Airline: {sample_airline}")
    print(f"   🕘 Departure: {departure_time}, Arrival: {arrival_time}")
    print(f"   📏 Distance: {distance} miles")
    print(f"   📅 Date: {flight_date}")
    
    # Validate inputs
    available_airlines = sorted(data["Airline"].unique())
    is_valid, error_msg = validate_all_inputs(
        sample_airline, available_airlines,
        sample_origin_state, sample_origin_city, sample_origin_airport,
        sample_dest_state, sample_dest_city, sample_dest_airport,
        departure_time, arrival_time, distance, flight_date
    )
    
    if not is_valid:
        print(f"   ❌ Validation failed: {error_msg}")
        return False
    
    print("   ✅ Input validation passed")
    
    # Encode features
    encoded_categorical = encode_categorical_features(
        encoders, sample_airline, sample_origin_airport, sample_dest_airport,
        sample_origin_city, sample_dest_city, sample_origin_state, sample_dest_state
    )
    print("   ✅ Features encoded successfully")
    
    # Prepare prediction data
    day_of_month = flight_date.day
    month = flight_date.month
    day_of_week = flight_date.weekday() + 1
    quarter = (month - 1) // 3 + 1
    crs_dep_time = departure_time.hour * 100 + departure_time.minute
    crs_arr_time = arrival_time.hour * 100 + arrival_time.minute
    
    input_df = prepare_prediction_data(
        encoded_categorical, crs_dep_time, crs_arr_time, distance,
        quarter, month, day_of_month, day_of_week
    )
    print("   ✅ Prediction data prepared")
    
    # Make prediction
    try:
        prediction = make_prediction(model, input_df)
        result = "RETRASO PROBABLE" if prediction == 1 else "SIN RETRASO"
        print(f"   🔮 Prediction: {result} (value: {prediction})")
        print("   ✅ Prediction completed successfully")
        return True
    except Exception as e:
        print(f"   ❌ Prediction failed: {str(e)}")
        return False

def test_error_handling():
    """Test error handling with invalid inputs."""
    print("\n🛡️ Testing error handling...")
    
    # Test invalid date (past)
    past_date = datetime.date.today() - datetime.timedelta(days=1)
    is_valid, error_msg = validate_all_inputs(
        "Delta Air Lines", ["Delta Air Lines"], "California", "Los Angeles", "LAX",
        "New York", "New York", "JFK", datetime.time(9, 0), datetime.time(16, 30),
        2500, past_date
    )
    
    if is_valid:
        print("   ❌ Should have failed validation for past date")
        return False
    else:
        print(f"   ✅ Correctly caught past date error: {error_msg}")
    
    # Test invalid distance
    is_valid, error_msg = validate_all_inputs(
        "Delta Air Lines", ["Delta Air Lines"], "California", "Los Angeles", "LAX",
        "New York", "New York", "JFK", datetime.time(9, 0), datetime.time(16, 30),
        50,  # Too short distance
        datetime.date.today() + datetime.timedelta(days=1)
    )
    
    if is_valid:
        print("   ❌ Should have failed validation for invalid distance")
        return False
    else:
        print(f"   ✅ Correctly caught invalid distance error: {error_msg}")
    
    return True

if __name__ == "__main__":
    print("🚀 Starting manual functionality tests...\n")
    
    try:
        # Test main workflow
        workflow_success = test_full_prediction_workflow()
        
        # Test error handling
        error_handling_success = test_error_handling()
        
        if workflow_success and error_handling_success:
            print("\n🎉 All tests passed! The application is working correctly.")
        else:
            print("\n❌ Some tests failed. Check the output above for details.")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n💥 Unexpected error during testing: {str(e)}")
        sys.exit(1)