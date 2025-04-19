**Dawn Framework: Descripción Detallada de Características y Arquitectura**

**1. Filosofía y Visión General**

Dawn es un framework Python de código abierto diseñado para la **creación estructurada y robusta de agentes de Inteligencia Artificial (AI)**. Su filosofía central se basa en la **gestión explícita y dinámica de flujos de trabajo (Workflows)**, permitiendo a los desarrolladores construir agentes capaces de descomponer tareas compleas, ejecutar secuencias de operaciones (incluyendo llamadas a LLMs y herramientas externas), manejar dependencias, evaluar resultados intermedios, y adaptar su comportamiento dinámicamente.

A diferencia de enfoques más simples que tratan al LLM como una caja negra monolítica, Dawn promueve la **modularidad** y la **orquestación explícita**, haciendo que los agentes sean más **fiables, mantenibles, depurables y adaptables** a escenarios complejos y del mundo real. Se inspira en las capacidades modernas de los LLMs (como el uso de herramientas y la planificación) pero proporciona una capa de gestión de procesos sólida.

**2. Componentes Fundamentales del Núcleo**

*   **`Agent`**:
    *   Representa la entidad principal que ejecuta un flujo de trabajo.
    *   Encapsula la configuración (ej. ID de agente, nombre, interfaz LLM por defecto, ID del Vector Store para LTM - planificado).
    *   Contiene el estado general y gestiona la ejecución de un `Workflow`.
    *   Métodos clave: `load_workflow(workflow_definition)`, `run(initial_input)`, `run_async()`.

*   **`Workflow`**:
    *   Define la estructura lógica de un proceso agéntico.
    *   Contiene una colección de objetos `Task`.
    *   Gestiona el estado general del flujo (`pending`, `running`, `completed`, `failed`).
    *   Define el orden de ejecución inicial y las dependencias entre tareas.
    *   Mantiene un diccionario de `variables` a nivel de flujo de trabajo, accesible por las tareas.
    *   Puede representar flujos secuenciales, paralelos y condicionales.
    *   Almacena un resumen de errores (`error_summary`) al finalizar.
    *   **Generación Dinámica (Planificada):** Puede ser instanciado desde una definición JSON validada, permitiendo la creación de flujos sobre la marcha.

*   **`Task`**:
    *   La unidad fundamental de trabajo dentro de un `Workflow`.
    *   Atributos clave:
        *   `task_id`: Identificador único dentro del flujo.
        *   `name`: Nombre descriptivo.
        *   `status`: Estado actual (`pending`, `running`, `completed`, `failed`, `skipped`).
        *   `input_data`: Diccionario con los datos de entrada (puede contener literales y/o referencias a variables: `${...}`).
        *   `output_data`: Diccionario estandarizado que almacena el resultado de la ejecución (ver sección 4).
        *   `is_llm_task`: Booleano que indica si la tarea implica una llamada a un LLM (usando `LLMInterface`).
        *   `tool_name`: Nombre de la herramienta a ejecutar (desde `ToolRegistry`), si no es `is_llm_task`.
        *   `dependencies`: Lista de `task_id`s de las que depende esta tarea.
        *   `next_task_id_on_success`: ID de la siguiente tarea si esta se completa con éxito.
        *   `next_task_id_on_failure`: ID de la siguiente tarea si esta falla.
        *   `condition`: Expresión Python (evaluada en un entorno seguro) que debe ser `True` para que la tarea se ejecute (ver sección 5).
        *   `max_retries`: Número máximo de reintentos en caso de fallo.
        *   `retry_count`: Contador interno de reintentos.
        *   `parallel`: Booleano que indica si la tarea puede ejecutarse en paralelo con otras tareas independientes.
        *   `join_type`: Para tareas que actúan como puntos de sincronización ('all', 'any', N).
        *   **Parámetros de File Search (Planificado):** `use_file_search`, `file_search_vector_store_ids`, `file_search_max_results`.
        *   **Parámetros de Salida (Opcional):** `outputs`: Lista de claves esperadas en `output_data`.
    *   **Subclases Especializadas:**
        *   **`DirectHandlerTask`**: Ejecuta una función Python directamente (pasada como `handler` o referenciada por `handler_name` desde `HandlerRegistry`) sin pasar por el `ToolRegistry`. Ideal para lógica específica del flujo, parsing, validación o transformaciones internas.
        *   **`CustomTask`**: Clase base para crear tipos de tareas completamente nuevos con estrategias de ejecución personalizadas (ver sección 6.4).

**3. Motor de Ejecución (WMS - Workflow Management System / WorkflowEngine)**

*   Es el corazón que orquesta la ejecución del `Workflow`.
*   **Gestión de Estado:** Rastrea el estado de cada `Task` y del `Workflow` general.
*   **Resolución de Dependencias:** Identifica qué tareas están listas para ejecutarse basándose en el estado de sus dependencias.
*   **Ejecución de Tareas:** Selecciona la estrategia de ejecución adecuada (LLM, Tool, DirectHandler, Custom) y la invoca.
    *   **Manejo Asíncrono:** Capaz de ejecutar tareas `async` (necesario para I/O, MCPTool).
*   **Resolución de Variables:** Procesa `input_data` antes de la ejecución, sustituyendo las referencias `${...}` con los valores correspondientes de `output_data` de tareas anteriores, variables del flujo (`workflow.variables`) o información de errores (`error.task_id.*`). Admite anidamiento (dot notation), índices de array y valores por defecto (`|`).
*   **Evaluación de Condiciones:** Evalúa el campo `condition` de una tarea (si existe) en un entorno Python restringido y seguro, usando el contexto de ejecución actual (salida de la tarea actual, salidas de otras tareas, variables del flujo). Determina si la tarea debe ejecutarse.
*   **Transiciones:** Utiliza `next_task_id_on_success` y `next_task_id_on_failure` para determinar el siguiente paso tras la finalización de una tarea.
*   **Gestión de Paralelismo:** (Si está implementado) Utiliza `asyncio` (u otro backend) para ejecutar tareas marcadas como `parallel` concurrentemente, respetando las dependencias y puntos de sincronización (`join_type`).
*   **Gestión de Reintentos:** Maneja la lógica de reintentos basada en `max_retries` y `retry_count`.
*   **Propagación de Errores:** Captura errores de las tareas, los almacena de forma estandarizada y los pone a disposición de las tareas posteriores (mediante la sintaxis `${error...}`). Mantiene un `ErrorContext` y genera un `error_summary`.

**4. Estructura de Salida Estandarizada de Tareas**

*   Todas las ejecuciones de tareas (LLM, Tool, Handler) deben devolver un diccionario estandarizado para consistencia y manejo de errores predecible.
*   **Formato:**
    ```python
    {
        "success": bool,          # True si la operación fue exitosa
        "status": str,            # "success", "error", "warning"
        "result": Any | None,     # Datos del resultado principal (obligatorio en éxito)
        "response": Any | None,   # Alias para 'result', útil para LLM (obligatorio en éxito)
        "error": str | None,      # Mensaje de error (obligatorio en fallo)
        "error_code": str | None, # Código de error estandarizado (opcional)
        "error_details": dict | None, # Detalles adicionales del error (opcional)
        "metadata": dict | None   # Metadatos adicionales (opcional)
    }
    ```
*   El framework proporciona utilidades (`create_success_response`, `create_error_response`) y decoradores (`@standardize_tool_response`) para facilitar la conformidad.

**5. Extensibilidad e Integración**

*   **`LLMInterface`**:
    *   Abstracción para interactuar con diferentes proveedores de LLM (inicialmente OpenAI `client.responses.create`).
    *   Maneja la construcción de la llamada API, incluyendo prompts, parámetros del modelo, y la configuración de `tools` (para function calling o herramientas integradas como `file_search`).
    *   Responsable de parsear la respuesta del LLM, incluyendo contenido de texto y llamadas a herramientas/anotaciones.
    *   **Integración File Search (Planificada):** Acepta parámetros (`use_file_search`, `vector_store_ids`, etc.) desde la `Task` para configurar la herramienta `file_search` en la llamada API. Extrae resultados y citaciones.

*   **`ToolRegistry` y Herramientas (`Tools`)**:
    *   Registro centralizado para capacidades reutilizables.
    *   Las herramientas son funciones Python o métodos de clase registrados con un nombre único.
    *   Descubrimiento automático de herramientas (plugin system).
    *   Ejecución gestionada por el WMS a través del `ToolRegistry`.
    *   Utilidades de acceso estandarizadas (`core.tools.registry_access`: `register_tool`, `execute_tool`, `tool_exists`).
    *   **Herramientas Base Incluidas:** `calculate`, `write_markdown`, `get_available_capabilities`, `log_alert`, `log_info`.
    *   **Herramientas OpenAI VS (Planificadas):** `vector_store_create`, `upload_file_to_vector_store`, `save_text_to_vector_store`, `list_vector_stores`, `delete_vector_store`.
    *   **Herramienta MCP (Planificada):** `MCPTool` actúa como wrapper dinámico para herramientas expuestas por servidores MCP externos.

*   **`HandlerRegistry` y `DirectHandlerTask`**:
    *   Permite ejecutar funciones Python específicas del flujo de trabajo sin registro global.
    *   Los handlers se registran en `HandlerRegistry` (usando decorador `@get_handler_registry().register()` o método directo) y se referencian por `handler_name` en `DirectHandlerTask`.
    *   Alternativamente, se puede pasar la función directamente al parámetro `handler` de `DirectHandlerTask`.
    *   El motor soporta firmas de handler de uno (`input_data`) o dos (`task`, `input_data`) parámetros.
    *   Ideal para parsing, validación, transformación de datos, lógica condicional compleja.

*   **Context-Awareness (RAG/LTM - Planificado)**:
    *   Basado en **OpenAI Vector Stores**.
    *   Herramientas para gestionar VS (crear, subir archivos, guardar texto).
    *   Integración de la herramienta **`file_search`** de OpenAI en tareas LLM para RAG.
    *   Concepto de **Long-Term Memory (LTM)** usando un VS dedicado por agente para almacenar y recuperar información relevante de interacciones pasadas (guardado explícito, recuperación implícita vía `file_search` en tareas LLM).

*   **Interoperabilidad (MCP - Planificado)**:
    *   **`MCPClientManager`**: Gestiona conexiones (stdio inicialmente) a servidores MCP externos configurados.
    *   **`MCPTool`**: Wrapper dinámico registrado en `ToolRegistry` que representa una herramienta externa. Genera modelos Pydantic desde el schema del MCP, llama a `call_tool` del servidor MCP de forma asíncrona.
    *   Requiere que el WMS/Engine soporte `await` para llamadas a herramientas asíncronas.

*   **Generación Dinámica de Flujos (JSON - Planificado)**:
    *   Definición de un **esquema JSON formal** para `Workflow` y `Task`.
    *   **Validación:** Utilidad para validar definiciones JSON contra el esquema (`jsonschema`).
    *   **Interpretación:** Lógica segura (`load_workflow_from_dict`) para construir objetos `Workflow`/`Task` desde un diccionario JSON validado.
    *   **Herramienta `execute_workflow_from_json`**: Tool que toma una definición JSON, la valida, la interpreta y ejecuta el flujo resultante.
    *   **Agente Generador (PoC):** Un agente Dawn que usa RAG sobre la documentación del propio framework (incluyendo el schema JSON) para generar estas definiciones JSON a partir de lenguaje natural.

**6. Experiencia del Desarrollador (DevEx)**

*   **Configuración Unificada (`core.config`)**:
    *   Sistema centralizado que carga desde archivos (JSON/YAML), variables de entorno (`DAWN_...`), y valores por defecto.
    *   Soporte para entornos (`development`, `test`, `production`).
    *   Acceso fácil mediante `get(key, default)` y `set(key, value)`.
    *   Manejo de valores sensibles.
*   **Observabilidad y Depuración:**
    *   **Logging:** Logging estructurado integrado (JSON opcional). Logs en puntos clave del WMS y ejecución de tareas.
    *   **Debug Mode:** Modo opcional (`DAWN_DEBUG_MODE=true`) que habilita logging más verboso, métricas de rendimiento básicas, y potencialmente un panel web (`/debug`).
    *   **Visualización:** Utilidad `visualize_workflow` (requiere `graphviz`) para generar diagramas de flujo.
*   **Testing Utilities (`core.utils.testing`)**:
    *   **`WorkflowTestHarness` / `TaskTestHarness`**: Clases para facilitar tests unitarios/integración de flujos y tareas.
    *   **Mocking:** Registro de herramientas mockeadas.
    *   **Tool Recording/Replaying:** Capacidad para grabar ejecuciones reales de herramientas y usarlas como mocks deterministas en tests.
*   **Calidad de Código:**
    *   Uso de `black`, `isort`, `flake8` con configuraciones pragmáticas y personalizables por archivo.
    *   Pre-commit hooks para asegurar estándares.
    *   Makefile/scripts para tareas comunes (lint, format, test).
*   **Empaquetado (Planificado):** Estructura preparada para ser empaquetada como una biblioteca Python distribuible (`setup.py`, `pyproject.toml`).

**7. Fortalezas Clave y Casos de Uso**

*   **Fortalezas:** Modularidad, gestión explícita de procesos complejos, adaptabilidad (condicionales, feedback), extensibilidad (tools, handlers, MCP), observabilidad, testabilidad.
*   **Casos de Uso Ideales:** Automatización de procesos de negocio multi-paso, asistentes de investigación complejos, sistemas de análisis de datos con múltiples fuentes, agentes de soporte técnico con acceso a base de conocimientos, herramientas de cumplimiento y auditoría, prototipado rápido de comportamientos agénticos estructurados.


