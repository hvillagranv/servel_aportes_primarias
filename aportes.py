import streamlit as st
import pandas as pd
from babel.dates import format_date
from candidatos import candidatos
from layout import mostrar_candidatos
from procesamiento import cargar_datos_remotos, procesar_datos, filtrar_aportes_candidato
from tablas import mostrar_tabla_aportes, mostrar_top_aportantes
from graficos import mostrar_graficos_aportes, mostrar_aportes_detallados

st.set_page_config(layout="wide")

# -------------------- Estilo CSS personalizado --------------------
def aplicar_estilo_personalizado(css_file):
    with open(css_file) as f:
        st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

aplicar_estilo_personalizado("utilidades/estilos.css")

st.title("Visualización de Aportes a Candidatos – Primarias 2025")

# -------------------- Cargar datos y mostrar fecha --------------------
url = "https://repodocgastoelectoral.blob.core.windows.net/public/Presidencial_Parlamentaria_2025/Primarias/Reporte_Aportes_PRIMARIAS_2025.xlsx"

try:
    df = cargar_datos_remotos(url)

    col_fecha = next((col for col in df.columns if "FECHA DE TRANSFERENCIA" in col.upper()), None)
    if col_fecha:
        df[col_fecha] = pd.to_datetime(df[col_fecha], errors="coerce")
        fecha_max = df[col_fecha].max()
        if pd.notnull(fecha_max):
            fecha_formateada = format_date(fecha_max, format="d 'de' MMMM 'de' y", locale="es")
            st.markdown(f"<span style='color:#6c757d'>Datos hasta el {fecha_formateada}</span>", unsafe_allow_html=True)

    # -------------------- Mostrar galería de candidatos --------------------
    mostrar_candidatos(candidatos)

    # -------------------- Procesamiento y visualización general --------------------
    suma_aportes, col_candidato, col_monto = procesar_datos(df, candidatos)

    mostrar_tabla_aportes(suma_aportes, col_candidato, col_monto, "Suma Total de Aportes por Candidato", candidatos)
    mostrar_graficos_aportes(suma_aportes, col_monto, "Aportes Totales por Candidato", "Distribución de Aportes por Candidato", candidatos)

    # -------------------- Selección de candidato para ver detalles --------------------
    nombres_candidatos = [c["nombre"] for c in candidatos]
    nombre_seleccionado = st.selectbox("Selecciona un candidato para ver sus aportes detallados:", nombres_candidatos)
    if nombre_seleccionado:
        candidato_obj = next((c for c in candidatos if c["nombre"] == nombre_seleccionado), None)
        if candidato_obj:
            df_candidato = filtrar_aportes_candidato(df, candidato_obj)
            mostrar_aportes_detallados(df_candidato, candidato_obj)
            mostrar_top_aportantes(df_candidato, candidato_obj)

except Exception as e:
    st.error(f"Error al cargar o procesar los datos: {e}")
