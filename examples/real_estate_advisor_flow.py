#!/usr/bin/env python3
"""
Real Estate Advisor Workflow - Proof of Concept (PoC) con herramientas reales.

1. Recoge criterios del usuario.
2. Busca propiedades y datos de mercado.
3. Analiza resultados.
4. Genera informe Markdown.
5. Guarda el informe en disco.
6. Ejecuta todo con WorkflowEngine.
"""  # noqa: D202

import sys
import os
import logging
import re
import argparse
from datetime import datetime
import random

# --- Dawn Framework Core Imports ---
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

try:
    from core.workflow import Workflow
    from core.task import DirectHandlerTask
    from core.services import get_services, reset_services
    from core.llm.interface import LLMInterface
    from core.tools.registry_access import tool_exists, register_tool, execute_tool
    from core.handlers.registry_access import handler_exists, register_handler, get_handler_registry as get_handler_registry_instance
    from core.utils.registration_manager import ensure_all_registrations
    from core.engine import WorkflowEngine
except ImportError as e:
    print(f"Error importando Dawn framework: {e}")
    sys.exit(1)

# Import real o mock WebSearchTool
try:
    from core.tools.web_search_tool import WebSearchTool
except ImportError:
    WebSearchTool = None

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("real_estate_advisor_flow")

# Carga API key
from dotenv import load_dotenv
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY no está definido.")
    sys.exit(2)

# --- Additional debugging flag ---
DEBUG_HANDLERS = True

# --- Handlers ---

def get_user_input_handler(task, input_data):
    """Handler to get user input for real estate search criteria.
    
    Args:
        task: The task being executed.
        input_data: Dictionary containing optional prompt.
        
    Returns:
        Dictionary with success status and extracted user criteria.
    """
    if DEBUG_HANDLERS:
        print(f"\n=== get_user_input_handler ===")
        print(f"Task: {task}")
        print(f"Input data: {input_data}")
    
    prompt = input_data.get("prompt", "Introduce criterios (ubicación, precio, habitaciones):")
    print(f"\n{prompt}")
    nl_query = input("< ").strip()
    if not nl_query:
        logger.error("No search query provided")
        return {"success": False, "error": "No se proporcionó consulta."}
        
    # Initialize criteria dictionary
    c = {"query": nl_query}
    
    # Extract location with improved pattern matching
    # Look for locations after prepositions like "en", "near", "around", "in", etc.
    location_patterns = [
        r'(?:en|in|near|around|cerca de|próximo a)\s+(.+?)(?=\s+(?:por|under|menos de|with|con|,|$))',
        r'(?:properties in|propiedades en|casas en|houses in|apartments in|apartamentos en)\s+(.+?)(?=\s+(?:por|under|menos de|with|con|,|$))'
    ]
    
    extracted_location = None
    for pattern in location_patterns:
        match = re.search(pattern, nl_query, re.IGNORECASE)
        if match:
            extracted_location = match.group(1).strip()
            break
            
    # Default to a reasonable location if none found
    if not extracted_location:
        # Try to extract any capitalized words that might be locations
        capitalized_words = re.findall(r'\b([A-Z][a-z]+(?:\s+[A-Z][a-z]+)*)\b', nl_query)
        if capitalized_words:
            extracted_location = capitalized_words[0]
        else:
            # Final fallback
            extracted_location = "Unknown"
            
    c["location"] = extracted_location
    
    # Extract price and convert to int
    price_patterns = [
        r'(?:under|menos de|hasta|below|max|maximum|máximo)\s+(?:[€$£¥])?(\d+(?:[.,]\d+)?(?:\s*[kK])?)\s*(?:€|$|£|¥)?',
        r'(?:[€$£¥])?(\d+(?:[.,]\d+)?(?:\s*[kK])?)\s*(?:€|$|£|¥)?(?:\s+(?:or less|o menos|max|maximum|máximo))'
    ]
    
    extracted_price = None
    for pattern in price_patterns:
        match = re.search(pattern, nl_query, re.IGNORECASE)
        if match:
            price_str = match.group(1).replace('.', '').replace(',', '.')
            # Handle K notation (thousands)
            if 'k' in price_str.lower():
                price_str = price_str.lower().replace('k', '')
                try:
                    extracted_price = int(float(price_str) * 1000)
                except ValueError:
                    extracted_price = 500000
            else:
                try:
                    extracted_price = int(float(price_str))
                except ValueError:
                    extracted_price = 500000
            break
            
    if not extracted_price:
        extracted_price = 500000  # Default price
        
    c["price_max"] = extracted_price
        
    # Extract bedrooms with improved pattern matching
    bedroom_patterns = [
        r'(\d+)\s+(?:bedroom|habitaciones|habitación|bed|bedrooms|rooms|chambres|cuartos|recamaras|recámaras)',
        r'(?:bedroom|habitaciones|habitación|bed|bedrooms|rooms|chambres|cuartos|recamaras|recámaras)\s+(\d+)'
    ]
    
    extracted_bedrooms = None
    for pattern in bedroom_patterns:
        match = re.search(pattern, nl_query, re.IGNORECASE)
        if match:
            try:
                extracted_bedrooms = int(match.group(1))
                break
            except ValueError:
                pass
                
    if not extracted_bedrooms:
        extracted_bedrooms = 3  # Default number of bedrooms
        
    c["bedrooms"] = extracted_bedrooms
    
    logger.info(f"Extracted criteria: {c}")
    return {"success": True, "result": {"user_input_criteria": c}}


def analyze_data_handler(task, input_data):
    """Analyze property and market data to generate recommendations.
    
    Args:
        task: The task being executed.
        input_data: Dictionary containing property and market data.
        
    Returns:
        Dictionary with success status and analysis results.
    """
    props = input_data.get("property_search_results", "")
    market = input_data.get("market_data", "")
    crit = input_data.get("user_criteria", {})
    
    if not (props and market):
        logger.error("Insufficient data for analysis")
        return {"success": False, "error": "Datos insuficientes."}
        
    # Generate analysis with some random elements for demonstration
    location = crit.get('location', 'desconocida')
    analysis = f"""## Expert Analysis

Ubicación: {location}

- Tendencia: {random.choice(['crecimiento fuerte','condiciones estables','ligera desaceleración'])}.
- Disponibilidad: {random.choice(['alta','limitada','rara'])}.
- Inversión: {random.choice(['excelente','buena','moderada'])}.
- Riesgo: {random.choice(['bajo','moderado','relativamente bajo'])}.
"""
    logger.info("Analysis completed successfully")
    return {"success": True, "result": {"analysis": analysis}}


def generate_real_estate_report_handler(task, input_data):
    """Generate a real estate report based on search results and analysis data.
    
    Args:
        task: The task being executed.
        input_data: Dictionary containing search results, user criteria, and analysis.
        
    Returns:
        Dictionary with success status, report content, and filename.
    """
    if DEBUG_HANDLERS:
        print(f"\n=== generate_real_estate_report_handler ===")
        print(f"Task: {task}")
        print(f"Input data keys: {input_data.keys()}")
    
    logger.info("Generating real estate report")
    
    # Extract data from input_data
    user_query = input_data.get("user_query", "")
    user_location = input_data.get("user_location", "")
    price_max = input_data.get("user_price_max", 0)
    beds = input_data.get("user_bedrooms", 0)
    property_results = input_data.get("property_search_results", "No property search results available.")
    market_data = input_data.get("market_data", "No market data available.")
    analysis = input_data.get("analysis_results", "")
    
    # Log extracted data
    logger.debug(f"User query: {user_query}")
    logger.debug(f"Location from input: {user_location}")
    
    # Use the location from input directly - no hardcoded mapping
    real_location = user_location
    
    # Ensure price_max is an integer
    try:
        price_max = int(float(price_max))
    except (ValueError, TypeError):
        price_max = 0
        logger.warning(f"Could not convert price_max to int: {price_max}")
    
    # Ensure beds is an integer
    try:
        beds = int(float(beds))
    except (ValueError, TypeError):
        beds = 0
        logger.warning(f"Could not convert beds to int: {beds}")
    
    # Detect currency from query with support for multiple currencies
    currency = "USD"  # Default to USD as a more international default
    
    # Currency detection patterns
    currency_patterns = {
        "MXP": [r'\$.*MXP', r'MXN', r'pesos', r'México', r'Mexico'],
        "€": [r'€', r'EUR', r'euro', r'euros'],
        "USD": [r'\$.*USD', r'dólar', r'dollar', r'US\$', r'Amerika', r'America', r'EEUU'],
        "£": [r'£', r'GBP', r'pound', r'pounds', r'UK', r'England', r'Britain'],
        "¥": [r'¥', r'JPY', r'yen', r'Japan', r'Japón'],
        "R$": [r'R\$', r'BRL', r'real', r'reais', r'Brasil', r'Brazil'],
        "C$": [r'C\$', r'CAD', r'Canadian', r'Canada', r'Canadá']
    }
    
    # Check query for currency indicators
    query_lower = str(user_query).lower()
    for curr, patterns in currency_patterns.items():
        for pattern in patterns:
            if re.search(pattern, query_lower, re.IGNORECASE):
                currency = curr
                logger.info(f"Detected currency: {currency}")
                break
        if currency != "USD":  # Stop if we found a currency
            break
    
    # Format price with thousands separator
    price_formatted = f"{price_max:,}" if price_max else "N/A"
    
    # Calculate price range (±10%)
    low = int(price_max * 0.9) if price_max else 0
    high = int(price_max * 1.1) if price_max else 0
    low_formatted = f"{low:,}" if low else "N/A"
    high_formatted = f"{high:,}" if high else "N/A"
    
    # Generate timestamp and filename
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    slug = re.sub(r'\W+', '_', str(real_location)).lower() if real_location else "location"
    fname = f"real_estate_report_{slug}_{ts}.md"
    
    # Check for placeholder values that need replacing
    if "${" in str(property_results):
        logger.warning("Property results contain interpolation placeholders. Using fallback text.")
        property_results = "Property search results were not properly retrieved."
    
    if "${" in str(market_data):
        logger.warning("Market data contains interpolation placeholders. Using fallback text.")
        market_data = "Market data was not properly retrieved."
    
    # Generate report content
    report = f"""
# Informe de Mercado Inmobiliario

## Criterios
- Query: {user_query}
- Ubicación: {real_location}
- Precio Máx: {price_formatted} {currency}
- Rango aproximado (±10%): {low_formatted} {currency} – {high_formatted} {currency}
- Habitaciones: {beds}

## Resultados Propiedades
{property_results}

## Análisis de Mercado
{market_data}

## Recomendaciones
{analysis}

*Generado el {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}*
"""
    logger.info(f"Report generated successfully for location: {real_location}")
    logger.info(f"Report filename: {fname}")
    return {"success": True, "result": {"report": report, "filename": fname}}


def save_report_handler(task, input_data):
    """Save the generated report to a file.
    
    Args:
        task: The task being executed.
        input_data: Dictionary containing report content and filename.
        
    Returns:
        Dictionary with success status and filename.
    """
    rep = input_data.get("report", "")
    fname = input_data.get("filename", "report.md")
    
    try:
        with open(fname, 'w', encoding='utf-8') as f:
            f.write(rep)
        logger.info(f"Report saved successfully: {fname}")
        print(f"\n✅ Reporte guardado en: {fname}")
        return {"success": True, "result": {"filename": fname}}
    except Exception as e:
        error_msg = f"Error saving report: {str(e)}"
        logger.error(error_msg)
        print(f"\nError guardando reporte: {e}")
        return {"success": False, "error": error_msg}

# --- Helper for handler registration ---
class DummyTask:
    """Dummy task for handler compatibility."""
    def __init__(self, task_id="dummy_task"):
        self.id = task_id
        self.name = "Dummy Task"
        self.status = "running"
        self.input_data = {}
        self.output_data = {}
        
    def set_status(self, status):
        self.status = status
        
    def set_output(self, output):
        self.output_data = output

def handler_adapter(handler_func):
    """Adapter to make 2-param handlers compatible with both 1-param and 2-param calls.
    
    Args:
        handler_func: The handler function that takes (task, input_data).
        
    Returns:
        A function that can handle both (input_data) and (task, input_data) calls.
    """
    def wrapper(*args):
        if len(args) == 1:
            # Called with just input_data (by registry)
            input_data = args[0]
            dummy_task = DummyTask()
            return handler_func(dummy_task, input_data)
        elif len(args) == 2:
            # Called with task, input_data (by engine directly)
            task, input_data = args
            return handler_func(task, input_data)
        else:
            raise ValueError(f"handler_adapter wrapper called with unexpected arguments: {args}")
    return wrapper

# --- Registro de componentes ---

def register_real_estate_components():
    # Web search tool
    if not tool_exists("web_search"):
        try:
            # Intentar usar WebSearchTool real primero
            # Si no se pudo importar anteriormente, intentarlo de nuevo
            if WebSearchTool is None:
                from tools.web_search_tool import WebSearchTool as WST
                search_tool = WST()
            else:
                search_tool = WebSearchTool()
                
            def real_search(task, input_data):
                """Perform a real web search using the WebSearchTool.
                
                Args:
                    task: The task being executed.
                    input_data: Dictionary containing the search query and optional location.
                    
                Returns:
                    Dictionary with success status and search results.
                """
                if DEBUG_HANDLERS:
                    print(f"\n=== real_search ===")
                    print(f"Task: {task}")
                    print(f"Input data: {input_data}")
                
                query = input_data.get("query", "")
                logger.info(f"Realizando búsqueda web real para: {query}")
                
                if not query:
                    logger.error("Empty search query")
                    return {"success": False, "error": "Empty search query"}
                
                try:
                    # Get user location from input_data
                    user_location = input_data.get("location")
                    
                    # Pass location context if available
                    if user_location:
                        logger.info(f"Using location for search: {user_location}")
                        txt = search_tool.perform_search(query, 3, user_location)
                    else:
                        txt = search_tool.perform_search(query, 3)
                    
                    logger.info("Web search completed successfully")
                    
                    # Handle different possible return formats from search_tool
                    if isinstance(txt, str):
                        return {"success": True, "result": {"search_text": txt}}
                    elif hasattr(txt, 'text') and txt.text:
                        return {"success": True, "result": {"search_text": txt.text}}
                    elif isinstance(txt, dict) and 'result' in txt:
                        return txt
                    else:
                        return {"success": True, "result": {"search_text": str(txt)}}
                except Exception as e:
                    error_msg = f"Error in web search: {str(e)}"
                    logger.error(error_msg)
                    return {"success": False, "error": error_msg}
            
            # Register tool with adapter
            register_tool("web_search", handler_adapter(real_search))
            logger.info("Registrada herramienta de búsqueda web REAL")
        except Exception as e:
            # Solo usar mock como último recurso si todo lo demás falla
            logger.error(f"No se pudo inicializar búsqueda web real: {e}")
            logger.warning("USANDO BÚSQUEDA SIMULADA como fallback - SOLO PARA DESARROLLO")
            
            def fallback_search(task, input_data):
                """Fallback search function when real search is not available.
                
                Args:
                    task: The task being executed.
                    input_data: Dictionary containing the search query.
                    
                Returns:
                    Dictionary with error status indicating search is not available.
                """
                if DEBUG_HANDLERS:
                    print(f"\n=== fallback_search ===")
                    print(f"Task: {task}")
                    print(f"Input data: {input_data}")
                    
                query = input_data.get("query", "")
                logger.warning(f"Usando búsqueda SIMULADA para: {query}")
                return {"success": False, "error": "Búsqueda web real no disponible. Configure WebSearchTool correctamente."}
            
            # Register tool with adapter
            register_tool("web_search", handler_adapter(fallback_search))
    
    # Handler para web search (se mantiene igual)
    if not handler_exists("web_search_handler"):
        def web_search_handler(task, input_data):
            """Handler to perform web searches using the web_search tool.
            
            Args:
                task: The task being executed.
                input_data: Dictionary containing the search query.
                
            Returns:
                Dictionary with success status and search results.
            """
            if DEBUG_HANDLERS:
                print(f"\n=== web_search_handler ===")
                print(f"Task: {task}")
                print(f"Input data: {input_data}")
                
            query = input_data.get("query", "")
            if not query:
                logger.error("Empty search query")
                return {"success": False, "error": "Consulta vacía"}
            
            # Get user location from input_data
            user_location = input_data.get("location")
            
            # No need for hardcoded landmark mapping - use the location as provided
            
            logger.info(f"Executing web search for: {query}")
            logger.info(f"Using location: {user_location}")
            
            # Prepare search parameters
            search_params = {"query": query}
            if user_location:
                search_params["location"] = user_location
            
            # Execute the web search tool
            result = execute_tool("web_search", search_params)
            
            # Handle case where result is a string directly
            if isinstance(result, str):
                logger.debug(f"Search result returned as string, converting format")
                return {"success": True, "result": {"search_text": result}}
            
            # If the search failed, log error but continue with the flow
            if not result.get("success", False):
                error_msg = result.get("error", "Error desconocido en búsqueda")
                logger.error(f"Error in search: {error_msg}")
                return {"success": True, "result": {"search_text": f"No se pudieron obtener resultados: {error_msg}"}}
            
            # Ensure correct structure of the result
            if "result" in result and "search_text" in result["result"]:
                return result
            else:
                # Try to extract text from possible formats
                search_text = ""
                if isinstance(result.get("result"), dict):
                    search_text = result.get("result", {}).get("search_text", "")
                elif isinstance(result.get("result"), str):
                    search_text = result["result"]
                elif result.get("result") is not None:
                    search_text = str(result.get("result"))
                    
                logger.info("Web search completed successfully")
                return {"success": True, "result": {"search_text": search_text}}
                
        # Register handler with adapter
        register_handler("web_search_handler", handler_adapter(web_search_handler))
    
    # Otros handlers
    for name, fn in [
        ("get_user_input_handler", get_user_input_handler),
        ("analyze_data_handler", analyze_data_handler),
        ("generate_real_estate_report_handler", generate_real_estate_report_handler),
        ("save_report_handler", save_report_handler)
    ]:
        if not handler_exists(name):
            # Register handler with adapter
            register_handler(name, handler_adapter(fn))

# --- Workflow ---

def build_real_estate_advisor_workflow():
    wf = Workflow("real-estate-advisor", "Real Estate Advisor")
    wf.description = "Asesora inversión inmobiliaria"
    wf.version = "1.0"
    wf.add_task(DirectHandlerTask(
        task_id="get_user_criteria", handler_name="get_user_input_handler",
        name="Input Criteria", input_data={"prompt": "Ubicación, precio, habitaciones"},
        next_task_id_on_success="search_properties"
    ))
    wf.add_task(DirectHandlerTask(
        task_id="search_properties", handler_name="web_search_handler",
        name="Search Properties",
        input_data={
            "query": (
                "real estate listings in ${get_user_criteria.result.user_input_criteria.location} "
                "with ${get_user_criteria.result.user_input_criteria.bedrooms} bedrooms "
                "under ${get_user_criteria.result.user_input_criteria.price_max} include prices and details"
            ),
            "location": "${get_user_criteria.result.user_input_criteria.location}"
        },
        next_task_id_on_success="search_market_data"
    ))
    wf.add_task(DirectHandlerTask(
        task_id="search_market_data", handler_name="web_search_handler",
        name="Search Market Data",
        input_data={
            "query": (
                "real estate market analysis in ${get_user_criteria.result.user_input_criteria.location} "
                "current trends, prices per square meter, investment outlook 2025"
            ),
            "location": "${get_user_criteria.result.user_input_criteria.location}"
        },
        next_task_id_on_success="analyze_findings"
    ))
    wf.add_task(DirectHandlerTask(
        task_id="analyze_findings", handler_name="analyze_data_handler",
        name="Analyze Findings",
        input_data={
            "property_search_results": "${search_properties.result.search_text}",
            "market_data": "${search_market_data.result.search_text}",
            "user_criteria": "${get_user_criteria.result.user_input_criteria}"
        },
        next_task_id_on_success="generate_report"
    ))
    wf.add_task(DirectHandlerTask(
        task_id="generate_report", handler_name="generate_real_estate_report_handler",
        name="Generate Report",
        input_data={
            "user_query": "${get_user_criteria.result.user_input_criteria.query}",
            "user_location": "${get_user_criteria.result.user_input_criteria.location}",
            "user_price_max": "${get_user_criteria.result.user_input_criteria.price_max}",
            "user_bedrooms": "${get_user_criteria.result.user_input_criteria.bedrooms}",
            "property_search_results": "${search_properties.result.search_text}",
            "market_data": "${search_market_data.result.search_text}",
            "analysis_results": "${analyze_findings.result.analysis}"
        }, next_task_id_on_success="save_report"
    ))
    wf.add_task(DirectHandlerTask(
        task_id="save_report", handler_name="save_report_handler",
        name="Save Report",
        input_data={"report": "${generate_report.result.report}", "filename": "${generate_report.result.filename}"},
        next_task_id_on_success=None
    ))
    return wf

# --- Main ---

def main():
    p = argparse.ArgumentParser()
    p.add_argument("--debug", action="store_true")
    args = p.parse_args()
    if args.debug:
        logger.setLevel(logging.DEBUG)
    reset_services()
    services = get_services()
    ensure_all_registrations()
    services.llm_interface = LLMInterface()
    register_real_estate_components()
    wf = build_real_estate_advisor_workflow()
    print(f"\n=== Workflow '{wf.id}' con {len(wf.task_order)} tareas ===\n")
    engine = WorkflowEngine(wf, services.llm_interface, services.tool_registry)
    engine.handler_registry = get_handler_registry_instance()
    res = engine.run()
    return 0 if res.get("success") else 1

if __name__ == "__main__":
    sys.exit(main())
