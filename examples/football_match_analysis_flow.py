#!/usr/bin/env python3
"""
Football Match Analysis Workflow

1. Collects user input about which match(es) to analyze
2. Searches for comprehensive match data through multiple web searches
3. Analyzes collected data to generate insights
4. Creates a detailed markdown report
5. Saves the report to disk
6. Generates a workflow visualization diagram
"""  # noqa: D202

import sys
import os
import logging
import re
import argparse
from datetime import datetime
from pathlib import Path

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
    print(f"Error importing Dawn framework: {e}")
    sys.exit(1)

# Import real or mock WebSearchTool
try:
    from tools.web_search_tool import WebSearchTool
except ImportError:
    try:
        from core.tools.web_search_tool import WebSearchTool
    except ImportError:
        WebSearchTool = None

# Visualization imports
import matplotlib.pyplot as plt
import networkx as nx

# --- Logging ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger("football_match_analysis_flow")

# Load API key
from dotenv import load_dotenv
load_dotenv()
if not os.getenv("OPENAI_API_KEY"):
    logger.error("OPENAI_API_KEY is not defined.")
    sys.exit(2)

# --- Debug flag ---
DEBUG_HANDLERS = True 

# Función para depurar variables
def debug_variables(task, prefix=""):
    if hasattr(task, 'workflow') and task.workflow:
        vars_dict = getattr(task.workflow, 'variables', {})
        logger.debug(f"{prefix} Workflow variables: {vars_dict}")

# SOLUCIÓN: Mejora en el decorador para resolver y propagar variables
def resolve_and_propagate(fn):
    """
    Decorador mejorado que:
    1. Resuelve referencias de variables entre tareas
    2. Propaga los resultados al objeto workflow
    3. Guarda variables tanto con prefijo de tarea como sin él
    """
    def wrapper(task, input_data):
        # Preparar variables del workflow
        workflow_vars = {}
        if hasattr(task, "workflow") and task.workflow:
            workflow_vars = task.workflow.variables
            logger.debug(f"WRAP[{task.id}] Initial workflow vars keys: {list(workflow_vars.keys())}")

        # SOLUCIÓN: Mejorar la resolución de variables
        resolved = {}
        for key, val in input_data.items():
            if isinstance(val, str) and val.startswith("${") and val.endswith("}"):
                ref = val[2:-1].strip()
                # Probar con la referencia exacta primero
                if ref in workflow_vars:
                    resolved[key] = workflow_vars[ref]
                    logger.debug(f"Resolved '{ref}' → '{resolved[key]}'")
                else:
                    # Intentar con diferentes formatos de clave
                    parts = ref.split(".")
                    if len(parts) > 1:
                        # Buscar solo la clave base (última parte)
                        base = parts[-1]
                        if base in workflow_vars:
                            resolved[key] = workflow_vars[base]
                            logger.debug(f"Resolved base '{base}' → '{resolved[key]}'")
                        # Buscar con el prefijo de task_id (primera parte)
                        elif f"{parts[0]}.{base}" in workflow_vars:
                            resolved[key] = workflow_vars[f"{parts[0]}.{base}"]
                            logger.debug(f"Resolved with prefix '{parts[0]}.{base}' → '{resolved[key]}'")
                        else:
                            # Si no encuentra, usar valor vacío
                            resolved[key] = ""
                            logger.debug(f"Could not resolve '{ref}', using empty string")
                    else:
                        # Si no encuentra y no tiene partes, usar valor vacío
                        resolved[key] = ""
                        logger.debug(f"Could not resolve '{ref}', using empty string")
            else:
                resolved[key] = val

        logger.debug(f"WRAP[{task.id}] Resolved input: {resolved}")

        # Ejecutar el handler con las variables resueltas
        result = fn(task, resolved)
        logger.debug(f"WRAP[{task.id}] Handler result keys: {list(result.keys())}")

        # SOLUCIÓN: Propagar resultados de manera consistente
        if result.get("success") and hasattr(task, "workflow") and task.workflow:
            logger.debug(f"WRAP[{task.id}] Propagating to workflow variables")
            for k, v in result.items():
                if k in ("success", "error"): 
                    continue
                    
                # Guardar la variable sin prefijo
                task.workflow.variables[k] = v
                
                # Guardar también con el prefijo de task_id
                task.workflow.variables[f"{task.id}.{k}"] = v
                
                logger.debug(f"WRAP[{task.id}] Set var '{k}' and '{task.id}.{k}'")
            
            # Imprimir todas las variables después de la modificación
            logger.debug(f"WRAP[{task.id}] After handler - workflow vars keys: {list(task.workflow.variables.keys())}")
        
        return result
    return wrapper

# Para mantener compatibilidad
record_and_propagate = resolve_and_propagate
propagate_outputs = resolve_and_propagate

# --- DummyTask for adapter ---
class DummyTask:
    def __init__(self, task_id="dummy_task"):
        self.id = task_id
        self.name = "Dummy Task"
        self.status = "running"
        self.input_data = {}
        self.output_data = {}
        self.workflow = None
    def set_status(self, status): self.status = status
    def set_output(self, output): self.output_data = output

@record_and_propagate
def simple_get_user_input_handler(task, input_data):
    """Handler to process user input for match analysis."""
    logger.info("Processing user input")
    debug_variables(task, "BEFORE INPUT PROCESSING")
    
    # Get or confirm the required fields
    home_team = input_data.get('home_team', '')
    away_team = input_data.get('away_team', '')
    match_date = input_data.get('match_date', datetime.now().strftime("%Y-%m-%d"))
    league = input_data.get('league', '')
    analysis_depth = input_data.get('analysis_depth', 'standard')
    
    # Create match title
    match_title = f"{home_team} vs {away_team}"
    if league:
        match_title += f" ({league})"
    
    # Validate required fields
    if not home_team or not away_team:
        return {"success": False, "error": "Home team and away team are required"}
    
    return {
        "success": True,
        "home_team": home_team,
        "away_team": away_team,
        "match_date": match_date,
        "league": league,
        "analysis_depth": analysis_depth,
        "match_title": match_title
    }

@record_and_propagate
def search_team_form_handler(task, input_data):
    """Handler to fetch team form information."""
    logger.info("Searching for team form data")
    debug_variables(task, "BEFORE TEAM FORM SEARCH")
    
    home_team = input_data.get('home_team', '')
    away_team = input_data.get('away_team', '')
    
    # In a real implementation, you might use the web search tool to get this data
    # For now, we'll use placeholder data
    home_team_form = "W W L D W"  # Example form data
    away_team_form = "L W W D D"  # Example form data
    
    return {
        "success": True,
        "home_team_form": f"Recent form (last 5 matches): {home_team_form}",
        "away_team_form": f"Recent form (last 5 matches): {away_team_form}"
    }

@record_and_propagate
def search_head_to_head_handler(task, input_data):
    """Handler to fetch head-to-head history between teams."""
    logger.info("Searching for head-to-head history")
    debug_variables(task, "BEFORE H2H SEARCH")
    
    home_team = input_data.get('home_team', '')
    away_team = input_data.get('away_team', '')
    
    # In a real implementation, you might use the web search tool to get this data
    # For now, we'll use placeholder data
    h2h_summary = f"{home_team} has won 3 times, {away_team} has won 2 times, with 1 draw"
    
    return {
        "success": True,
        "head_to_head": h2h_summary
    }

@record_and_propagate
def search_league_position_handler(task, input_data):
    """Handler to fetch league position information."""
    logger.info("Searching for league position data")
    debug_variables(task, "BEFORE LEAGUE POSITION SEARCH")
    
    home_team = input_data.get('home_team', '')
    away_team = input_data.get('away_team', '')
    league = input_data.get('league', 'Unknown League')
    
    # In a real implementation, you might use the web search tool to get this data
    # For now, we'll use placeholder data
    home_position = "4th"
    away_position = "7th"
    
    return {
        "success": True,
        "league_positions": f"{home_team} is currently {home_position} in {league}, while {away_team} is {away_position}"
    }

@record_and_propagate
def search_team_stats_handler(task, input_data):
    """Handler to fetch team statistics."""
    logger.info("Searching for team statistics")
    debug_variables(task, "BEFORE TEAM STATS SEARCH")
    
    home_team = input_data.get('home_team', '')
    away_team = input_data.get('away_team', '')
    
    # In a real implementation, you might use the web search tool to get this data
    # For now, we'll use placeholder data
    home_stats = "Goals scored: 24, Goals conceded: 12, Clean sheets: 5"
    away_stats = "Goals scored: 18, Goals conceded: 20, Clean sheets: 3"
    
    return {
        "success": True,
        "home_team_stats": f"{home_team} stats: {home_stats}",
        "away_team_stats": f"{away_team} stats: {away_stats}"
    }

@record_and_propagate
def search_player_info_handler(task, input_data):
    """Handler to fetch information about key players and injuries."""
    logger.info("Searching for player information")
    debug_variables(task, "BEFORE PLAYER INFO SEARCH")
    
    home_team = input_data.get('home_team', '')
    away_team = input_data.get('away_team', '')
    
    # In a real implementation, you might use the web search tool to get this data
    # For now, we'll use placeholder data
    players_info = f"{home_team} missing 2 key players through injury. {away_team} has a full squad available."
    
    return {
        "success": True,
        "player_info": players_info
    }

@record_and_propagate
def search_contextual_factors_handler(task, input_data):
    """Handler to fetch contextual factors like weather and pitch conditions."""
    logger.info("Searching for contextual factors")
    debug_variables(task, "BEFORE CONTEXTUAL FACTORS SEARCH")
    
    home_team = input_data.get('home_team', '')
    away_team = input_data.get('away_team', '')
    match_date = input_data.get('match_date', '')
    
    # In a real implementation, you might use the web search tool to get this data
    # For now, we'll use placeholder data
    contextual_data = f"Weather forecast for match day: Clear skies, 22°C. Pitch in excellent condition."
    
    return {
        "success": True,
        "contextual_factors": contextual_data
    }

@record_and_propagate
def search_betting_info_handler(task, input_data):
    """Handler to fetch betting odds and predictions."""
    logger.info("Searching for betting information")
    debug_variables(task, "BEFORE BETTING INFO SEARCH")
    
    home_team = input_data.get('home_team', '')
    away_team = input_data.get('away_team', '')
    
    # In a real implementation, you might use the web search tool to get this data
    # For now, we'll use placeholder data
    betting_data = f"Odds: {home_team} win: 2.10, Draw: 3.40, {away_team} win: 3.80"
    
    return {
        "success": True,
        "betting_info": betting_data
    }

@record_and_propagate
def generate_analysis_handler(task, input_data):
    """Handler to generate a comprehensive match analysis report."""
    logger.info("Generating match analysis report")
    debug_variables(task, "BEFORE ANALYSIS GENERATION")
    
    # Get essential data from input
    home_team = input_data.get('home_team', '')
    away_team = input_data.get('away_team', '')
    match_date = input_data.get('match_date', '')
    league = input_data.get('league', '')
    match_title = input_data.get('match_title', f"{home_team} vs {away_team}")
    
    # Get analysis components
    home_team_form = input_data.get('home_team_form', 'No form data available')
    away_team_form = input_data.get('away_team_form', 'No form data available')
    head_to_head = input_data.get('head_to_head', 'No head-to-head data available')
    league_positions = input_data.get('league_positions', 'No league position data available')
    home_team_stats = input_data.get('home_team_stats', 'No home team stats available')
    away_team_stats = input_data.get('away_team_stats', 'No away team stats available')
    player_info = input_data.get('player_info', 'No player information available')
    contextual_factors = input_data.get('contextual_factors', 'No contextual factors available')
    betting_info = input_data.get('betting_info', 'No betting information available')
    
    # DEBUGGING: Imprimir valores obtenidos para verificar
    logger.debug(f"Analysis inputs: home_team_form={home_team_form[:30]}...")
    logger.debug(f"Analysis inputs: away_team_form={away_team_form[:30]}...")
    logger.debug(f"Analysis inputs: head_to_head={head_to_head[:30]}...")
    
    # Generate report content
    report_content = f"""# Match Analysis: {match_title}
    
## Match Overview
- **Home Team**: {home_team}
- **Away Team**: {away_team}
- **Date**: {match_date}
- **League**: {league}

## Team Form
### {home_team} Form
{home_team_form}

### {away_team} Form
{away_team_form}

## Head-to-Head History
{head_to_head}

## League Positions
{league_positions}

## Team Statistics
### {home_team}
{home_team_stats}

### {away_team}
{away_team_stats}

## Key Players & Injuries
{player_info}

## Contextual Factors
{contextual_factors}

## Betting Analysis
{betting_info}

## Conclusion
Based on all available data, this match is expected to be competitive with a slight advantage for {home_team if "3" not in home_team_form else away_team}.

---
Analysis generated: {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
"""
    
    # Create report directory if it doesn't exist
    reports_dir = Path("reports")
    reports_dir.mkdir(exist_ok=True)
    
    # Get the absolute path to the report directory
    abs_reports_dir = reports_dir.absolute()
    
    # Save report to file
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    safe_title = re.sub(r'[^\w\-_]', '_', match_title)
    filename = f"match_analysis_{safe_title}_{timestamp}.md"
    filepath = abs_reports_dir / filename
    
    try:
        with open(filepath, 'w') as f:
            f.write(report_content)
        logger.info(f"Analysis saved to {filepath}")
    except Exception as e:
        logger.error(f"Failed to save analysis: {e}")
        return {
            "success": False,
            "error": f"Failed to save analysis: {str(e)}"
        }
    
    # Verificar que la ruta existe
    if not os.path.exists(filepath):
        logger.warning(f"Generated file not found: {filepath}")
    else:
        logger.info(f"Confirmed file exists: {filepath}")
    
    # Convertir a string para el retorno
    str_filepath = str(filepath)
    
    # Imprimir la ruta completa para verificación
    print(f"REPORT PATH: {str_filepath}")
    
    return {
        "success": True,
        "report_path": str_filepath,
        "report_content": report_content
    }

@record_and_propagate
def visualize_workflow_handler(task, input_data):
    """Handler to create a visualization of the workflow execution."""
    logger.info("Visualizing workflow execution")
    debug_variables(task, "BEFORE VISUALIZATION")
    
    # Get workflow reference if available
    workflow = None
    if hasattr(task, 'workflow'):
        workflow = task.workflow
    
    if not workflow:
        return {
            "success": False,
            "error": "No workflow reference available for visualization"
        }
    
    try:
        # Create a directed graph
        G = nx.DiGraph()
        
        # Add nodes for each task in the workflow
        for task_id, task_obj in workflow.tasks.items():
            G.add_node(task_id, label=task_obj.name)
            
            # Add edges based on next_task_id relationships
            if hasattr(task_obj, 'next_task_id_on_success') and task_obj.next_task_id_on_success:
                G.add_edge(task_id, task_obj.next_task_id_on_success)
        
        # Create visualization directory if it doesn't exist
        viz_dir = Path("visualizations")
        viz_dir.mkdir(exist_ok=True)
        
        # Get absolute path
        abs_viz_dir = viz_dir.absolute()
        
        # Generate filename
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"workflow_visualization_{timestamp}.png"
        filepath = abs_viz_dir / filename
        
        # Set up plot
        plt.figure(figsize=(12, 8))
        pos = nx.spring_layout(G, seed=42)
        
        # Draw the graph
        nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=3000, alpha=0.8)
        nx.draw_networkx_edges(G, pos, width=2, alpha=0.7, edge_color='gray', arrows=True)
        nx.draw_networkx_labels(G, pos, font_size=10, font_family='sans-serif')
        
        # Add title and save
        plt.title(f"{workflow.name} - Workflow Visualization")
        plt.axis('off')
        plt.tight_layout()
        plt.savefig(filepath, dpi=300, bbox_inches='tight')
        plt.close()
        
        # Convert to string
        str_filepath = str(filepath)
        
        # Verify file exists
        if not os.path.exists(filepath):
            logger.warning(f"Generated visualization file not found: {filepath}")
        else:
            logger.info(f"Confirmed visualization file exists: {filepath}")
        
        # Print path for debugging
        print(f"VISUALIZATION PATH: {str_filepath}")
        
        logger.info(f"Workflow visualization saved to {str_filepath}")
        
        return {
            "success": True,
            "visualization_path": str_filepath
        }
    except Exception as e:
        logger.error(f"Failed to create visualization: {e}")
        return {
            "success": False,
            "error": f"Failed to create visualization: {str(e)}"
        }

def build_football_match_analysis_workflow():
    wf = Workflow("football-match-analysis", "Football Match Analysis")
    wf.description = "Comprehensive football match analysis"
    wf.version = "1.0"
    
    # SOLUCIÓN: Mejorar input_data - usar referencias más simples
    wf.add_task(DirectHandlerTask(
        task_id="get_user_input", 
        handler_name="get_user_input_handler",
        name="Get User Input", 
        input_data={
            "home_team":"${home_team:}",
            "away_team":"${away_team:}",
            "match_date":"${match_date:}",
            "league":"${league:}",
            "analysis_depth":"${analysis_depth:standard}"
        },
        next_task_id_on_success="search_team_form"
    ))
    
    wf.add_task(DirectHandlerTask(
        task_id="search_team_form", 
        handler_name="search_team_form_handler",
        name="Search Team Form", 
        input_data={
            "home_team":"${home_team}",
            "away_team":"${away_team}"
        },
        next_task_id_on_success="search_head_to_head"
    ))
    
    wf.add_task(DirectHandlerTask(
        task_id="search_head_to_head", 
        handler_name="search_head_to_head_handler",
        name="Search Head-to-Head", 
        input_data={
            "home_team":"${home_team}",
            "away_team":"${away_team}"
        },
        next_task_id_on_success="search_league_position"
    ))
    
    wf.add_task(DirectHandlerTask(
        task_id="search_league_position", 
        handler_name="search_league_position_handler",
        name="Search League Position", 
        input_data={
            "home_team":"${home_team}",
            "away_team":"${away_team}",
            "league":"${league}"
        },
        next_task_id_on_success="search_team_stats"
    ))
    
    wf.add_task(DirectHandlerTask(
        task_id="search_team_stats", 
        handler_name="search_team_stats_handler",
        name="Search Team Stats", 
        input_data={
            "home_team":"${home_team}",
            "away_team":"${away_team}"
        },
        next_task_id_on_success="search_player_info"
    ))
    
    wf.add_task(DirectHandlerTask(
        task_id="search_player_info", 
        handler_name="search_player_info_handler",
        name="Search Player Info", 
        input_data={
            "home_team":"${home_team}",
            "away_team":"${away_team}"
        },
        next_task_id_on_success="search_contextual_factors"
    ))
    
    wf.add_task(DirectHandlerTask(
        task_id="search_contextual_factors", 
        handler_name="search_contextual_factors_handler",
        name="Search Contextual Factors", 
        input_data={
            "home_team":"${home_team}",
            "away_team":"${away_team}",
            "match_date":"${match_date}"
        },
        next_task_id_on_success="search_betting_info"
    ))
    
    wf.add_task(DirectHandlerTask(
        task_id="search_betting_info", 
        handler_name="search_betting_info_handler",
        name="Search Betting Info", 
        input_data={
            "home_team":"${home_team}",
            "away_team":"${away_team}",
            "match_date":"${match_date}"
        },
        next_task_id_on_success="generate_analysis"
    ))
    
    # SOLUCIÓN: Usar claves sin prefijo para `generate_analysis`
    wf.add_task(DirectHandlerTask(
        task_id="generate_analysis",
        handler_name="generate_analysis_handler",
        name="Generate Match Analysis",
        input_data={
            "home_team": "${home_team}",
            "away_team": "${away_team}",
            "match_date": "${match_date}",
            "league": "${league}",
            "match_title": "${match_title}",
            "home_team_form": "${home_team_form}",
            "away_team_form": "${away_team_form}",
            "head_to_head": "${head_to_head}",
            "league_positions": "${league_positions}",
            "home_team_stats": "${home_team_stats}",
            "away_team_stats": "${away_team_stats}",
            "player_info": "${player_info}",
            "contextual_factors": "${contextual_factors}",
            "betting_info": "${betting_info}"
        },
        next_task_id_on_success="visualize_workflow"
    ))
    
    wf.add_task(DirectHandlerTask(
        task_id="visualize_workflow", 
        handler_name="visualize_workflow_handler",
        name="Visualize Workflow", 
        input_data={},
        next_task_id_on_success=None
    ))
    
    # Important: Set workflow reference on each task
    for task in wf.tasks.values():
        task.workflow = wf
        # Ensure the task also has an ID
        if not hasattr(task, 'id'):
            task.id = task.task_id
        logger.debug(f"Initialized task {task.id} with workflow reference")
    
    # Initialize workflow variables
    if not hasattr(wf, 'variables'):
        wf.variables = {}
    
    logger.debug(f"Initialized workflow with {len(wf.tasks)} tasks")
    
    return wf

def get_var(workflow_vars, input_data, keys, default=""):
    """Try multiple keys in workflow_vars, then input_data, with fallback to default"""
    if not isinstance(keys, list):
        keys = [keys]
    for k in keys:
        if k in workflow_vars:
            return workflow_vars[k]
    if isinstance(input_data, dict):
        for k in keys:
            if k in input_data:
                return input_data[k]
    return default

# --- Register handlers with simple direct handler ---
def register_handlers():
    # Simple handlers for data input and collection
    register_handler("get_user_input_handler", simple_get_user_input_handler)
    
    # Search handlers
    register_handler("search_team_form_handler", search_team_form_handler)
    register_handler("search_head_to_head_handler", search_head_to_head_handler)
    register_handler("search_league_position_handler", search_league_position_handler)
    register_handler("search_team_stats_handler", search_team_stats_handler)
    register_handler("search_player_info_handler", search_player_info_handler)
    register_handler("search_contextual_factors_handler", search_contextual_factors_handler)
    register_handler("search_betting_info_handler", search_betting_info_handler)
    
    # Analysis and visualization handlers
    register_handler("generate_analysis_handler", generate_analysis_handler)
    register_handler("visualize_workflow_handler", visualize_workflow_handler)

# --- Main ---
# --- Main ---
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--debug", action="store_true", help="Enable debug logging")
    parser.add_argument("--home_team", help="Name of the home team")
    parser.add_argument("--away_team", help="Name of the away team")
    parser.add_argument("--league", help="League name")
    parser.add_argument("--match_date", help="Match date in YYYY-MM-DD format")
    parser.add_argument("-i", "--interactive", action="store_true", help="Prompt for input interactively")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed output")
    args = parser.parse_args()

    if args.debug or args.verbose:
        logger.setLevel(logging.DEBUG)
        logging.getLogger().setLevel(logging.DEBUG)
        logger.debug("Debug logging enabled")
    
    # Reset services
    reset_services()
    services = get_services()
    ensure_all_registrations()
    
    # Create LLM interface
    services.llm_interface = LLMInterface()
    
    # Make sure handler registry exists and is accessible
    try:
        from core.handlers.registry import HandlerRegistry
        from core.handlers.registry_access import reset_handler_registry
        
        # Reset and get a clean handler registry
        reset_handler_registry()
        handler_registry = get_handler_registry_instance()
        
        # Add it to services if possible
        if hasattr(services, 'set_service'):
            services.set_service('handler_registry', handler_registry)
        
        logger.info(f"Created fresh handler registry: {id(handler_registry)}")
    except ImportError as e:
        logger.warning(f"Could not properly set up handler registry: {e}")
        handler_registry = None

    # Register handlers
    register_handlers()
    
    # Build workflow
    wf = build_football_match_analysis_workflow()
    print(f"\n=== Workflow '{wf.id}' with {len(wf.task_order)} tasks ===\n")
    
    # Get input data
    data = {}
    if args.interactive or not (args.home_team and args.away_team):
        # Interactive mode - prompt for input
        data = {
            'home_team': input("Home Team: ") or "Default Home",
            'away_team': input("Away Team: ") or "Default Away",
            'match_date': input("Match Date [YYYY-MM-DD]: ") or datetime.now().strftime("%Y-%m-%d"),
            'league': input("League: ") or "",
            'analysis_depth': input("Analysis Depth [standard/comprehensive]: ") or 'standard'
        }
    else:
        # Use command line arguments
        data = {
            'home_team': args.home_team or "Default Home",
            'away_team': args.away_team or "Default Away",
            'match_date': args.match_date or datetime.now().strftime("%Y-%m-%d"),
            'league': args.league or "",
            'analysis_depth': 'comprehensive'
        }

    # Create match title
    match_title = f"{data['home_team']} vs {data['away_team']}"
    if data['league']:
        match_title += f" ({data['league']})"
    data['match_title'] = match_title
    
    # Initialize workflow variables directly
    logger.debug(f"Setting initial variables: {data.keys()}")
    
    # Set variables with and without prefixes to ensure availability
    for key, value in data.items():
        # Direct variables
        wf.variables[key] = value
        # Also with get_user_input prefix for first task
        wf.variables[f"get_user_input.{key}"] = value
        logger.debug(f"Set initial variable: {key} = {value}")
        logger.debug(f"Set initial variable: get_user_input.{key} = {value}")
    
    # Verify variables are set
    if args.verbose or args.debug:
        logger.debug(f"Initial workflow variables: {wf.variables}")
    
    # Print summary
    print("\nAnalyzing match:")
    print(f"Teams: {data['home_team']} vs {data['away_team']}")
    print(f"League: {data['league'] or 'Not specified'}")
    print(f"Date: {data['match_date']}")
    print()
    
    if args.verbose:
        print(f"Workflow variables: {wf.variables}")
    
    # Initialize workflow engine with handler registry
    engine = WorkflowEngine(wf, services.llm_interface, services.tool_registry)
    
    # Set handler registry explicitly
    if handler_registry:
        engine.handler_registry = handler_registry
        
        # Verify handler registry has our handlers
        handler_names = handler_registry.list_handlers() if hasattr(handler_registry, 'list_handlers') else []
        logger.info(f"Handler registry contains {len(handler_names)} handlers: {handler_names}")
    else:
        logger.warning("No handler registry available, workflow may fail")
    
    # Run workflow with initial data
    res = engine.run(data)

    # Process results
    if res.get("success"):
        print("\n✅ Match analysis completed successfully!")
        
        # Obtener ruta del análisis
        analysis_path = None
        
        # Intentar obtener la ruta del reporte directamente de las variables del workflow
        if hasattr(wf, 'variables') and 'report_path' in wf.variables:
            analysis_path = wf.variables['report_path']
        
        # Si no está en variables, buscar en las tareas completadas
        if not analysis_path:
            generate_task = res.get("tasks", {}).get("generate_analysis", {})
            if generate_task and isinstance(generate_task, dict):
                output_data = generate_task.get("output_data", {})
                analysis_path = output_data.get("report_path", "No report path available")
        
        print(f"📝 Analysis saved: {analysis_path}")
        
        # Obtener ruta de la visualización
        viz_path = None
        
        # Intentar obtener la ruta de la visualización directamente de las variables del workflow
        if hasattr(wf, 'variables') and 'visualization_path' in wf.variables:
            viz_path = wf.variables['visualization_path']
        
        # Si no está en variables, buscar en las tareas completadas
        if not viz_path:
            viz_task = res.get("tasks", {}).get("visualize_workflow", {})
            if viz_task and isinstance(viz_task, dict):
                output_data = viz_task.get("output_data", {})
                viz_path = output_data.get("visualization_path", "No visualization path available")
        
        print(f"📊 Visualization saved: {viz_path}")
        
        # Imprimir algunos mensajes adicionales para verificar las rutas
        logger.info(f"Debug - Analysis path: {analysis_path}")
        logger.info(f"Debug - Visualization path: {viz_path}")
        
        # Imprimir las variables del workflow al final
        if args.debug or args.verbose:
            logger.debug("Final workflow variables:")
            for key, value in wf.variables.items():
                if key in ['report_path', 'visualization_path', 'generate_analysis.report_path', 'visualize_workflow.visualization_path']:
                    logger.debug(f"  {key} = {value}")
    else:
        error = res.get('workflow_error', 'Unknown error')
        print(f"\n❌ Analysis failed: {error}")
        
        # Print task errors for debugging
        if 'tasks' in res:
            for task_id, task_data in res['tasks'].items():
                if task_data.get('status') == 'failed':
                    task_error = task_data.get('output_data', {}).get('error', 'No error message')
                    print(f"  - Task '{task_id}' failed: {task_error}")
    
    return 0 if res.get("success") else 1

if __name__ == "__main__":
    sys.exit(main())