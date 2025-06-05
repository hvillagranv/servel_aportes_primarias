import streamlit.components.v1 as components

def mostrar_candidatos_html(candidatos):
    html_blocks = ""
    for idx, c in enumerate(candidatos):
        html_blocks += f"""
        <div style="text-align: center; width: 220px; margin: 15px;">
            <div onclick="toggleInfo{idx}()" style="
                width: 160px;
                height: 160px;
                border-radius: 10px;
                overflow: hidden;
                box-shadow: 0 2px 6px rgba(0,0,0,0.2);
                border-top: 8px solid {c["color_partido"]};
                position: relative;
                cursor: pointer;
                margin: auto;
            ">
                <img src="{c["imagen"]}" style="width: 100%; height: 100%; object-fit: cover; object-position: {c["ajuste"]}; display: block;">
                <img src="{c["icono_partido"]}" title="{c["partido"]}" style="
                    width: 32px;
                    height: 32px;
                    position: absolute;
                    bottom: 5px;
                    right: 5px;
                    border-radius: 50%;
                    border: 2px solid white;
                    background: white;
                    box-shadow: 0 0 4px rgba(0,0,0,0.4);
                ">
            </div>
            <div style="margin-top: 10px; font-size: 18px; font-weight: bold;">{c["nombre"]}</div>
            <div style="font-size: 14px; color: #888;">({c["partido"]})</div>
            <div id="info{idx}" style="display: none; margin-top: 10px; border-radius: 8px; padding: 10px; font-size: 13px; color: white; text-align: left;">
                <div><strong>Edad:</strong> {c["edad"]}</div>
                <div><strong>Profesión:</strong> {c["profesion"]}</div>
                <div><strong>Programa:</strong> <a href="{c["programa"]}" target="_blank">ver</a></div>
                <div><strong>Sitio web:</strong> <a href="{c["web"]}" target="_blank">visitar</a></div>
                <div style="margin-top: 6px;">
                    <a href="{c["twitter"]}" target="_blank" style="margin-right: 8px;">
                        <img src="https://cdn-icons-png.flaticon.com/24/733/733579.png" title="Twitter">
                    </a>
                    <a href="{c["instagram"]}" target="_blank">
                        <img src="https://cdn-icons-png.flaticon.com/24/2111/2111463.png" title="Instagram">
                    </a>
                </div>
            </div>
        </div>
        <script>
            function toggleInfo{idx}() {{
                var x = document.getElementById("info{idx}");
                x.style.display = (x.style.display === "none") ? "block" : "none";
            }}
        </script>
        """
    final_html = f"<div style='display: flex; flex-wrap: wrap; justify-content: center;'>{html_blocks}</div>"
    components.html(final_html, height=400, scrolling=True)