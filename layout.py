import streamlit.components.v1 as components
from candidatos import candidatos

# Calcular altura dinámica basada en el número de candidatos
num_candidatos = len(candidatos)

def mostrar_candidatos(candidatos):
    # Genera los bloques HTML de cada candidato
    html_blocks = ""
    for idx, c in enumerate(candidatos):
        # Agregar clase 'activo' al primer candidato para móvil
        clase_activo = "activo" if idx == 0 else ""
        html_blocks += f"""
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
                <img src="{c["imagen"]}" style="
                    width: 100%;
                    height: 100%;
                    object-fit: cover;
                    object-position: {c["ajuste"]};
                    display: block;
                ">
                <img src="{c["icono_partido"]}" title="{c["partido"]}" style="
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

    # HTML, CSS y JS embebido con altura optimizada
    final_html = f"""
    <style>
    .candidato-container {{
        position: relative;
        width: 100%;
        overflow: visible;
        padding: 10px 0;
    }}

    .candidato-wrapper {{
        display: grid;
        gap: 15px;
        padding: 20px;
        justify-content: center;
        align-items: start;
        width: 100%;
    }}

    .candidato-card {{
        background-color: rgba(255, 255, 255, 0.02);
        border-radius: 14px;
        padding: 12px;
        text-align: center;
        color: white;
        font-family: sans-serif;
        box-sizing: border-box;
        height: fit-content;
        min-height: 380px;
    }}

    /* Pantallas grandes (>1024px): 4 candidatos por fila */
    @media (min-width: 1025px) {{
        .candidato-wrapper {{
            grid-template-columns: repeat(4, 1fr);
            max-width: 1040px;
            margin: 0 auto;
        }}
        
        .candidato-card {{
            width: 100%;
            max-width: 240px;
            display: block !important;
        }}
        
        .navigation {{
            display: none !important;
        }}
    }}

    /* Pantallas medianas (621px-1024px): 2 candidatos por fila */
    @media (min-width: 621px) and (max-width: 1024px) {{
        .candidato-wrapper {{
            grid-template-columns: repeat(2, 1fr);
            max-width: 520px;
            margin: 0 auto;
        }}
        
        .candidato-card {{
            width: 100%;
            max-width: 240px;
            display: block !important;
        }}
        
        .navigation {{
            display: none !important;
        }}
    }}

    /* Pantallas pequeñas (≤620px): 1 candidato visible con navegación compacta */
    @media (max-width: 620px) {{
        .candidato-container {{
            /* Altura fija para contener solo 1 candidato + navegación */
            min-height: 480px;
            max-height: 480px;
        }}
        
        .candidato-wrapper {{
            grid-template-columns: 1fr;
            max-width: 260px;
            margin: 0 auto;
            padding: 20px 20px 10px 20px; /* Reducir padding inferior */
        }}
        
        .candidato-card {{
            width: 100%;
            max-width: 240px;
            display: none;
        }}
        
        .candidato-card.activo {{
            display: block !important;
        }}
        
        .navigation {{
            display: flex !important;
            justify-content: space-between;
            align-items: center;
            margin-top: 15px;
            padding: 0 20px;
            position: absolute;
            bottom: 10px;
            left: 0;
            right: 0;
        }}
    }}

    /* Flechas de navegación */
    .flecha {{
        background-color: rgba(0, 0, 0, 0.7);
        color: white;
        border: none;
        border-radius: 50%;
        width: 36px;
        height: 36px;
        font-size: 16px;
        cursor: pointer;
        transition: background-color 0.3s ease;
        display: flex;
        align-items: center;
        justify-content: center;
    }}

    .flecha:hover {{
        background-color: rgba(0, 0, 0, 0.9);
    }}

    .flecha:disabled {{
        background-color: rgba(0, 0, 0, 0.3);
        cursor: not-allowed;
    }}

    /* Indicadores */
    .indicadores {{
        display: flex;
        justify-content: center;
        gap: 6px;
    }}

    .indicador {{
        width: 8px;
        height: 8px;
        border-radius: 50%;
        background-color: rgba(255, 255, 255, 0.3);
        cursor: pointer;
        transition: all 0.3s ease;
    }}

    .indicador:hover {{
        background-color: rgba(255, 255, 255, 0.6);
        transform: scale(1.2);
    }}

    .indicador.activo {{
        background-color: rgba(255, 255, 255, 0.9);
        transform: scale(1.3);
    }}

    /* Contador de candidatos */
    .contador-info {{
        display: flex;
        flex-direction: column;
        align-items: center;
        gap: 6px;
    }}

    .contador {{
        color: white;
        font-size: 12px;
        font-family: sans-serif;
        font-weight: 500;
    }}

    .navigation {{
        display: none;
    }}
    </style>

    <div class="candidato-container" id="candidatoContainer">
        <div class="candidato-wrapper" id="candidatosWrapper">
            {html_blocks}
        </div>
        
        <div class="navigation" id="navigation">
            <button class="flecha" id="prevBtn" onclick="cambiarCandidato(-1)">&#8592;</button>
            <div class="contador-info">
                <div class="contador" id="contador">1 / {len(candidatos)}</div>
                <div class="indicadores" id="indicadores"></div>
            </div>
            <button class="flecha" id="nextBtn" onclick="cambiarCandidato(1)">&#8594;</button>
        </div>
    </div>

    <script>
    let currentIndex = 0;
    const candidatos = document.querySelectorAll('.candidato-card');
    const totalCandidatos = candidatos.length;
    
    // Función para ajustar altura optimizada
    function ajustarAlturaAutomatica() {{
        const container = document.getElementById('candidatoContainer');
        if (container) {{
            let alturaCalculada;
            
            if (window.innerWidth <= 620) {{
                // En móvil: altura fija para 1 candidato + navegación
                alturaCalculada = 480;
            }} else {{
                // En desktop/tablet: altura automática basada en contenido
                alturaCalculada = container.scrollHeight;
            }}
            
            // Comunicar altura a Streamlit
            if (window.parent && window.parent.postMessage) {{
                window.parent.postMessage({{
                    type: 'streamlit:componentReady',
                    height: alturaCalculada + 20
                }}, '*');
            }}
            
            if (window.frameElement) {{
                window.frameElement.style.height = (alturaCalculada + 20) + 'px';
            }}
        }}
    }}
    
    // Función para actualizar la vista
    function actualizarVista() {{
        const width = window.innerWidth;
        
        if (width <= 620) {{
            // Mostrar solo un candidato con navegación
            candidatos.forEach((card, index) => {{
                card.classList.toggle('activo', index === currentIndex);
            }});
            
            // Actualizar indicadores
            actualizarIndicadores();
            
            // Actualizar contador
            const contador = document.getElementById('contador');
            if (contador) {{
                contador.textContent = `${{currentIndex + 1}} / ${{totalCandidatos}}`;
            }}
            
            // Actualizar botones
            const prevBtn = document.getElementById('prevBtn');
            const nextBtn = document.getElementById('nextBtn');
            
            if (prevBtn) prevBtn.disabled = currentIndex === 0;
            if (nextBtn) nextBtn.disabled = currentIndex === totalCandidatos - 1;
            
            // Mostrar navegación solo si hay más de 1 candidato
            const navigation = document.getElementById('navigation');
            if (navigation && totalCandidatos > 1) {{
                navigation.style.display = 'flex';
            }} else if (navigation) {{
                navigation.style.display = 'none';
            }}
        }} else {{
            // Mostrar todos los candidatos en desktop/tablet
            candidatos.forEach(card => {{
                card.classList.remove('activo');
                card.style.display = 'block';
            }});
            
            // Ocultar navegación
            const navigation = document.getElementById('navigation');
            if (navigation) {{
                navigation.style.display = 'none';
            }}
        }}
        
        // Ajustar altura después de cambiar la vista
        setTimeout(ajustarAlturaAutomatica, 100);
    }}
    
    // Función para actualizar indicadores
    function actualizarIndicadores() {{
        const indicadores = document.querySelectorAll('.indicador');
        indicadores.forEach((ind, index) => {{
            ind.classList.toggle('activo', index === currentIndex);
        }});
    }}
    
    // Función para cambiar candidato
    function cambiarCandidato(direccion) {{
        if (window.innerWidth > 620 || totalCandidatos <= 1) return;
        
        const newIndex = currentIndex + direccion;
        if (newIndex >= 0 && newIndex < totalCandidatos) {{
            currentIndex = newIndex;
            actualizarVista();
        }}
    }}
    
    // Función para ir a un candidato específico
    function irACandidato(index) {{
        if (window.innerWidth > 620 || totalCandidatos <= 1) return;
        if (index >= 0 && index < totalCandidatos) {{
            currentIndex = index;
            actualizarVista();
        }}
    }}
    
    // Crear indicadores
    function crearIndicadores() {{
        const indicadoresContainer = document.getElementById('indicadores');
        if (!indicadoresContainer) return;
        
        indicadoresContainer.innerHTML = '';
        
        // Solo crear indicadores si hay más de 1 candidato
        if (totalCandidatos > 1) {{
            for (let i = 0; i < totalCandidatos; i++) {{
                const indicador = document.createElement('div');
                indicador.className = 'indicador';
                if (i === currentIndex) indicador.classList.add('activo');
                indicador.onclick = () => irACandidato(i);
                indicadoresContainer.appendChild(indicador);
            }}
        }}
    }}
    
    // Manejar cambio de tamaño de ventana
    window.addEventListener('resize', () => {{
        const width = window.innerWidth;
        if (width > 620) {{
            currentIndex = 0;
        }}
        actualizarVista();
    }});
    
    // Manejar navegación con teclado
    document.addEventListener('keydown', (e) => {{
        if (window.innerWidth <= 620 && totalCandidatos > 1) {{
            if (e.key === 'ArrowLeft') cambiarCandidato(-1);
            if (e.key === 'ArrowRight') cambiarCandidato(1);
        }}
    }});
    
    // Soporte para gestos táctiles en móvil
    let startX = 0;
    let endX = 0;
    
    document.addEventListener('touchstart', (e) => {{
        if (window.innerWidth <= 620 && totalCandidatos > 1) {{
            startX = e.touches[0].clientX;
        }}
    }});
    
    document.addEventListener('touchend', (e) => {{
        if (window.innerWidth <= 620 && totalCandidatos > 1) {{
            endX = e.changedTouches[0].clientX;
            const diffX = startX - endX;
            
            // Swipe izquierda (siguiente)
            if (diffX > 50 && currentIndex < totalCandidatos - 1) {{
                currentIndex++;
                actualizarVista();
            }}
            // Swipe derecha (anterior)
            else if (diffX < -50 && currentIndex > 0) {{
                currentIndex--;
                actualizarVista();
            }}
        }}
    }});
    
    // Inicializar cuando el DOM esté listo
    function inicializar() {{
        if (window.innerWidth <= 620 && candidatos.length > 0) {{
            candidatos[0].classList.add('activo');
        }}
        
        crearIndicadores();
        actualizarVista();
        
        // Ajustar altura inicial
        setTimeout(ajustarAlturaAutomatica, 200);
    }}
    
    // Ejecutar inicialización
    if (document.readyState === 'loading') {{
        document.addEventListener('DOMContentLoaded', inicializar);
    }} else {{
        inicializar();
    }}
    
    // Observador para detectar cambios en el contenido
    const observer = new ResizeObserver(entries => {{
        setTimeout(ajustarAlturaAutomatica, 50);
    }});
    
    // Observar el contenedor principal
    const container = document.getElementById('candidatoContainer');
    if (container) {{
        observer.observe(container);
    }}
    </script>
    """

    # Usar height=None para que Streamlit permita altura automática
    components.html(final_html, height=None, scrolling=False)