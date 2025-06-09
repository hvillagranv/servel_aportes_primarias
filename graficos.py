import streamlit as st
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from utilidades.utilidades import formato_clp
from tablas import mostrar_tabla_detallada_aportes
from procesamiento import filtrar_aportes_candidato

# -------------------- Gráfico de resumen general --------------------
def mostrar_graficos_aportes(df, col_monto, titulog1, titulog2, candidatos):
    nombres = df["NOMBRE_FORMATO"]
    montos = df[col_monto]
    total = montos.sum()

    colores_dict = {
        c["nombre"].strip().title(): c.get("color_partido", "#1f77b4")
        for c in candidatos
    }
    colores = [colores_dict.get(n.title(), "#1f77b4") for n in nombres]

    col1, col2 = st.columns(2)

    # --- Barras ---
    with col1:
        fig_bar, ax = plt.subplots(figsize=(7, 5), facecolor="#0E1117")
        bars = ax.bar(nombres, montos, color=colores)
        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + total * 0.01,
                f'{int(height):,}'.replace(",", "."),
                ha='center', va='bottom', fontsize=9, color='white'
            )
        ax.set_title(titulog1, color='white', fontsize=12)
        ax.set_ylabel("Monto en pesos", color='white')
        ax.set_xlabel("Candidato", color='white')
        ax.tick_params(colors='white')
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color('white')
        ax.spines["bottom"].set_color('white')
        ax.set_facecolor("#0E1117")
        plt.xticks(rotation=45, ha='right', color='white')
        plt.yticks(color='white')
        st.pyplot(fig_bar)

    # --- Dona ---
    with col2:
        etiquetas = [
            f"{nombres[i]}\n${montos[i]:,.0f}".replace(",", ".") + f" ({montos[i]/total:.1%})"
            for i in range(len(nombres))
        ]
        fig_dona, ax = plt.subplots(figsize=(7, 5), facecolor="#0E1117")
        wedges, _ = ax.pie(
            montos, startangle=90, radius=1,
            wedgeprops=dict(width=0.35, edgecolor='#0E1117'),
            labels=None, colors=colores
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
            ax.text(x, y, etiquetas[i], ha=ha, va='center', fontsize=8, color='white')
        ax.add_artist(plt.Circle((0, 0), 0.6, color='#0E1117'))
        ax.set_title(titulog2, color='white', fontsize=12, pad=12)
        ax.axis('equal')
        fig_dona.patch.set_facecolor('#0E1117')
        st.pyplot(fig_dona)

# -------------------- Gráfico de aportes por tipo --------------------
def mostrar_grafico_aportes_por_tipo(df_candidato, candidato):
    col_monto = [col for col in df_candidato.columns if "MONTO" in col.upper()]
    col_monto = col_monto[0] if col_monto else None

    if col_monto and "TIPO DE APORTE" in df_candidato.columns:
        df_candidato[col_monto] = pd.to_numeric(df_candidato[col_monto], errors='coerce')
        resumen = df_candidato.groupby("TIPO DE APORTE")[col_monto].sum()
        total = resumen.sum()
        etiquetas = [
            f"{tipo.title()}\n{formato_clp(monto)} ({monto/total:.1%})"
            for tipo, monto in resumen.items()
        ]
        fig, ax = plt.subplots(figsize=(5, 4), dpi=100, facecolor="#0E1117")
        wedges, _ = ax.pie(
            resumen, labels=None, startangle=90,
            wedgeprops=dict(width=0.4, edgecolor="#0E1117"),
            colors=plt.cm.Set2.colors
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
            ax.text(x, y, etiquetas[i], ha=ha, va='center', fontsize=8, color='white')
        ax.add_artist(plt.Circle((0, 0), 0.6, color="#0E1117"))
        ax.set_title(
            f"Tipos de aportes recibidos por {candidato['nombre']}",
            fontsize=12, color='white', pad=15
        )
        ax.axis('equal')
        fig.patch.set_facecolor("#0E1117")
        col1, col2, col3 = st.columns([0.5, 2, 0.5])
        with col2:
            st.pyplot(fig, clear_figure=True)
    else:
        st.info("No hay datos suficientes para generar el gráfico.")

# -------------------- Resumen --------------------
def resumen_aportes_candidato(df_candidato):
    col_monto = [col for col in df_candidato.columns if "MONTO" in col.upper()]
    col_monto = col_monto[0] if col_monto else None
    if not col_monto:
        return "Sin datos"
    total = pd.to_numeric(df_candidato[col_monto], errors='coerce').sum()
    cantidad = len(df_candidato)
    return f"**Total aportes recibidos:** {formato_clp(total)}  \n**Número de aportes:** {cantidad}"

# -------------------- Panel por candidato --------------------
def mostrar_aportes_detallados(df, candidato):
    st.markdown(f"### Detalle de aportes recibidos por **{candidato['nombre']}**")
    df_candidato = filtrar_aportes_candidato(df, candidato)
    if df_candidato.empty:
        st.warning("No se encontraron aportes registrados para este candidato.")
        return
    st.markdown(resumen_aportes_candidato(df_candidato))
    mostrar_tabla_detallada_aportes(df_candidato, candidato)
    st.subheader("Distribución de tipos de aporte")
    mostrar_grafico_aportes_por_tipo(df_candidato, candidato)
