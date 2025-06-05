import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from io import BytesIO
import requests

def cargar_datos_remotos(url):
    response = requests.get(url)
    response.raise_for_status()
    df_raw = pd.read_excel(BytesIO(response.content), header=None)

    # Detectar encabezado
    for idx, row in df_raw.iterrows():
        if row.astype(str).str.contains("TIPO DE APORTE", case=False).any():
            inicio = idx
            break
    df = pd.read_excel(BytesIO(response.content), header=inicio)
    return df

def procesar_datos(df):
    df_filtrado = df[df['TIPO DE APORTE'].str.strip().str.upper() != 'PROPIO']
    col_candidato = [col for col in df_filtrado.columns if "CANDIDATO" in col.upper()][0]
    col_monto = [col for col in df_filtrado.columns if "MONTO" in col.upper()][0]
    df_filtrado[col_monto] = pd.to_numeric(df_filtrado[col_monto], errors='coerce')
    suma_aportes = df_filtrado.groupby(col_candidato)[col_monto].sum().reset_index()

    def capitalizar_y_recortar(nombre):
        partes = nombre.strip().title().split()
        if len(partes) >= 3:
            return f"{partes[0]} {partes[1]}"
        return " ".join(partes)

    suma_aportes["NOMBRE_FORMATO"] = suma_aportes[col_candidato].apply(capitalizar_y_recortar)
    return suma_aportes, col_candidato, col_monto

def mostrar_tabla_aportes(df, col_candidato, col_monto, titulo):
    st.subheader(titulo)
    st.dataframe(df[[col_candidato, col_monto]].rename(columns={col_candidato: "Candidato", col_monto: "Monto"}))

def mostrar_graficos_aportes(df, col_monto, titulog1, titulog2):
    nombres = df["NOMBRE_FORMATO"]
    montos = df[col_monto]
    total = montos.sum()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gráfico de barras")
        fig_bar, ax = plt.subplots(figsize=(10, 5))
        bars = ax.bar(nombres, montos)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 10000, f'{int(height):,}', ha='center', va='bottom', fontsize=9)
        ax.set_title(titulog1)
        ax.set_ylabel("Monto en pesos")
        ax.set_xlabel("Candidato")
        plt.xticks(rotation=0)
        st.pyplot(fig_bar)

    with col2:
        st.subheader("Gráfico de donas")
        etiquetas_grafico = [
            f"{nombres[i]}\n${montos[i]:,.0f}".replace(",", ".") + f" ({montos[i]/total:.1%})"
            for i in range(len(nombres))
        ]
        etiquetas_leyenda = [str(n) for n in nombres]

        fig_dona, ax = plt.subplots(figsize=(6.5, 5))
        wedges, _ = ax.pie(
            montos,
            startangle=90,
            radius=1,
            wedgeprops=dict(width=0.35),
            labels=None
        )

        ys_usados = []
        for i, wedge in enumerate(wedges):
            ang = (wedge.theta2 + wedge.theta1) / 2
            rad = np.deg2rad(ang)
            x = np.cos(rad) * 1.25
            y = np.sin(rad) * 1.25
            while any(abs(y - y2) < 0.12 for y2 in ys_usados):
                y += 0.12
            ys_usados.append(y)
            x0 = np.cos(rad) * 1.05
            y0 = np.sin(rad) * 1.05
            ax.plot([x0, x], [y0, y], color='gray', lw=0.8)
            ha = 'left' if x > 0 else 'right'
            ax.text(x, y, etiquetas_grafico[i], ha=ha, va='center', fontsize=8)

        ax.add_artist(plt.Circle((0, 0), 0.6, color='white'))

        ax.legend(
            wedges,
            etiquetas_leyenda,
            title="Candidatos",
            loc="center left",
            bbox_to_anchor=(0.78, 0.5),
            fontsize=8,
            title_fontsize=9
        )

        ax.set_title(titulog2, fontsize=12, pad=12)
        ax.axis('equal')
        plt.subplots_adjust(left=0.1, right=0.85)

        st.pyplot(fig_dona)
