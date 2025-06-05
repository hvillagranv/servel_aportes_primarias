import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from io import BytesIO
import requests
import unicodedata
from st_aggrid import AgGrid, GridOptionsBuilder

# -------------------- Utilidades --------------------

def normalizar(texto):
    return ''.join(
        c for c in unicodedata.normalize('NFD', str(texto))
        if unicodedata.category(c) != 'Mn'
    ).lower()

def capitalizar_nombre(nombre):
    partes = nombre.strip().title().split()
    return " ".join(partes)

def formato_clp(valor):
    try:
        return f"${int(valor):,}".replace(",", ".")
    except:
        return valor

# -------------------- Carga de datos --------------------

def cargar_datos_remotos(url):
    response = requests.get(url)
    response.raise_for_status()
    contenido = BytesIO(response.content)
    df_raw = pd.read_excel(contenido, header=None)

    # Detectar encabezado
    for idx, row in df_raw.iterrows():
        if row.astype(str).str.contains("TIPO DE APORTE", case=False).any():
            inicio = idx
            break
    df = pd.read_excel(contenido, header=inicio)
    return df

# -------------------- Procesamiento --------------------

def procesar_datos(df, candidatos):
    col_candidato_df = [col for col in df.columns if "CANDIDATO" in col.upper()][0]
    col_aportante_df = [col for col in df.columns if "NOMBRE APORTANTE" in col.upper()][0]
    col_tipo_aporte_df = [col for col in df.columns if "TIPO DE APORTE" in col.upper()][0]
    col_monto_df = [col for col in df.columns if "MONTO" in col.upper()][0]

    df[col_monto_df] = pd.to_numeric(df[col_monto_df], errors='coerce')
    df["__CANDIDATO_NORM__"] = df[col_candidato_df].astype(str).apply(normalizar)
    df["__APORTANTE_NORM__"] = df[col_aportante_df].astype(str).apply(normalizar)

    resultado = []

    for c in candidatos:
        nombre_norm = normalizar(c["nombre"])
        partido_norm = normalizar(c["partido"])

        # Coincidencia flexible: nombres que comiencen con el del candidato
        filtro_candidato = df["__CANDIDATO_NORM__"].apply(lambda x: x.startswith(nombre_norm))

        # Aportes del partido, excluyendo si el receptor es el mismo partido
        filtro_partido = (df["__APORTANTE_NORM__"] == partido_norm) & \
                         (df["__CANDIDATO_NORM__"] != partido_norm)

        filtro_total = (filtro_candidato | filtro_partido) & \
                       (df[col_tipo_aporte_df].str.upper() != "PROPIO")

        df_filtrado = df[filtro_total].copy()

        resultado.append({
            "nombre": c["nombre"],
            "NOMBRE_FORMATO": capitalizar_nombre(c["nombre"]),
            col_monto_df: df_filtrado[col_monto_df].sum()
        })

    df_resultado = pd.DataFrame(resultado)
    return df_resultado, "nombre", col_monto_df

# -------------------- Tablas Generales --------------------

def mostrar_tabla_aportes(df, col_candidato, col_monto, titulo):
    st.subheader(titulo)

    # Preprocesamiento del DataFrame
    df_tabla = df[[col_candidato, col_monto]].copy()
    df_tabla[col_monto] = pd.to_numeric(df_tabla[col_monto], errors='coerce')
    df_tabla["Candidato"] = df_tabla[col_candidato].apply(capitalizar_nombre)
    df_tabla = df_tabla.sort_values(by=col_monto, ascending=False)

    # Renombrar la columna de monto para presentación
    df_vista = df_tabla[["Candidato", col_monto]].rename(columns={col_monto: "Monto"}).reset_index(drop=True)

    # Configuración de AgGrid
    gb = GridOptionsBuilder.from_dataframe(df_vista)
    gb.configure_column(
        "Monto",
        type=["numericColumn", "rightAligned"],
        valueFormatter='data.Monto.toLocaleString("es-CL", {style: "currency", currency: "CLP"})'
    )
    gb.configure_default_column(sortable=True, filter=True)
    grid_options = gb.build()

    # Mostrar tabla interactiva
    AgGrid(
        df_vista,
        gridOptions=grid_options,
        fit_columns_on_grid_load=True,
        enable_enterprise_modules=False,
        height=400
    )


# -------------------- Gráficos Generales--------------------

def mostrar_graficos_aportes(df, col_monto, titulog1, titulog2):
    nombres = df["NOMBRE_FORMATO"]
    montos = df[col_monto]
    total = montos.sum()

    col1, col2 = st.columns(2)

    with col1:
        st.subheader("Gráfico de barras")
        fig_bar, ax = plt.subplots(figsize=(max(10, len(nombres) * 0.5), 5))
        bars = ax.bar(nombres, montos)
        for bar in bars:
            height = bar.get_height()
            ax.text(bar.get_x() + bar.get_width()/2, height + 10000, f'{int(height):,}', ha='center', va='bottom', fontsize=9)
        ax.set_title(titulog1)
        ax.set_ylabel("Monto en pesos")
        ax.set_xlabel("Candidato")
        plt.xticks(rotation=45, ha='right')
        st.pyplot(fig_bar)

    with col2:
        st.subheader("Gráfico de donas")
        etiquetas_grafico = [
            f"{nombres[i]}\n${montos[i]:,.0f}".replace(",", ".") + f" ({montos[i]/total:.1%})"
            for i in range(len(nombres))
        ]
        etiquetas_leyenda = list(nombres)

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

# -------------------- Detalles por candidato --------------------
def filtrar_aportes_candidato(df, candidato):
    col_candidato = [col for col in df.columns if "CANDIDATO" in col.upper()][0]
    df["__NORMALIZADO__"] = df[col_candidato].astype(str).apply(normalizar)
    candidato_filtrado = normalizar(candidato["nombre"])

    df_directos = df[df["__NORMALIZADO__"].str.contains(candidato_filtrado, na=False)].copy()

    partido_normalizado = normalizar(candidato["partido"])
    df_propios = pd.DataFrame()
    if "NOMBRE APORTANTE" in df.columns:
        df_propios = df[
            (df["TIPO DE APORTE"].str.upper() == "PROPIO") &
            (df["NOMBRE APORTANTE"].astype(str).apply(normalizar) == partido_normalizado)
        ].copy()

    df_candidato = pd.concat([df_directos, df_propios], ignore_index=True)
    return df_candidato

# -------------------- Tabla de aportes por candidato --------------------

def mostrar_tabla_detallada_aportes(df_candidato):
    columnas_excluir = ["TIPO DONATARIO", "ELECCION", "TERRITORIO ELECTORAL", "PACTO", "PARTIDO", "__NORMALIZADO__"]
    columnas_mostrar = [col for col in df_candidato.columns if col.upper() not in columnas_excluir]
    df_limpio = df_candidato[columnas_mostrar].copy()

    col_fecha = next((col for col in df_limpio.columns if "FECHA" in col.upper()), None)
    if col_fecha:
        df_limpio[col_fecha] = pd.to_datetime(df_limpio[col_fecha], errors='coerce').dt.strftime("%Y-%m-%d")

    col_monto = [col for col in df_limpio.columns if "MONTO" in col.upper()]
    if col_monto:
        col_monto = col_monto[0]
        df_limpio[col_monto] = df_limpio[col_monto].apply(
            lambda x: f"**{formato_clp(x)}**" if pd.notnull(x) and x != '' else x
        )

    st.subheader("Tabla de aportes individuales")
    st.dataframe(df_limpio, use_container_width=True)

# -------------------- Gráfico de aportes por candidato --------------------
def mostrar_grafico_aportes_por_tipo(df_candidato):
    col_monto_real = [col for col in df_candidato.columns if "MONTO" in col.upper()]
    col_monto_real = col_monto_real[0] if col_monto_real else None

    if col_monto_real and "TIPO DE APORTE" in df_candidato.columns:
        df_candidato[col_monto_real] = pd.to_numeric(df_candidato[col_monto_real], errors='coerce')
        resumen = df_candidato.groupby("TIPO DE APORTE")[col_monto_real].sum()
        total = resumen.sum()

        etiquetas = [
            f"{tipo}\n{formato_clp(monto)} ({monto/total:.1%})"
            for tipo, monto in resumen.items()
        ]

        fig, ax = plt.subplots(figsize=(5, 5))
        wedges, texts = ax.pie(
            resumen,
            labels=etiquetas,
            startangle=90,
            wedgeprops=dict(width=0.4)
        )
        ax.set_title("Tipos de aportes recibidos")
        ax.axis('equal')

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.pyplot(fig)
    else:
        st.info("No hay datos suficientes para generar el gráfico.")

def mostrar_aportes_detallados(df, candidato):
    st.markdown(f"### Detalle de aportes recibidos por **{candidato['nombre']}**")

    df_candidato = filtrar_aportes_candidato(df, candidato)

    if df_candidato.empty:
        st.warning("No se encontraron aportes registrados para este candidato.")
        return

    mostrar_tabla_detallada_aportes(df_candidato)
    st.subheader("Distribución de tipos de aporte")
    mostrar_grafico_aportes_por_tipo(df_candidato)
