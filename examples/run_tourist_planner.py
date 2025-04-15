#!/usr/bin/env python3
"""
Workflow de Ejemplo: Buscador de Rutas Económicas para Turistas (MVP Estático)

Este workflow busca la ruta de transporte público más económica entre dos puntos
en una ciudad, verifica la disponibilidad de servicios adicionales y genera un
informe en Markdown. Se enfoca en el caso AIFA -> Estadio Azteca, CDMX.
"""
# noqa: D202

import sys
import os
import logging
import json
import re
from typing import Dict, Any, List, Optional, Callable
from datetime import datetime, timedelta

# Añadir raíz del proyecto al path para importaciones correctas
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
if project_root not in sys.path:
    sys.path.insert(0, project_root)

# Importaciones Core de Dawn
from core.workflow import Workflow
from core.task import Task, DirectHandlerTask
from core.services import get_services, reset_services
from core.llm.interface import LLMInterface
from core.tools.registry import ToolRegistry
from core.handlers.registry import HandlerRegistry
from core.tools.registry_access import execute_tool, tool_exists, register_tool
from core.handlers.registry_access import handler_exists, register_handler
from core.utils.visualizer import visualize_workflow
from core.utils.registration_manager import ensure_all_registrations # Asume que esto registra web_search, write_markdown, calculate

# Importar herramientas adicionales
import networkx as nx
import matplotlib
matplotlib.use('Agg')  # Usar backend no interactivo
import matplotlib.pyplot as plt
import folium
from folium.features import CustomIcon
import requests
import io
from PIL import Image
import base64

# Configurar logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("tourist_route_finder_workflow")

# Generar mapa estático al iniciar el script (antes de cualquier otra función)
def generate_static_maps_immediately():
    """Genera los mapas estáticos inmediatamente al inicio del script."""
    print("Generando mapas estáticos...")
    try:
        # Puntos fijos para la ruta AIFA-Estadio Azteca
        fixed_route = [
            {"name": "AIFA", "coords": (19.7449, -99.0323)},
            {"name": "Buenavista", "coords": (19.4467, -99.1534)},
            {"name": "Indios Verdes", "coords": (19.4954, -99.1193)},
            {"name": "Martín Carrera", "coords": (19.4855, -99.1046)},
            {"name": "La Raza", "coords": (19.4409, -99.1369)},
            {"name": "Universidad", "coords": (19.3242, -99.1740)},
            {"name": "Taxqueña", "coords": (19.3444, -99.1422)},
            {"name": "Estadio Azteca", "coords": (19.3033, -99.1506)}
        ]
        
        # Modos de transporte para cada segmento
        transport_modes = [
            "Tren Suburbano",
            "Metro",
            "Metro",
            "Metro",
            "Metro",
            "Metro",
            "Autobús"
        ]
        
        # Colores para diferentes modos de transporte
        mode_colors = {
            "Metro": "red",
            "Metrobús": "orange",
            "Autobús": "blue",
            "Tren Suburbano": "purple",
            "Caminar": "green"
        }
        
        # 1. Crear mapa HTML con folium
        m = folium.Map(
            location=[19.5, -99.1],  # Centro entre AIFA y Estadio Azteca
            zoom_start=10,
            tiles="OpenStreetMap"
        )
        
        # Añadir marcadores y líneas
        for i, point in enumerate(fixed_route):
            # Determinar el color del marcador
            icon_color = "green" if i == 0 else "red" if i == len(fixed_route) - 1 else "blue"
                
            # Añadir marcador al mapa
            folium.Marker(
                location=point["coords"],
                popup=point["name"],
                icon=folium.Icon(color=icon_color, icon="info-sign")
            ).add_to(m)
            
            # Conectar con el punto anterior con una línea si no es el primer punto
            if i > 0:
                mode = transport_modes[i-1]
                color = mode_colors.get(mode, "gray")
                
                folium.PolyLine(
                    locations=[fixed_route[i-1]["coords"], point["coords"]],
                    color=color,
                    weight=4,
                    opacity=0.8,
                    popup=mode
                ).add_to(m)
        
        # Añadir leyenda
        legend_html = """
        <div style="position: fixed; bottom: 50px; left: 50px; width: 180px; height: auto; 
        background-color: white; border:2px solid grey; z-index:9999; font-size:12px;
        padding: 10px; border-radius: 5px;">
        <p><b>Modos de Transporte</b></p>
        """
        
        for mode, color in mode_colors.items():
            if mode in transport_modes:
                legend_html += f"""
                <div style="display: flex; align-items: center; margin-bottom: 5px;">
                    <div style="background-color: {color}; width: 15px; height: 5px; margin-right: 5px;"></div>
                    <span>{mode}</span>
                </div>
                """
        
        legend_html += "</div>"
        m.get_root().html.add_child(folium.Element(legend_html))
        
        # Asegurar que el directorio examples exista
        os.makedirs("examples", exist_ok=True)
        
        # Guardar mapa HTML
        output_path_html = "examples/ruta_aifa_azteca_mapa.html"
        m.save(output_path_html)
        print(f"Mapa HTML generado en: {output_path_html}")
        
        # 2. Crear mapa PNG con matplotlib
        plt.figure(figsize=(12, 8))
        
        # Extraer coordenadas para graficar
        lats = [p["coords"][0] for p in fixed_route]
        lons = [p["coords"][1] for p in fixed_route]
        names = [p["name"] for p in fixed_route]
        
        # Dibujar puntos
        plt.scatter(lons, lats, c='blue', s=100, zorder=2)
        
        # Dibujar líneas con colores según el modo
        for i in range(len(fixed_route) - 1):
            mode = transport_modes[i]
            color = mode_colors.get(mode, "gray")
            plt.plot([lons[i], lons[i+1]], [lats[i], lats[i+1]], color=color, linewidth=2, zorder=1, 
                     label=mode if mode not in plt.gca().get_legend_handles_labels()[1] else "")
        
        # Añadir etiquetas para cada punto
        for i, name in enumerate(names):
            plt.annotate(name, (lons[i], lats[i]), fontsize=9, ha='right',
                        xytext=(5, 5), textcoords='offset points')
        
        # Añadir título y leyenda
        plt.title('Ruta AIFA → Estadio Azteca', fontsize=14)
        
        # Añadir leyenda sin duplicados
        handles, labels = plt.gca().get_legend_handles_labels()
        by_label = dict(zip(labels, handles))
        plt.legend(by_label.values(), by_label.keys(), title="Modos de Transporte", loc='upper right')
        
        plt.axis('off')  # Ocultar ejes
        
        # Guardar como imagen PNG
        output_path_png = "examples/ruta_aifa_azteca_mapa.png"
        plt.savefig(output_path_png, format="png", dpi=300, bbox_inches="tight")
        plt.close()
        
        print(f"Mapa PNG generado en: {output_path_png}")
        
        return True
    except Exception as e:
        import traceback
        error_details = traceback.format_exc()
        print(f"Error generando mapas estáticos: {e}\n{error_details}")
        
        # Plan B: Crear un mapa aún más simple como imagen
        try:
            plt.figure(figsize=(10, 6))
            plt.text(0.5, 0.5, "Ruta AIFA → Estadio Azteca\n\n" + 
                    "AIFA → Buenavista (Tren Suburbano)\n" +
                    "Buenavista → Indios Verdes → Martín Carrera → La Raza (Metro)\n" +
                    "La Raza → Universidad → Taxqueña (Metro)\n" +
                    "Taxqueña → Estadio Azteca (Autobús)", 
                    ha='center', va='center', fontsize=12)
            plt.axis('off')
            
            os.makedirs("examples", exist_ok=True)
            output_path_fallback = "examples/ruta_aifa_azteca_mapa.png"
            plt.savefig(output_path_fallback, format="png", dpi=200)
            plt.close()
            
            # Crear un HTML mínimo
            html_content = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>Ruta AIFA-Estadio Azteca</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 20px; }
                    h1 { color: #2c3e50; }
                    .route { margin: 20px 0; }
                    .segment { margin: 10px 0; padding: 10px; border-left: 4px solid #3498db; }
                    .subway { border-color: red; }
                    .bus { border-color: blue; }
                    .train { border-color: purple; }
                </style>
            </head>
            <body>
                <h1>Ruta AIFA → Estadio Azteca</h1>
                <div class="route">
                    <div class="segment train">
                        <strong>Tren Suburbano:</strong> AIFA → Buenavista
                    </div>
                    <div class="segment subway">
                        <strong>Metro:</strong> Buenavista → Indios Verdes → Martín Carrera → La Raza → Universidad → Taxqueña
                    </div>
                    <div class="segment bus">
                        <strong>Autobús:</strong> Taxqueña → Estadio Azteca
                    </div>
                </div>
                <p><em>Nota: Este es un mapa de respaldo. No se pudo generar la visualización interactiva.</em></p>
            </body>
            </html>
            """
            
            with open("examples/ruta_aifa_azteca_mapa.html", "w", encoding="utf-8") as f:
                f.write(html_content)
            
            print("Mapas alternativos generados con éxito")
            return True
        except Exception as nested_e:
            print(f"Falló incluso el plan de respaldo: {nested_e}")
            return False

# Ejecutar generación inmediata
generate_static_maps_immediately()

# --- Handlers Específicos para Construir Consultas ---

def build_public_transport_route_query_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    """Construye la query para buscar rutas de transporte público."""
    start = input_data.get("start_location", "")
    end = input_data.get("end_location", "")
    city = input_data.get("city", "")
    if not all([start, end, city]):
        return {"success": False, "error": "Missing start, end, or city", "status": "failed"}
    # Query optimizada para buscar rutas en fuentes comunes como Google Maps/Moovit
    query = f"ruta transporte público más barata desde {start} hasta {end} en {city} pasos detallados"
    logger.info(f"Generated public transport query: {query}")
    return {"success": True, "result": {"query": query}, "status": "completed"}

def build_rideshare_check_query_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    """Construye la query para verificar apps de rideshare."""
    city = input_data.get("city", "")
    if not city:
        return {"success": False, "error": "Missing city", "status": "failed"}
    query = f"Uber o Didi disponible en {city}"
    logger.info(f"Generated rideshare check query: {query}")
    return {"success": True, "result": {"query": query}, "status": "completed"}

def build_autonomous_check_query_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    """Construye la query para verificar vehículos autónomos."""
    city = input_data.get("city", "")
    if not city:
        return {"success": False, "error": "Missing city", "status": "failed"}
    # Se pueden añadir más nombres si se conocen otros servicios prominentes
    query = f"Servicio taxi autónomo Waymo Cruise Zoox disponible en {city}"
    logger.info(f"Generated autonomous check query: {query}")
    return {"success": True, "result": {"query": query}, "status": "completed"}

def build_fare_query_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    """Construye la query para buscar tarifas de un modo de transporte."""
    mode = input_data.get("transport_mode", "")
    city = input_data.get("city", "")
    if not all([mode, city]):
        return {"success": False, "error": "Missing transport_mode or city", "status": "failed"}
    query = f"costo tarifa {mode} en {city} 2023 precio actual por viaje"
    logger.info(f"Generated fare query: {query}")
    return {"success": True, "result": {"query": query}, "status": "completed"}

# --- Handler para Calcular Costo Total ---

def calculate_total_cost_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    """Calcula el costo total estimado de la ruta basada en los pasos y tarifas."""
    route_steps = input_data.get("route_steps", []) 
    fare_data = input_data.get("fare_data", {})     

    if not isinstance(route_steps, list): route_steps = []
    if not isinstance(fare_data, dict): fare_data = {}

    total_cost = 0.0
    total_time_minutes = 0
    cost_breakdown = []
    unknown_fares = set()

    logger.info(f"Calculating cost for {len(route_steps)} steps with fares: {fare_data}")

    # Mapa de normalización expandido
    mode_mapping = {
        "metro": "Metro",
        "metrobús": "Metrobús", 
        "metrobus": "Metrobús",
        "bus": "Autobús", 
        "autobús": "Autobús", 
        "autobus": "Autobús",
        "camión": "Autobús", 
        "camion": "Autobús",
        "rtp": "Autobús RTP",
        "tren ligero": "Tren Ligero",
        "cablebús": "Cablebús",
        "cablebus": "Cablebús", 
        "mexicable": "Mexicable",
        "trolebús": "Trolebús", 
        "trolebus": "Trolebús",
        "tren suburbano": "Tren Suburbano",
        "suburbano": "Tren Suburbano",
        "ecobici": "Ecobici",
        "taxi": "Taxi",
    }

    for i, step in enumerate(route_steps):
        if not isinstance(step, dict): continue
        step_desc = step.get("step", f"Paso {i+1}")
        mode = step.get("mode", "Desconocido").strip().lower()
        time_minutes = step.get("time_minutes", 0)
        
        if isinstance(time_minutes, (int, float)):
            total_time_minutes += time_minutes
        elif isinstance(time_minutes, str):
            try:
                total_time_minutes += float(time_minutes)
            except ValueError:
                pass
        
        # Normalización mejorada con mejor detección
        normalized_mode = None
        for key, value in mode_mapping.items():
            if key in mode:
                normalized_mode = value
                break
        
        if not normalized_mode:
            normalized_mode = mode.capitalize()
        
        # Intentar encontrar el costo más específico primero, luego más genérico
        cost = None
        # Buscar por modo exacto primero
        if mode in fare_data:
            cost = fare_data.get(mode)
        # Luego por modo normalizado
        elif normalized_mode in fare_data:
            cost = fare_data.get(normalized_mode)
        # Finalmente por categorías generales si contienen palabras clave
        else:
            for fare_key in fare_data:
                if any(keyword in mode for keyword in fare_key.lower().split()):
                    cost = fare_data.get(fare_key)
                    break

        step_cost_str = "No encontrado"
        if cost is not None:
            try:
                # Manejar casos donde el costo tiene formato "$5.00 MXN"
                if isinstance(cost, str):
                    cost = cost.replace("$", "").replace("MXN", "").strip()
                    # Extraer solo números del string
                    cost_match = re.search(r'(\d+(?:\.\d+)?)', cost)
                    if cost_match:
                        cost = cost_match.group(1)
                
                step_cost = float(cost)
                total_cost += step_cost
                step_cost_str = f"${step_cost:.2f} MXN"
            except (ValueError, TypeError):
                logger.warning(f"Could not convert fare '{cost}' for mode '{mode}' to float.")
                unknown_fares.add(mode)
        else:
             logger.warning(f"Fare not found for mode '{mode}' (Normalized: '{normalized_mode}').")
             unknown_fares.add(mode)

        cost_breakdown.append({
            "step": step_desc,
            "mode": mode,
            "normalized_mode": normalized_mode,
            "cost": step_cost_str,
            "time_minutes": time_minutes
        })

    # Formato de tiempo en horas:minutos
    hours, minutes = divmod(total_time_minutes, 60)
    time_formatted = f"{int(hours)}h {int(minutes)}min"

    logger.info(f"Calculated total cost: {total_cost:.2f}, total time: {time_formatted}. Unknown fares for: {unknown_fares}")

    return {
        "success": True,
        "status": "completed",
        "result": {
            "total_cost": round(total_cost, 2),
            "total_time_minutes": total_time_minutes,
            "time_formatted": time_formatted,
            "cost_breakdown": cost_breakdown,
            "unknown_fare_modes": list(unknown_fares)
        }
    }

# --- Añadir función para visualizar la ruta (versión corregida) ---
def visualize_route_handler(task: DirectHandlerTask, input_data: dict) -> dict:
    """Devuelve rutas a los mapas estáticos pre-generados."""
    # Verificar que los archivos existan
    png_path = "examples/ruta_aifa_azteca_mapa.png"
    html_path = "examples/ruta_aifa_azteca_mapa.html"
    
    png_exists = os.path.exists(png_path)
    html_exists = os.path.exists(html_path)
    
    if not png_exists or not html_exists:
        # Si no existen, intentar generarlos de nuevo
        success = generate_static_maps_immediately()
        if not success:
            return {
                "success": False,
                "error": "No se pudieron generar los mapas",
                "status": "failed"
            }
    
    return {
        "success": True,
        "status": "completed",
        "result": {
            "visualization_path": png_path,
            "html_map_path": html_path,
            "note": "Mapa pre-generado para ruta AIFA-Estadio Azteca."
        }
    }

# --- Definición del Workflow ---

def build_tourist_route_workflow() -> Workflow:
    """Construye el workflow estático para el buscador de rutas."""
    workflow = Workflow(
        workflow_id="tourist_route_finder_cdmx",
        name="Buscador de Rutas Económicas para Turistas (CDMX AIFA-Azteca)"
    )

    # --- Tareas de Construcción de Queries (Paralelas) ---
    task_build_route_q = DirectHandlerTask(
        task_id="build_route_query", name="Build Public Transport Query",
        handler_name="build_public_transport_route_query_handler",
        input_data={"start_location": "${start_location}", "end_location": "${end_location}", "city": "${city}"},
        next_task_id_on_success="search_route"  # Add explicit next task
    )
    task_build_rideshare_q = DirectHandlerTask(
        task_id="build_rideshare_query", name="Build Rideshare Check Query",
        handler_name="build_rideshare_check_query_handler",
        input_data={"city": "${city}"},
        next_task_id_on_success="search_rideshare"  # Add explicit next task
    )
    task_build_autonomous_q = DirectHandlerTask(
        task_id="build_autonomous_query", name="Build Autonomous Check Query",
        handler_name="build_autonomous_check_query_handler",
        input_data={"city": "${city}"},
        next_task_id_on_success="search_autonomous"  # Add explicit next task
    )
    task_build_fare_q_metro = DirectHandlerTask(
        task_id="build_fare_query_metro", name="Build Metro Fare Query",
        handler_name="build_fare_query_handler",
        input_data={"transport_mode": "Metro", "city": "${city}"},
        next_task_id_on_success="search_fare_metro"
    )
    task_build_fare_q_bus = DirectHandlerTask(
        task_id="build_fare_query_bus", name="Build Bus Fare Query",
        handler_name="build_fare_query_handler",
        input_data={"transport_mode": "Autobús", "city": "${city}"},
        next_task_id_on_success="search_fare_bus"
    )
    task_build_fare_q_metrobus = DirectHandlerTask(
        task_id="build_fare_query_metrobus", name="Build Metrobus Fare Query",
        handler_name="build_fare_query_handler",
        input_data={"transport_mode": "Metrobús", "city": "${city}"},
        next_task_id_on_success="search_fare_metrobus"
    )
    task_build_fare_q_suburbano = DirectHandlerTask(
        task_id="build_fare_query_suburbano", name="Build Suburban Train Fare Query",
        handler_name="build_fare_query_handler",
        input_data={"transport_mode": "Tren Suburbano AIFA", "city": "${city}"},
        next_task_id_on_success="search_fare_suburbano"
    )

    # --- Tareas de Búsqueda Web (Paralelas, dependen de las queries) ---
    task_search_route = Task(
        task_id="search_route", name="Search Public Transport Route",
        tool_name="web_search",
        input_data={"query": "${build_route_query.result.query}"},
        dependencies=["build_route_query"],
        next_task_id_on_success="extract_route_steps"  # Add explicit next task
    )
    task_search_rideshare = Task(
        task_id="search_rideshare", name="Check Rideshare Availability",
        tool_name="web_search",
        input_data={"query": "${build_rideshare_query.result.query}"},
        dependencies=["build_rideshare_query"],
        next_task_id_on_success="extract_availability"  # Add explicit next task
    )
    task_search_autonomous = Task(
        task_id="search_autonomous", name="Check Autonomous Availability",
        tool_name="web_search",
        input_data={"query": "${build_autonomous_query.result.query}"},
        dependencies=["build_autonomous_query"],
        next_task_id_on_success="extract_availability"  # Add explicit next task
    )
    task_search_fare_metro = Task(
        task_id="search_fare_metro", name="Search Metro Fare",
        tool_name="web_search",
        input_data={"query": "${build_fare_query_metro.result.query}"},
        dependencies=["build_fare_query_metro"],
        next_task_id_on_success="extract_fares"  # Add explicit next task
    )
    task_search_fare_bus = Task(
        task_id="search_fare_bus", name="Search Bus Fare",
        tool_name="web_search",
        input_data={"query": "${build_fare_query_bus.result.query}"},
        dependencies=["build_fare_query_bus"],
        next_task_id_on_success="extract_fares"  # Add explicit next task
    )
    task_search_fare_metrobus = Task(
        task_id="search_fare_metrobus", name="Search Metrobus Fare",
        tool_name="web_search",
        input_data={"query": "${build_fare_query_metrobus.result.query}"},
        dependencies=["build_fare_query_metrobus"],
        next_task_id_on_success="extract_fares"
    )
    task_search_fare_suburbano = Task(
        task_id="search_fare_suburbano", name="Search Suburban Train Fare",
        tool_name="web_search",
        input_data={"query": "${build_fare_query_suburbano.result.query}"},
        dependencies=["build_fare_query_suburbano"],
        next_task_id_on_success="extract_fares"
    )

    # --- Tareas de Extracción LLM (Paralelas, dependen de las búsquedas) ---
    task_extract_route = Task(
        task_id="extract_route_steps", name="Extract Route Steps",
        is_llm_task=True,
        input_data={
            "prompt": """
            Analiza los siguientes resultados de búsqueda para una ruta de transporte público desde '${start_location}' hasta '${end_location}'.
            Resultados:
            ```
            ${search_route.result.result | search_route.result}
            ```
            Extrae los pasos detallados de la ruta en un formato estructurado. Para cada paso:
            1. Identifica el modo de transporte (ej: Autobús, Metro, Tren Ligero, Metrobús, Cablebús, Caminar)
            2. La línea o ruta específica si se menciona (ej: Línea 3, Ruta 101)
            3. Los puntos clave (estación de inicio, estación de fin, punto de transbordo)
            4. El tiempo estimado en minutos para cada paso

            IMPORTANTE: Es crucial que para cada paso indiques claramente:
            - Un origen y destino concretos para ese paso (en el campo "details")
            - Un valor numérico para el tiempo en minutos (en el campo "time_minutes")
            
            Usa el siguiente formato para el campo "details": "Origen a Destino"
            Ejemplo: "Indios Verdes a Politécnico" o "Buenavista a Terminal AIFA"
            
            Responde ÚNICAMENTE con un array JSON válido con la siguiente estructura:
            ```json
            [
              {
                "step": "Descripción completa del paso", 
                "mode": "Modo de Transporte", 
                "line": "Línea/Ruta (o null)", 
                "details": "Origen a Destino",
                "time_minutes": tiempo_estimado_en_minutos
              }
            ]
            ```
            
            Si no encuentras tiempo estimado para algún paso, haz una estimación razonable según:
            - Caminata: 5 min por 400 metros
            - Metro: 2-3 min entre estaciones
            - Autobús: 4-5 min entre paradas
            - Tren Suburbano a AIFA: 40 min desde Buenavista
            - Esperas para transbordos: 5-10 min
            
            Si no puedes determinar los pasos, proporciona al menos una estimación básica de la ruta completa.
            """
        },
        dependencies=["search_route"],
        next_task_id_on_success="calculate_cost"
    )
    task_extract_availability = Task(
        task_id="extract_availability", name="Extract Service Availability",
        is_llm_task=True,
        input_data={
            "prompt": """
            Analiza los siguientes resultados de búsqueda sobre disponibilidad de servicios en '${city}'.
            Resultados Rideshare (Uber/Didi):
            ```
            ${search_rideshare.result.result | search_rideshare.result}
            ```
            Resultados Vehículos Autónomos (Waymo/Cruise/Zoox):
            ```
            ${search_autonomous.result.result | search_autonomous.result}
            ```
            Determina la disponibilidad de cada servicio.
            Responde ÚNICAMENTE con un objeto JSON válido con la siguiente estructura:
            ```json
            {
              "rideshare_available": "Sí" | "No" | "Incierto",
              "autonomous_available": "Sí" | "No" | "Incierto" | "Nombre del Servicio (si se encontró)"
            }
            ```
            """
        },
        dependencies=["search_rideshare", "search_autonomous"],
        next_task_id_on_success="synthesize_report"  # Add explicit next task
    )
    task_extract_fares = Task(
        task_id="extract_fares", name="Extract Fare Costs",
        is_llm_task=True,
        input_data={
            "prompt": """
            Analiza los siguientes resultados de búsqueda sobre tarifas de transporte en '${city}'.
            
            Resultados Tarifa Metro:
            ```
            ${search_fare_metro.result.result | search_fare_metro.result}
            ```
            Resultados Tarifa Autobús:
            ```
            ${search_fare_bus.result.result | search_fare_bus.result}
            ```
            Resultados Tarifa Metrobús:
            ```
            ${search_fare_metrobus.result.result | search_fare_metrobus.result}
            ```
            Resultados Tarifa Tren Suburbano AIFA:
            ```
            ${search_fare_suburbano.result.result | search_fare_suburbano.result}
            ```
            
            Extrae el costo numérico estimado por viaje para cada modo de transporte. Si encuentras un rango, usa el valor más común o promedio. Ignora tarifas especiales (estudiantes, etc.) a menos que sea la única mencionada.
            
            Busca específicamente las tarifas para:
            1. Metro (todas las líneas)
            2. Autobús (RTP, local)
            3. Metrobús
            4. Tren Suburbano (particularmente la ruta hacia/desde AIFA)
            5. Cualquier otro transporte público mencionado
            
            Si encuentras tarifas específicas para la ruta AIFA-Estadio Azteca o partes de ella (como AIFA-Indios Verdes), inclúyelas.
            
            Para cada tarifa, extrae el valor numérico (ejemplo: "6" para "Cuesta $6 pesos"). Si hay rangos de precios para distancia, incluye el rango completo (ejemplo: "7-15").
            
            Responde ÚNICAMENTE con un objeto JSON válido con la siguiente estructura. Usa valores numéricos, no strings con "$":
            ```json
            {
              "Metro": <costo_numero_o_null>,
              "Autobús": <costo_numero_o_null>,
              "Metrobús": <costo_numero_o_null>,
              "Tren Suburbano": <costo_numero_o_null>,
              "Autobús RTP": <costo_numero_o_null>,
              "Metro Línea 5": <costo_numero_o_null>,
              "AIFA-Indios Verdes": <costo_numero_o_null>,
              "Indios Verdes-Estadio Azteca": <costo_numero_o_null>
            }
            ```
            Si encuentras otros modos relevantes, añádelos al JSON. Si no encuentras alguno, usa `null` o elimina esa clave.
            """
        },
        dependencies=["search_fare_metro", "search_fare_bus", "search_fare_metrobus", "search_fare_suburbano"],
        next_task_id_on_success="calculate_cost"
    )

    # --- Tarea de Cálculo de Costo (Depende de pasos y tarifas extraídas) ---
    task_calculate_cost = DirectHandlerTask(
        task_id="calculate_cost", name="Calculate Total Estimated Cost",
        handler_name="calculate_total_cost_handler",
        input_data={
            "route_steps": "${extract_route_steps.result.result | []}",
            "fare_data": "${extract_fares.result.result | {}}"
        },
        dependencies=["extract_route_steps", "extract_fares"],
        next_task_id_on_success="synthesize_report"  # Add explicit next task
    )

    # --- Tarea de Visualización ---
    task_visualize_route = DirectHandlerTask(
        task_id="visualize_route", name="Visualize Route as Graph",
        handler_name="visualize_route_handler",
        input_data={
            "route_steps": "${extract_route_steps.result.result | []}"
        },
        dependencies=["extract_route_steps"],
        next_task_id_on_success="synthesize_report"
    )

    # --- Tarea de Síntesis Final y Generación de Informe (LLM) ---
    task_synthesize_report = Task(
        task_id="synthesize_report", name="Synthesize Final Report",
        is_llm_task=True,
        input_data={
            "prompt": """
            Eres un asistente de planificación de rutas para turistas. Genera un informe detallado en formato MARKDOWN para la ruta más económica desde '${start_location}' hasta '${end_location}' en '${city}'.

            Utiliza la siguiente información recopilada:
            - Pasos de la Ruta: ${extract_route_steps.result.result | 'No se encontraron pasos.'}
            - Disponibilidad de Servicios: ${extract_availability.result.result | 'No se encontró información.'}
            - Desglose de Costos por Paso: ${calculate_cost.result.cost_breakdown | 'No disponible.'}
            - Costo Total Estimado: ${calculate_cost.result.total_cost | 'No disponible'} MXN
            - Tiempo Total Estimado: ${calculate_cost.result.time_formatted | 'No disponible'}
            - Modos con Tarifa Desconocida: ${calculate_cost.result.unknown_fare_modes | []}
            
            El informe DEBE incluir las siguientes secciones EXACTAS con formato Markdown:

            ## Ruta Detallada (Transporte Público)
            *Lista numerada de los pasos extraídos.*
            *Si no se encontraron pasos, indica: "No se pudo determinar una ruta detallada de transporte público."*

            ## Tiempos y Costos Estimados
            *Crea una tabla Markdown con columnas: | Paso | Modo de Transporte | Tiempo Est. | Costo Est. |*
            *Llena la tabla con la información de 'Desglose de Costos por Paso'.*
            *Si el desglose no está disponible, indica: "No se pudo generar el desglose de costos."*
            *Si hubo modos con tarifa desconocida, añade una nota al final de la tabla mencionándolos.*

            ## Resumen de la Ruta
            - **Tiempo Total Estimado:** ${calculate_cost.result.time_formatted | 'No disponible'}
            - **Costo Total Estimado:** ${calculate_cost.result.total_cost | 'No disponible'} MXN
            *Añade una recomendación sobre la mejor hora del día para este viaje (evitar horas pico, etc.).*

            ## Otros Servicios de Transporte en ${city}
            - **Apps (Uber/Didi):** *Indica la disponibilidad extraída.*
            - **Vehículos Autónomos:** *Indica la disponibilidad extraída.*
            *Menciona brevemente la posibilidad de usar rutas híbridas (ej. metro + Uber para el último tramo) si las apps están disponibles.*

            ## Mapa de la Ruta

            ![Mapa de Ruta](examples/ruta_aifa_azteca_mapa.png)

            **Para una visualización interactiva completa, abra el archivo:** examples/ruta_aifa_azteca_mapa.html

            *Mapa pre-generado para ruta AIFA-Estadio Azteca.*

            ## Flujo de la Ruta (Resumen)
            *Describe la secuencia principal de modos de transporte, los puntos clave y tiempos en una línea. Ejemplo: AIFA -(Autobús Z, 25min, $A)-> Indios Verdes -(Metro L3, 30min, $B)-> Estadio Azteca.*
            *Si no hay pasos detallados, indica: "No disponible."*

            ## Descargo de Responsabilidad
            *Incluye este texto:* "Nota: La información de rutas, tiempos y costos se basa en búsquedas web públicas y puede no ser exacta o estar desactualizada. Las tarifas y tiempos son estimados y pueden variar. No se consideran posibles retrasos ni tráfico. Verifica siempre la información localmente antes de viajar."

            --- FIN DEL INFORME ---

            Genera ÚNICAMENTE el contenido Markdown del informe. No incluyas explicaciones adicionales antes o después.
            """
        },
        dependencies=[
            "extract_route_steps",
            "extract_availability",
            "calculate_cost",
            "visualize_route"
        ],
        next_task_id_on_success="write_report"
    )

    # --- Tarea Final: Escribir Informe a Archivo ---
    task_write_report = Task(
        task_id="write_report", name="Write Report to Markdown File",
        tool_name="write_markdown",
        input_data={
            "file_path": "examples/ruta_aifa_azteca.md",
            "content": "${synthesize_report.result}"  # Changed from result.response to just result
        },
        dependencies=["synthesize_report"]
    )

    # Add all tasks to the workflow
    workflow.add_task(task_build_route_q)
    workflow.add_task(task_build_rideshare_q)
    workflow.add_task(task_build_autonomous_q)
    workflow.add_task(task_build_fare_q_metro)
    workflow.add_task(task_build_fare_q_bus)
    workflow.add_task(task_build_fare_q_metrobus)
    workflow.add_task(task_build_fare_q_suburbano)
    workflow.add_task(task_search_route)
    workflow.add_task(task_search_rideshare)
    workflow.add_task(task_search_autonomous)
    workflow.add_task(task_search_fare_metro)
    workflow.add_task(task_search_fare_bus)
    workflow.add_task(task_search_fare_metrobus)
    workflow.add_task(task_search_fare_suburbano)
    workflow.add_task(task_extract_route)
    workflow.add_task(task_extract_availability)
    workflow.add_task(task_extract_fares)
    workflow.add_task(task_calculate_cost)
    workflow.add_task(task_visualize_route)
    workflow.add_task(task_synthesize_report)
    workflow.add_task(task_write_report)

    # Define the task order for the workflow
    workflow.task_order = [
        # Query building tasks (parallel)
        "build_route_query",
        "build_rideshare_query",
        "build_autonomous_query",
        "build_fare_query_metro",
        "build_fare_query_bus",
        "build_fare_query_metrobus",
        "build_fare_query_suburbano",
        # Search tasks (parallel)
        "search_route",
        "search_rideshare",
        "search_autonomous",
        "search_fare_metro",
        "search_fare_bus",
        "search_fare_metrobus",
        "search_fare_suburbano",
        # Extraction tasks (parallel)
        "extract_route_steps",
        "extract_availability",
        "extract_fares",
        # Cost calculation
        "calculate_cost",
        # Visualization
        "visualize_route",
        # Report generation
        "synthesize_report",
        # Final output
        "write_report"
    ]

    return workflow

# --- Función Principal de Ejecución ---

def main():
    """Punto de entrada para ejecutar el workflow."""
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    logger = logging.getLogger(__name__)

    logger.info("--- Inicializando Buscador de Rutas para Turistas ---")
    reset_services() # Asegura un estado limpio
    services = get_services()
    services.initialize() # Inicializa LLM, registros, etc.
    
    # Registrar Handlers específicos de este workflow
    handlers_to_register = {
        "build_public_transport_route_query_handler": build_public_transport_route_query_handler,
        "build_rideshare_check_query_handler": build_rideshare_check_query_handler,
        "build_autonomous_check_query_handler": build_autonomous_check_query_handler,
        "build_fare_query_handler": build_fare_query_handler,
        "calculate_total_cost_handler": calculate_total_cost_handler,
        "visualize_route_handler": visualize_route_handler,
    }
    for name, func in handlers_to_register.items():
        register_handler(name, func, replace=True)
    logger.info(f"Registered {len(handlers_to_register)} custom handlers.")

    # Asegurarse que las herramientas base estén registradas (web_search, write_markdown, calculate)
    ensure_all_registrations()
    logger.info(f"Tools available: {list(services.tool_registry.tools.keys())}")
    logger.info(f"Handlers available: {services.handler_registry.list_handlers()}")

    # Initialize LLM interface
    from core.llm.interface import LLMInterface
    llm_interface = LLMInterface()
    services.register_llm_interface(llm_interface)

    # Construir el workflow
    workflow = build_tourist_route_workflow()
    logger.info(f"Workflow '{workflow.name}' construido.")

    # (Opcional) Visualizar
    try:
        output_dir = os.path.join(os.path.dirname(__file__), "visualizations")
        os.makedirs(output_dir, exist_ok=True)
        viz_path = os.path.join(output_dir, f"{workflow.id}_graph")
        visualize_workflow(workflow, filename=viz_path, format="png", view=False)
        logger.info(f"Visualización guardada en {viz_path}.png (si graphviz está instalado)")
    except Exception as e:
        logger.warning(f"No se pudo generar visualización: {e}")

    # Definir la entrada inicial para el caso de uso
    initial_input = {
        "start_location": "Aeropuerto Internacional Felipe Ángeles (AIFA)",
        "end_location": "Estadio Azteca",
        "city": "Ciudad de México",
        "output_file_path": "examples/ruta_aifa_azteca.md" # Nombre del archivo de salida
    }
    logger.info(f"Input inicial: {initial_input}")

    # Ejecutar el workflow
    logger.info("--- Iniciando Ejecución del Workflow ---")
    from core.engine import WorkflowEngine # Importar aquí si no está global
    engine = WorkflowEngine(
        workflow=workflow,
        llm_interface=llm_interface,  # Use the initialized LLM interface
        tool_registry=services.tool_registry,
        services=services
    )
    
    # Asegurar que el motor tenga acceso a los registros correctos
    engine.handler_registry = services.handler_registry

    result = engine.run(initial_input=initial_input)

    # Imprimir resultados
    logger.info(f"--- Ejecución del Workflow Finalizada (Estado General: {workflow.status}) ---")
    if result.get("success"):
        # Get the final report path
        final_report_task = workflow.get_task("write_report")
        synthesis_task = workflow.get_task("synthesize_report")
        
        # Debug: Check the output structure of synthesize_report task
        if synthesis_task and synthesis_task.status == "completed":
            logger.info(f"Synthesis task output structure: {type(synthesis_task.output_data)}")
            for key, value in synthesis_task.output_data.items():
                logger.info(f"Key: {key}, Value Type: {type(value)}")
            
            # Check if we have the response field
            response_content = None
            if isinstance(synthesis_task.output_data, dict):
                if 'result' in synthesis_task.output_data and isinstance(synthesis_task.output_data['result'], dict):
                    response_content = synthesis_task.output_data['result'].get('response')
                elif 'response' in synthesis_task.output_data:
                    response_content = synthesis_task.output_data['response']
            
            # If we have content and the write task failed, try writing manually
            if response_content and (not final_report_task or final_report_task.status != "completed"):
                logger.info("Attempting to write report manually")
                try:
                    # Use the tool registry to write the file
                    write_result = execute_tool("write_markdown", {
                        "file_path": "examples/ruta_aifa_azteca_manual.md",
                        "content": response_content
                    })
                    logger.info(f"Manual write result: {write_result}")
                    if write_result.get('success'):
                        print(f"\nReport manually written to: {write_result.get('result', {}).get('file_path', 'N/A')}")
                except Exception as e:
                    logger.error(f"Error in manual write: {e}")
        
        if final_report_task and final_report_task.status == "completed":
            final_report_task_output = final_report_task.output_data
            if isinstance(final_report_task_output, dict):
                report_path = final_report_task_output.get("result", "N/A")
                if isinstance(report_path, dict):
                    report_path = report_path.get("file_path", "N/A")
                print(f"\nReport written to: {report_path}")
            else:
                print("\nError: Invalid response format from write_markdown tool")
        else:
            print("\nError: Report writing task failed or not completed")
    else:
        print("\n❌ WORKFLOW FALLÓ")
        failed_task_id = result.get("failed_task_id", "N/A")
        error_message = result.get("workflow_error", "Error desconocido")
        print(f"   Tarea Fallida: {failed_task_id}")
        print(f"   Error: {error_message}")
        # Imprimir detalles del error de la tarea fallida si está disponible
        failed_task = workflow.get_task(failed_task_id)
        if failed_task and failed_task.output_data:
            print(f"   Detalles del Error de la Tarea: {failed_task.output_data.get('error', 'N/A')}")

if __name__ == "__main__":
    main()
