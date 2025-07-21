# Guía de Uso - Predictor de Retrasos de Vuelos

## 🚀 Inicio Rápido

### Requisitos
- Python 3.8+
- Dependencias listadas en `requirements.txt`

### Instalación
```bash
cd src
pip install -r requirements.txt
```

### Ejecutar la aplicación
```bash
streamlit run app.py
```

La aplicación se abrirá en tu navegador en `http://localhost:8501`

## 📱 Cómo usar la aplicación

### 1. Seleccionar Origen
- **Estado de origen**: Elige el estado donde se origina el vuelo
- **Ciudad de origen**: Selecciona la ciudad (se filtra automáticamente)
- **Aeropuerto de origen**: Elige el aeropuerto específico

### 2. Seleccionar Destino
- **Estado de destino**: Elige el estado de destino
- **Ciudad de destino**: Selecciona la ciudad de destino
- **Aeropuerto de destino**: Elige el aeropuerto de destino

### 3. Detalles del Vuelo
- **Aerolínea**: Selecciona la aerolínea
- **Hora de salida**: Hora programada de salida (formato 24h)
- **Hora de llegada**: Hora programada de llegada (formato 24h)
- **Distancia**: Distancia del vuelo en millas (100-5000)
- **Fecha del vuelo**: Fecha del vuelo (no puede ser en el pasado)

### 4. Obtener Predicción
1. Revisa el resumen del vuelo que aparece en pantalla
2. Haz clic en "🚀 Predecir retraso"
3. Ve el resultado de la predicción

## ✅ Validaciones Automáticas

La aplicación incluye validaciones para asegurar datos coherentes:

- **Duración del vuelo**: Entre 30 minutos y 20 horas
- **Distancia**: Entre 100 y 5000 millas
- **Fecha**: No puede ser en el pasado ni más de 1 año en el futuro
- **Ruta**: El aeropuerto de origen debe ser diferente al de destino
- **Aerolínea**: Debe seleccionarse de la lista disponible

## 🔍 Resultados de Predicción

### ✅ Sin Retraso
- Indicador verde
- Mensaje: "¡Excelentes noticias! Su vuelo tiene baja probabilidad de retraso"
- Animación de celebración

### ⚠️ Con Retraso
- Indicador amarillo/naranja
- Mensaje: "Atención: Su vuelo tiene alta probabilidad de retraso"
- Recomendaciones adicionales

## 🧪 Testing

### Ejecutar tests unitarios
```bash
cd src
python test_app.py
```

### Ejecutar test de integración
```bash
cd src
python manual_test.py
```

## 📂 Estructura de Archivos

```
src/
├── app.py              # Aplicación principal Streamlit
├── config.py           # Configuración y constantes
├── utils.py            # Utilidades (carga de datos, modelo)
├── validation.py       # Validación de entradas
├── test_app.py         # Tests unitarios
├── manual_test.py      # Test de integración
├── requirements.txt    # Dependencias
├── Combined_Flights_2021_streamlit.parquet  # Dataset
└── best_model_*.pkl    # Modelo entrenado
```

## 🚨 Solución de Problemas

### Error: "Faltan archivos requeridos"
- Verifica que todos los archivos estén en las rutas correctas
- Asegúrate de estar ejecutando desde el directorio `src/`

### Error: "No hay ciudades/aeropuertos disponibles"
- Esto indica un problema con los datos de mapeo
- Verifica que el archivo parquet esté completo

### Error de predicción
- Revisa que todos los campos estén completados
- Verifica que las validaciones hayan pasado
- Consulta los logs para más detalles

## 📈 Características del Modelo

- **Algoritmo**: XGBoost
- **Variables**: Aerolínea, origen, destino, horarios, distancia, fecha
- **Objetivo**: Predicción binaria (retraso/sin retraso)
- **Precisión**: Basado en datos históricos de vuelos de 2021

## 💡 Notas Importantes

- La predicción se basa en patrones históricos
- Factores como clima extremo o emergencias no están incluidos
- Siempre verifica el estado del vuelo antes de viajar
- La aplicación es una herramienta de apoyo, no garantiza resultados

## 🔧 Desarrollo

Para modificar o extender la aplicación:

1. **Agregar nuevas validaciones**: Modifica `validation.py`
2. **Cambiar configuración**: Edita `config.py`
3. **Agregar funcionalidades**: Extiende `utils.py`
4. **Modificar UI**: Actualiza `app.py`
5. **Agregar tests**: Extiende `test_app.py`

Siempre ejecuta los tests después de hacer cambios:
```bash
python test_app.py && python manual_test.py
```