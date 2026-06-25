import os
import sys

# Añadir el directorio raíz del proyecto al sys.path para resolver importaciones
root_path = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if root_path not in sys.path:
    sys.path.insert(0, root_path)

import streamlit as st
from services.pdf_processor import extraer_texto_pdf
from services.cv_evaluator import agente_cv

st.set_page_config(page_title="Analizador por Capas - HV", page_icon="👔", layout="wide")

st.title("👔 Evaluador Avanzado de Hojas de Vida")
st.subheader("Arquitectura de Producción Modular")

col_formulario, col_metricas = st.columns([1, 1], gap="large")

with col_formulario:
    st.header("📥 Entrada de Datos")
    archivo_cargado = st.file_uploader("Subir Currículum del Candidato (PDF)", type=["pdf"])
    requisitos_vacante = st.text_area("Requisitos Clave de la Vacante", height=220, placeholder="Pega el perfil buscado aquí...")
    btn_ejecutar = st.button("Ejecutar Análisis de Selección", type="primary")

with col_metricas:
    st.header("📊 Reporte de Compatibilidad")
    
    if btn_ejecutar:
        if archivo_cargado and requisitos_vacante.strip():
            with st.spinner("Agente LangGraph procesando las capas lógicas de forma local..."):
                # Extraer texto directo desde los bytes en memoria (Video 2)
                texto_cv = extraer_texto_pdf(archivo_cargado.read())
                
                # Invocación limpia del grafo pasando el estado inicial
                inputs = {
                    "texto_completo": texto_cv,
                    "descripcion_puesto": requisitos_vacante
                }
                output = agente_cv.invoke(inputs)
                res = output["resultado_estructurado"]
            
            # Gestión visual dinámica de alertas (Lógica explicada en el Video 2)
            alerta_nivel = "BAJO"
            if res.porcentaje_ajuste >= 70:
                alerta_nivel = "EXCELENTE"
                st.success(f"🟢 **CANDIDATO ALTAMENTE RECOMENDADO** ({res.porcentaje_ajuste}%)")
            elif res.porcentaje_ajuste >= 50:
                alerta_nivel = "ACEPTABLE"
                st.warning(f"🟡 **CANDIDATO EN EVALUACIÓN** ({res.porcentaje_ajuste}%)")
            else:
                st.error(f"🔴 **CANDIDATO NO ALINEADO A LA VACANTE** ({res.porcentaje_ajuste}%)")
            
            # Renderizado del componente Metric principal
            st.metric(label="Ajuste Semántico del Perfil", value=f"{res.porcentaje_ajuste}%", delta=alerta_nivel)
            
            # Desglose de campos Pydantic validados
            st.markdown(f"**Nombre Identificado:** {res.nombre_candidato}")
            st.markdown(f"**Años de Experiencia Estimados:** {res.experiencia_anos} años")
            st.markdown(f"**Educación / Títulos:** {res.education}")
            
            st.subheader("🎯 Fortalezas de Selección")
            for f in res.fotalezas:
                st.markdown(f"- {f}")
                
            st.subheader("📈 Áreas de Mejora / Gaps")
            for am in res.areas_mejora:
                st.markdown(f"- {am}")
                
            st.subheader("🛠️ Skills & Tech Stack")
            st.write(", ".join(f"`{h}`" for h in res.habilidades_clave))
            
            st.markdown("---")
            st.caption("**Historial Laboral Relevante Extraído:**")
            st.info(res.experiencia_relevante)
        else:
            st.error("Por favor, asegúrate de subir la Hoja de Vida en PDF y rellenar los requisitos del puesto.")
