import streamlit.components.v1 as components

def mostrar_candidatos_html(candidatos):
    html_blocks = ""
    for idx, c in enumerate(candidatos):
        html_blocks += f"""
        <div style="
            width: 240px;
            margin: 10px;
            background-color: rgba(255, 255, 255, 0.02);
            border: 3px solid {c["color_partido"]};
            border-radius: 14px;
            padding: 12px;
            text-align: center;
            color: white;
            font-family: sans-serif;
        ">
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

            <div style="margin-top: 10px; font-size: 17px; font-weight: bold;">{c["nombre"]}</div>
            <div style="font-size: 13px; color: #ccc; font-style: italic;">({c["partido"]})</div>

            <div style="
                margin-top: 10px;
                font-size: 13px;
                text-align: left;
            ">
                <div><strong>Edad:</strong> {c["edad"]}</div>
                <div><strong>Profesión:</strong> {c["profesion"]}</div>
                <div><strong>Programa:</strong> <a href="{c["programa"]}" target="_blank" style="color:#00AEEF;">ver</a></div>
                <div><strong>Sitio web:</strong> <a href="{c["web"]}" target="_blank" style="color:#00AEEF;">visitar</a></div>
                <div style="margin-top: 6px;">
                    <a href="{c["twitter"]}" target="_blank" style="margin-right: 10px;">
                        <img src="https://cdn-icons-png.flaticon.com/24/733/733579.png" title="Twitter">
                    </a>
                    <a href="{c["instagram"]}" target="_blank">
                        <img src="https://cdn-icons-png.flaticon.com/24/2111/2111463.png" title="Instagram">
                    </a>
                </div>
            </div>
        </div>
        """

    final_html = f"""
    <div style='display: flex; flex-wrap: wrap; justify-content: center; margin-bottom: 10px;'>
        {html_blocks}
    </div>
    """
    components.html(final_html, height=380, scrolling=False)
