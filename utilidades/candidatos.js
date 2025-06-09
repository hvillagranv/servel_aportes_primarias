// components/script.js

let currentIndex = 0;
let candidatos = [];
let totalCandidatos = 0;

function ajustarAltura() {
    const container = document.getElementById('candidatoContainer');
    if (!container) return;
    const altura = window.innerWidth <= 620 ? 480 : container.scrollHeight;
    if (window.parent?.postMessage) {
        window.parent.postMessage({ type: 'streamlit:componentReady', height: altura + 20 }, '*');
    }
    if (window.frameElement) {
        window.frameElement.style.height = (altura + 20) + 'px';
    }
}

function actualizarVista() {
    if (window.innerWidth <= 620) {
        candidatos.forEach((card, i) => {
            card.classList.toggle('activo', i === currentIndex);
        });
        document.getElementById('contador').textContent = `${currentIndex + 1} / ${totalCandidatos}`;
        document.getElementById('prevBtn').disabled = currentIndex === 0;
        document.getElementById('nextBtn').disabled = currentIndex === totalCandidatos - 1;
    } else {
        candidatos.forEach(card => card.classList.remove('activo'));
    }
    ajustarAltura();
}

function cambiarCandidato(direccion) {
    const nuevo = currentIndex + direccion;
    if (nuevo >= 0 && nuevo < totalCandidatos) {
        currentIndex = nuevo;
        actualizarVista();
    }
}

function inicializar() {
    candidatos = document.querySelectorAll('.candidato-card');
    totalCandidatos = candidatos.length;
    if (window.innerWidth <= 620 && candidatos.length > 0) {
        candidatos[0].classList.add('activo');
    }
    document.getElementById('prevBtn')?.addEventListener('click', () => cambiarCandidato(-1));
    document.getElementById('nextBtn')?.addEventListener('click', () => cambiarCandidato(1));
    actualizarVista();
}

if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', inicializar);
} else {
    inicializar();
}
window.addEventListener('resize', () => {
    if (window.innerWidth > 620) currentIndex = 0;
    actualizarVista();
});
