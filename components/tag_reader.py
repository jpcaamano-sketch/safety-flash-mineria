"""
Safety_Flash Pro - TAG Reader Component
Identificación de trabajadores por código TAG
"""

import streamlit as st
from typing import Optional, Dict

from core.database import get_database


def render_tag_input() -> Optional[Dict]:
    """
    Render TAG input component for worker identification

    Options:
    1. Manual TAG code entry
    2. Worker selector (for demo)
    3. Future: NFC reader integration

    Returns:
        Worker data dict if identified, None otherwise
    """
    db = get_database()

    st.subheader("👤 Identificación del Trabajador")

    # Show demo mode indicator
    if db.is_demo_mode():
        st.info("🔧 Modo Demo - Usando datos de prueba")

    # Method selection
    method = st.radio(
        "Método de identificación",
        ["Código TAG", "Buscar por nombre"],
        horizontal=True,
        label_visibility="collapsed"
    )

    worker = None

    if method == "Código TAG":
        col1, col2 = st.columns([3, 1])

        with col1:
            tag = st.text_input(
                "Ingresa tu código TAG",
                placeholder="Ej: MIN-2345",
                key="tag_input"
            )

        with col2:
            st.write("")  # Spacing
            st.write("")  # Spacing
            search_clicked = st.button("🔍 Buscar", use_container_width=True)

        # Search for worker
        if tag:
            if search_clicked or tag != st.session_state.get("last_tag", ""):
                st.session_state["last_tag"] = tag
                found_worker = db.get_worker_by_tag(tag.strip())
                if found_worker:
                    st.session_state["found_worker"] = found_worker
                else:
                    st.session_state["found_worker"] = None
                    st.error(f"❌ TAG '{tag}' no encontrado en el sistema")
                    st.caption("TAGs de ejemplo: MIN-2345, MIN-3456, MIN-4567")

            # Show worker if found
            if st.session_state.get("found_worker"):
                worker = st.session_state["found_worker"]
                show_worker_card(worker)

    else:
        # Worker selector for demo
        workers = db.get_all_workers()

        if workers:
            selected = st.selectbox(
                "Selecciona trabajador",
                workers,
                format_func=lambda x: f"{x['name']} - {x['cargo']}",
                key="worker_selector"
            )

            if selected:
                worker = selected
                show_worker_card(worker)
        else:
            st.warning("No hay trabajadores disponibles")

    return worker


def show_worker_card(worker: Dict):
    """Display worker information card"""
    st.success(f"""
    **{worker['name']}**

    📋 **Cargo:** {worker['cargo']}
    🏢 **Área:** {worker['area']}
    ⏰ **Turno:** {worker['turno']}
    🏭 **Empresa:** {worker['empresa']}
    🏷️ **TAG:** {worker['tag_code']}
    """)


def render_quick_tag_input() -> Optional[Dict]:
    """
    Compact TAG input for streamlined workflow

    Returns:
        Worker data dict if identified, None otherwise
    """
    db = get_database()

    col1, col2 = st.columns([4, 1])

    with col1:
        tag = st.text_input(
            "Código TAG",
            placeholder="MIN-2345",
            label_visibility="collapsed",
            key="quick_tag"
        )

    with col2:
        if st.button("✓", key="quick_tag_btn"):
            if tag:
                worker = db.get_worker_by_tag(tag.strip())
                if worker:
                    return worker
                else:
                    st.error("TAG no encontrado")

    # Auto-search on Enter
    if tag:
        worker = db.get_worker_by_tag(tag.strip())
        if worker:
            st.caption(f"✅ {worker['name']} - {worker['cargo']}")
            return worker

    return None


def get_worker_summary(worker: Dict) -> str:
    """Get a one-line summary of worker info"""
    return f"{worker['name']} ({worker['cargo']}) - {worker['area']}"
