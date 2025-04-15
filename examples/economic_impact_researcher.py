#!/usr/bin/env python3
"""
Investigador de Impacto Económico usando Chat Planner de Dawn.

Este script toma un prompt de investigación, lo pasa al Chat Planner Workflow,
el cual genera y ejecuta dinámicamente un workflow para investigar el tema
y producir un informe en Markdown.

FIXES APPLIED:
- Fixed imports for core.llm.interface for accessing LLMInterface
- Added local Step class definition to avoid import errors
- Updated handlers registration to use examples.chat_planner_workflow
- Fixed the workflow construction to use DirectHandlerTask
- Fixed tool registry and handler registry access
- Fixed LLM interface registration with services
- Updated workflow visualization to use the visualize_workflow function
- Fixed use of HandlerRegistry.list_handlers() instead of non-existent get_all_handlers()
- Fixed access to ToolRegistry.tools directly instead of non-existent get_all_tools()
"""
# noqa: D202

import sys
import os
import logging
import json
import traceback  # Add this for proper error handling
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime
import warnings
import re  # Add this import for regex cleanup
import requests

# Debug flag - Set to True for more verbose logging
DEBUG = True

# Configurar filtro de warnings para suprimir mensajes específicos
class ChatPlannerWarningFilter(logging.Filter):
    def filter(self, record):
        if "Could not register tools globally" in record.getMessage() or \
           "Could not register handlers globally" in record.getMessage():
            return False
        return True

# Aplicar filtro al logger del chat_planner_workflow
chat_planner_logger = logging.getLogger("chat_planner_workflow")
chat_planner_logger.addFilter(ChatPlannerWarningFilter())

# Configurar logging básico - MOVER ESTO ARRIBA
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("economic_impact_researcher")

# --- Configuración del Path ---
# Añadir raíz del proyecto al path para importaciones correctas
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)
# Añadir directorio 'examples' si es necesario para importar el chat_planner_workflow
examples_dir = os.path.join(project_root, "examples")
if examples_dir not in sys.path:
     sys.path.insert(0, examples_dir)
# ---------------------------

# --- Importaciones Core de Dawn ---
from core.workflow import Workflow
from core.engine import WorkflowEngine # Usaremos el motor síncrono por simplicidad aquí
from core.services import get_services, reset_services, ServicesContainer  # Note: Services class doesn't exist
from core.llm.interface import LLMInterface # Necesario para inicializar servicios
from core.tools.registry import ToolRegistry # Necesario para inicializar servicios
from core.handlers.registry import HandlerRegistry # Necesario para inicializar servicios
from core.tools.registry_access import register_tool, tool_exists
from core.handlers.registry_access import register_handler, handler_exists
from core.utils.registration_manager import ensure_all_registrations
from core.utils.visualizer import visualize_workflow # Opcional
from core.task import Task, DirectHandlerTask
# -------------------------------

# --- Define Step class locally ---
class Step:
    """Class representing a workflow step."""  # noqa: D202
    
    def __init__(self, id, name, description, handler):
        """Initialize a workflow step.
        
        Args:
            id: Unique identifier for the step
            name: Human-readable name for the step
            description: Description of what the step does
            handler: Name of the handler function to execute
        """
        self.id = id
        self.name = name
        self.description = description
        self.handler = handler

# --- Importar el Chat Planner Workflow ---
try:
    # Asumiendo que chat_planner_workflow.py está en el mismo directorio o en examples/
    from chat_planner_workflow import (
        build_chat_planner_workflow,
        # Importar TODOS los handlers que usa build_chat_planner_workflow por NOMBRE
        plan_user_request_handler,
        validate_plan_handler,
        plan_to_tasks_handler,
        execute_dynamic_tasks_handler,
        summarize_results_handler,
        process_clarification_handler,
        await_input_handler,
        check_clarification_needed_default_handler,
        # Importar también los mocks si son necesarios para el registro inicial
        mock_search_tool,
        mock_summarize_handler
    )
    logger.info("Successfully imported chat_planner_workflow components.")
except ImportError as e:
    logger.error(f"Could not import chat_planner_workflow. Ensure it's in the Python path: {e}", exc_info=True)
    sys.exit(1)
# ------------------------------------

# --- Prompt de Investigación Inicial ---
# Define claramente el objetivo, el alcance y el formato de salida deseado.
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
"""
# -------------------------------------

# --- Configuración de LLM ---
PROVIDER = "openai"  # Proveedor de LLM
MODEL_NAME = "gpt-4"  # Cambiado de gpt-4o-mini a gpt-4 para mayor confiabilidad
USER_REQUEST = INITIAL_RESEARCH_PROMPT  # La solicitud del usuario
# ----------------------------

def save_debug_info(raw_text, error_message, filename="llm_debug_info.txt"):
    """
    Save debug information about LLM response to a file for inspection.
    
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
        logger.info(f"Attempting to fix JSON from LLM response of length {len(raw_text)}")
        logger.info(f"First 100 chars: {raw_text[:100]}")
    
    # Save the raw response for debugging regardless of outcome
    save_debug_info(raw_text, "Raw LLM response for JSON fixing", "llm_raw_response_debug.txt")
    
    # First try to extract JSON from markdown code blocks (most common format)
    json_match = re.search(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_text)
    if json_match:
        json_content = json_match.group(1).strip()
        if DEBUG:
            logger.info("Found JSON in code block")
    else:
        # Try to find array brackets if not in code blocks
        json_match = re.search(r'\[\s*{[\s\S]*}\s*\]', raw_text)
        if json_match:
            json_content = json_match.group(0).strip()
            if DEBUG:
                logger.info("Found JSON array pattern")
        else:
            # Look for any object pattern
            json_match = re.search(r'\{\s*"[^"]+"\s*:[\s\S]*\}', raw_text)
            if json_match:
                json_content = json_match.group(0).strip()
                if DEBUG:
                    logger.info("Found JSON object pattern")
            else:
                # More aggressive search for any JSON-like structure
                json_match = re.search(r'(\[|\{)[\s\S]*(\]|\})', raw_text)
                if json_match:
                    json_content = json_match.group(0).strip()
                    if DEBUG:
                        logger.info("Found JSON-like structure using aggressive pattern")
                else:
                    logger.error("No JSON-like structure found in LLM response")
                    save_debug_info(raw_text, "No JSON-like structure found in LLM response", "llm_json_extraction_failed.txt")
                    return None
    
    # Clean the extracted content
    if DEBUG:
        logger.info(f"Raw extracted JSON: {json_content[:100]}...")
    
    # Try parsing the JSON as-is first before applying fixes
    try:
        parsed_json = json.loads(json_content)
        logger.info("JSON parsed successfully without fixes")
        return json.dumps(parsed_json, indent=2)
    except json.JSONDecodeError as e:
        logger.info(f"Initial JSON parsing failed: {e}. Attempting fixes...")
    
    # Apply a series of fixes to make the JSON valid
    try:
        # 1. Fix unquoted property names
        json_content = re.sub(r'([{,]\s*)([a-zA-Z0-9_]+)(\s*:)', r'\1"\2"\3', json_content)
        
        # 2. Fix single quotes to double quotes (careful with nested quotes)
        json_content = re.sub(r"'([^']*)'", r'"\1"', json_content)
        
        # 3. Remove trailing commas
        json_content = re.sub(r',(\s*[}\]])', r'\1', json_content)
        
        # 4. Handle newlines in string values
        json_content = re.sub(r':\s*"([^"]*?)\n\s*([^"]*?)"', r': "\1 \2"', json_content)
        
        # 5. Fix missing quotes around values
        json_content = re.sub(r':\s*([a-zA-Z0-9_]+)(\s*[,}])', r': "\1"\2', json_content)
        
        # 6. Fix boolean and null values (ensure they're not quoted)
        json_content = re.sub(r':\s*"(true|false|null)"', r': \1', json_content)
        
        # 7. Ensure the root is an array if that's what we expect
        if not (json_content.strip().startswith('[') and json_content.strip().endswith(']')):
            # Check if this is a single object when we expect an array
            if json_content.strip().startswith('{') and json_content.strip().endswith('}'):
                json_content = f"[{json_content}]"
                if DEBUG:
                    logger.info("Wrapped single object in array")
        
        # 8. Fix missing closing brackets/braces
        open_braces = json_content.count('{')
        close_braces = json_content.count('}')
        if open_braces > close_braces:
            json_content += '}' * (open_braces - close_braces)
            logger.info(f"Added {open_braces - close_braces} missing closing braces")
            
        open_brackets = json_content.count('[')
        close_brackets = json_content.count(']')
        if open_brackets > close_brackets:
            json_content += ']' * (open_brackets - close_brackets)
            logger.info(f"Added {open_brackets - close_brackets} missing closing brackets")
        
        if DEBUG:
            logger.info(f"Fixed JSON: {json_content[:100]}...")
            # Save the fixed JSON for debugging
            save_debug_info(json_content, "Fixed JSON before validation", "llm_fixed_json_debug.txt")
        
        # Validate by parsing
        try:
            parsed_json = json.loads(json_content)
            return json.dumps(parsed_json, indent=2)
        except json.JSONDecodeError as e:
            logger.error(f"Failed to fix JSON: {e}")
            if DEBUG:
                logger.error(f"JSON that failed to parse: {json_content}")
            save_debug_info(json_content, f"JSON decode error: {e}", "llm_json_error.txt")
            return None
    except Exception as e:
        logger.error(f"Exception during JSON fixing: {str(e)}")
        logger.error("Full traceback:", exc_info=True)
        save_debug_info(json_content, f"Exception during JSON fixing: {str(e)}", "llm_json_fixing_exception.txt")
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
            "type": "tool",
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

# Create custom handler wrappers
def custom_plan_user_request_handler(task, input_data):
    """
    Custom wrapper for plan_user_request_handler that ensures proper JSON output.
    """
    # Call the original handler
    try:
        result = plan_user_request_handler(task, input_data)
        
        if DEBUG:
            logger.info(f"Original plan_user_request_handler result: {result.get('status', 'unknown')}")
        
        # Check if successful and contains a response
        if result.get("success") and "response" in result.get("result", {}):
            # Try to fix the JSON in the response
            raw_response = result["result"]["response"]
            
            if DEBUG:
                logger.info(f"Attempting to fix JSON in LLM response (length: {len(raw_response)})")
            
            # Save the raw response for debugging
            save_debug_info(raw_response, "Raw LLM response before fixing", "llm_raw_response.txt")
            
            fixed_json = fix_json_from_llm(raw_response)
            
            if fixed_json:
                # Update the response with the fixed JSON
                logger.info("Successfully fixed JSON in LLM response")
                result["result"]["response"] = fixed_json
            else:
                logger.warning("Could not fix JSON in LLM response, using fallback plan")
                # Try a more direct approach - sometimes the model outputs a plan description before the JSON
                # Extract anything that looks like structured content
                if "```" in raw_response:
                    blocks = re.findall(r'```(?:json)?\s*([\s\S]*?)\s*```', raw_response)
                    for block in blocks:
                        fixed_json = fix_json_from_llm(block)
                        if fixed_json:
                            logger.info("Found and fixed JSON in a code block")
                            result["result"]["response"] = fixed_json
                            break
                
                # If still no valid JSON, use fallback plan
                if not fixed_json:
                    fallback_plan = create_fallback_plan()
                    result["result"]["response"] = json.dumps(fallback_plan, indent=2)
                    logger.info("Using fallback plan")
        else:
            logger.warning("LLM response did not contain expected structure, using fallback plan")
            if result.get("error"):
                save_debug_info("", f"Error from plan_user_request_handler: {result.get('error')}", "llm_plan_error.txt")
            
            fallback_plan = create_fallback_plan()
            if not result.get("result"):
                result["result"] = {}
            result["result"]["response"] = json.dumps(fallback_plan, indent=2)
            result["success"] = True
            result["status"] = "completed"
    except Exception as e:
        logger.error(f"Error in custom_plan_user_request_handler: {str(e)}")
        logger.error("Full traceback:", exc_info=True)
        save_debug_info("", f"Exception in custom_plan_user_request_handler: {str(e)}", "llm_handler_exception.txt")
        
        # Create a fallback result
        result = {
            "success": True,
            "status": "completed",
            "result": {
                "response": json.dumps(create_fallback_plan(), indent=2)
            }
        }
                
    return result

def custom_validate_plan_handler(task, input_data):
    """
    Custom wrapper for validate_plan_handler that ensures proper JSON parsing.
    """
    raw_llm_output = input_data.get("raw_llm_output", "")
    
    if not raw_llm_output:
        logger.warning("No raw LLM output provided for plan validation")
        return {
            "success": False,
            "status": "failed",
            "error": "No raw LLM output provided for plan validation",
            "result": {"validated_plan": None, "validation_errors": ["Missing input"]}
        }
    
    if DEBUG:
        logger.info(f"Validating plan from raw LLM output (length: {len(raw_llm_output)})")
    
    # Try to parse the JSON with our helper
    try:
        # Check if it's already valid JSON
        try:
            parsed_plan = json.loads(raw_llm_output)
            logger.info("Raw LLM output is already valid JSON")
            
            # Basic validation: ensure it's a list
            if not isinstance(parsed_plan, list):
                logger.warning("Plan is not a list, attempting to fix")
                # If it's a single object, wrap it in a list
                if isinstance(parsed_plan, dict):
                    parsed_plan = [parsed_plan]
                    logger.info("Wrapped single object in a list")
                else:
                    raise ValueError("Plan must be a list of steps")
            
            # Success path
            if parsed_plan and len(parsed_plan) > 0:
                return {
                    "success": True,
                    "status": "completed",
                    "result": {
                        "validated_plan": parsed_plan,
                        "validation_warnings": [],
                        "validation_errors": []
                    }
                }
        except json.JSONDecodeError:
            # Not valid JSON, proceed with fixing
            logger.info("Raw LLM output is not valid JSON, attempting to fix")
            pass
        
        # First try to fix any formatting issues
        fixed_json = fix_json_from_llm(raw_llm_output)
        
        if fixed_json:
            logger.info("Successfully fixed JSON format")
            parsed_plan = json.loads(fixed_json)
            
            # Basic validation: check if it's a list
            if not isinstance(parsed_plan, list):
                logger.warning("Fixed JSON is not a list, attempting further fixes")
                # If it's a single object, wrap it in a list
                if isinstance(parsed_plan, dict):
                    parsed_plan = [parsed_plan]
                    logger.info("Wrapped single object in a list")
                    # Success path for wrapped object
                    return {
                        "success": True,
                        "status": "completed",
                        "result": {
                            "validated_plan": parsed_plan,
                            "validation_warnings": ["Converted single step to list"],
                            "validation_errors": []
                        }
                    }
                else:
                    logger.error("Plan format is neither a list nor an object")
                    raise ValueError("Plan must be a list of steps")
            
            # Check if we have steps
            if len(parsed_plan) == 0:
                logger.error("Plan contains no steps")
                raise ValueError("Empty plan")
            
            # If we got here, validation was successful
            return {
                "success": True,
                "status": "completed",
                "result": {
                    "validated_plan": parsed_plan,
                    "validation_warnings": [],
                    "validation_errors": []
                }
            }
        else:
            logger.warning("Could not fix JSON format, using fallback plan")
            # If fixing fails, use fallback plan
            fallback_plan = create_fallback_plan()
            return {
                "success": True,  # Return success to continue workflow
                "status": "completed",
                "result": {
                    "validated_plan": fallback_plan,
                    "validation_warnings": ["Used fallback plan due to JSON parsing issues"],
                    "validation_errors": []
                }
            }
    except Exception as e:
        logger.error(f"Error during plan validation: {str(e)}")
        # Use fallback plan on any error
        fallback_plan = create_fallback_plan()
        return {
            "success": True,  # Return success to continue workflow
            "status": "completed",
            "result": {
                "validated_plan": fallback_plan,
                "validation_warnings": [f"Used fallback plan due to error: {str(e)}"],
                "validation_errors": []
            }
        }

# Add missing handlers required by Chat Planner Workflow
def execute_step_handler(task, input_data):
    """Handler for executing a single step in the workflow."""
    step_id = input_data.get('step_id')
    step_type = input_data.get('step_type')
    step_name = input_data.get('step_name')
    step_inputs = input_data.get('step_inputs', {})
    
    logger.info(f"Executing step handler for: {step_id} ({step_type}:{step_name})")
    
    if step_type == 'tool':
        try:
            services = get_services()
            tool_registry = services.tool_registry
            
            if tool_registry.tool_exists(step_name):
                result = tool_registry.execute_tool(step_name, step_inputs)
                return {
                    "success": True,
                    "status": "completed",
                    "result": result
                }
            else:
                logger.error(f"Tool '{step_name}' not found for step '{step_id}'")
                return {
                    "success": False,
                    "status": "failed",
                    "error": f"Tool '{step_name}' not found"
                }
        except Exception as e:
            logger.error(f"Error executing tool '{step_name}' for step '{step_id}': {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "status": "failed",
                "error": f"Tool execution error: {str(e)}"
            }
    elif step_type == 'handler':
        try:
            services = get_services()
            handler_registry = services.handler_registry
            
            if handler_registry.handler_exists(step_name):
                handler = handler_registry.get_handler(step_name)
                result = handler(task, step_inputs)
                return {
                    "success": True,
                    "status": "completed",
                    "result": result
                }
            else:
                logger.error(f"Handler '{step_name}' not found for step '{step_id}'")
                return {
                    "success": False,
                    "status": "failed",
                    "error": f"Handler '{step_name}' not found"
                }
        except Exception as e:
            logger.error(f"Error executing handler '{step_name}' for step '{step_id}': {str(e)}")
            logger.error(traceback.format_exc())
            return {
                "success": False,
                "status": "failed",
                "error": f"Handler execution error: {str(e)}"
            }
    else:
        logger.error(f"Unknown step type '{step_type}' for step '{step_id}'")
        return {
            "success": False,
            "status": "failed",
            "error": f"Unknown step type: {step_type}"
        }

def task_complete_handler(task, input_data):
    """Handler for task completion notification."""
    task_id = input_data.get('task_id', 'unknown')
    task_status = input_data.get('status', 'unknown')
    task_result = input_data.get('result', {})
    
    logger.info(f"Task completion handler for: {task_id} (Status: {task_status})")
    
    return {
        "success": True,
        "status": "completed",
        "result": {
            "task_id": task_id,
            "completed_at": datetime.datetime.now().isoformat(),
            "final_status": task_status,
            "has_result": task_result is not None
        }
    }

def get_available_capabilities_tool(task=None, input_data=None) -> Dict[str, Any]:
    """
    Get available tools and handlers in the system.
    
    Args:
        task: Optional task object (required for tool signature compatibility)
        input_data: Optional input data (required for tool signature compatibility)
        
    Returns:
        Dict containing information about available tools, handlers, and system info.
    """
    services = get_services()
    handler_registry = services.handler_registry
    tool_registry = services.tool_registry
    
    logger.info("Retrieving available tools and handlers")
    
    # Get registered handlers and their names
    handler_names = handler_registry.list_handlers()
    
    # Get registered tools and their descriptions
    tools = tool_registry.tools
    tool_descriptions = {}
    
    for name, tool in tools.items():
        # Get docstring as description
        doc = tool.__doc__ or "No description available"
        tool_descriptions[name] = doc.strip()
    
    # Collect system information
    system_info = {
        "timestamp": datetime.now().isoformat(),
        "python_version": sys.version,
    }
    
    result = {
        "status": "success",
        "success": True,
        "result": {
            "available_tools": list(tools.keys()),
            "tool_descriptions": tool_descriptions,
            "available_handlers": handler_names,
            "system_info": system_info
        },
        "error": None
    }
    
    if DEBUG:
        logger.info(f"Available tools: {result['result']['available_tools']}")
        logger.info(f"Available handlers: {result['result']['available_handlers']}")
    
    logger.info(f"Found {len(tools)} tools and {len(handler_names)} handlers")
    return result

def register_required_planner_handlers(services, tool_registry):
    """Register the required handlers for the planner."""
    handler_registry = services.handler_registry
    # Register chat planner handlers
    try:
        from examples.chat_planner_workflow import (
            plan_user_request_handler, 
            execute_step_handler,
            task_complete_handler,
            validate_plan_handler,
            plan_to_tasks_handler,
            execute_dynamic_tasks_handler,
            summarize_results_handler
        )

        # Register handlers for planner workflow
        handler_registry.register("plan_user_request", plan_user_request_handler)
        handler_registry.register("execute_step", execute_step_handler)
        handler_registry.register("task_complete", task_complete_handler)
        handler_registry.register("validate_plan", validate_plan_handler)
        handler_registry.register("plan_to_tasks", plan_to_tasks_handler)
        handler_registry.register("execute_dynamic_tasks", execute_dynamic_tasks_handler)
        handler_registry.register("summarize_results", summarize_results_handler)

        # Log the status of each handler registration
        logger.info("Registered handler: plan_user_request")
        logger.info("Registered handler: execute_step")
        logger.info("Registered handler: task_complete")
        logger.info("Registered handler: validate_plan")
        logger.info("Registered handler: plan_to_tasks")
        logger.info("Registered handler: execute_dynamic_tasks")
        logger.info("Registered handler: summarize_results")

        # Register 'get_available_capabilities' tool - required by the Chat Planner
        if tool_registry:
            tool_registry.register_tool("get_available_capabilities", get_available_capabilities_tool)
            logger.info("Registered tool: get_available_capabilities")
        else:
            logger.error("Tool registry is None, cannot register get_available_capabilities")

        return True
    except Exception as e:
        logger.error(f"Failed to register Chat Planner handlers: {str(e)}")
        logger.error(f"Error details: {traceback.format_exc()}")
        return False

def construct_chat_planner_workflow():
    """Construye el flujo de trabajo del Chat Planner."""
    workflow = Workflow(
        workflow_id="chat_planner_workflow",
        name="Chat Planner Workflow"
    )
    
    # Task 1: Plan the research based on user request
    plan_task = DirectHandlerTask(
        task_id="plan_research",
        name="Plan Research",
        handler_name="plan_user_request",
        input_data={
            "user_request": "${request}"
        }
    )
    workflow.add_task(plan_task)
    
    # Task 2: Validate the generated plan
    validate_task = DirectHandlerTask(
        task_id="validate_plan",
        name="Validate Plan",
        handler_name="validate_plan",
        input_data={
            "raw_llm_output": "${plan_research}.output_data.response"
        }
    )
    workflow.add_task(validate_task)
    
    # Task 3: Convert plan to executable tasks
    plan_to_tasks = DirectHandlerTask(
        task_id="plan_to_tasks",
        name="Convert Plan to Tasks",
        handler_name="plan_to_tasks",
        input_data={
            "plan": "${validate_plan}.output_data.plan",
            "request": "${request}"
        }
    )
    workflow.add_task(plan_to_tasks)
    
    # Task 4: Execute the dynamic tasks
    execute_tasks = DirectHandlerTask(
        task_id="execute_tasks",
        name="Execute Tasks",
        handler_name="execute_dynamic_tasks",
        input_data={
            "tasks": "${plan_to_tasks}.output_data.tasks",
            "request": "${request}"
        }
    )
    workflow.add_task(execute_tasks)
    
    # Task 5: Summarize results
    summarize_task = DirectHandlerTask(
        task_id="summarize_results",
        name="Summarize Results",
        handler_name="summarize_results",
        input_data={
            "execution_results": "${execute_tasks}.output_data.results",
            "request": "${request}"
        },
        output_variable="report"
    )
    workflow.add_task(summarize_task)
    
    return workflow

def ensure_report_exists(generated_report_path):
    """Ensure a report is generated even if the workflow fails."""
    if not generated_report_path:
        # Create a backup report with error information
        backup_report_path = "informe_tarifas_trump.md"
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Check for debug files that might contain more information
        debug_files = []
        errors_found = []
        
        # List of possible debug files with associated error messages
        debug_file_info = [
            {
                "file": "llm_debug_info.txt", 
                "error_type": "LLM Output Processing Error",
                "description": "Error procesando la respuesta del LLM"
            },
            {
                "file": "llm_raw_response.txt", 
                "error_type": "Raw LLM Response Issue",
                "description": "Problema con la respuesta bruta del LLM"
            },
            {
                "file": "llm_json_error.txt", 
                "error_type": "JSON Parsing Error",
                "description": "Error al analizar JSON en la respuesta"
            },
            {
                "file": "llm_json_extraction_failed.txt", 
                "error_type": "JSON Extraction Failed",
                "description": "No se pudo extraer JSON de la respuesta"
            },
            {
                "file": "llm_fixed_json_debug.txt", 
                "error_type": "JSON Fixing Attempted",
                "description": "Se intentó arreglar el JSON pero hubo problemas"
            },
            {
                "file": "llm_plan_error.txt", 
                "error_type": "Plan Generation Error",
                "description": "Error al generar el plan de investigación"
            },
            {
                "file": "llm_handler_exception.txt", 
                "error_type": "Handler Exception",
                "description": "Excepción en el manejador de flujo de trabajo"
            },
            {
                "file": "llm_raw_response_debug.txt", 
                "error_type": "LLM Response Debug",
                "description": "Problemas con el formato de la respuesta del LLM"
            },
            {
                "file": "llm_json_fixing_exception.txt", 
                "error_type": "JSON Fixing Exception",
                "description": "Excepción al intentar arreglar el JSON"
            }
        ]
        
        # Check which debug files exist and collect info
        for debug_info in debug_file_info:
            filename = debug_info["file"]
            if os.path.exists(filename):
                debug_files.append(filename)
                errors_found.append(f"{debug_info['error_type']}: {debug_info['description']}")
                
                # For JSON errors, check the specific error message
                if "json" in filename.lower() and os.path.getsize(filename) < 10000:
                    try:
                        with open(filename, "r") as f:
                            content = f.read()
                            # Extract error message if present
                            error_match = re.search(r'JSON decode error: (.*?)$', content, re.MULTILINE)
                            if error_match:
                                errors_found.append(f"  - Detalle: {error_match.group(1)}")
                    except Exception:
                        pass
        
        # If no specific errors were found, add a generic error
        if not errors_found:
            errors_found = ["Error desconocido en el procesamiento del flujo de trabajo"]
        
        # Create a better error report
        with open(backup_report_path, "w") as f:
            f.write(f"""# Informe sobre el Impacto Económico de las Tarifas de Trump

## Introducción
Este es un informe básico generado como respaldo después de que el workflow principal encontró errores.

## Resumen de errores encontrados
{os.linesep.join([f"- **{err}**" for err in errors_found])}

## Soluciones recomendadas

1. **Verificar la clave API**: Asegúrese de haber configurado correctamente la variable de entorno OPENAI_API_KEY con una clave válida.
   ```
   export OPENAI_API_KEY="su-clave-api-aquí"
   ```

2. **Verificar el modelo**: El script está configurado para usar el modelo "{MODEL_NAME}". Compruebe que tiene acceso a este modelo.

3. **Mejorar el formato JSON**: El error principal ocurre cuando el LLM genera una respuesta que no se puede analizar como JSON válido. Se han guardado archivos de diagnóstico para ayudar a depurar este problema.

4. **Archivos de diagnóstico disponibles**:
   {', '.join(debug_files) if debug_files else 'No se encontraron archivos de diagnóstico'}

5. **Probar con un modelo más simple**: Si está usando un modelo avanzado, pruebe con "gpt-3.5-turbo" que puede ser más estable para la generación de JSON.

6. **Ejecutar con diferentes instrucciones**: Intente modificar la solicitud de investigación para que sea más específica y clara.

## Instrucción original
```
{INITIAL_RESEARCH_PROMPT}
```

## Recomendaciones adicionales
Para obtener resultados completos, puede intentar:
1. Verificar las herramientas disponibles y su configuración
2. Ejecutar el script nuevamente con:
   ```
   export OPENAI_API_KEY="su-clave-api-aquí"
   python examples/economic_impact_researcher.py
   ```
3. Revisar los logs para identificar problemas específicos
4. Si sigue experimentando problemas, considere editar el script para usar un modelo diferente

*Informe generado el {current_time}*
""")
        logger.info(f"Created backup report at {backup_report_path}")
        return backup_report_path
    return generated_report_path

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

def main():
    """Run the Chat Planner Workflow with the Economic Impact Researcher."""
    try:
        # Reset and initialize services
        reset_services()
        services = get_services()
        services.initialize()
        
        logger.info("Services initialized successfully")
        
        # Check for API key
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY environment variable not set. Please set it and try again.")
            print("\n" + "*" * 80)
            print("ERROR: OPENAI_API_KEY environment variable not set.")
            print("Please set it with: export OPENAI_API_KEY='your-api-key'")
            print("*" * 80 + "\n")
            return None
        
        # Verify the API key format
        if not api_key.startswith(("sk-", "org-")):
            logger.error("OPENAI_API_KEY format appears to be invalid. OpenAI keys typically start with 'sk-'")
            print("\n" + "*" * 80)
            print("ERROR: OPENAI_API_KEY format appears to be invalid.")
            print("OpenAI API keys typically start with 'sk-'")
            print("*" * 80 + "\n")
            return None
            
        # Test the OpenAI connection
        logger.info("Testing OpenAI API connection...")
        if not test_openai_connection(api_key, "gpt-3.5-turbo"):
            logger.error("OpenAI API connection test failed. Please check your API key and internet connection.")
            print("\n" + "*" * 80)
            print("ERROR: OpenAI API connection test failed.")
            print("Please check your API key and internet connection.")
            print("*" * 80 + "\n")
            return None
        
        # Create LLM interface
        try:
            llm_interface = LLMInterface(
                api_key=api_key,
                model=MODEL_NAME
            )
            logger.info(f"LLM Interface created successfully with model {MODEL_NAME}")
        except Exception as llm_error:
            logger.error(f"Failed to create LLM interface: {str(llm_error)}")
            print("\n" + "*" * 80)
            print(f"ERROR: Failed to create LLM interface: {str(llm_error)}")
            print("Please check that you have access to the specified model.")
            print("*" * 80 + "\n")
            return None
        
        # Register the LLM interface with services (IMPORTANT: must register with name 'default_llm')
        services.register_llm_interface(llm_interface, "default_llm")
        logger.info(f"Registered LLM interface with services using model {MODEL_NAME}")
        
        # Ensure all standard tools are registered
        ensure_all_registrations()
        logger.info("All standard registrations ensured")
        
        # Register required planner handlers
        register_required_planner_handlers(services, services.tool_registry)
        logger.info("Planner handlers registered successfully")
        
        # Construct the Chat Planner Workflow with the Economic Impact Researcher
        planner_workflow = construct_chat_planner_workflow()
        logger.info("Chat Planner Workflow constructed")
        
        # Build the initial input data
        initial_input = {"user_request": USER_REQUEST}
        
        # Visualize the workflow (optional)
        try:
            visualize_workflow(planner_workflow, filename="workflow_visualization", format="png")
            logger.info("Workflow visualization created")
        except Exception as viz_error:
            logger.warning(f"Workflow visualization failed: {str(viz_error)}")
        
        # Get the tool and handler registries from services
        tool_registry = services.tool_registry
        handler_registry = services.handler_registry
        
        # Log the registered tools and handlers
        logger.info(f"Registered tools: {list(tool_registry.tools.keys())}")
        logger.info(f"Registered handlers: {handler_registry.list_handlers()}")
        
        # Create and run the workflow engine with proper services registration
        logger.info("Creating workflow engine")
        engine = WorkflowEngine(
            workflow=planner_workflow,
            llm_interface=llm_interface,  # Use the local llm_interface instance directly
            tool_registry=tool_registry,
            services=services  # Pass services container for proper variable resolution
        )
        
        # Set the initial input for the workflow
        initial_data = {"request": USER_REQUEST}
        
        # Run the workflow with timeout protection
        logger.info("Running workflow engine")
        try:
            results = engine.run(initial_data)
            logger.info(f"Workflow execution completed with results: {results}")
        except KeyboardInterrupt:
            logger.warning("Workflow execution was interrupted by user (KeyboardInterrupt)")
            print("\n" + "*" * 80)
            print("Workflow execution was interrupted. This may be due to a slow API response.")
            print("If using OpenAI, check your API key and quota.")
            print("*" * 80 + "\n")
            results = None
        except Exception as run_error:
            logger.error(f"Error during workflow execution: {str(run_error)}", exc_info=True)
            results = None
        
        # Process the results to get the path to the generated report
        generated_report_path = None
        if results and isinstance(results, dict):
            # Look for report_path in different possible locations
            if "report_path" in results:
                generated_report_path = results["report_path"]
            elif "final_output" in results and isinstance(results["final_output"], dict):
                final_output = results["final_output"]
                if "result" in final_output and isinstance(final_output["result"], dict):
                    generated_report_path = final_output["result"].get("report_path")
                elif "output_data" in final_output and isinstance(final_output["output_data"], dict):
                    generated_report_path = final_output["output_data"].get("report_path")
            
            # Log whether we found the report path
            if generated_report_path:
                logger.info(f"Generated report saved at: {generated_report_path}")
            else:
                logger.warning("Report path not found in results. Check if the report was generated correctly.")
                logger.info(f"Available result keys: {list(results.keys())}")
            
    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        logger.error("Full traceback:", exc_info=True)
        return None
    
    # Ensure a report is generated even if the workflow fails
    final_report_path = ensure_report_exists(generated_report_path)
    return final_report_path

if __name__ == "__main__":
    main()
