import pypdf
from io import BytesIO
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_core.documents import Document

import re

def normalizar_texto_spaced(text: str) -> str:
    """Encuentra palabras espaciadas (ej. P E R F I L o D e s a r r o l l a d o r) y las colapsa."""
    def repl(match):
        return match.group(0).replace(" ", "")
    
    # Busca 3 o más letras consecutivas separadas por un espacio
    pattern = r'(?:[a-zA-ZáéíóúÁÉÍÓÚñÑ]\s){3,}[a-zA-ZáéíóúÁÉÍÓÚñÑ]'
    cleaned = re.sub(pattern, repl, text)
    
    # Normaliza espacios múltiples resultantes
    cleaned = re.sub(r' +', ' ', cleaned)
    return cleaned

def extraer_texto_pdf(file_bytes) -> str:
    """Extrae el texto completo de un archivo PDF binario sin escribir en disco (Video 2)."""
    pdf_reader = pypdf.PdfReader(BytesIO(file_bytes))
    texto = ""
    for pagina in pdf_reader.pages:
        texto += pagina.extract_text() or ""
    return normalizar_texto_spaced(texto)

def crear_chunks_documento(texto: str) -> list:
    """Divide el texto extraído en fragmentos semánticos pequeños (Video 4)."""
    text_splitter = RecursiveCharacterTextSplitter(chunk_size=1500, chunk_overlap=150)
    return [Document(page_content=chunk) for chunk in text_splitter.split_text(texto)]