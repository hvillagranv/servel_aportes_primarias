import pandas as pd
import requests
from io import BytesIO
import matplotlib.pyplot as plt

# Descargar el archivo
url = "https://repodocgastoelectoral.blob.core.windows.net/public/Presidencial_Parlamentaria_2025/Primarias/Reporte_Aportes_PRIMARIAS_2025.xlsx"
response = requests.get(url)
response.raise_for_status()

# Cargar sin encabezados para inspeccionar manualmente
df_raw = pd.read_excel(BytesIO(response.content), header=None)

# Mostrar las primeras 15 filas para inspección (opcional)
for idx, row in df_raw.iterrows():
    if row.astype(str).str.contains("TIPO DE APORTE", case=False).any():
        inicio = idx
        break

# Leer desde esa fila como encabezado
aportes = pd.read_excel(BytesIO(response.content), header=inicio)

# Verificar nombre exacto de la columna que contiene al candidato
aportes_filtrado = aportes[aportes['TIPO DE APORTE'].str.strip().str.upper() != 'PROPIO']

col_candidato = [col for col in aportes_filtrado.columns if "CANDIDATO" in col.upper()][0]
col_monto = [col for col in aportes_filtrado.columns if "MONTO" in col.upper()][0]

# Asegurar que el monto sea numérico
aportes_filtrado[col_monto] = pd.to_numeric(aportes_filtrado[col_monto], errors='coerce')

# Agrupar y sumar
suma_aportes = aportes_filtrado.groupby(col_candidato)[col_monto].sum().reset_index()

# Mostrar resultado
print(suma_aportes)

# Obtener columnas
nombres = suma_aportes[col_candidato]
montos = suma_aportes[col_monto]

# Crear figura y eje
fig, ax = plt.subplots(figsize=(10, 6))

# Crear gráfico de barras con nombres reales
bars = ax.bar(nombres, montos)

# Añadir los montos encima de cada barra
for bar in bars:
    height = bar.get_height()
    ax.text(bar.get_x() + bar.get_width()/2, height + 10000, f'{int(height):,}',
            ha='center', va='bottom', fontsize=10)

# Configurar etiquetas y diseño
ax.set_title("Suma de Aportes por Candidato")
ax.set_ylabel("Monto")
ax.set_xlabel("Candidato")
plt.xticks(rotation=0, ha='center')
plt.tight_layout()
plt.show()

import matplotlib.pyplot as plt
import numpy as np

# Datos
suma_aportes_df = suma_aportes.reset_index()
nombres = suma_aportes_df[col_candidato]
montos = suma_aportes_df[col_monto]
total = montos.sum()

# Capitalizar nombres y eliminar segundo apellido
def capitalizar_y_recortar(nombre):
    partes = nombre.strip().title().split()
    if len(partes) >= 3:
        return f"{partes[0]} {partes[1]}"  # Nombre + primer apellido
    return " ".join(partes)

nombres = nombres.apply(capitalizar_y_recortar)

# Etiquetas del gráfico
etiquetas_grafico = [
    f"{nombres[i]}\n${montos[i]:,.0f}".replace(",", ".") + f" ({montos[i]/total:.1%})"
    for i in range(len(nombres))
]

# Leyenda solo con nombres
etiquetas_leyenda = [str(n) for n in nombres]

# Figura angosta
fig, ax = plt.subplots(figsize=(6.5, 5))

# Gráfico de dona
wedges, _ = ax.pie(
    montos,
    startangle=90,
    radius=1,
    wedgeprops=dict(width=0.35),
    labels=None
)

# Etiquetas sin superposición
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

# Círculo blanco
ax.add_artist(plt.Circle((0, 0), 0.6, color='white'))

# LEYENDA más pegada
ax.legend(
    wedges,
    etiquetas_leyenda,
    title="Candidatos",
    loc="center left",
    bbox_to_anchor=(0.78, 0.5),  # más pegado aún
    fontsize=8,
    title_fontsize=9
)

# Título
ax.set_title("Distribución de Aportes por Candidato", fontsize=12, pad=12)
ax.axis('equal')

# APLICAR ajuste sin usar tight_layout
plt.subplots_adjust(left=0.1, right=0.85)
plt.show()