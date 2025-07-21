"""
Flight Delay Prediction App using XGBoost and Streamlit.

This application predicts flight delays based on various flight characteristics
including airline, origin/destination, scheduled times, and flight date.
"""
import pandas as pd
import streamlit as st
import datetime
import logging
from typing import Optional

# Import custom modules
from config import (
    APP_TITLE, SIDEBAR_HEADER, DEFAULT_DEPARTURE_HOUR, DEFAULT_DEPARTURE_MINUTE,
    DEFAULT_ARRIVAL_HOUR, DEFAULT_ARRIVAL_MINUTE, DEFAULT_DISTANCE, validate_paths
)
from utils import (
    load_and_prepare_data, load_encoders, load_model, create_mappings,
    encode_categorical_features, prepare_prediction_data, make_prediction,
    DataLoadingError, ModelLoadingError, EncoderLoadingError
)
from validation import validate_all_inputs

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_app() -> tuple:
    """
    Initialize the application by loading all required resources.
    
    Returns:
        Tuple containing (data, encoders, model, mappings)
        
    Raises:
        Exception: If initialization fails
    """
    try:
        # Validate that all required files exist
        if not validate_paths():
            st.error("❌ Faltan archivos requeridos. Verifique la configuración del proyecto.")
            st.stop()
        
        # Load resources
        data = load_and_prepare_data()
        encoders = load_encoders()
        model = load_model()
        mappings = create_mappings(data)
        
        logger.info("Application initialized successfully")
        return data, encoders, model, mappings
        
    except (DataLoadingError, EncoderLoadingError, ModelLoadingError) as e:
        st.error(f"❌ Error de inicialización: {str(e)}")
        st.stop()
    except Exception as e:
        st.error(f"❌ Error inesperado durante la inicialización: {str(e)}")
        logger.error(f"Unexpected initialization error: {str(e)}")
        st.stop()

# Initialize application resources
data, encoders, model, (
    state_to_city_mapping, 
    city_to_airport_mapping, 
    dest_state_to_city_mapping, 
    dest_city_to_airport_mapping
) = initialize_app()

# Streamlit UI
st.title(APP_TITLE)

# Add information about the app
with st.expander("ℹ️ Información sobre la aplicación"):
    st.write("""
    Esta aplicación utiliza un modelo XGBoost entrenado para predecir retrasos en vuelos
    basándose en características como aerolínea, origen, destino, horarios y fecha del vuelo.
    
    **Instrucciones:**
    1. Seleccione el estado y ciudad de origen, luego el aeropuerto
    2. Seleccione el estado y ciudad de destino, luego el aeropuerto  
    3. Elija la aerolínea y configure los horarios del vuelo
    4. Ingrese la distancia del vuelo y seleccione la fecha
    5. Haga clic en "Predecir retraso" para obtener la predicción
    """)

# Sidebar for user input
st.sidebar.header(SIDEBAR_HEADER)

# Origin selection with cascading dropdowns
st.sidebar.subheader("🛫 Origen")
origin_state = st.sidebar.selectbox(
    "Estado de origen", 
    list(state_to_city_mapping.keys()),
    help="Seleccione el estado donde se originará el vuelo"
)

origin_city_options = state_to_city_mapping.get(origin_state, [])
if not origin_city_options:
    st.sidebar.error("No hay ciudades disponibles para el estado seleccionado")
    st.stop()

origin_city = st.sidebar.selectbox(
    "Ciudad de origen", 
    origin_city_options,
    help="Seleccione la ciudad de origen"
)

origin_airport_options = city_to_airport_mapping.get(origin_city, [])
if not origin_airport_options:
    st.sidebar.error("No hay aeropuertos disponibles para la ciudad seleccionada")
    st.stop()

origin_airport = st.sidebar.selectbox(
    "Aeropuerto de origen", 
    origin_airport_options,
    help="Seleccione el aeropuerto de origen"
)

# Destination selection with cascading dropdowns
st.sidebar.subheader("🛬 Destino")
dest_state = st.sidebar.selectbox(
    "Estado de destino", 
    list(dest_state_to_city_mapping.keys()),
    help="Seleccione el estado de destino"
)

dest_city_options = dest_state_to_city_mapping.get(dest_state, [])
if not dest_city_options:
    st.sidebar.error("No hay ciudades disponibles para el estado seleccionado")
    st.stop()

dest_city = st.sidebar.selectbox(
    "Ciudad de destino", 
    dest_city_options,
    help="Seleccione la ciudad de destino"
)

dest_airport_options = dest_city_to_airport_mapping.get(dest_city, [])
if not dest_airport_options:
    st.sidebar.error("No hay aeropuertos disponibles para la ciudad seleccionada")
    st.stop()

dest_airport = st.sidebar.selectbox(
    "Aeropuerto de destino", 
    dest_airport_options,
    help="Seleccione el aeropuerto de destino"
)

# Flight details
st.sidebar.subheader("✈️ Detalles del vuelo")
airline = st.sidebar.selectbox(
    "Aerolínea", 
    sorted(data["Airline"].unique()),
    help="Seleccione la aerolínea"
)

departure_time = st.sidebar.time_input(
    "Hora de salida (24h)", 
    value=datetime.time(DEFAULT_DEPARTURE_HOUR, DEFAULT_DEPARTURE_MINUTE),
    help="Hora programada de salida en formato 24 horas"
)

arrival_time = st.sidebar.time_input(
    "Hora de llegada (24h)", 
    value=datetime.time(DEFAULT_ARRIVAL_HOUR, DEFAULT_ARRIVAL_MINUTE),
    help="Hora programada de llegada en formato 24 horas"
)

distance = st.sidebar.number_input(
    "Distancia (en millas)", 
    min_value=100, 
    max_value=5000, 
    value=DEFAULT_DISTANCE,
    help="Distancia del vuelo en millas"
)

flight_date = st.sidebar.date_input(
    "Fecha del vuelo", 
    min_value=datetime.date.today(),
    help="Fecha del vuelo (no puede ser en el pasado)"
)

# Display flight summary
st.subheader("📋 Resumen del vuelo")
col1, col2 = st.columns(2)

with col1:
    st.write("**Origen:**")
    st.write(f"• Estado: {origin_state}")
    st.write(f"• Ciudad: {origin_city}")
    st.write(f"• Aeropuerto: {origin_airport}")
    st.write(f"• Hora de salida: {departure_time}")

with col2:
    st.write("**Destino:**")
    st.write(f"• Estado: {dest_state}")
    st.write(f"• Ciudad: {dest_city}")
    st.write(f"• Aeropuerto: {dest_airport}")
    st.write(f"• Hora de llegada: {arrival_time}")

st.write("**Otros detalles:**")
col3, col4, col5 = st.columns(3)
with col3:
    st.write(f"• Aerolínea: {airline}")
with col4:
    st.write(f"• Distancia: {distance} millas")
with col5:
    st.write(f"• Fecha: {flight_date}")

# Process input data for prediction
try:
    # Calculate date features
    day_of_month = flight_date.day
    month = flight_date.month
    day_of_week = flight_date.weekday() + 1  # Monday=1, Sunday=7
    quarter = (month - 1) // 3 + 1

    # Convert time to military format (HHMM)
    crs_dep_time = departure_time.hour * 100 + departure_time.minute
    crs_arr_time = arrival_time.hour * 100 + arrival_time.minute

    # Validate all inputs
    available_airlines = sorted(data["Airline"].unique())
    is_valid, validation_error = validate_all_inputs(
        airline, available_airlines, origin_state, origin_city, origin_airport,
        dest_state, dest_city, dest_airport, departure_time, arrival_time,
        distance, flight_date
    )

    if not is_valid:
        st.error(f"❌ Error de validación: {validation_error}")
        st.stop()

    # Encode categorical features
    encoded_categorical = encode_categorical_features(
        encoders, airline, origin_airport, dest_airport,
        origin_city, dest_city, origin_state, dest_state
    )

    # Check for encoding failures
    failed_encodings = [k for k, v in encoded_categorical.items() if v == -1]
    if failed_encodings:
        st.warning(f"⚠️ Advertencia: No se pudieron codificar algunas características: {failed_encodings}")

    # Prepare prediction data
    input_df = prepare_prediction_data(
        encoded_categorical, crs_dep_time, crs_arr_time, distance,
        quarter, month, day_of_month, day_of_week
    )

    # Show encoded data in expandable section
    with st.expander("🔍 Ver datos codificados para el modelo"):
        st.json(input_df.iloc[0].to_dict())

except Exception as e:
    st.error(f"❌ Error al procesar los datos: {str(e)}")
    logger.error(f"Data processing error: {str(e)}")
    st.stop()

# Prediction section
st.subheader("🔮 Predicción de retraso")

if st.button("🚀 Predecir retraso", type="primary", use_container_width=True):
    try:
        with st.spinner("Realizando predicción..."):
            # Make prediction
            prediction = make_prediction(model, input_df)
            
            # Display results
            if prediction == 0:
                st.success("✅ **¡Excelentes noticias!** Su vuelo tiene baja probabilidad de retraso.")
                st.balloons()
            else:
                st.warning("⚠️ **Atención:** Su vuelo tiene alta probabilidad de retraso. "
                          "Le recomendamos verificar el estado del vuelo antes de dirigirse al aeropuerto.")
            
            # Add some additional context
            st.info("💡 **Nota:** Esta predicción se basa en datos históricos y patrones de vuelo. "
                   "Factores como el clima, problemas técnicos o situaciones imprevistas no están "
                   "incluidos en el modelo.")
            
    except ValueError as e:
        st.error(f"❌ Error en la predicción: {str(e)}")
        logger.error(f"Prediction error: {str(e)}")
    except Exception as e:
        st.error(f"❌ Error inesperado: {str(e)}")
        logger.error(f"Unexpected prediction error: {str(e)}")

# Footer with additional information
st.markdown("---")
st.markdown(
    """
    <div style='text-align: center; color: #666; font-size: 0.8em;'>
        🛩️ Predictor de Retrasos de Vuelos - Powered by XGBoost<br>
        Desarrollado para ayudar a los viajeros a planificar mejor sus vuelos
    </div>
    """, 
    unsafe_allow_html=True
)