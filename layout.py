import streamlit.components.v1 as components

def mostrar_candidatos(candidatos):
    # Cargar CSS externo
    with open("candidatos.css", encoding="utf-8") as f:
        estilos = f"<style>{f.read()}</style>"

    # Cargar JS externo
    with open("candidatos.js", encoding="utf-8") as f:
        script = f"<script>{f.read()}</script>"

    # Crear todos los bloques HTML de los candidatos
    html_cards = "\n".join([
        generar_candidato_card(c, idx == 0)
        for idx, c in enumerate(candidatos)
    ])

    # Navegación (solo móvil)
    navigation = f"""
    <div class="navigation" id="navigation">
        <button class="flecha" id="prevBtn">&#8592;</button>
        <div class="contador-info">
            <div class="contador" id="contador">1 / {len(candidatos)}</div>
            <div class="indicadores" id="indicadores"></div>
        </div>
        <button class="flecha" id="nextBtn">&#8594;</button>
    </div>
    """

    # HTML final
    html_final = f"""
    {estilos}

    <div class="candidato-container" id="candidatoContainer">
        <div class="candidato-wrapper" id="candidatosWrapper">
            {html_cards}
        </div>
        {navigation}
    </div>

    {script}
    """

    # Renderizar en Streamlit
    components.html(html_final, height=None, scrolling=False)

def generar_candidato_card(c, activo=False):
    clase_activo = "activo" if activo else ""
    return f"""
    <div class="candidato-card {clase_activo}" style="border: 3px solid {c["color_partido"]};">
        <div style="
            width: 160px;
            height: 160px;
            border-radius: 10px;
            overflow: hidden;
            margin: auto;
            position: relative;
            box-shadow: 0 2px 6px rgba(0,0,0,0.3);
        ">
            <img src="{c["imagen"]}" alt="Foto de {c["nombre"]}" style="
                width: 100%;
                height: 100%;
                object-fit: cover;
                object-position: {c["ajuste"]};
                display: block;
            ">
            <img src="{c["icono_partido"]}" alt="Logo de {c["partido"]}" title="{c["partido"]}" style="
                width: 32px;
                height: 32px;
                position: absolute;
                bottom: 6px;
                right: 6px;
                border-radius: 50%;
                border: 2px solid white;
                background: white;
                box-shadow: 0 0 4px rgba(0,0,0,0.4);
            ">
        </div>

        <div style="margin-top: 10px; font-size: 17px; font-weight: bold; text-align: center;">{c["nombre"]}</div>
        <div style="font-size: 13px; color: #ccc; font-style: italic; text-align: center;">({c["partido"]})</div>

        <div style="margin-top: 10px; font-size: 13px; text-align: center;">
            <div><strong>Edad:</strong> {c["edad"]}</div>
            <div><strong>Profesión:</strong> {c["profesion"]}</div>
            <div><strong>Programa:</strong> <a href="{c["programa"]}" target="_blank" style="color:#00AEEF; text-decoration: none;">ver</a></div>
            <div><strong>Sitio web:</strong> <a href="{c["web"]}" target="_blank" style="color:#00AEEF; text-decoration: none;">visitar</a></div>
            <div style="margin-top: 6px; display: flex; justify-content: center; gap: 10px; align-items: center;">
                <a href="{c["twitter"]}" target="_blank" style="text-decoration: none; display: inline-block;">
                    <img src="https://cdn.jsdelivr.net/npm/simple-icons@latest/icons/x.svg" title="X (Twitter)" style="width: 24px; height: 24px; filter: invert(1);">
                </a>
                <a href="{c["instagram"]}" target="_blank" style="text-decoration: none; display: inline-block;">
                    <img src="https://cdn-icons-png.flaticon.com/24/2111/2111463.png" title="Instagram" style="width: 24px; height: 24px;">
                </a>
            </div>
        </div>
    </div>
    """
