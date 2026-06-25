import os
from typing import TypedDict
from models import AnalisisCV
from langchain_community.document_loaders import PyPDFLoader
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_chroma import Chroma
from langchain_ollama import OllamaEmbeddings, ChatOllama
from langchain_core.prompts import ChatPromptTemplate
from langgraph.graph import StateGraph, END

# Definición del Estado del Grafo (State)
class AgenteState(TypedDict):
    path_pdf: str
    descripcion_puesto: str
    contexto_recuperado: str
    resultado_estructurado: AnalisisCV

# NODO 1: Extracción, Particionamiento y Recuperación RAG
def nodo_recuperar_informacion(state: AgenteState):
    # Configurar embeddings locales con Llama 3.2
    embeddings_locales = OllamaEmbeddings(model="nomic-embed-text")
    
    # Cargar el PDF de la HV (Concepto visto en el Video 3)
    loader = PyPDFLoader(state["path_pdf"])
    paginas = loader.load()
    
    # Segmentación inteligente en chunks para no saturar el contexto (Video 4)
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=2000, chunk_overlap=200)
    chunks = text_splitter.split_documents(paginas)
    
    # Almacenamiento e indexación vectorial temporal en ChromaDB
    vector_db = Chroma.from_documents(documents=chunks, embedding=embeddings_locales)
    
    # Recuperación por similitud semántica comparando con la vacante
    retriever = vector_db.as_retriever(search_kwargs={"k": 4})
    docs_relevantes = retriever.invoke(state["descripcion_puesto"])
    
    # Unificar el contexto recuperado
    contexto = "\n\n".join(doc.page_content for doc in docs_relevantes)
    
    # Vaciar la colección temporal de la memoria
    vector_db.delete_collection()
    
    return {"contexto_recuperado": contexto}

# NODO 2: Evaluación del Candidato con Salida Estructurada
def nodo_analizar_perfil(state: AgenteState):
    # Inicializar Llama 3.2 con temperatura baja para garantizar fidelidad técnica
    llm = ChatOllama(model="llama3.2:3b", temperature=0.1)
    llm_estructurado = llm.with_structured_output(AnalisisCV)
    
    # Prompts de Reclutador Senior (Diseño visto en el Video 1)
    prompt_sistema = """Eres un reclutador senior experto con más de 15 años de experiencia en la selección de talento humano técnico.
Tu tarea es evaluar la Hoja de Vida de un candidato utilizando únicamente el contexto extraído de su CV y compararlo críticamente con los requisitos de la vacante.

Debes completar obligatoriamente cada campo del esquema estructurado solicitado. Si algún dato no se encuentra explícito, infiérelo con criterio profesional o inicialízalo con valores genéricos en lugar de fallar."""

    prompt_analisis = """
REQUISITOS DEL PUESTO DE TRABAJO:
{descripcion_puesto}

CONTEXTO EXTRAÍDO DE LA HOJA DE VIDA DEL CANDIDATO:
{contexto_recuperado}

Realiza el análisis y devuelve la estructura de datos requerida."""

    prompt_template = ChatPromptTemplate.from_messages([
        ("system", prompt_sistema),
        ("human", prompt_analisis)
    ])
    
    prompt_formateado = prompt_template.format_messages(
        descripcion_puesto=state["descripcion_puesto"],
        contexto_recuperado=state["contexto_recuperado"]
    )
    
    # Invocar al LLM local para obtener la respuesta formateada en el modelo Pydantic
    analisis_final = llm_estructurado.invoke(prompt_formateado)
    return {"resultado_estructurado": analisis_final}

# Configuración y Orquestación del Grafo Condicional (LangGraph)
workflow = StateGraph(AgenteState)

# Agregar los componentes funcionales
workflow.add_node("recuperar_info", nodo_recuperar_informacion)
workflow.add_node("analizar_cv", nodo_analizar_perfil)

# Establecer las líneas de flujo
workflow.set_entry_point("recuperar_info")
workflow.add_edge("recuperar_info", "analizar_cv")
workflow.add_edge("analizar_cv", END)

# Compilar el agente
agente_analizador = workflow.compile()