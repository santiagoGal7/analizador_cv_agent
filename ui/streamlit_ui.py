import os
import sys

# Añadir el directorio raíz del proyecto al sys.path para resolver importaciones
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import streamlit as st
from dotenv import load_dotenv
from services.pdf_processor import extraer_texto_pdf
from services.cv_evaluator import agente_cv

# Cargar variables de entorno
load_dotenv()

st.set_page_config(page_title="Analizador por Capas - HV", page_icon="👔", layout="wide")

# Estilos CSS Premium (Optimizados y sin bugs de emojis o contenedores rotos)
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Outfit:wght@300;400;500;600;700&display=swap');

/* Aplicar la fuente Outfit */
html, body, [class*="css"], .stMarkdown {
    font-family: 'Outfit', sans-serif !important;
}

/* Eliminar el padding superior excesivo por defecto de Streamlit */
.block-container {
    padding-top: 1.5rem !important;
    padding-bottom: 1rem !important;
}

/* Título Principal con Gradiente (Separado del Emoji para evitar el cuadro azul) */
.title-container {
    text-align: center;
    padding: 0.5rem 0 1rem 0 !important;
}
.emoji-header {
    font-size: 3rem;
    margin-bottom: 0.2rem;
}
.main-title {
    font-size: 2.8rem;
    font-weight: 700;
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 50%, #ec4899 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    margin: 0;
    line-height: 1.2;
}
.main-subheader {
    font-size: 1.1rem;
    color: #8a99ad;
    margin-top: 0.5rem;
}

/* Botón Ejecutar */
div.stButton > button {
    background: linear-gradient(135deg, #3b82f6 0%, #8b5cf6 100%);
    color: white !important;
    border: none !important;
    padding: 0.8rem 1.5rem !important;
    font-size: 1.1rem !important;
    font-weight: 600 !important;
    border-radius: 12px !important;
    box-shadow: 0 4px 15px rgba(59, 130, 246, 0.3) !important;
    transition: all 0.3s ease !important;
    width: 100% !important;
    cursor: pointer;
    margin-top: 1rem;
}
div.stButton > button:hover {
    background: linear-gradient(135deg, #8b5cf6 0%, #ec4899 100%) !important;
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 25px rgba(139, 92, 246, 0.4) !important;
}

/* Badges / Pastillas para Skills */
.skill-pill {
    display: inline-block;
    background: rgba(59, 130, 246, 0.12);
    border: 1px solid rgba(59, 130, 246, 0.25);
    color: #60a5fa !important;
    padding: 0.35rem 0.85rem;
    border-radius: 20px;
    font-size: 0.85rem;
    font-weight: 500;
    margin-right: 0.5rem;
    margin-bottom: 0.5rem;
}

/* Alertas de Nivel */
.alert-badge {
    padding: 1rem 1.5rem;
    border-radius: 12px;
    font-weight: 600;
    font-size: 1.1rem;
    display: flex;
    align-items: center;
    gap: 0.6rem;
    margin-bottom: 1.5rem;
}
.alert-badge.excellent {
    background: rgba(16, 185, 129, 0.08);
    border: 1px solid rgba(16, 185, 129, 0.25);
    color: #34d399;
}
.alert-badge.acceptable {
    background: rgba(245, 158, 11, 0.08);
    border: 1px solid rgba(245, 158, 11, 0.25);
    color: #fbbf24;
}
.alert-badge.low {
    background: rgba(239, 68, 68, 0.08);
    border: 1px solid rgba(239, 68, 68, 0.25);
    color: #f87171;
}

/* Elementos de Lista (Fortalezas / Gaps) */
.bullet-item {
    display: flex;
    align-items: flex-start;
    gap: 0.6rem;
    margin-bottom: 0.6rem;
    font-size: 0.95rem;
    line-height: 1.4;
}
.bullet-item.strength::before {
    content: "✓";
    color: #34d399;
    font-weight: bold;
    font-size: 1.1rem;
}
.bullet-item.gap::before {
    content: "⚠";
    color: #fbbf24;
    font-weight: bold;
    font-size: 1.1rem;
}

/* Placeholder de Espera */
.waiting-placeholder {
    text-align: center;
    padding: 5rem 2rem;
    color: #6b7280;
    border: 2px dashed rgba(255, 255, 255, 0.08);
    border-radius: 16px;
    background: rgba(255, 255, 255, 0.01);
}
</style>
""", unsafe_allow_html=True)

# Barra lateral para configuración de IA y modelo
with st.sidebar:
    st.markdown("""
        <div style='text-align: center; padding: 0.5rem 0;'>
            <span style='font-size: 2.5rem;'>⚙️</span>
            <h3 style='margin: 10px 0 15px 0;'>Configuración de IA</h3>
        </div>
    """, unsafe_allow_html=True)
    
    model_provider = st.selectbox(
        "Proveedor de IA",
        options=["Ollama (Local - Libre y Privado)", "Google Gemini (Nube - Alta Precisión)"],
        index=0,
        help="Elige si deseas procesar tu análisis usando un modelo local (Ollama) o el servicio en la nube de Google (Gemini)."
    )
    
    provider_key = "Ollama" if "Ollama" in model_provider else "Gemini"
    
    if provider_key == "Ollama":
        model_name = st.selectbox(
            "Modelo Local (Ollama)",
            options=["qwen2.5-coder:7b", "llama3.2:3b", "llama3.1:8b", "Otro (Especificar)"],
            index=0
        )
        if model_name == "Otro (Especificar)":
            model_name = st.text_input("Nombre de modelo personalizado en Ollama", value="qwen2.5-coder:7b")
    else:
        model_name = st.selectbox(
            "Modelo Gemini",
            options=["gemini-2.5-flash", "gemini-2.5-pro", "gemini-2.0-flash", "gemini-2.0-flash-lite", "Otro (Especificar)"],
            index=0
        )
        if model_name == "Otro (Especificar)":
            model_name = st.text_input("Nombre de modelo personalizado Gemini", value="gemini-2.5-flash")

# Contenedor del Título de la Aplicación (Emoji fuera del título con gradiente)
st.markdown("""
<div class="title-container">
    <div class="emoji-header">👔</div>
    <h1 class="main-title">Evaluador Inteligente de Hojas de Vida</h1>
    <p class="main-subheader">Análisis de Perfiles y Ajuste Semántico con Inteligencia Artificial Local y Nube</p>
</div>
""", unsafe_allow_html=True)

col_formulario, col_metricas = st.columns([1, 1], gap="large")

with col_formulario:
    # Usamos container con borde de Streamlit para un diseño limpio y moderno nativo
    with st.container(border=True):
        st.subheader("📥 Carga de Información")
        archivo_cargado = st.file_uploader("Subir Currículum del Candidato (PDF)", type=["pdf"])
        requisitos_vacante = st.text_area("Requisitos Clave de la Vacante", height=220, placeholder="Pega el perfil buscado aquí...")
        btn_ejecutar = st.button("Ejecutar Análisis de Selección", type="primary")

with col_metricas:
    if btn_ejecutar:
        # Detectar API key en entorno / .env
        api_key = os.getenv("GEMINI_API_KEY") or os.getenv("GOOGLE_API_KEY") or ""
        
        if provider_key == "Gemini" and not api_key.strip():
            st.error("❌ Por favor, configura tu Clave API de Gemini en el archivo `.env` (usando `GEMINI_API_KEY=tu_clave`) para poder continuar.")
        elif archivo_cargado and requisitos_vacante.strip():
            spinner_msg = "Procesando capas lógicas en tu servidor local de IA..." if provider_key == "Ollama" else f"Procesando capas lógicas con {model_name} en la nube..."
            with st.spinner(spinner_msg):
                # Extraer texto directo desde los bytes en memoria
                texto_cv = extraer_texto_pdf(archivo_cargado.read())
                
                # Invocación limpia del grafo pasando el estado inicial con el modelo seleccionado
                inputs = {
                    "texto_completo": texto_cv,
                    "descripcion_puesto": requisitos_vacante,
                    "model_provider": provider_key,
                    "model_name": model_name,
                    "api_key": api_key
                }
                output = agente_cv.invoke(inputs)
                res = output["resultado_estructurado"]
            
            # Encapsulamos los resultados en un contenedor estético
            with st.container(border=True):
                st.subheader("📊 Reporte de Compatibilidad")
                
                # Alerta visual basada en el porcentaje
                if res.porcentaje_ajuste >= 70:
                    st.markdown(f'<div class="alert-badge excellent">🟢 <b>CANDIDATO ALTAMENTE RECOMENDADO</b> ({res.porcentaje_ajuste}%)</div>', unsafe_allow_html=True)
                elif res.porcentaje_ajuste >= 50:
                    st.markdown(f'<div class="alert-badge acceptable">🟡 <b>CANDIDATO EN EVALUACIÓN</b> ({res.porcentaje_ajuste}%)</div>', unsafe_allow_html=True)
                else:
                    st.markdown(f'<div class="alert-badge low">🔴 <b>CANDIDATO NO ALINEADO A LA VACANTE</b> ({res.porcentaje_ajuste}%)</div>', unsafe_allow_html=True)
                
                # Métricas Principales
                col_metric_1, col_metric_2 = st.columns(2)
                with col_metric_1:
                    st.metric(label="Ajuste del Perfil", value=f"{res.porcentaje_ajuste}%")
                with col_metric_2:
                    st.metric(label="Experiencia Laboral", value=f"{res.experiencia_anos} años")
                
                st.markdown("---")
                
                # Datos de Identificación
                st.markdown(f"👤 **Candidato:** {res.nombre_candidato}")
                st.markdown(f"🎓 **Formación:** {res.education}")
                
                # Fortalezas y Áreas de Mejora
                st.markdown("### 🎯 Fortalezas de Selección")
                for f in res.fotalezas:
                    st.markdown(f'<div class="bullet-item strength">{f}</div>', unsafe_allow_html=True)
                    
                st.markdown("### 📈 Áreas de Mejora / Gaps")
                if res.areas_mejora:
                    for am in res.areas_mejora:
                        st.markdown(f'<div class="bullet-item gap">{am}</div>', unsafe_allow_html=True)
                else:
                    st.write("No se identificaron brechas críticas.")
                    
                # Skills & Tech Stack
                st.markdown("### 🛠️ Skills & Tech Stack")
                skills_html = " ".join(f'<span class="skill-pill" style="display: inline-block; margin-right: 8px; margin-bottom: 8px; padding: 0.35rem 0.85rem; border-radius: 20px; font-size: 0.85rem; font-weight: 500;">{h}</span>' for h in res.habilidades_clave)
                st.markdown(f'<div>{skills_html}</div>', unsafe_allow_html=True)
                
                st.markdown("---")
                st.caption("**Historial Laboral Relevante Extraído:**")
                st.info(res.experiencia_relevante)
        else:
            st.error("Por favor, asegúrate de subir la Hoja de Vida en PDF y rellenar los requisitos del puesto.")
    else:
        st.markdown("""
        <div class="waiting-placeholder">
            <div style="font-size: 3rem; margin-bottom: 1rem;">📄</div>
            <h3>Esperando Carga de Datos</h3>
            <p>Sube la Hoja de Vida en formato PDF y define los requisitos de la vacante, luego presiona "Ejecutar Análisis de Selección".</p>
        </div>
        """, unsafe_allow_html=True)