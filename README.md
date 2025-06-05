
# 🗳️ Visualización de Aportes Electorales – Primarias 2025

Este proyecto permite explorar de manera interactiva los aportes económicos recibidos por los candidatos a las elecciones primarias de Chile en 2025. Utiliza **Streamlit** y **pandas** para construir dashboards visuales que incluyen tablas, gráficos de barras y gráficos de dona.

🔎 Puedes acceder directamente al visualizador aquí:

👉 **[https://primarias2025cl.streamlit.app/](https://primarias2025cl.streamlit.app/)**

## 📊 Funcionalidades principales

- **Visualización general**: muestra el total de aportes por candidato.
- **Detalle por candidato**: entrega tabla de aportes individuales con filtros.
- **Gráficos**: distribución de tipos de aporte por candidato.
- **Descarga** de datos filtrados como CSV.

## 🧰 Tecnologías utilizadas

- [Python 3.9+](https://www.python.org/)
- [Streamlit](https://streamlit.io/)
- [matplotlib](https://matplotlib.org/)
- [st-aggrid](https://pypi.org/project/streamlit-aggrid/)
- [requests](https://docs.python-requests.org/en/latest/)

## 🚀 Cómo ejecutar el proyecto

1. **Clonar el repositorio:**

```bash
git clone https://github.com/hvillagranv/servel_aportes_primarias.git
cd servel_aportes_primarias
```

2. **Crear entorno virtual (opcional):**

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

3. **Instalar dependencias:**

```bash
pip install -r requirements.txt
```

4. **Ejecutar la aplicación:**

```bash
streamlit run app.py
```

## 📁 Estructura del proyecto

```
├── aportes.py                   # Archivo principal de Streamlit
├── graficos.py                  # Funciones de visualización y tablas
├── layout.py                    # Visualización de información de candidatos
├── candidatos.py                # Lista y metadatos de candidatos
├── requirements.txt             # Paquetes necesarios
├── estilos.css                  # Hoja de estilos del sitio
├── README.md                    # Este archivo
```

## 🌐 Fuente de datos

Los datos se obtienen automáticamente desde el sitio oficial de Servel:

```
https://repodocgastoelectoral.blob.core.windows.net/public/Presidencial_Parlamentaria_2025/Primarias/Reporte_Aportes_PRIMARIAS_2025.xlsx
```


## 📝 Licencia

MIT License. Libre para uso personal, educativo o institucional.

## 👤 Créditos

Desarrollado por [Hans Villagrán](https://www.linkedin.com/in/hvillagran/)