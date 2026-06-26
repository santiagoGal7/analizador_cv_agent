# Evaluador Inteligente de Hojas de Vida

Esta aplicacion es una herramienta diseñada para ayudar a reclutadores y profesionales de talento humano a comparar hojas de vida con los requisitos de una vacante de empleo. Utiliza inteligencia artificial para analizar el contenido del curriculum y determinar que tan alineado esta el perfil del candidato con lo que busca la empresa.

El sistema permite realizar el analisis utilizando inteligencia artificial local, lo que garantiza total privacidad de los datos, o mediante servicios en la nube para una mayor precision.

## Funciones Principales

- Lectura automatica de archivos en formato PDF.
- Comparacion automatica entre la hoja de vida cargada y la descripcion del puesto de trabajo.
- Calculo de un porcentaje estimado de afinidad o compatibilidad.
- Identificacion de las principales fortalezas del candidato.
- Deteccion de brechas o areas donde el candidato podria necesitar capacitacion o no cumple plenamente con los requisitos.
- Listado visual de las habilidades y conocimientos tecnologicos del postulante.
- Opcion de elegir entre procesar la informacion de manera local en su computadora o usar los servicios en la nube de Google.

## Requisitos de Sistema

Para poder ejecutar esta aplicacion en su equipo, necesitara lo siguiente:

- Python instalado en su sistema (version 3.9 o superior).
- Si desea utilizar la inteligencia artificial local: tener instalado Ollama en su computadora con alguno de los modelos soportados (por ejemplo, qwen2.5-coder o llama3.2).
- Si desea utilizar la inteligencia artificial en la nube: una clave de acceso de Google Gemini (API Key).

## Instalacion y Configuracion

Siga estos pasos para preparar la aplicacion en su computadora:

1. **Descargar los archivos del proyecto** en una carpeta local.

2. **Instalar las dependencias necesarias** abriendo una terminal o consola de comandos en la carpeta del proyecto y ejecutando el siguiente comando:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configurar las credenciales** creando un archivo llamado `.env` en la carpeta raiz del proyecto si no existe. Dentro de este archivo, agregue su clave de Google Gemini si planea usar el modo en la nube:
   ```env
   GEMINI_API_KEY=su_clave_aqui
   ```

## Instrucciones de Uso

Una vez completada la instalacion, puede iniciar la aplicacion siguiendo estos pasos:

1. Abra una terminal en la carpeta raiz del proyecto.
2. Inicie la interfaz de usuario ejecutando el siguiente comando:
   ```bash
   streamlit run ui/streamlit_ui.py
   ```
3. El sistema abrira automaticamente una ventana en su navegador web.
4. En el panel lateral izquierdo, elija el proveedor de inteligencia artificial que prefiera (Ollama para ejecucion local o Google Gemini para ejecucion en la nube).
5. En la seccion central, suba la hoja de vida en formato PDF utilizando el cargador de archivos.
6. Pegue los requisitos o la descripcion del puesto en el cuadro de texto correspondiente.
7. Presione el boton para iniciar el analisis.
8. Revise los resultados estructurados en pantalla, que incluyen el porcentaje de ajuste, historial laboral, fortalezas y habilidades detectadas.

---

Desarrollado por: Santiago Gallo
