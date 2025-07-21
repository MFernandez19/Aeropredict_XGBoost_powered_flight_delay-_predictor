"""
Input validation functions for the flight delay predictor.
"""
import datetime
from typing import Optional, Tuple, List

from config import MIN_DISTANCE, MAX_DISTANCE

class ValidationError(Exception):
    """Custom exception for validation errors."""
    pass

def validate_time_input(departure_time: datetime.time, arrival_time: datetime.time) -> bool:
    """
    Validate that departure and arrival times are reasonable.
    
    Args:
        departure_time: Scheduled departure time
        arrival_time: Scheduled arrival time
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If times are invalid
    """
    # Convert to minutes for easier comparison
    dep_minutes = departure_time.hour * 60 + departure_time.minute
    arr_minutes = arrival_time.hour * 60 + arrival_time.minute
    
    # Allow for flights that arrive the next day (add 24 hours)
    if arr_minutes < dep_minutes:
        arr_minutes += 24 * 60
    
    flight_duration = arr_minutes - dep_minutes
    
    # Validate reasonable flight duration (30 minutes to 20 hours)
    if flight_duration < 30:
        raise ValidationError("El vuelo debe durar al menos 30 minutos")
    
    if flight_duration > 20 * 60:  # 20 hours
        raise ValidationError("El vuelo no puede durar más de 20 horas")
    
    return True

def validate_distance(distance: int) -> bool:
    """
    Validate flight distance.
    
    Args:
        distance: Flight distance in miles
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If distance is invalid
    """
    if not MIN_DISTANCE <= distance <= MAX_DISTANCE:
        raise ValidationError(
            f"La distancia debe estar entre {MIN_DISTANCE} y {MAX_DISTANCE} millas"
        )
    
    return True

def validate_flight_date(flight_date: datetime.date) -> bool:
    """
    Validate flight date.
    
    Args:
        flight_date: Selected flight date
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If date is invalid
    """
    today = datetime.date.today()
    
    # Allow dates from today up to 1 year in the future
    max_future_date = today + datetime.timedelta(days=365)
    
    if flight_date < today:
        raise ValidationError("La fecha del vuelo no puede ser en el pasado")
    
    if flight_date > max_future_date:
        raise ValidationError("La fecha del vuelo no puede ser más de un año en el futuro")
    
    return True

def validate_route(origin_state: str, origin_city: str, origin_airport: str,
                  dest_state: str, dest_city: str, dest_airport: str) -> bool:
    """
    Validate flight route selection.
    
    Args:
        origin_state, origin_city, origin_airport: Origin location details
        dest_state, dest_city, dest_airport: Destination location details
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If route is invalid
    """
    # Check that origin and destination are different
    if origin_airport == dest_airport:
        raise ValidationError("El aeropuerto de origen y destino deben ser diferentes")
    
    # Validate that selections are not empty
    required_fields = [
        (origin_state, "estado de origen"),
        (origin_city, "ciudad de origen"),
        (origin_airport, "aeropuerto de origen"),
        (dest_state, "estado de destino"),
        (dest_city, "ciudad de destino"),
        (dest_airport, "aeropuerto de destino")
    ]
    
    for field_value, field_name in required_fields:
        if not field_value or field_value.strip() == "":
            raise ValidationError(f"Debe seleccionar un {field_name}")
    
    return True

def validate_airline(airline: str, available_airlines: List[str]) -> bool:
    """
    Validate airline selection.
    
    Args:
        airline: Selected airline
        available_airlines: List of available airlines
        
    Returns:
        True if valid
        
    Raises:
        ValidationError: If airline is invalid
    """
    if not airline or airline.strip() == "":
        raise ValidationError("Debe seleccionar una aerolínea")
    
    if airline not in available_airlines:
        raise ValidationError("La aerolínea seleccionada no es válida")
    
    return True

def validate_all_inputs(
    airline: str,
    available_airlines: List[str],
    origin_state: str,
    origin_city: str,
    origin_airport: str,
    dest_state: str,
    dest_city: str,
    dest_airport: str,
    departure_time: datetime.time,
    arrival_time: datetime.time,
    distance: int,
    flight_date: datetime.date
) -> Tuple[bool, Optional[str]]:
    """
    Validate all user inputs.
    
    Args:
        All input parameters from the UI
        
    Returns:
        Tuple of (is_valid, error_message)
    """
    try:
        validate_airline(airline, available_airlines)
        validate_route(origin_state, origin_city, origin_airport,
                      dest_state, dest_city, dest_airport)
        validate_time_input(departure_time, arrival_time)
        validate_distance(distance)
        validate_flight_date(flight_date)
        
        return True, None
        
    except ValidationError as e:
        return False, str(e)
    except Exception as e:
        return False, f"Error de validación inesperado: {str(e)}"