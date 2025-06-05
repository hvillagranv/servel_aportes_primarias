import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import streamlit as st
from io import BytesIO
import requests
import unicodedata
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import matplotlib.ticker as mticker

# -------------------- Utilidades --------------------

def normalizar(texto):
    texto = str(texto).strip()  # Eliminar espacios antes/después
    return ''.join(
        c for c in unicodedata.normalize('NFD', texto)
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
        partido_norm = normalizar(c["partido"].strip())

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

def mostrar_tabla_aportes(df, col_candidato, col_monto, titulo, candidatos):
    st.subheader(titulo)

    # Crear diccionario {nombre_normalizado: nombre (partido)}
    partidos_dict = {
        normalizar(c["nombre"]): f'{capitalizar_nombre(c["nombre"])} ({c["partido"]})'
        for c in candidatos
    }

    df_tabla = df[[col_candidato, col_monto]].copy()
    df_tabla[col_monto] = pd.to_numeric(df_tabla[col_monto], errors='coerce')
    df_tabla["__NORM__"] = df_tabla[col_candidato].astype(str).apply(normalizar)
    df_tabla["Candidato"] = df_tabla["__NORM__"].map(partidos_dict)
    df_tabla = df_tabla.sort_values(by=col_monto, ascending=False)

    df_vista = df_tabla[["Candidato", col_monto]].rename(columns={col_monto: "Monto"}).reset_index(drop=True)

    gb = GridOptionsBuilder.from_dataframe(df_vista)
    gb.configure_column(
        "Monto",
        type=["numericColumn", "rightAligned"],
        valueFormatter='data.Monto.toLocaleString("es-CL", {style: "currency", currency: "CLP"})'
    )
    gb.configure_grid_options(rowHeight=32)
    gb.configure_default_column(sortable=True, filter=True)
    grid_options = gb.build()

    altura = 40 + len(df_vista) * 32
    AgGrid(
        df_vista,
        gridOptions=grid_options,
        fit_columns_on_grid_load=True,
        height=altura,
        enable_enterprise_modules=False,
        theme="balham-dark",
        custom_css={
            ".ag-root": {"background-color": "#1e1e1e !important"},
            ".ag-header": {"background-color": "#111111"},
            ".ag-header-cell-label": {"color": "white"},
            ".ag-cell-value": {"color": "white !important"},
            ".ag-row": {"background-color": "#1e1e1e !important"},
            ".ag-cell": {"background-color": "#1e1e1e !important"},
            ".ag-header-icon": {"filter": "invert(1)"}
        }
    )

# -------------------- Gráficos Generales--------------------

def mostrar_graficos_aportes(df, col_monto, titulog1, titulog2, candidatos):
    nombres = df["NOMBRE_FORMATO"]
    montos = df[col_monto]
    total = montos.sum()

    # Obtener lista de colores desde los candidatos
    colores_dict = {
        capitalizar_nombre(c["nombre"]): c.get("color_partido", "#1f77b4")
        for c in candidatos
    }
    colores = [colores_dict.get(nombre, "#1f77b4") for nombre in nombres]

    col1, col2 = st.columns(2)

    # --- Gráfico de barras ---
    with col1:
        fig_bar, ax = plt.subplots(figsize=(7, 5), facecolor="#0E1117")
        bars = ax.bar(nombres, montos, color=colores)

        for bar in bars:
            height = bar.get_height()
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                height + total * 0.01,
                f'{int(height):,}'.replace(",", "."),
                ha='center',
                va='bottom',
                fontsize=9,
                color='white'
            )

        ax.set_title(titulog1, color='white', fontsize=12)
        ax.set_ylabel("Monto en pesos", color='white')
        ax.set_xlabel("Candidato", color='white')
        ax.tick_params(colors='white')
        ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"${int(x):,}".replace(",", ".")))
        ax.spines["top"].set_visible(False)
        ax.spines["right"].set_visible(False)
        ax.spines["left"].set_color('white')
        ax.spines["bottom"].set_color('white')
        ax.set_facecolor("#0E1117")
        plt.xticks(rotation=45, ha='right', color='white')
        plt.yticks(color='white')

        st.pyplot(fig_bar)

    # --- Gráfico de donas ---
    with col2:
        etiquetas_grafico = [
            f"{nombres[i]}\n${montos[i]:,.0f}".replace(",", ".") + f" ({montos[i]/total:.1%})"
            for i in range(len(nombres))
        ]
        etiquetas_leyenda = [str(n) for n in nombres]

        fig_dona, ax = plt.subplots(figsize=(7, 5), facecolor="#0E1117")
        wedges, _ = ax.pie(
            montos,
            startangle=90,
            radius=1,
            wedgeprops=dict(width=0.35, edgecolor='#0E1117'),
            labels=None,
            colors=colores
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
            ax.text(x, y, etiquetas_grafico[i], ha=ha, va='center', fontsize=8, color='white')

        # Círculo interior del dona igual al fondo
        ax.add_artist(plt.Circle((0, 0), 0.6, color='#0E1117'))

        ax.set_title(titulog2, color='white', fontsize=12, pad=12)
        ax.axis('equal')
        plt.subplots_adjust(left=0.1, right=0.85)

        # Leyenda
        legend = ax.legend(
            wedges,
            etiquetas_leyenda,
            title="Candidatos",
            loc="center left",
            bbox_to_anchor=(0.78, 0.5),
            fontsize=8,
            title_fontsize=9,
            labelcolor='white',
            frameon=False
        )
        legend.get_title().set_color("white")

        fig_dona.patch.set_facecolor('#0E1117')
        ax.set_facecolor("#0E1117")
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

def ajustes_columnas_aportes(df_candidato):
    columnas_ocultas = [
        "TIPO DONATARIO", "ELECCION", "TERRITORIO ELECTORAL", 
        "PACTO", "PARTIDO", "__NORMALIZADO__", "__CANDIDATO_NORM__", "__APORTANTE_NORM__"
    ]

    columnas_visibles = [col for col in df_candidato.columns if col.upper() not in columnas_ocultas]
    df_limpio = df_candidato[columnas_visibles].copy()

    # Formato de fecha
    col_fecha = next((col for col in df_limpio.columns if "FECHA" in col.upper()), None)
    if col_fecha:
        df_limpio[col_fecha] = pd.to_datetime(df_limpio[col_fecha], errors='coerce').dt.strftime("%Y-%m-%d")

    # Formato de monto y columna oculta para orden
    col_monto = [col for col in df_limpio.columns if "MONTO" in col.upper()]
    if col_monto:
        col_monto = col_monto[0]
        df_limpio[col_monto + "_OCULTO"] = pd.to_numeric(df_limpio[col_monto], errors='coerce')
        df_limpio[col_monto] = df_limpio[col_monto + "_OCULTO"].apply(formato_clp)

    # Orden sugerido de columnas
    columnas_ordenadas = sorted(df_limpio.columns, key=lambda x: (
        0 if "TIPO DE APORTE" in x.upper() else
        1 if "NOMBRE APORTANTE" in x.upper() else
        2 if "MONTO" in x.upper() and "_OCULTO" not in x.upper() else
        3 if "FECHA" in x.upper() else
        4
    ))

    df_limpio = df_limpio[columnas_ordenadas]
    return df_limpio


def mostrar_tabla_detallada_aportes(df_candidato, candidato):
    df_limpio = ajustes_columnas_aportes(df_candidato)

    # Detectar columna del candidato (sin depender de mayúsculas exactas)
    col_candidato_partido = next(
        (col for col in df_limpio.columns if col.strip().upper() == "NOMBRE CANDIDATO-PARTIDO POLITICO"),
        None
    )
    if col_candidato_partido:
        df_limpio["Candidato"] = (
            df_limpio[col_candidato_partido]
            .astype(str).str.lower().str.title()
        )
        df_limpio.drop(columns=[col_candidato_partido], inplace=True)

    # Capitalizar columnas clave
    columnas_a_capitalizar = ["NOMBRE APORTANTE", "TIPO DE APORTE", "TIPO APORTANTE"]
    for col in columnas_a_capitalizar:
        if col in df_limpio.columns:
            df_limpio[col] = df_limpio[col].astype(str).str.lower().str.title()

    # Detectar y renombrar columna de monto a 'Monto'
    col_monto = next((col for col in df_limpio.columns if "MONTO" in col.upper()), None)
    if col_monto and col_monto != "Monto":
        df_limpio.rename(columns={col_monto: "Monto"}, inplace=True)
        col_monto = "Monto"

    # Limpiar montos en formato CLP y convertir
    if "Monto" in df_limpio.columns:
        df_limpio["Monto"] = (
            df_limpio["Monto"]
            .astype(str)
            .str.replace(".", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.replace(" ", "", regex=False)
        )
        df_limpio["Monto"] = pd.to_numeric(df_limpio["Monto"], errors="coerce")

    # Quitar columnas ocultas
    df_mostrar = df_limpio.drop(columns=[c for c in df_limpio.columns if "_OCULTO" in c], errors="ignore")

    # Validar y limpiar 'Monto'
    if "Monto" in df_mostrar.columns:
        df_mostrar["Monto"] = pd.to_numeric(df_mostrar["Monto"], errors="coerce")
        df_mostrar = df_mostrar[df_mostrar["Monto"].notna()]

    # Capitalizar Candidato si existe
    if "Candidato" in df_mostrar.columns:
        df_mostrar["Candidato"] = df_mostrar["Candidato"].astype(str).str.lower().str.title()

    st.subheader(f"Tabla de aportes individuales de {candidato['nombre']}")

    if df_mostrar.empty:
        st.warning("⚠️ No hay aportes registrados para este candidato.")
        return

    # Configurar AgGrid
    gb = GridOptionsBuilder.from_dataframe(df_mostrar)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=10)
    gb.configure_grid_options(
        rowHeight=32,
        domLayout='normal',
        suppressRowClickSelection=True,
        suppressHorizontalScroll=True
    )
    gb.configure_default_column(sortable=True, filter=True)

    for col in df_mostrar.columns:
        header = col.capitalize()
        if col == "TIPO DE APORTE":
            valores = df_mostrar[col].dropna().unique().tolist()
            gb.configure_column(
                col,
                header_name=header,
                filter="agSetColumnFilter",
                filterParams={"values": valores}
            )
        elif col == "Nombre Aportante":
            gb.configure_column(col, header_name=header, filter="agTextColumnFilter")
        elif col == "Monto":
            gb.configure_column(
                col,
                header_name="Monto",
                type=["numericColumn", "rightAligned"],
                valueFormatter='data.Monto.toLocaleString("es-CL", {style: "currency", currency: "CLP"})',
                cellStyle={"fontWeight": "bold"}
            )
        else:
            gb.configure_column(col, header_name=header)

    grid_options = gb.build()

    # Calcular altura de la tabla
    row_height = 32
    barra_paginacion = 20  # Altura constante de la barra de paginación
    header = 56  # Header + margen superior
    n_filas = len(df_mostrar)
    filas_visibles = min(n_filas, 10)
    altura_total = header + filas_visibles * row_height + barra_paginacion

    # Mostrar tabla
    AgGrid(
    df_mostrar,
    gridOptions=grid_options,
    update_mode=GridUpdateMode.NO_UPDATE,
    data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
    fit_columns_on_grid_load=True,
    theme="balham-dark",
    height=100 if len(df_mostrar) == 1 else (altura_total),
    allow_unsafe_jscode=True,
    enable_enterprise_modules=False,
    custom_css={
        ".ag-root": {"background-color": "#1e1e1e !important"},
        ".ag-header": {"background-color": "#111111"},
        ".ag-header-cell-label": {"color": "white"},
        ".ag-cell-value": {"color": "white !important"},
        ".ag-row": {"background-color": "#1e1e1e !important"},
        ".ag-cell": {"background-color": "#1e1e1e !important"},
        ".ag-header-icon": {"filter": "invert(1)"}
        }
    )

    with st.container():
        st.markdown('<div class="boton-descarga">', unsafe_allow_html=True)
        st.download_button(
            "📥 Descargar aportes",
            data=df_mostrar.to_csv(index=False).encode("utf-8-sig"),
            file_name="aportes_candidatos.csv",
            mime="text/csv"
        )
    st.markdown('</div>', unsafe_allow_html=True)

# -------------------- Gráfico de aportes por candidato --------------------

def mostrar_grafico_aportes_por_tipo(df_candidato, candidato):
    col_monto_real = [col for col in df_candidato.columns if "MONTO" in col.upper()]
    col_monto_real = col_monto_real[0] if col_monto_real else None

    if col_monto_real and "TIPO DE APORTE" in df_candidato.columns:
        df_candidato[col_monto_real] = pd.to_numeric(df_candidato[col_monto_real], errors='coerce')
        resumen = df_candidato.groupby("TIPO DE APORTE")[col_monto_real].sum()
        total = resumen.sum()

        etiquetas = [
            f"{tipo.title()}\n{formato_clp(monto)} ({monto/total:.1%})"
            for tipo, monto in resumen.items()
        ]

        fig, ax = plt.subplots(figsize=(5, 4), facecolor="#0E1117")
        wedges, _ = ax.pie(
            resumen,
            labels=None,
            startangle=90,
            wedgeprops=dict(width=0.4, edgecolor="#0E1117"),
            colors=plt.cm.Set2.colors
        )

        # Añadir líneas y etiquetas separadas (estilo profesional)
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

        # Centro del gráfico del mismo color
        ax.add_artist(plt.Circle((0, 0), 0.6, color="#0E1117"))

        ax.set_title(
            f"Tipos de aportes recibidos por {candidato['nombre']}",
            fontsize=12,
            color='white',
            pad=30
        )
        ax.axis('equal')
        ax.set_facecolor("#0E1117")
        fig.patch.set_facecolor("#0E1117")

        plt.subplots_adjust(top=0.80, bottom=0.05)

        col1, col2, col3 = st.columns([1, 2, 1])
        with col2:
            st.pyplot(fig)
    else:
        st.info("No hay datos suficientes para generar el gráfico.")

def resumen_aportes_candidato(df_candidato):
    col_monto = [col for col in df_candidato.columns if "MONTO" in col.upper()]
    col_monto = col_monto[0] if col_monto else None
    if not col_monto:
        return "Sin datos"

    total = pd.to_numeric(df_candidato[col_monto], errors='coerce').sum()
    cantidad = len(df_candidato)

    resumen = f"**Total aportes recibidos:** {formato_clp(total)}  \n"
    resumen += f"**Número de aportes:** {cantidad}"
    return resumen


def mostrar_aportes_detallados(df, candidato):
    st.markdown(f"### Detalle de aportes recibidos por **{candidato['nombre']}**")
    df_candidato = filtrar_aportes_candidato(df, candidato)

    if df_candidato.empty:
        st.warning("No se encontraron aportes registrados para este candidato.")
        return

    # Mostrar resumen antes de tabla y gráfico
    st.markdown(resumen_aportes_candidato(df_candidato))

    mostrar_tabla_detallada_aportes(df_candidato,candidato)

    st.subheader("Distribución de tipos de aporte")
    mostrar_grafico_aportes_por_tipo(df_candidato, candidato)
