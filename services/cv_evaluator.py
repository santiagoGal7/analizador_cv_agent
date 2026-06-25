from typing import TypedDict, Optional
from models.cv_model import AnalisisCV
from prompts.cv_prompts import SYSTEM_PROMPT, ANALISIS_PROMPT
from services.pdf_processor import crear_chunks_documento
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# Definición del Estado del Grafo (State)
class AgenteState(TypedDict, total=False):
    texto_completo: str
    descripcion_puesto: str
    contexto_recuperado: str
    resultado_estructurado: AnalisisCV
    model_provider: str
    model_name: str
    api_key: str

# NODO 1: Indexación RAG Temporal con ChromaDB
def nodo_recuperar_contexto(state: AgenteState):
    provider = state.get("model_provider", "Ollama")
    api_key = state.get("api_key", "")
    
    if provider == "Gemini":
        from langchain_google_genai import GoogleGenerativeAIEmbeddings
        embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=api_key if api_key else None
        )
    else:
        embeddings = OllamaEmbeddings(model="nomic-embed-text")
        
    chunks = crear_chunks_documento(state["texto_completo"])
    
    # Crear base de datos vectorial temporal en memoria para la búsqueda semántica
    vector_db = Chroma.from_documents(documents=chunks, embedding=embeddings)
    retriever = vector_db.as_retriever(search_kwargs={"k": 3})
    
    docs_relevantes = retriever.invoke(state["descripcion_puesto"])
    contexto = "\n\n".join(d.page_content for d in docs_relevantes)
    
    vector_db.delete_collection()  # Limpieza de memoria instantánea
    return {"contexto_recuperado": contexto}

# NODO 2: Extracción con Llama 3.2/Gemini Structured Output
def nodo_analizar_cv(state: AgenteState):
    provider = state.get("model_provider", "Ollama")
    model_name = state.get("model_name", "qwen2.5-coder:7b")
    api_key = state.get("api_key", "")
    
    if provider == "Gemini":
        from langchain_google_genai import ChatGoogleGenerativeAI
        llm = ChatGoogleGenerativeAI(
            model=model_name,
            temperature=0.0,
            google_api_key=api_key if api_key else None
        )
    else:
        llm = ChatOllama(model=model_name, temperature=0.0)
        
    llm_estructurado = llm.with_structured_output(AnalisisCV)
    
    prompt_template = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("human", ANALISIS_PROMPT)
    ])
    
    prompt_formateado = prompt_template.format_messages(
        descripcion_puesto=state["descripcion_puesto"],
        texto_cv=state["texto_completo"],
        contexto_semantico=state["contexto_recuperado"]
    )
    
    try:
        resultado = llm_estructurado.invoke(prompt_formateado)
    except Exception as e:
        # Fallback seguro para evitar que la UI se rompa si falla la estructuración
        resultado = AnalisisCV(
            nombre_candidato=f"Error en análisis ({provider})",
            experiencia_anos=0,
            habilidades_clave=[],
            education="No extraído",
            experiencia_relevante=f"Error al procesar la salida estructurada: {str(e)}",
            fotalezas=[],
            areas_mejora=[],
            porcentaje_ajuste=0
        )
        
    return {"resultado_estructurado": resultado}

# Construcción de la Máquina de Estados (LangGraph)
workflow = StateGraph(AgenteState)
workflow.add_node("recuperar_contexto", nodo_recuperar_contexto)
workflow.add_node("analizar_cv", nodo_analizar_cv)

workflow.set_entry_point("recuperar_contexto")
workflow.add_edge("recuperar_contexto", "analizar_cv")
workflow.add_edge("analizar_cv", END)

agente_cv = workflow.compile()