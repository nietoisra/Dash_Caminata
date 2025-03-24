## python -m streamlit run c:/Users/Nieto/Desktop/DASHBOARDS/datos_caminata_STRM.py

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import find_peaks, butter, filtfilt
import base64
import io
import streamlit as st
import plotly.graph_objects as go

# Función para aplicar un filtro pasa-bajas Butterworth
def butter_lowpass_filter(data, cutoff, fs=100, order=3):
    """
    Aplica un filtro pasa-bajas Butterworth.

    Parámetros:
    - data: Señal de entrada (array).
    - cutoff: Frecuencia de corte (Hz).
    - fs: Frecuencia de muestreo (Hz).
    - order: Orden del filtro.

    Retorna:
    - y: Señal filtrada.
    """
    nyquist = 0.5 * fs  # Frecuencia de Nyquist
    normal_cutoff = cutoff / nyquist  # Frecuencia de corte normalizada
    b, a = butter(order, normal_cutoff, btype='low', analog=False)  # Diseño del filtro
    y = filtfilt(b, a, data)  # Aplicar el filtro
    return y

# Título de la aplicación
st.title("Análisis de Datos en la Caminata")

# Cargar archivo CSV
uploaded_file = st.file_uploader("Cargar Archivo CSV", type=["csv"])
if uploaded_file is not None:
    try:
        # Leer el archivo CSV
        data = pd.read_csv(uploaded_file)
        
        # Extraer columnas relevantes
        tiempo = data['Tiempo'].values
        acc_x = data['Acc X'].values
        
        # Aplicar filtro pasa-bajas
        fs = 1 / np.mean(np.diff(tiempo))  # Frecuencia de muestreo estimada
        cutoff_frequency = 5  # Frecuencia de corte ajustable
        filtered_acc_x = butter_lowpass_filter(acc_x, cutoff_frequency, fs)
        
        # Detección de picos
        peaks, _ = find_peaks(filtered_acc_x, height=np.mean(filtered_acc_x), distance=35)
        n_pasos = len(peaks)
        
        # Calcular intervalos de tiempo entre picos consecutivos
        intervalos_tiempo = np.diff(tiempo[peaks])
        frecuencia_ciclos = 1 / intervalos_tiempo
        cadencia = frecuencia_ciclos * 120  # Convertir a ciclos por minuto
        
        # Calcular velocidad y distancia
        longitud_paso = 0.7  # Suposición de longitud promedio de paso en metros
        pasos_por_pierna = n_pasos
        distancia_total = pasos_por_pierna * 2 * longitud_paso
        velocidad_promedio = distancia_total / tiempo[-1]
        
        # Mostrar estadísticas
        st.subheader("Resultados:")
        st.write(f"Pasos detectados: {n_pasos:.2f} pasos")
        st.write(f"Cadencia promedio: {np.mean(cadencia):.2f} pasos/min")
        st.write(f"Velocidad promedio: {velocidad_promedio:.2f} m/s")
        st.write(f"Distancia total recorrida: {distancia_total:.2f} m")
        st.write(f"Desviación estándar de la cadencia: {np.std(cadencia):.2f}")
        
        # Gráfico de aceleración
        acceleration_fig = go.Figure()
        acceleration_fig.add_trace(go.Scatter(x=tiempo, y=acc_x, mode='lines', name='Acc (original)', line=dict(color='blue', width=1)))
        acceleration_fig.add_trace(go.Scatter(x=tiempo, y=filtered_acc_x, mode='lines', name='Acc (filtrada)', line=dict(color='red', width=2)))
        acceleration_fig.add_trace(go.Scatter(x=tiempo[peaks], y=filtered_acc_x[peaks], mode='markers', name='Pasos detectados', marker=dict(color='green', size=9)))
        acceleration_fig.update_layout(title="Detección de Pasos en Aceleración Filtrada", xaxis_title="Tiempo (s)", yaxis_title="Aceleración (m/s²)")
        st.plotly_chart(acceleration_fig)
        
        # Histograma de cadencia
        cadence_hist_fig = go.Figure()
        cadence_hist_fig.add_trace(go.Histogram(x=cadencia, nbinsx=20, marker_color='blue', name='Cadencia'))
        cadence_hist_fig.update_layout(title="Distribución de la Cadencia", xaxis_title="Cadencia (pasos/min)", yaxis_title="Frecuencia")
        st.plotly_chart(cadence_hist_fig)
    
    except Exception as e:
        st.error(f"Error al procesar el archivo: {e}")
else:
    st.info("Por favor, cargue un archivo CSV.")
