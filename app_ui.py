import os
import streamlit as st
from graph_agent import agente_analizador

st.set_page_config(
    page_title="Evaluador de HVs - Agente Inteligente", 
    page_icon="👔", 
    layout="wide"
)

st.title("👔 Sistema de Evaluación de HVs con Agentes de IA")
st.subheader("Flujo Local: LangGraph + ChromaDB + Llama 3.2")

# Crear Layout de dos columnas grandes (Video 2)
col_formulario, col_resultados = st.columns([1, 1], gap="large")

with col_formulario:
    st.header("📥 Carga de Información")
    
    # Input para el archivo PDF del currículum
    archivo_cv = st.file_uploader("1. Sube el CV del candidato (Formato PDF)", type=["pdf"])
    
    # Input para el perfil del puesto vacante
    descripcion_puesto = st.text_area(
        "2. Perfil Técnico y Requisitos de la Vacante", 
        height=250,
        placeholder="Ejemplo:\nDesarrollador Backend .NET\n- Experiencia en C# y Arquitectura Hexagonal.\n- Manejo de bases de datos relacionales y SQL."
    )
    
    # Botón de disparo
    btn_analizar = st.button("🚀 Iniciar Análisis de Candidato", type="primary")

with col_resultados:
    st.header("📊 Reporte de Selección")
    
    if btn_analizar:
        # Validación de campos obligatorios antes de ejecutar el grafo
        if archivo_cv is not None and descripcion_puesto.strip() != "":
            
            # Guardar el PDF temporalmente en el disco local para que el loader de LangChain lo lea
            path_temporal = f"temp_{archivo_cv.name}"
            with open(path_temporal, "wb") as f:
                f.write(archivo_cv.getbuffer())
            
            # Animación y visualización del flujo del agente (Concepto del Video 2)
            with st.spinner("El Agente está evaluando el perfil..."):
                barra_progreso = st.progress(0)
                
                st.caption("🤖 [Nodo: recuperar_info] Extrayendo texto y mapeando embeddings en ChromaDB...")
                barra_progreso.progress(40)
                
                # Ejecutar el grafo inyectando las variables de entrada
                inputs = {
                    "path_pdf": path_temporal,
                    "descripcion_puesto": descripcion_puesto
                }
                
                st.caption("🧠 [Nodo: analizar_cv] Comparando requisitos y estructurando respuesta con Llama 3.2...")
                barra_progreso.progress(75)
                
                output = agente_analizador.invoke(inputs)
                resultado = output["resultado_estructurado"]
                
                barra_progreso.progress(100)
                st.success("¡Análisis del Agente Completado con Éxito!")
            
            # Eliminar el archivo PDF temporal del sistema
            if os.path.exists(path_temporal):
                os.remove(path_temporal)
                
            # --- RENDERIZADO DE LOS RESULTADOS EXTRAÍDOS ---
            # Determinar el tag de nivel basado en el porcentaje de ajuste
            estado_candidato = "BAJO"
            if resultado.porcentaje_ajuste >= 70:
                estado_candidato = "EXCELENTE"
            elif resultado.porcentaje_ajuste >= 50:
                estado_candidato = "ACEPTABLE"
                
            # Mostrar la tarjeta de métrica principal
            st.metric(
                label="Porcentaje de Ajuste Semántico", 
                value=f"{resultado.porcentaje_ajuste}%", 
                delta=estado_candidato
            )
            
            # Alertas condicionales de color (Lógica del Video 2)
            if resultado.porcentaje_ajuste >= 70:
                st.success("🟢 **PERFIL RECOMENDADO:** El candidato cumple sólidamente con los criterios de la vacante.")
            elif resultado.porcentaje_ajuste >= 50:
                st.warning("🟡 **PERFIL EN EVALUACIÓN:** Posee las competencias base, pero requiere entrevista técnica profunda.")
            else:
                st.error("🔴 **PERFIL NO ALINEADO:** Las competencias del candidato no cubren los mínimos requeridos.")
            
            # Datos Generales
            st.markdown(f"**Candidato:** {resultado.nombre_candidato}")
            st.markdown(f"**Experiencia Total Calculada:** {resultado.experiencia_anos} años")
            st.markdown(f"**Educación / Certificaciones:** {resultado.education}")
            
            # Bloque de Fortalezas y Mejoras
            st.subheader("🎯 Fortalezas Principales")
            for f in resultado.fotalezas:
                st.markdown(f"- {f}")
                
            st.subheader("📈 Áreas de Crecimiento / Mejora")
            for am in resultado.areas_mejora:
                st.markdown(f"- {am}")
                
            # Etiquetas visuales de Skills
            st.subheader("🛠️ Tech Stack & Skills Identificadas")
            st.write(", ".join(f"`{h}`" for h in resultado.habilidades_clave))
            
            st.markdown("---")
            st.caption("**Detalle de Experiencia Relevante Extrada:**")
            st.info(resultado.experiencia_relevante)
            
        else:
            st.error("⚠️ Error: Asegúrate de cargar un archivo PDF y describir los requisitos de la vacante.")