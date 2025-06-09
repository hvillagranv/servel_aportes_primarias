import streamlit as st
from st_aggrid import AgGrid, GridOptionsBuilder, GridUpdateMode, DataReturnMode
import pandas as pd
from utilidades.utilidades import normalizar, capitalizar_nombre, formato_clp

# -------------------- Tabla general de resumen --------------------

def mostrar_tabla_aportes(df, col_candidato, col_monto, titulo, candidatos):
    st.subheader(titulo)

    partidos_dict = {
        normalizar(c["nombre"]): f'{capitalizar_nombre(c["nombre"])} ({c["abreviatura"]})'
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
    gb.configure_grid_options(rowHeight=32, domLayout='autoHeight')
    gb.configure_default_column(sortable=True, filter=True, resizable=True, flex=1)
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
            ".ag-header-icon": {"filter": "invert(1)"},
            ".ag-root-wrapper": {"width": "100% !important"},
            ".ag-center-cols-viewport": {
                "overflow-x": "auto",
                "min-height": "100px !important",
                "width": "100% !important"
            },
            ".ag-body-viewport": {
                "overflow-y": "auto !important",
                "width": "100% !important"
            }
        },
        update_mode='model_changed',
        key=f"grid_{titulo}"
    )


# -------------------- Ajustes y tabla detallada --------------------
def ajustes_columnas_aportes(df_candidato):
    columnas_ocultas = [
        "TIPO DONATARIO", "ELECCION", "TERRITORIO ELECTORAL",
        "PACTO", "PARTIDO", "__NORMALIZADO__", "__CANDIDATO_NORM__", "__APORTANTE_NORM__"
    ]
    columnas_visibles = [col for col in df_candidato.columns if col.upper() not in columnas_ocultas]
    df_limpio = df_candidato[columnas_visibles].copy()

    col_fecha = next((col for col in df_limpio.columns if "FECHA" in col.upper()), None)
    if col_fecha:
        df_limpio[col_fecha] = pd.to_datetime(df_limpio[col_fecha], errors='coerce').dt.strftime("%Y-%m-%d")

    col_monto = [col for col in df_limpio.columns if "MONTO" in col.upper()]
    if col_monto:
        col_monto = col_monto[0]
        df_limpio[col_monto + "_OCULTO"] = pd.to_numeric(df_limpio[col_monto], errors='coerce')
        df_limpio[col_monto] = df_limpio[col_monto + "_OCULTO"].apply(formato_clp)

    columnas_ordenadas = sorted(df_limpio.columns, key=lambda x: (
        0 if "TIPO DE APORTE" in x.upper() else
        1 if "NOMBRE APORTANTE" in x.upper() else
        2 if "MONTO" in x.upper() and "_OCULTO" not in x.upper() else
        3 if "FECHA" in x.upper() else 4
    ))
    return df_limpio[columnas_ordenadas]

def mostrar_tabla_detallada_aportes(df_candidato, candidato):
    df_limpio = ajustes_columnas_aportes(df_candidato)

    col_candidato_partido = next(
        (col for col in df_limpio.columns if col.strip().upper() == "NOMBRE CANDIDATO-PARTIDO POLITICO"),
        None
    )
    if col_candidato_partido:
        df_limpio["Candidato"] = df_limpio[col_candidato_partido].astype(str).str.lower().str.title()
        df_limpio.drop(columns=[col_candidato_partido], inplace=True)

    for col in ["NOMBRE APORTANTE", "TIPO DE APORTE", "TIPO APORTANTE"]:
        if col in df_limpio.columns:
            df_limpio[col] = df_limpio[col].astype(str).str.lower().str.title()

    col_monto = next((col for col in df_limpio.columns if "MONTO" in col.upper()), None)
    if col_monto and col_monto != "Monto":
        df_limpio.rename(columns={col_monto: "Monto"}, inplace=True)
        col_monto = "Monto"

    if "Monto" in df_limpio.columns:
        df_limpio["Monto"] = (
            df_limpio["Monto"]
            .astype(str).str.replace(".", "", regex=False)
            .str.replace("$", "", regex=False)
            .str.replace(" ", "", regex=False)
        )
        df_limpio["Monto"] = pd.to_numeric(df_limpio["Monto"], errors="coerce")

    df_mostrar = df_limpio.drop(columns=[c for c in df_limpio.columns if "_OCULTO" in c], errors="ignore")
    df_mostrar = df_mostrar[df_mostrar["Monto"].notna()]
    if "Candidato" in df_mostrar.columns:
        df_mostrar["Candidato"] = df_mostrar["Candidato"].astype(str).str.lower().str.title()

    col1, col2 = st.columns([3, 1])
    with col1:
        st.subheader(f"Tabla de aportes individuales de {candidato['nombre']}")
    with col2:
        page_size = st.selectbox(
            "Filas por página", options=[10, 20, 50, 100], index=0,
            key=f"page_size_{candidato['nombre']}"
        )

    if df_mostrar.empty:
        st.warning("⚠️ No hay aportes registrados para este candidato.")
        return

    gb = GridOptionsBuilder.from_dataframe(df_mostrar)
    gb.configure_pagination(paginationAutoPageSize=False, paginationPageSize=page_size)
    gb.configure_grid_options(
        rowHeight=40, domLayout='autoHeight', suppressHorizontalScroll=False,
        alwaysShowHorizontalScroll=True, suppressRowClickSelection=True,
        suppressColumnVirtualisation=True, ensureDomOrder=True
    )
    gb.configure_default_column(
        sortable=True, filter=True, resizable=True, flex=1,
        minWidth=120, maxWidth=600, wrapText=True, autoHeight=True
    )

    for col in df_mostrar.columns:
        header = col.capitalize()
        if col == "Tipo de aporte":
            valores = df_mostrar[col].dropna().unique().tolist()
            gb.configure_column(
                col, header_name=header, filter="agSetColumnFilter",
                filterParams={"values": valores}, width=180, pinned="left",
                cellStyle={"white-space": "normal"}
            )
        elif col == "Nombre aportante":
            gb.configure_column(
                col, header_name=header, filter="agTextColumnFilter", width=220,
                tooltipField=col, cellRenderer="agAnimateShowChangeCellRenderer",
                cellStyle={"white-space": "normal"}
            )
        elif col == "Monto":
            gb.configure_column(
                col, header_name="Monto",
                type=["numericColumn", "rightAligned"],
                valueFormatter='data.Monto.toLocaleString("es-CL", {style: "currency", currency: "CLP"})',
                cellStyle={"fontWeight": "bold"}, width=150
            )
        elif col == "Fecha de transferencia":
            gb.configure_column(col, header_name=header, width=150, filter="agDateColumnFilter")
        elif col == "Candidato":
            gb.configure_column(col, header_name=header, hide=True)
        else:
            gb.configure_column(col, header_name=header, width=150)

    custom_css = {
        ".ag-root": {
            "background-color": "#1e1e1e !important",
            "font-family": "Arial, sans-serif",
            "width": "100% !important"
        },
        ".ag-header": {
            "background-color": "#111111 !important",
            "position": "sticky !important",
            "top": "0 !important",
            "z-index": "100 !important"
        },
        ".ag-header-cell-label": {"color": "white !important", "font-size": "14px !important"},
        ".ag-cell-value": {"color": "white !important", "font-size": "13px !important"},
        ".ag-row": {"background-color": "#1e1e1e !important"},
        ".ag-cell": {"background-color": "#1e1e1e !important"},
        ".ag-header-icon": {"filter": "invert(1) !important"},
        ".ag-center-cols-viewport": {"overflow-x": "auto !important"},
        ".ag-body-viewport": {"overflow-y": "auto !important"},
        ".ag-paging-panel": {"background-color": "#1e1e1e !important", "color": "white !important"}
    }

    AgGrid(
        df_mostrar,
        gridOptions=gb.build(),
        update_mode=GridUpdateMode.NO_UPDATE,
        data_return_mode=DataReturnMode.FILTERED_AND_SORTED,
        fit_columns_on_grid_load=True,
        theme="balham-dark",
        height=400,
        allow_unsafe_jscode=True,
        enable_enterprise_modules=False,
        custom_css=custom_css,
        key=f"grid_{candidato['nombre']}",
        reload_data=False
    )

    st.download_button(
        "📅 Descargar datos completos",
        data=df_mostrar.to_csv(index=False, encoding='utf-8-sig'),
        file_name=f"aportes_{candidato['nombre'].replace(' ', '_')}.csv",
        mime="text/csv",
        use_container_width=True
    )

def mostrar_top_aportantes(df_candidato, candidato):
    st.subheader("Top 10 aportantes por monto total")

    col_aportante = next((col for col in df_candidato.columns if "APORTANTE" in col.upper()), None)
    col_monto = next((col for col in df_candidato.columns if "MONTO" in col.upper()), None)
    col_tipo_aporte = next((col for col in df_candidato.columns if "TIPO DE APORTE" in col.upper()), None)

    if not col_aportante or not col_monto or not col_tipo_aporte:
        st.warning("No se pudo identificar columnas válidas.")
        return

    df_candidato[col_monto] = pd.to_numeric(df_candidato[col_monto], errors='coerce')
    df_candidato[col_aportante] = df_candidato[col_aportante].fillna("").astype(str).str.strip()
    df_candidato[col_tipo_aporte] = df_candidato[col_tipo_aporte].fillna("").astype(str).str.strip()

    # Agrupar anónimos que son "Aporte menor sin publicidad"
    df_candidato["__APORTANTE_NOMBRE__"] = df_candidato.apply(
        lambda row: "Aportante sin Publicidad"
        if row[col_tipo_aporte].upper() == "APORTE MENOR SIN PUBLICIDAD" and row[col_aportante] in ["", "-", "–", "—"]
        else capitalizar_nombre(row[col_aportante]),
        axis=1
    )

    # Filtrar solo los que son 'Aporte con Publicidad' y tienen nombre válido (no son anónimos)
    df_con_publicidad = df_candidato[
        (df_candidato[col_tipo_aporte].str.upper() == "APORTE CON PUBLICIDAD") &
        (~df_candidato["__APORTANTE_NOMBRE__"].isin(["Aportante sin Publicidad"]))
    ]

    # Combinar con los anónimos sin publicidad
    df_sin_publicidad = df_candidato[
        df_candidato["__APORTANTE_NOMBRE__"] == "Aportantes sin Publicidad"
    ]

    df_top = pd.concat([df_con_publicidad, df_sin_publicidad], ignore_index=True)

    # Agrupar y sumar
    top = (
        df_top
        .groupby("__APORTANTE_NOMBRE__")[col_monto]
        .sum()
        .sort_values(ascending=False)
        .head(10)
        .reset_index()
        .rename(columns={"__APORTANTE_NOMBRE__": "Aportante", col_monto: "Monto"})
    )
    top["Monto"] = top["Monto"].apply(formato_clp)

    # Estilo uniforme
    gb = GridOptionsBuilder.from_dataframe(top)
    gb.configure_column("Monto", type=["numericColumn", "rightAligned"])
    gb.configure_default_column(sortable=True, filter=True, resizable=True, flex=1)
    gb.configure_grid_options(domLayout='autoHeight')
    custom_css = {
        ".ag-root": {"background-color": "#1e1e1e !important"},
        ".ag-header": {"background-color": "#111111"},
        ".ag-header-cell-label": {"color": "white"},
        ".ag-cell-value": {"color": "white !important"},
        ".ag-row": {"background-color": "#1e1e1e !important"},
        ".ag-cell": {"background-color": "#1e1e1e !important"},
        ".ag-header-icon": {"filter": "invert(1)"},
        ".ag-root-wrapper": {"width": "100% !important"},
        ".ag-center-cols-viewport": {"overflow-x": "auto"}
    }

    altura = 40 + len(top) * 32  # Altura base + 32 px por fila

    AgGrid(
        top,
        gridOptions=gb.build(),
        fit_columns_on_grid_load=True,
        height=altura,
        enable_enterprise_modules=False,
        theme="balham-dark",
        custom_css=custom_css,
        key=f"top_aportantes_{candidato['nombre']}"
    )

    # Totales sin publicidad y propios
    sin_pub = df_candidato[df_candidato[col_tipo_aporte].str.upper() == "APORTE MENOR SIN PUBLICIDAD"]
    total_sin_pub = sin_pub[col_monto].sum()

    partido_norm = normalizar(candidato["partido"])
    df_propios = df_candidato[
        (df_candidato[col_tipo_aporte].str.upper() == "PROPIO") &
        (df_candidato[col_aportante].astype(str).apply(normalizar) == partido_norm)
    ]
    total_propios = df_propios[col_monto].sum()

    st.markdown(f"**🕶 Total aportes sin publicidad:** {formato_clp(total_sin_pub)}")
    st.markdown(f"**🏛 Aportes propios del partido:** {formato_clp(total_propios)}")