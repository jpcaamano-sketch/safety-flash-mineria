"""
Safety_Flash Pro - Location Selector Component
Selector jerárquico de ubicación en la mina
"""

import streamlit as st
from typing import Optional, Dict, List

from core.database import get_database


def render_location_selector() -> Optional[Dict]:
    """
    Render hierarchical location selector

    Structure: Nivel → Sector → Ubicación específica

    Returns:
        Location data dict if selected, None otherwise
    """
    db = get_database()

    st.subheader("📍 Ubicación del Incidente")

    # Get all locations for filtering
    all_locations = db.get_all_locations()

    if not all_locations:
        st.warning("No hay ubicaciones disponibles")
        return None

    # Extract unique levels and sectors
    niveles = sorted(list(set([loc["nivel"] for loc in all_locations])), reverse=True)
    sectores = sorted(list(set([loc["sector"] for loc in all_locations])))

    # Level and Sector selection
    col1, col2 = st.columns(2)

    with col1:
        nivel = st.selectbox(
            "Nivel",
            niveles,
            key="location_nivel",
            help="Selecciona el nivel de la mina"
        )

    with col2:
        # Filter sectors available for selected level
        available_sectores = sorted(list(set([
            loc["sector"] for loc in all_locations
            if loc["nivel"] == nivel
        ])))

        sector = st.selectbox(
            "Sector",
            available_sectores if available_sectores else sectores,
            key="location_sector",
            help="Selecciona el sector"
        )

    # Filter locations for selected level and sector
    filtered_locations = [
        loc for loc in all_locations
        if loc["nivel"] == nivel and loc["sector"] == sector
    ]

    # Location selection
    if filtered_locations:
        location = st.selectbox(
            "Ubicación específica",
            filtered_locations,
            format_func=lambda x: f"{x['name']} ({x['tipo']})",
            key="location_specific",
            help="Selecciona la ubicación específica"
        )
    else:
        # If no specific location, create a generic one
        location = {
            "id": "custom",
            "code": f"N-{nivel}-{sector[:1]}-00",
            "name": f"Nivel {nivel} - {sector}",
            "nivel": nivel,
            "sector": sector,
            "tipo": "general"
        }
        st.info(f"Ubicación: Nivel {nivel} - Sector {sector}")

    # Reference point (optional)
    referencia = st.text_input(
        "Punto de referencia (opcional)",
        placeholder="Ej: Frente de avance, cerca de refugio #3, estación de ventilación",
        key="location_reference"
    )

    if location:
        # Create complete location info
        location_info = {
            **location,
            "referencia": referencia if referencia else None,
            "display_name": f"{location['name']} - Nivel {location['nivel']}"
        }

        # Show selection summary
        show_location_summary(location_info)

        return location_info

    return None


def show_location_summary(location: Dict):
    """Display location selection summary"""
    ref_text = f"\n📌 **Referencia:** {location['referencia']}" if location.get('referencia') else ""

    st.success(f"""
    **{location['name']}**

    🏔️ **Nivel:** {location['nivel']}
    🧭 **Sector:** {location['sector']}
    🏗️ **Tipo:** {location['tipo']}{ref_text}
    """)


def render_quick_location_selector() -> Optional[Dict]:
    """
    Compact location selector for streamlined workflow

    Returns:
        Location data dict if selected, None otherwise
    """
    db = get_database()
    all_locations = db.get_all_locations()

    if not all_locations:
        return None

    # Single dropdown with all locations
    location = st.selectbox(
        "Ubicación",
        all_locations,
        format_func=lambda x: f"N{x['nivel']} - {x['name']} ({x['sector']})",
        key="quick_location"
    )

    if location:
        st.caption(f"📍 {location['name']} - Nivel {location['nivel']}, Sector {location['sector']}")
        return location

    return None


def get_location_display(location: Dict) -> str:
    """Get formatted location display string"""
    base = f"{location['name']} (Nivel {location['nivel']}, {location['sector']})"
    if location.get('referencia'):
        base += f" - {location['referencia']}"
    return base


def render_location_map_placeholder():
    """Placeholder for future mine map integration"""
    st.info("""
    🗺️ **Mapa de la Mina** (Próximamente)

    En una versión futura, aquí se mostrará un mapa interactivo
    de la mina donde podrás seleccionar la ubicación tocando el mapa.
    """)
