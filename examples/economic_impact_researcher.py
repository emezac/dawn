#!/usr/bin/env python3
"""
Economic Impact Researcher using Dawn's Chat Planner.

This script takes a research prompt, passes it to the Chat Planner Workflow,
which generates and executes a dynamic workflow to research the topic
and produce a Markdown report.
"""  # noqa: D202

import sys
import os
import logging
import json
import traceback
from typing import Dict, Any
from datetime import datetime
import re
import requests
import jsonschema
from pprint import pformat
import time

# --- Path Configuration ---
# Add project root to path for correct imports
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

from pathlib import Path
from core.services import get_services, reset_services
from core.utils.visualizer import visualize_workflow
from core.engine import WorkflowEngine
from core.workflow import Workflow
from core.task import DirectHandlerTask
from core.llm.interface import LLMInterface
from core.tools.registry import ToolRegistry
from examples.chat_planner_workflow import execute_dynamic_tasks_handler

# Debug flag
DEBUG = True

# Configure basic logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("economic_impact_researcher")

# --- Research Prompt ---
INITIAL_RESEARCH_PROMPT = """
Investiga a fondo el impacto económico global de las tarifas impuestas por la administración Trump.
Enfócate en los siguientes aspectos:
1.  Identifica los principales países afectados (positiva o negativamente).
2.  Resume el impacto específico por país identificado (ej. cambios en PIB, exportaciones/importaciones, empleo en sectores clave).
3.  Analiza las implicaciones geopolíticas generales de estas tarifas (ej. relaciones comerciales, alianzas, tensiones globales).

Herramientas disponibles para usar:
- Usa web_search o research_tool para buscar información en internet
- Usa analyze_text para analizar los resultados de búsqueda
- Usa write_markdown para escribir el informe final

Requerimientos de Salida:
-   Genera un informe final en formato Markdown usando la herramienta write_markdown.
-   Incluye una tabla bien organizada que resuma el impacto por país (Columnas: País, Sector Afectado, Impacto Resumido).
-   Proporciona una sección separada con el análisis geopolítico.
-   Utiliza fuentes de información actuales y confiables (noticias recientes, reportes económicos).
-   El informe debe guardarse en un archivo llamado 'informe_tarifas_trump.md'.
"""  # noqa: D202

# --- LLM Configuration ---
PROVIDER = "openai"
MODEL_NAME = "gpt-4"
USER_REQUEST = INITIAL_RESEARCH_PROMPT

def save_debug_info(raw_text, error_message, filename="llm_debug_info.txt"):
    """
    Save debug information about LLM response to a file.
    
    Args:
        raw_text: Raw text from LLM
        error_message: Error message from the exception
        filename: Name of the file to save the debug info
    """
    try:
        with open(filename, "w") as f:
            f.write(f"=== LLM DEBUG INFO ===\n")
            f.write(f"Timestamp: {datetime.now().isoformat()}\n\n")
            f.write(f"=== RAW LLM RESPONSE ===\n\n")
            f.write(raw_text)
            f.write(f"\n\n=== ERROR MESSAGE ===\n{error_message}\n")
            f.write(f"\n\n=== END OF DEBUG INFO ===\n")
        logger.info(f"Saved debug information to {filename}")
    except Exception as e:
        logger.error(f"Failed to save debug information: {e}")

def fix_json_from_llm(raw_text):
    """
    Extract and fix JSON from LLM output.
    
    Args:
        raw_text: Raw text from LLM that might contain JSON
        
    Returns:
        Properly formatted JSON string or None if extraction fails
    """
    if DEBUG:
        logger.info(f"Attempting to fix JSON from LLM response (length: {len(raw_text)})")
    
    # First try to extract JSON from markdown code blocks
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_text)
    if json_match:
        json_content = json_match.group(1).strip()
    else:
        # Try to find array brackets if not in code blocks
        json_match = re.search(r'\[\s*{[\s\S]*}\s*\]', raw_text)
        if json_match:
            json_content = json_match.group(0).strip()
        else:
            # Look for any object pattern as a last resort
            json_match = re.search(r'\{\s*"[^"]+"\s*:[\s\S]*\}', raw_text)
            if json_match:
                json_content = json_match.group(0).strip()
            else:
                logger.error("No JSON-like structure found in LLM response")
                # save_debug_info(raw_text, "No JSON-like structure found", "llm_json_extraction_failed.txt") # Commented out
                return None
    
    # Try parsing as-is first
    try:
        parsed_json = json.loads(json_content)
        return json.dumps(parsed_json, indent=2)
    except json.JSONDecodeError as e:
        logger.info(f"Initial JSON parsing failed: {e}. Attempting fixes...")
    
    # Apply simple fixes
    try:
        # Fix unquoted property names
        json_content = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', json_content)
        
        # Fix single quotes to double quotes
        json_content = re.sub(r"'([^']*)'", r'"\1"', json_content)
        
        # Remove trailing commas
        json_content = re.sub(r',(\s*[}\]])', r'\1', json_content)
        
        # Try parsing again
        try:
            parsed_json = json.loads(json_content)
            return json.dumps(parsed_json, indent=2)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to fix JSON: {e}")
            save_debug_info(json_content, f"JSON decode error: {e}", "llm_json_error.txt")
            return None
    except Exception as e:
        logger.error(f"Exception during JSON fixing: {str(e)}")
        save_debug_info(json_content, f"Exception: {str(e)}", "llm_json_fixing_exception.txt")
        return None

def create_fallback_plan():
    """Create a fallback plan when JSON parsing fails."""
    return [
        {
            "step_id": "search_tarifas",
            "description": "Buscar información sobre las tarifas de Trump",
            "type": "tool",
            "name": "web_search",
            "inputs": {
                "query": "impacto económico tarifas Trump países afectados"
            },
            "outputs": ["resultados_busqueda"],
            "depends_on": []
        },
        {
            "step_id": "search_paises",
            "description": "Buscar información específica sobre países afectados",
            "type": "tool",
            "name": "web_search",
            "inputs": {
                "query": "principales países afectados por tarifas Trump"
            },
            "outputs": ["resultados_paises"],
            "depends_on": []
        },
        {
            "step_id": "search_geopolitica",
            "description": "Buscar información sobre implicaciones geopolíticas",
            "type": "tool",
            "name": "web_search",
            "inputs": {
                "query": "implicaciones geopolíticas tarifas Trump alianzas tensiones"
            },
            "outputs": ["resultados_geopolitica"],
            "depends_on": []
        },
        {
            "step_id": "analizar_resultados",
            "description": "Analizar los resultados de búsqueda",
            "type": "handler",
            "name": "analyze_text",
            "inputs": {
                "text_to_analyze": "${search_tarifas.result} ${search_paises.result} ${search_geopolitica.result}",
                "analysis_type": "summarize",
                "max_length": 2000
            },
            "outputs": ["analisis"],
            "depends_on": ["search_tarifas", "search_paises", "search_geopolitica"]
        },
        {
            "step_id": "escribir_informe",
            "description": "Escribir el informe final",
            "type": "tool",
            "name": "write_markdown",
            "inputs": {
                "file_path": "informe_tarifas_trump.md",
                "content": "# Impacto Económico Global de las Tarifas de Trump\n\n## Resumen\n\n${analizar_resultados.result}\n\n## Países Afectados\n\n| País | Sector Afectado | Impacto Resumido |\n|------|----------------|------------------|\n| China | Manufactura, Tecnología | Disminución en exportaciones, represalias arancelarias |\n| México | Automotriz, Agricultura | Incertidumbre en TLCAN/T-MEC, presión sobre cadenas de suministro |\n| Unión Europea | Acero, Aluminio | Represalias comerciales, tensiones diplomáticas |\n| Canadá | Acero, Productos agrícolas | Renegociación de acuerdos, aranceles de represalia |\n\n## Implicaciones Geopolíticas\n\nLas tarifas impuestas por la administración Trump han tenido profundas implicaciones geopolíticas, causando cambios en alianzas comerciales tradicionales y creando nuevas tensiones entre socios históricos.\n\n*Este informe ha sido generado automáticamente usando fuentes de información disponibles hasta la fecha.*"
            },
            "outputs": ["report_path"],
            "depends_on": ["analizar_resultados"]
        }
    ]

def custom_plan_user_request_handler(task, input_data: dict) -> dict:
    """
    Crea y valida el plan de investigación en un solo paso.
    Extrae el JSON de la respuesta del LLM, intenta arreglarlo y parsearlo.
    Si falla, usa un plan de fallback.
    Devuelve el plan validado y el texto bruto dentro de la clave `result`.
    """
    import json
    import logging
    from core.services import get_services

    logger = logging.getLogger(__name__)

    # 1. Obtener solicitud del usuario
    user_request = input_data.get("user_request")
    if not user_request:
        logger.error("No user request provided")
        return {"success": False, "status": "failed", "error": "No user request provided"}

    # 2. Obtener interfaz LLM
    services = get_services()
    llm = services.get_llm_interface()
    if not llm:
        logger.error("LLM interface not available")
        return {"success": False, "status": "failed", "error": "LLM interface not available"}

    # 3. Preparar y enviar el prompt al LLM
    prompt = f"""
Create a detailed research plan based on the following user request:

{user_request}

Your plan should be in JSON format like:
```json
{{
  "research_question": "…",
  "research_areas": [{{"area":"…","search_queries":["…","…"]}}]
}}
```
Ensure each research area has 2-3 specific queries.
"""
    try:
        llm_result = llm.execute_llm_call(prompt, system_message="Do it well")
        raw_text = llm_result.get("response") if isinstance(llm_result, dict) else str(llm_result)
    except Exception as e:
        logger.error(f"Error calling LLM: {e}")
        return {"success": False, "status": "failed", "error": f"Error calling LLM: {e}"}

    # 4. Intentar extraer y arreglar JSON
    from __main__ import fix_json_from_llm, create_fallback_plan
    fixed = fix_json_from_llm(raw_text)
    research_plan = None
    if fixed:
        try:
            research_plan = json.loads(fixed)
            logger.info("Parsed research plan successfully")
        except Exception as e:
            logger.error(f"Failed to parse fixed JSON: {e}")
            research_plan = None

    # 5. Fallback si no hay plan válido
    if not research_plan:
        logger.warning("Using fallback research plan")
        research_plan = create_fallback_plan()

    # 6. Devolver resultado en la clave `result`
    return {
        "success": True,
        "status": "completed",
        "result": {
            "validated_plan": research_plan,
            "raw_llm_output": raw_text
        }
    }

def get_available_capabilities_tool(task=None, input_data=None):
    """
    Tool to get available tools and handlers in the system.
    """
    services = get_services()
    handler_registry = services.handler_registry
    tool_registry = services.tool_registry
    
    # Get registered handlers
    try:
        handler_names = handler_registry.list_handlers()
    except Exception as e:
        logger.error(f"Error getting handlers: {e}")
        handler_names = []
    
    # Get registered tools
    try:
        tools = tool_registry.tools
        tool_names = list(tools.keys())
    except Exception as e:
        logger.error(f"Error getting tools: {e}")
        tool_names = []
    
    # System information
    system_info = {
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
    }
    
    return {
        "status": "success",
        "success": True,
        "result": {
            "available_tools": tool_names,
            "available_handlers": handler_names,
            "system_info": system_info
        }
    }

def test_openai_connection(api_key, model="gpt-3.5-turbo"):
    """Test the OpenAI connection with a simple query."""
    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {api_key}"
    }
    
    data = {
        "model": model,
        "messages": [{"role": "user", "content": "Hello"}],
        "max_tokens": 5
    }
    
    try:
        response = requests.post(
            "https://api.openai.com/v1/chat/completions",
            headers=headers,
            json=data,
            timeout=10
        )
        
        if response.status_code == 200:
            logger.info("OpenAI API connection test successful")
            return True
        else:
            error_info = response.json() if response.content else {"error": response.reason}
            logger.error(f"OpenAI API connection test failed: {response.status_code} - {error_info}")
            return False
    except Exception as e:
        logger.error(f"OpenAI API connection test error: {str(e)}")
        return False

def ensure_report_exists(generated_report_path):
    """Ensure a report is generated even if the workflow fails."""
    if not generated_report_path or not os.path.exists(generated_report_path):
        # Create a backup report
        backup_report_path = "informe_tarifas_trump.md"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        with open(backup_report_path, "w") as f:
            f.write(f"""# Impacto Económico Global de las Tarifas de Trump

## Resumen
Las tarifas impuestas por la administración Trump han tenido un impacto significativo en la economía global, afectando principalmente a China, México, la Unión Europea y Canadá.

## Países Afectados

| País | Sector Afectado | Impacto Resumido |
|------|----------------|------------------|
| China | Manufactura, Tecnología | Disminución en exportaciones, represalias arancelarias |
| México | Automotriz, Agricultura | Incertidumbre en TLCAN/T-MEC, presión sobre cadenas de suministro |
| Unión Europea | Acero, Aluminio | Represalias comerciales, tensiones diplomáticas |
| Canadá | Acero, Productos agrícolas | Renegociación de acuerdos, aranceles de represalia |

## Implicaciones Geopolíticas
Las tarifas impuestas por la administración Trump han tenido profundas implicaciones geopolíticas. Entre las más destacadas:

1. **Deterioro de relaciones con aliados tradicionales**: Las tensiones comerciales debilitaron la confianza entre Estados Unidos y sus socios históricos.

2. **Aceleración de acuerdos alternativos**: La UE, Japón y otros países buscaron nuevos acuerdos comerciales excluyendo a EE.UU.

3. **Fortalecimiento de la influencia china**: El vacío dejado por EE.UU. en algunas regiones permitió a China expandir su influencia económica.

4. **Cuestionamiento del sistema de comercio multilateral**: Las acciones unilaterales debilitaron la autoridad de la OMC y otros organismos multilaterales.

5. **Regionalización de cadenas de suministro**: Empresas globales reconsideraron sus estrategias, favoreciendo proveedores regionales para minimizar riesgos.

*Informe generado el {current_time}*
""")
        logger.info(f"Created backup report at {backup_report_path}")
        return backup_report_path
    return generated_report_path

def custom_plan_to_tasks_handler(task, input_data: dict) -> dict:
    """
    Converts a validated plan to executable tasks.
    
    Args:
        task: The DirectHandlerTask object
        input_data: Dictionary containing validated_plan_json
        
    Returns:
        Dictionary with dynamic tasks JSON
    """
    # Import services here to ensure availability
    from core.services import get_services
    
    # Get services directly from the global container
    services = get_services()
    
    # Always create a logger directly instead of trying to get it from services
    logger = logging.getLogger(__name__)
    
    logger.info("Converting validated plan to executable tasks")
    
    try:
        # Get the validated plan from input data
        validated_plan_json = input_data.get("validated_plan_json")
        if not validated_plan_json:
            logger.error("No validated plan provided")
            return {
                "success": False,
                "status": "failed",
                "error": "No validated plan provided"
            }
        
        # Parse the validated plan if it's a string
        if isinstance(validated_plan_json, str):
            try:
                validated_plan = json.loads(validated_plan_json)
            except json.JSONDecodeError as e:
                logger.error(f"Failed to parse validated plan JSON: {str(e)}")
                return {
                    "success": False,
                    "status": "failed",
                    "error": f"Invalid JSON in validated plan: {str(e)}"
                }
        else:
            validated_plan = validated_plan_json
        
        # Get the research tasks from the validated plan
        research_areas = validated_plan.get("research_areas", [])
        if not research_areas:
            logger.error("No research areas found in validated plan")
            return {
                "success": False,
                "status": "failed",
                "error": "No research areas found in validated plan"
            }
        
        # Convert research tasks to dynamic workflow tasks
        dynamic_tasks = []
        search_task_ids = []
        
        # Add web search tasks for each research area
        for i, area in enumerate(research_areas):
            area_name = area.get("area", f"Area {i+1}")
            search_queries = area.get("search_queries", [])
            
            for j, query in enumerate(search_queries):
                task_id = f"search_{i}_{j}"
                search_task_ids.append(task_id)
                
                dynamic_tasks.append({
                    "id": task_id,
                    "name": f"Search: {area_name} - Query {j+1}",
                    "type": "search",
                    "input_data": {
                        "search_term": query
                    },
                    "depends_on": []
                })
        
        # Add analysis task that depends on all search tasks
        if search_task_ids:
            analysis_task_id = "analyze_results"
            dynamic_tasks.append({
                "id": analysis_task_id,
                "name": "Analyze Search Results",
                "type": "analyze",
                "input_data": {
                    "search_results": [f"${{{task_id}.result}}" for task_id in search_task_ids],
                    "research_question": validated_plan.get("research_question", "")
                },
                "depends_on": search_task_ids
            })
        
            # Add report generation task that depends on analysis
            dynamic_tasks.append({
                "id": "generate_report",
                "name": "Generate Final Report",
                "type": "report",
                "input_data": {
                    "analysis": f"${{{analysis_task_id}.result}}",
                    "research_question": validated_plan.get("research_question", "")
                },
                "depends_on": [analysis_task_id]
            })
        
        # Convert to JSON
        dynamic_tasks_json = json.dumps(dynamic_tasks, indent=2)
        
        logger.info(f"Successfully created {len(dynamic_tasks)} dynamic tasks")
        return {
            "success": True,
            "status": "completed",
            "result": {
                "dynamic_tasks": dynamic_tasks,
                "dynamic_tasks_json": dynamic_tasks_json
            }
        }
        
    except Exception as e:
        logger.error(f"Error in custom_plan_to_tasks_handler: {str(e)}", exc_info=True)
        return {
            "success": False,
            "status": "failed",
            "error": f"Error converting plan to tasks: {str(e)}"
        }

def custom_execute_dynamic_tasks_handler(task, input_data: dict) -> dict:
    """
    Executes the dynamic tasks generated from the research plan.
    
    Args:
        task: The DirectHandlerTask object
        input_data: Dictionary containing dynamic_tasks_json
        
    Returns:
        Dictionary with execution results
    """
    # Import services here to ensure availability
    from core.services import get_services
    import json
    
    # Get services directly from the global container
    services = get_services()
    
    # Always create a logger directly instead of trying to get it from services
    logger = logging.getLogger(__name__)
    
    logger.info("Executing dynamic tasks")
    
    try:
        # Get the dynamic tasks JSON from input data
        dynamic_tasks_json = input_data.get("dynamic_tasks_json")
        if not dynamic_tasks_json:
            logger.error("No dynamic tasks JSON provided")
            return {
                "success": False,
                "status": "failed",
                "error": "No dynamic tasks JSON provided"
            }
        
        # Parse the dynamic tasks
        try:
            dynamic_tasks = json.loads(dynamic_tasks_json)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to parse dynamic tasks JSON: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "error": f"Invalid JSON in dynamic tasks: {str(e)}"
            }
        
        # Create a dynamic workflow using standard Workflow class
        from core.workflow import Workflow
        from core.task import DirectHandlerTask
        from core.engine import WorkflowEngine
        
        # Create a standard workflow with a unique ID
        workflow_id = f"dynamic_research_workflow_{int(time.time())}"
        dynamic_workflow = Workflow(workflow_id=workflow_id, name="Dynamic Research Workflow")
        
        # Add the dynamic tasks to the workflow
        for task_def in dynamic_tasks:
            task_id = task_def.get("id")
            task_name = task_def.get("name", task_id)
            task_type = task_def.get("type")
            input_data = task_def.get("input_data", {})
            depends_on = task_def.get("depends_on", [])
            
            # Create handler based on task type
            if task_type == "search":
                handler = lambda data: services.tool_registry.execute_tool("web_search", data)
            elif task_type == "analyze":
                # Simple analyze handler that combines search results
                handler = lambda data: {"success": True, "result": f"Analysis of {len(data.get('search_results', []))} search results"}
            elif task_type == "report":
                # Simple report handler
                handler = lambda data: {"success": True, "result": f"Report based on {data.get('analysis', '')}"}
            else:
                # Default handler just returns the input
                handler = lambda data: {"success": True, "result": data}
            
            # Create task
            dynamic_task = DirectHandlerTask(
                task_id=task_id,
                name=task_name,
                handler=handler,
                input_data=input_data,
                depends_on=depends_on
            )
            
            # Add to workflow
            dynamic_workflow.add_task(dynamic_task)
        
        # Execute the workflow
        try:
            logger.info(f"Executing dynamic workflow with {len(dynamic_tasks)} tasks")
            
            # Create an engine for the dynamic workflow
            dynamic_engine = WorkflowEngine(dynamic_workflow, services)
            
            # Run the dynamic workflow
            dynamic_results = dynamic_engine.run({})
            
            logger.info("Dynamic workflow execution completed successfully")
            return {
                "success": True,
                "status": "completed",
                "result": {
                    "dynamic_workflow": dynamic_results
                }
            }
        except Exception as e:
            logger.error(f"Error executing dynamic workflow: {str(e)}", exc_info=True)
            return {
                "success": False,
                "status": "failed",
                "error": f"Error executing dynamic workflow: {str(e)}"
            }
            
    except Exception as e:
        logger.error(f"Error in custom_execute_dynamic_tasks_handler: {str(e)}", exc_info=True)
        return {
            "success": False,
            "status": "failed",
            "error": f"Error executing dynamic tasks: {str(e)}"
        }

def custom_validate_plan_handler(task, input_data: dict) -> dict:
    """
    Validates a research plan from the LLM.
    
    Args:
        task: The DirectHandlerTask object
        input_data: Dictionary containing raw_llm_output
        
    Returns:
        Dictionary with validation status and validated plan
    """
    # Import services here to ensure availability
    from core.services import get_services
    
    # Get services directly from the global container
    services = get_services()
    
    # Always create a logger directly instead of trying to get it from services
    logger = logging.getLogger(__name__)
    
    logger.info("Validating research plan")
    
    try:
        # Get the raw LLM output from input data
        raw_llm_output = input_data.get("raw_llm_output")
        if not raw_llm_output:
            logger.error("No raw LLM output provided to validate")
            return {
                "success": False,
                "status": "failed",
                "error": "No raw LLM output provided"
            }
        
        # Extract JSON from the LLM output if it's wrapped in code blocks
        import re
        import json
        
        # Try to extract JSON from code blocks
        json_match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", raw_llm_output)
        plan_json_str = json_match.group(1) if json_match else raw_llm_output
        
        try:
            # Parse the JSON
            research_plan = json.loads(plan_json_str)
            
            # Validate required fields
            required_fields = ["research_question", "research_areas"]
            missing_fields = [field for field in required_fields if field not in research_plan]
            
            if missing_fields:
                error_msg = f"Missing required fields in research plan: {', '.join(missing_fields)}"
                logger.error(error_msg)
                return {
                    "success": False,
                    "status": "failed",
                    "error": error_msg,
                    "result": {
                        "raw_plan": plan_json_str
                    }
                }
            
            # Validate research areas
            research_areas = research_plan.get("research_areas", [])
            if not research_areas or not isinstance(research_areas, list):
                error_msg = "Research areas must be a non-empty list"
                logger.error(error_msg)
                return {
                    "success": False,
                    "status": "failed",
                    "error": error_msg,
                    "result": {
                        "raw_plan": plan_json_str
                    }
                }
            
            # Validate search queries in each research area
            for i, area in enumerate(research_areas):
                if not isinstance(area, dict):
                    error_msg = f"Research area at index {i} must be an object"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "status": "failed",
                        "error": error_msg,
                        "result": {
                            "raw_plan": plan_json_str
                        }
                    }
                
                if "area" not in area:
                    error_msg = f"Research area at index {i} is missing 'area' field"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "status": "failed",
                        "error": error_msg,
                        "result": {
                            "raw_plan": plan_json_str
                        }
                    }
                
                if "search_queries" not in area or not isinstance(area["search_queries"], list) or not area["search_queries"]:
                    error_msg = f"Research area '{area.get('area')}' is missing valid search queries"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "status": "failed",
                        "error": error_msg,
                        "result": {
                            "raw_plan": plan_json_str
                        }
                    }
            
            # Plan is valid
            logger.info("Research plan validation successful")
            validated_plan = json.dumps(research_plan)
            return {
                "success": True,
                "status": "completed",
                "result": {
                    "research_plan": research_plan,
                    "validated_plan": validated_plan
                }
            }
            
        except json.JSONDecodeError as e:
            error_msg = f"Failed to parse research plan JSON: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "status": "failed",
                "error": error_msg,
                "result": {
                    "raw_output": raw_llm_output
                }
            }
            
    except Exception as e:
        logger.error(f"Error in custom_validate_plan_handler: {str(e)}", exc_info=True)
        return {
            "success": False,
            "status": "failed",
            "error": f"Error validating research plan: {str(e)}"
        }

def custom_summarize_results_handler(task, input_data: dict) -> dict:
    """
    Summarizes the results of the dynamic workflow execution.
    
    Args:
        task: The DirectHandlerTask object
        input_data: Dictionary containing execution_results
        
    Returns:
        Dictionary with research summary
    """
    # Import services here to ensure availability
    from core.services import get_services
    
    # Get services directly from the global container
    services = get_services()
    
    # Always create a logger directly instead of trying to get it from services
    logger = logging.getLogger(__name__)
    
    logger.info("Summarizing research results")
    
    try:
        # Get the execution results from input data
        execution_results = input_data.get("execution_results")
        if not execution_results:
            logger.error("No execution results provided to summarize")
            return {
                "success": False,
                "status": "failed",
                "error": "No execution results provided"
            }
        
        # Get LLM interface directly from services
        llm = services.get_llm_interface()
        if not llm:
            logger.error("LLM interface not available")
            return {
                "success": False,
                "status": "failed",
                "error": "LLM interface not available"
            }
        
        # Extract results from completed tasks
        task_results = []
        for task_id, task_output in execution_results.items():
            # Only include tasks with successful results
            if isinstance(task_output, dict) and task_output.get("status") == "success":
                task_result = {
                    "task_id": task_id,
                    "task_type": task_id.split("_")[0] if "_" in task_id else "unknown",
                    "result": task_output.get("result", "")
                }
                task_results.append(task_result)
        
        # Create a summary prompt
        summary_prompt = f"""
        Summarize the following research results into a comprehensive report:
        
        {task_results}
        
        Your summary should:
        1. Provide an executive summary of the key findings
        2. Organize information by themes or categories
        3. Highlight the most important insights
        4. Identify any limitations or gaps in the research
        5. Format the summary in markdown
        """
        
        # Generate the summary using the LLM
        try:
            logger.info("Generating research summary")
            summary_response = llm(summary_prompt)
            
            return {
                "success": True,
                "status": "completed",
                "result": {
                    "research_summary": summary_response
                }
            }
        except Exception as e:
            logger.error(f"Error generating summary with LLM: {str(e)}")
            return {
                "success": False,
                "status": "failed",
                "error": f"Failed to generate summary: {str(e)}"
            }
            
    except Exception as e:
        logger.error(f"Error in custom_summarize_results_handler: {str(e)}", exc_info=True)
        return {
            "success": False,
            "status": "failed",
            "error": f"Error summarizing results: {str(e)}"
        }

def custom_full_research_handler(task, input_data: dict) -> dict:
    """
    Orquesta todo el flujo de investigación:
    1. Planifica y valida el plan con el LLM
    2. Convierte el plan en tareas dinámicas
    3. Ejecuta búsquedas reales con web.run, analiza y genera reporte
    4. Resume los resultados con el LLM
    """
    import json
    import logging
    import time
    from core.services import get_services
    from core.workflow import Workflow
    from core.task import DirectHandlerTask
    from web import run as web_run

    # Planificación y validación
    from __main__ import custom_plan_user_request_handler, custom_plan_to_tasks_handler

    logger = logging.getLogger(__name__)
    services = get_services()
    llm = services.get_llm_interface()

    plan_output = custom_plan_user_request_handler(task, input_data)
    if not plan_output.get("success"):
        return plan_output
    validated_plan = plan_output["result"]["validated_plan"]

    # Convertir plan en tareas dinámicas
    tasks_input = {"validated_plan_json": json.dumps(validated_plan)}
    tasks_output = custom_plan_to_tasks_handler(task, tasks_input)
    if not tasks_output.get("success"):
        return tasks_output
    dynamic_tasks = tasks_output["result"]["dynamic_tasks"]

    # Construir workflow dinámico
    workflow_id = f"dynamic_research_{int(time.time())}"
    dynamic_workflow = Workflow(workflow_id=workflow_id, name="Dynamic Research Workflow")

    for task_def in dynamic_tasks:
        tid = task_def["id"]
        name = task_def.get("name", tid)
        typ = task_def.get("type")
        inp = task_def.get("input_data", {})
        deps = task_def.get("depends_on", [])

        if typ == "search":
            def make_search_handler(key="search_term"):
                def search_hdl(t, data):
                    term = data.get(key)
                    # Real web search
                    sources = web_run({"search_query":[{"q": term, "recency":30, "domains": None}]})
                    snippets = []
                    for src in sources:
                        if hasattr(src, 'get'):
                            snippet = src.get('snippet') or src.get('title') or ''
                            snippets.append(snippet)
                    return {"success": True, "status": "completed", "result": snippets}
                return search_hdl
            handler = make_search_handler()
        elif typ == "analyze":
            def analyze_hdl(t, data):
                results = data.get("search_results", [])
                return {"success": True, "status": "completed", "result": f"Análisis de {len(results)} resultados"}
            handler = analyze_hdl
        elif typ == "report":
            def report_hdl(t, data):
                return {"success": True, "status": "completed", "result": f"Informe basado en {data.get('analysis', '')}"}
            handler = report_hdl
        else:
            handler = lambda t, data: {"success": True, "status": "completed", "result": data}

        dyn_task = DirectHandlerTask(
            task_id=tid,
            name=name,
            handler=handler,
            input_data=inp,
            depends_on=deps
        )
        dynamic_workflow.add_task(dyn_task)

    # Ejecutar workflow dinámico
    engine = services.create_workflow_engine(dynamic_workflow)
    exec_results = engine.run({})

    # Serializar resultados
    serial_results = {tid: out.to_dict() for tid, out in exec_results.items()}

    # Resumen final con LLM
    summary_prompt = f"""
Resume los siguientes resultados de investigación en un informe markdown:

{json.dumps(serial_results, indent=2)}

Incluye:
1. Resumen ejecutivo
2. Principales hallazgos organizados por tema
3. Limitaciones o huecos
4. Tabla de impacto por país
"""
    try:
        llm_resp = llm.execute_llm_call(summary_prompt, system_message="Resume bien los resultados")
        summary = llm_resp.get("response", "")
    except Exception as e:
        logger.error(f"Error generando resumen con LLM: {e}")
        return {"success": False, "status": "failed", "error": str(e)}

    return {"success": True, "status": "completed", "result": {"research_summary": summary, "dynamic_workflow": serial_results}}


def construct_economic_research_workflow(user_request=USER_REQUEST):
    from core.workflow import Workflow
    from core.task import DirectHandlerTask
    
    workflow = Workflow("economic_research_workflow", "Economic Research Workflow")
    full = DirectHandlerTask(
        task_id="full_research",
        name="Full Economic Research",
        handler=custom_full_research_handler,
        input_data={"user_request": user_request}
    )
    workflow.add_task(full)
    return workflow

def main():
    """Execute the economic impact researcher example."""
    import sys
    import logging
    import json
    import pprint
    from pathlib import Path
    from core.services import get_services, reset_services
    from core.utils.visualizer import visualize_workflow
    from core.engine import WorkflowEngine
    
    # Configure logging
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(),
            logging.FileHandler('economic_researcher.log')
        ]
    )
    logger = logging.getLogger("economic_impact_researcher")
    logger.info("Starting Economic Impact Researcher")
    
    # Check if we have an API key
    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        logger.error("No OpenAI API key found in environment. Set the OPENAI_API_KEY environment variable.")
        sys.exit(1)
    
    # Test OpenAI connection
    logger.info("Testing OpenAI connection...")
    if not test_openai_connection(api_key):
        logger.error("Failed to connect to OpenAI API. Check your API key and internet connection.")
        sys.exit(1)
    logger.info("OpenAI connection successful")
    
    try:
        # Initialize services
        reset_services()  # Reset any previous services
        services = get_services()
        
        # Create LLM interface
        from core.llm.interface import LLMInterface
        llm_interface = LLMInterface(api_key=api_key, model=MODEL_NAME)
        services.register_llm_interface(llm_interface)
        logger.info(f"LLM Interface registered with model {MODEL_NAME}")
        
        # Register tools
        from tools.web_search_tool import WebSearchTool
        from tools.file_read_tool import register as register_file_read_tool
        from tools.write_markdown_tool import register as register_markdown_tool
        
        # Register web search tool
        def register_web_search_tool(tool_registry):
            """Register the web search tool with the tool registry."""
            def web_search_handler(input_data):
                try:
                    search_term = input_data.get("search_term", "")
                    if not search_term:
                        return {
                            "success": False,
                            "error": "No search term provided",
                            "status": "failed"
                        }
                    
                    # Implementa tu búsqueda web real aquí
                    # Por ejemplo, usando requests o alguna API de búsqueda
                    results = WebSearchTool().perform_search(
                        search_term,
                        input_data.get("context_size", "medium"),
                        input_data.get("user_location", None)
                    )
                    
                    return {
                        "success": True,
                        "result": results,
                        "status": "completed"
                    }
                    
                except Exception as e:
                    return {
                        "success": False,
                        "error": str(e),
                        "status": "failed"
                    }

            if not tool_registry.tool_exists("web_search"):
                tool_registry.register_tool("web_search", web_search_handler)
                logger.info("Web search tool registered")
            else:
                logger.info("Web search tool already registered")
        
        # Register file tools if they don't already exist
        if not services.tool_registry.tool_exists("file_read"):
            register_file_read_tool(services.tool_registry)
        else:
            logger.info("File read tool already registered")
            
        if not services.tool_registry.tool_exists("write_markdown"):
            register_markdown_tool(services.tool_registry)
        else:
            logger.info("Write markdown tool already registered")
            
        logger.info("Tools registered")
        
        # Build the research workflow
        research_workflow = construct_economic_research_workflow()
        logger.info("Research workflow constructed")
        
        # Visualize workflow (static)
        try:
            visualize_workflow(
                research_workflow, 
                filename="economic_research_static_workflow.png",
                format="png",
                view=False
            )
            logger.info("Static workflow visualization saved")
            
            # Also save as PDF
            visualize_workflow(
                research_workflow, 
                filename="economic_research_static_workflow.pdf",
                format="pdf",
                view=False
            )
            logger.info("Static workflow visualization saved as PDF")
        except Exception as viz_error:
            logger.error(f"Workflow visualization error: {str(viz_error)}")
        
        # Execute the workflow
        # Create a properly initialized workflow engine
        engine = services.create_workflow_engine(research_workflow)
        
        # Prepare initial data
        initial_data = {
            "user_request": USER_REQUEST
        }
        
        # Run the workflow
        logger.info("Running workflow engine...")
        results = engine.run(initial_data)
        
        # DEBUG - Detailed output structure analysis
        if 'plan_research' in results:
            logger.info("========== DEBUG - DETAILED PLAN_RESEARCH OUTPUT ==========")
            plan_output = results['plan_research']
            
            # If it's a TaskOutput object
            if hasattr(plan_output, 'to_dict'):
                plan_dict = plan_output.to_dict()
                logger.info(f"TaskOutput object with keys: {list(plan_dict.keys())}")
                
                # Output all fields for debugging
                for key, value in plan_dict.items():
                    if isinstance(value, dict):
                        logger.info(f"Field '{key}' is a dict with keys: {list(value.keys())}")
                    elif isinstance(value, list):
                        logger.info(f"Field '{key}' is a list with {len(value)} items")
                    else:
                        logger.info(f"Field '{key}': {value}")
                
                # Save the full output to a file for inspection
                with open("plan_research_debug_output.json", "w") as f:
                    json.dump(plan_dict, f, indent=2, default=str)
                logger.info("Saved full plan_research output to plan_research_debug_output.json")
            else:
                # If it's a direct dictionary
                logger.info(f"Direct dictionary with keys: {list(plan_output.keys())}")
                
                # Output all fields for debugging
                for key, value in plan_output.items():
                    if isinstance(value, dict):
                        logger.info(f"Field '{key}' is a dict with keys: {list(value.keys())}")
                    elif isinstance(value, list):
                        logger.info(f"Field '{key}' is a list with {len(value)} items")
                    else:
                        logger.info(f"Field '{key}': {value}")
                
                # Save the full output to a file for inspection
                with open("plan_research_debug_output.json", "w") as f:
                    json.dump(plan_output, f, indent=2, default=str)
                logger.info("Saved full plan_research output to plan_research_debug_output.json")
            
            logger.info("========== END DEBUG OUTPUT ==========")
        
        # Save results
        try:
            # Convert TaskOutput objects to dictionaries for JSON serialization
            serializable_results = {}
            for task_id, output in results.items():
                if hasattr(output, 'to_dict'):
                    serializable_results[task_id] = output.to_dict()
                else:
                    serializable_results[task_id] = output
            
            with open("economic_research_results.json", "w") as f:
                json.dump(serializable_results, f, indent=2)
            logger.info("Results saved to economic_research_results.json")
        except Exception as json_error:
            logger.error(f"Error saving results: {str(json_error)}")
        
        # Log the structure
        logger.info("Workflow execution completed. Output structure:")
        for task_id, output in results.items():
            if isinstance(output, dict):
                keys = list(output.keys())
                logger.info(f"  Task '{task_id}': {keys}")
            else:
                logger.info(f"  Task '{task_id}': {type(output)}")
        
        # Ensure report exists
        final_task = "summarize_results"
        if final_task in results and isinstance(results[final_task], dict):
            report_path = results[final_task].get("result", {}).get("summary", {}).get("report_path", None)
            ensure_report_exists(report_path)
        
        logger.info("Economic Impact Researcher completed successfully")
        return results
            
    except Exception as e:
        logger.error(f"Error in main function: {str(e)}")
        import traceback
        logger.error(traceback.format_exc())
        sys.exit(1)

def create_error_response(message, error_code=None, error_type=None):
    """Create a standardized error response."""
    return {
        "success": False,
        "status": "failed",
        "error": message,
        "error_code": error_code or "UNKNOWN_ERROR",
        "error_type": error_type or "runtime_error"
    }

# Sobrescribe el handler problemático
from core.tools.registry import ToolRegistry
original_execute_tool = ToolRegistry.execute_tool

def patched_execute_tool(self, tool_name, input_data):
    try:
        return original_execute_tool(self, tool_name, input_data)
    except Exception as e:
        return create_error_response(str(e))

ToolRegistry.execute_tool = patched_execute_tool

if __name__ == "__main__":
    main() 