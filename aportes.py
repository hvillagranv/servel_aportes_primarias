import streamlit as st
from candidatos import candidatos
import pandas as pd
from layout import mostrar_candidatos
from graficos import (
    cargar_datos_remotos,
    procesar_datos,
    mostrar_tabla_aportes,
    mostrar_graficos_aportes,
    mostrar_aportes_detallados
)

from babel.dates import format_date

st.set_page_config(layout="wide")

def aplicar_estilo_personalizado(css_file):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)
# Aplicar el CSS
aplicar_estilo_personalizado("estilos.css")
st.title("Visualización de Aportes a Candidatos – Primarias 2025")


url = "https://repodocgastoelectoral.blob.core.windows.net/public/Presidencial_Parlamentaria_2025/Primarias/Reporte_Aportes_PRIMARIAS_2025.xlsx"
df = cargar_datos_remotos(url)

col_fecha = next((col for col in df.columns if "FECHA DE TRANSFERENCIA" in col.upper()), None)
if col_fecha:
    try:
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")
        fecha_max = df[col_fecha].max()
        if pd.notnull(fecha_max):
            fecha_formateada = format_date(fecha_max, format="d 'de' MMMM 'de' y", locale="es")
            
        st.markdown(f"<span style='color:#6c757d'>Datos hasta el {fecha_formateada}</span>", unsafe_allow_html=True)
    except:
        pass

# Mostrar galería de candidatos con clic para expandir detalles
mostrar_candidatos(candidatos)


# Cargar y procesar los datos reales desde Servel
try:
    df = cargar_datos_remotos(url)
    suma_aportes, col_candidato, col_monto = procesar_datos(df, candidatos)

    # Mostrar tabla y gráficos generales
    titulo_tabla = "Suma Total de Aportes por Candidato"
    mostrar_tabla_aportes(suma_aportes, col_candidato, col_monto, titulo_tabla, candidatos)
    titulo_g1 = "Aportes Totales por Candidato"
    titulo_g2 = "Distribución de Aportes por Candidato"
    mostrar_graficos_aportes(suma_aportes, col_monto, titulo_g1, titulo_g2, candidatos)

    # Selección de candidato para ver detalles
    nombres_candidatos = [c["nombre"] for c in candidatos]
    nombre_seleccionado = st.selectbox("Selecciona un candidato para ver sus aportes detallados:", nombres_candidatos)
    if nombre_seleccionado:
        candidato_obj = next((c for c in candidatos if c["nombre"] == nombre_seleccionado), None)
        if candidato_obj:
            mostrar_aportes_detallados(df, candidato_obj)

except Exception as e:
    st.error(f"Error al cargar o procesar los datos: {e}")
