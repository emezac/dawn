Okay, basándome en los problemas identificados al crear `run_tourist_planner.py` (interpolación de variables, manejo de herramientas/handlers, markdown), aquí tienes una TODO list detallada y profunda para refactorizar y mejorar el *core* del framework Dawn:

**Objetivo General:** Hacer el framework más robusto, flexible y predecible, especialmente en cuanto al manejo de datos entre tareas, la ejecución de lógica personalizada y la gestión de errores, para soportar mejor workflows dinámicos y complejos como el del planificador turístico.

---

## 📋 TODO List Detallado: Mejoras Core del Framework Dawn

### Fase 1: Refactorización Fundamental del Manejo de Datos y Tareas

**1. Estandarización Rigurosa de la Salida de Tareas:**
    *   [ ] **Definir Esquema de Salida Estándar:** Establecer y documentar un formato de diccionario Python *obligatorio* para la salida de CUALQUIER tarea (sea `Task` estándar, `DirectHandlerTask`, o LLM).
        *   **Campos Obligatorios:** `success` (bool), `status` (str: "completed", "failed", "skipped", "warning").
        *   **Campos Condicionales (Éxito):** `result` (Any) - Contiene el dato principal. `response` (Any) - Incluir *además* de `result` por compatibilidad, especialmente para tareas LLM, ambos apuntando al mismo dato si es posible.
        *   **Campos Condicionales (Fallo):** `error` (str) - Mensaje legible. `error_code` (str, opcional) - Código estandarizado. `error_details` (dict, opcional) - Contexto adicional.
        *   **Campos Opcionales (Éxito/Warning):** `warning` (str), `warning_code` (str), `metadata` (dict).
    *   [ ] **Refactorizar `WorkflowEngine.execute_task` (y `AsyncWorkflowEngine`):** Modificar la lógica de ejecución para *forzar* que la salida de cualquier herramienta, handler o llamada LLM se ajuste a este formato estándar antes de almacenarla en `task.output_data`. Capturar excepciones durante la ejecución de la herramienta/handler y formatearlas correctamente en la salida estándar de error.
    *   [ ] **Refactorizar `Task.set_output`:** Asegurar que valide (o intente convertir) la entrada al formato estándar.
    *   [ ] **Crear `core.errors` robusto:** Definir excepciones personalizadas (`DawnError`, `ValidationError`, `ExecutionError`, etc.) y un `ErrorCode` enum/clase con códigos estandarizados. Añadir utilidades `create_success_response`, `create_error_response`, `create_warning_response`.

**2. Mejora Profunda del Sistema de Resolución de Variables:**
    *   [ ] **Refactorizar `core.utils.variable_resolver.resolve_variables`:**
        *   **Soporte Nativo Dot-Notation:** Implementar parseo robusto para acceder a campos anidados en diccionarios y atributos de objetos (ej: `${task_1.output_data.result.user.name}`).
        *   **Soporte Indexación de Listas:** Permitir acceso a elementos de listas (ej: `${task_1.output_data.result.items[0].id}`).
        *   **Manejo de Tipos:** No asumir que los valores resueltos son siempre strings. Devolver el tipo original (int, bool, list, dict, etc.). Si se necesita un string (ej. para prompts LLM), la conversión debe ser explícita donde se usa, no en el resolver.
        *   **Sintaxis de Default:** Implementar y documentar una sintaxis clara para valores por defecto si la variable no se resuelve (ej: `${task_1.output_data.result.priority | 'medium'}`).
        *   **Reporte de Errores Detallado:** Si una variable no se resuelve (y no hay default), loguear un WARNING claro indicando la variable exacta y la tarea. *Opcional:* Añadir un modo "estricto" que falle la tarea si una variable no se resuelve.
        *   **Contexto Completo:** Asegurar que el contexto (`data_context` pasado a `resolve_variables`) contenga *todos* los `output_data` de las tareas completadas hasta ese punto, además de las variables globales del workflow.
    *   [ ] **Refactorizar `WorkflowEngine.process_task_input`:** Asegurar que use la versión mejorada de `resolve_variables` y maneje correctamente los tipos de datos resueltos.
    *   [ ] **Utilidad `Task.get_output_value(path)`:** Crear o mejorar un método helper en la clase `Task` que use el resolver mejorado para obtener un valor específico de su `output_data` usando dot-notation y manejo de defaults.

**3. Promoción y Robustecimiento de `DirectHandlerTask`:**
    *   [ ] **Convertir en Ciudadano de Primera Clase:** Documentar `DirectHandlerTask` como la forma *recomendada* para lógica personalizada dentro de un workflow, diferenciándolo claramente de las herramientas globales reutilizables del `ToolRegistry`.
    *   [ ] **Asegurar Compatibilidad Total con Motores:** Verificar que `DirectHandlerTask` se ejecute correctamente tanto en `WorkflowEngine` (síncrono) como en `AsyncWorkflowEngine` (asíncrono, si existe o se planea).
    *   [ ] **Manejo de Firmas de Handler:** (Ya implementado parcialmente) Finalizar y documentar el soporte para handlers con firma `handler(input_data)` y `handler(task, input_data)`.
    *   [ ] **Acceso al Contexto del Workflow:** Proveer una forma documentada y segura para que un `DirectHandlerTask` acceda a variables globales del workflow o a la salida de otras tareas si es *absolutamente necesario* (idealmente, pasar datos vía `input_data`).
    *   [ ] **Validación de Parámetros:** Implementar o mejorar la validación de los parámetros pasados al constructor de `DirectHandlerTask` (ej. `handler` debe ser callable).

### Fase 2: Mejora de Herramientas y Handlers Específicos

**4. Refactorizar Herramientas Propensas a Problemas de Variables (ej. `write_markdown`):**
    *   [ ] **Modificar `write_markdown_handler`:**
        *   Intentar resolver las variables en el campo `content` *dentro* del handler.
        *   Si la resolución falla para *alguna* variable, en lugar de fallar toda la tarea:
            *   Loguear un WARNING detallado indicando qué variables no se pudieron resolver.
            *   Reemplazar las variables no resueltas con un placeholder claro (ej. `[VARIABLE_NO_RESUELTA: ${task_id...}]`) en el contenido final.
            *   Permitir que la tarea se complete *exitosamente* (o con `status: "warning"`) pero con el contenido parcialmente resuelto.
        *   Asegurar que maneje correctamente el tipo de dato del `content` (no asumir string si viene de una variable resuelta como dict/list). Convertir a string de forma segura si es necesario.
    *   [ ] **Revisar Otras Herramientas:** Aplicar lógica similar a otras herramientas que tomen strings complejos con variables (ej. prompts para LLMs si se construyen fuera del LLMInterface, herramientas de API calls).

**5. Implementar Tarea/Handler Explícito de Parseo JSON:**
    *   [ ] **Crear `parse_json_handler` (Direct Handler):**
        *   Tomar un string (`input_string`) como entrada.
        *   Intentar parsearlo como JSON (`json.loads`).
        *   **Limpieza de Markdown:** Intentar eliminar ` ```json ` y ` ``` ` si el parseo inicial falla.
        *   **Manejo de Errores Robusto:** Si el parseo falla, devolver `success: False` con `error` descriptivo y `error_code` `JSON_PARSE_ERROR`. *Opcional:* Devolver `success: True` pero con un `result` indicando el fallo y el string original para workflows que puedan manejar texto plano como fallback.
    *   [ ] **Documentar Patrón:** Recomendar explícitamente usar una `DirectHandlerTask` con `parse_json_handler` *después* de cualquier tarea LLM que se espere devuelva JSON, antes de intentar acceder a campos anidados con resolución de variables.

### Fase 3: Mejoras del Motor de Workflow y Experiencia de Desarrollo

**6. Mejorar Manejo de Errores y Propagación en el Engine:**
    *   [ ] **Contexto de Error Persistente:** Introducir un objeto `ErrorContext` en el `WorkflowEngine` que rastree los errores de cada tarea (`task_id`, `error_message`, `error_code`, `error_details`, `timestamp`).
    *   [ ] **Acceso a Errores Previos:** Modificar `resolve_variables` para permitir referenciar errores de tareas anteriores usando una sintaxis especial (ej: `${error.task_id.error_message}`, `${error.task_id.error_details.field}`).
    *   [ ] **Estado de Workflow Detallado:** El estado final del workflow (`result` de `engine.run()`) debe incluir un resumen de errores si ocurrieron (`error_summary` con `tasks_with_errors`).
    *   [ ] **Manejo de Fallos en `process_task_input`:** Si la resolución de variables falla *antes* de ejecutar la tarea (y no hay defaults), marcar la tarea como fallida con un error específico (`VARIABLE_RESOLUTION_ERROR`).

**7. Reforzar Pruebas Unitarias y de Integración:**
    *   [ ] **Pruebas para `resolve_variables`:** Añadir casos de prueba exhaustivos cubriendo dot-notation, indexación de listas, tipos de datos mixtos, valores por defecto y escenarios de error.
    *   [ ] **Pruebas para `DirectHandlerTask`:** Verificar ejecución, manejo de firmas, paso de contexto y salida estandarizada.
    *   [ ] **Pruebas para `parse_json_handler`:** Probar con JSON válido, inválido, envuelto en markdown, etc.
    *   [ ] **Pruebas para `write_markdown`:** Testear el manejo de variables resueltas y no resueltas.
    *   [ ] **Pruebas de Workflow:** Crear workflows de prueba que explícitamente usen estas características (anidación profunda, parseo, defaults, manejo de errores) y verificar el comportamiento.

**8. Actualizar Documentación y Ejemplos:**
    *   [ ] **Documentar Resolución de Variables:** Explicar claramente la sintaxis (dot-notation, listas, defaults), los tipos de datos y el manejo de errores.
    *   [ ] **Documentar Salida Estándar:** Detallar el formato esperado y cómo acceder a `result`, `response`, `error`, etc.
    *   [ ] **Documentar `DirectHandlerTask`:** Explicar su propósito, uso, firmas de handler y diferencias con `ToolRegistry`.
    *   [ ] **Documentar Patrón de Parseo JSON:** Mostrar cómo y por qué usar la tarea de parseo después de llamadas LLM.
    *   [ ] **Refactorizar Ejemplos Existentes:** Actualizar `smart_compliance_workflow.py`, `context_aware_legal_review_workflow.py`, y otros ejemplos relevantes para usar los nuevos patrones y sintaxis. Eliminar soluciones temporales (como wrappers `create_task`).
    *   [ ] **Crear Nuevos Ejemplos:** Añadir un ejemplo específico que demuestre la resolución de variables complejas y el manejo robusto de errores.

---

Este TODO list es extenso pero aborda las causas raíz de los problemas observados. Completar estas tareas debería resultar en un framework Dawn significativamente más fiable, predecible y fácil de usar para construir workflows complejos.
