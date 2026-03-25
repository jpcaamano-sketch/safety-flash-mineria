"""
Safety_Flash Pro - Report Editor Component
Editor y revisión de reportes generados por IA
"""

import streamlit as st
from typing import Optional, Dict
from datetime import datetime

from core.config import RISK_LEVELS, INCIDENT_CATEGORIES
from core.notifications import get_notification_preview


def render_report_editor(ai_report: Dict, worker_info: Dict, location_info: Dict) -> Optional[Dict]:
    """
    Render report editor for reviewing and editing AI-generated report

    Args:
        ai_report: AI-generated report data
        worker_info: Worker information
        location_info: Location information

    Returns:
        Final edited report data if approved, None otherwise
    """
    st.subheader("📋 Revisar y Aprobar Reporte")

    # Report header
    col1, col2, col3 = st.columns(3)

    with col1:
        st.metric("Reportante", worker_info.get("name", "N/A"))

    with col2:
        st.metric("Ubicación", f"Nivel {location_info.get('nivel', 'N/A')}")

    with col3:
        st.metric("Fecha", datetime.now().strftime("%d/%m/%Y %H:%M"))

    st.markdown("---")

    # Category selection
    st.write("**Categoría del Incidente**")

    categories = list(INCIDENT_CATEGORIES.keys())
    category_names = [f"{INCIDENT_CATEGORIES[c]['icon']} {INCIDENT_CATEGORIES[c]['name']}" for c in categories]

    # Find default index from AI suggestion
    default_category = ai_report.get("categoria_codigo", "GEO")
    default_idx = categories.index(default_category) if default_category in categories else 0

    selected_category_idx = st.selectbox(
        "Categoría",
        range(len(categories)),
        format_func=lambda x: category_names[x],
        index=default_idx,
        label_visibility="collapsed",
        key="report_category"
    )

    selected_category_code = categories[selected_category_idx]
    selected_category = INCIDENT_CATEGORIES[selected_category_code]

    # Risk level selection
    st.write("**Nivel de Riesgo**")

    risk_levels = list(RISK_LEVELS.keys())
    default_risk = ai_report.get("nivel_riesgo", "MEDIO")
    default_risk_idx = risk_levels.index(default_risk) if default_risk in risk_levels else 1

    risk_cols = st.columns(4)
    selected_risk = default_risk

    for idx, level in enumerate(risk_levels):
        with risk_cols[idx]:
            risk_config = RISK_LEVELS[level]
            if st.button(
                f"{risk_config['icon']} {level}",
                key=f"risk_{level}",
                use_container_width=True,
                type="primary" if level == default_risk else "secondary"
            ):
                selected_risk = level
                st.session_state["selected_risk"] = level

    # Use session state risk if set
    if "selected_risk" in st.session_state:
        selected_risk = st.session_state["selected_risk"]

    # Show risk justification
    if ai_report.get("justificacion_riesgo"):
        with st.expander("ℹ️ Justificación del nivel de riesgo (IA)"):
            st.write(ai_report["justificacion_riesgo"])

    st.markdown("---")

    # Description editor
    st.write("**Descripción Técnica**")

    final_description = st.text_area(
        "Descripción",
        value=ai_report.get("descripcion_tecnica", ""),
        height=150,
        label_visibility="collapsed",
        key="report_description",
        help="Revisa y edita la descripción generada por IA"
    )

    # Actions editor
    st.write("**Acciones Inmediatas**")

    actions_list = ai_report.get("acciones_inmediatas", [])
    actions_text = "\n".join(actions_list) if isinstance(actions_list, list) else str(actions_list)

    final_actions = st.text_area(
        "Acciones",
        value=actions_text,
        height=120,
        label_visibility="collapsed",
        key="report_actions",
        help="Revisa y edita las acciones sugeridas"
    )

    st.markdown("---")

    # Notification preview
    st.write("**📧 Notificaciones**")

    preview_report = {
        "final_risk_level": selected_risk,
        "categoria_codigo": selected_category_code,
        "worker_info": worker_info
    }

    recipients = get_notification_preview(preview_report)

    if recipients:
        recipient_text = ", ".join([f"{r['name']}" for r in recipients])
        st.info(f"Se notificará a: {recipient_text}")

        with st.expander("Ver detalles de notificación"):
            for r in recipients:
                channels = ", ".join(r.get("channels", ["email"]))
                st.write(f"- **{r['name']}** ({r['role']}): {channels}")
    else:
        st.info("Se notificará al supervisor directo")

    st.markdown("---")

    # Approval buttons
    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        approved = st.button(
            "✅ Aprobar y Enviar Reporte",
            type="primary",
            use_container_width=True,
            key="approve_report"
        )

    if approved:
        # Compile final report
        final_report = {
            "categoria_codigo": selected_category_code,
            "categoria_nombre": selected_category["name"],
            "final_risk_level": selected_risk,
            "final_description": final_description,
            "final_actions": final_actions,
            "ai_description": ai_report.get("descripcion_tecnica"),
            "ai_risk_level": ai_report.get("nivel_riesgo"),
            "ai_immediate_actions": actions_text,
            "palabras_clave": ai_report.get("palabras_clave", []),
            "worker_info": worker_info,
            "location_info": location_info,
            "approved_at": datetime.now().isoformat(),
            "status": "approved"
        }

        return final_report

    return None


def render_report_preview(report: Dict):
    """
    Render read-only preview of a report

    Args:
        report: Complete report data
    """
    risk_level = report.get("final_risk_level") or report.get("ai_risk_level", "MEDIO")
    risk_config = RISK_LEVELS.get(risk_level, RISK_LEVELS["MEDIO"])
    category_code = report.get("categoria_codigo", "GEO")
    category = INCIDENT_CATEGORIES.get(category_code, INCIDENT_CATEGORIES["GEO"])

    # Header with risk level color
    st.markdown(f"""
    <div style="background-color: {risk_config['color']}; padding: 10px; border-radius: 5px; color: white; text-align: center;">
        <h2>{risk_config['icon']} NIVEL DE RIESGO: {risk_level}</h2>
    </div>
    """, unsafe_allow_html=True)

    st.markdown("---")

    # Report details
    col1, col2 = st.columns(2)

    with col1:
        st.write("**Reporte #:**", report.get("report_number", "N/A"))
        st.write("**Fecha:**", report.get("created_at", datetime.now().isoformat())[:16].replace("T", " "))
        st.write("**Reportante:**", report.get("worker_info", {}).get("name", "N/A"))

    with col2:
        st.write("**Categoría:**", f"{category['icon']} {category['name']}")
        st.write("**Ubicación:**", report.get("location_info", {}).get("name", "N/A"))
        st.write("**Nivel:**", report.get("location_info", {}).get("nivel", "N/A"))

    st.markdown("---")

    # Description
    st.write("**Descripción:**")
    st.write(report.get("final_description") or report.get("ai_description", "N/A"))

    # Actions
    st.write("**Acciones Inmediatas:**")
    actions = report.get("final_actions") or report.get("ai_immediate_actions", "N/A")
    st.write(actions)


def render_report_summary_card(report: Dict):
    """
    Render compact report summary card

    Args:
        report: Report data
    """
    risk_level = report.get("final_risk_level") or report.get("ai_risk_level", "MEDIO")
    risk_config = RISK_LEVELS.get(risk_level, RISK_LEVELS["MEDIO"])

    st.markdown(f"""
    <div style="border-left: 4px solid {risk_config['color']}; padding: 10px; margin: 10px 0; background: #f5f5f5;">
        <strong>{risk_config['icon']} Reporte #{report.get('report_number', 'N/A')}</strong><br>
        📍 {report.get('location_info', {}).get('name', 'N/A')}<br>
        👤 {report.get('worker_info', {}).get('name', 'N/A')}<br>
        📅 {str(report.get('created_at', ''))[:16]}
    </div>
    """, unsafe_allow_html=True)
