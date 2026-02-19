import pandas as pd
import requests
from io import BytesIO
from pathlib import Path
from utilidades.utilidades import normalizar, capitalizar_nombre

def cargar_datos_remotos(url, cache_dir="data"):
    response = requests.get(url)
    response.raise_for_status()

    cache_path = Path(cache_dir)
    cache_path.mkdir(parents=True, exist_ok=True)
    filename = url.split("/")[-1]
    file_path = cache_path / filename

    remote_size = len(response.content)
    if file_path.exists():
        local_size = file_path.stat().st_size
        if local_size != remote_size:
            file_path.write_bytes(response.content)
    else:
        file_path.write_bytes(response.content)

    contenido = BytesIO(file_path.read_bytes())
    df_raw = pd.read_excel(contenido, header=None, sheet_name="REPORTE_PRIMARIAS")
    for idx, row in df_raw.iterrows():
        if row.astype(str).str.contains("TIPO DE APORTE", case=False).any():
            inicio = idx
            break
    contenido.seek(0)
    return pd.read_excel(contenido, header=inicio)

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

        filtro_candidato = df["__CANDIDATO_NORM__"].apply(lambda x: x.startswith(nombre_norm))
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

    return pd.concat([df_directos, df_propios], ignore_index=True)
