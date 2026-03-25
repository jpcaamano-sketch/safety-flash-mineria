"""
Safety_Flash Pro - Sistema de Reportes de Incidentes Mineros
Flujo: TAG → Foto → Audio → IA genera reporte profesional
"""

import streamlit as st
from datetime import datetime

from core.config import APP_CONFIG, RISK_LEVELS, DEMO_WORKERS, DEMO_LOCATIONS
from core.database import get_database
from core.ai_client import init_ai, analyze_image, generate_professional_report
from core.speech import is_transcription_available, get_speech_to_text
from core.vision import is_vision_available
from core.notifications import send_report_notifications
from utils.pdf_generator import generate_flash_report_pdf, get_pdf_filename

st.set_page_config(
    page_title=APP_CONFIG["page_title"],
    page_icon=APP_CONFIG["page_icon"],
    layout=APP_CONFIG["layout"],
    initial_sidebar_state=APP_CONFIG["initial_sidebar_state"]
)

st.markdown("""
<style>
    #MainMenu { visibility: hidden; }
    footer    { visibility: hidden; }

    .main-header {
        text-align: center;
        padding: 0.8rem 0;
        border-bottom: 2px solid #e0e0e0;
        margin-bottom: 1rem;
    }
    .main-header h1 { font-size: clamp(1.4rem, 5vw, 2rem); margin: 0; }
    .main-header p  { font-size: clamp(0.8rem, 3vw, 1rem); margin: 0; }

    .risk-badge {
        display: inline-block;
        padding: 5px 15px;
        border-radius: 20px;
        color: white;
        font-weight: bold;
    }
    .stButton>button {
        width: 100%;
        min-height: 52px;
        font-size: clamp(0.9rem, 3vw, 1rem);
        border-radius: 10px;
    }
    .worker-card {
        background: #f8f9fa;
        padding: 15px;
        border-radius: 10px;
        border-left: 4px solid #ff4b4b;
        margin: 10px 0;
    }
    .info-box {
        background: #e3f2fd;
        padding: 10px 15px;
        border-radius: 8px;
        margin: 10px 0;
    }
    /* Inputs más grandes en móvil */
    .stTextInput input {
        font-size: clamp(1rem, 4vw, 1.2rem) !important;
        padding: 10px !important;
    }
    .block-container {
        padding-left: 1rem !important;
        padding-right: 1rem !important;
        max-width: 750px !important;
    }
</style>
""", unsafe_allow_html=True)


def init_session_state():
    """Initialize session state variables"""
    defaults = {
        "step": 1,
        "worker": None,
        "location": None,
        "photo": None,
        "photo_analysis": None,
        "audio": None,
        "transcription": None,
        "ai_report": None,
        "final_report": None,
        "pdf_bytes": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_report():
    """Reset all report data"""
    st.session_state.step = 1
    st.session_state.worker = None
    st.session_state.location = None
    st.session_state.photo = None
    st.session_state.photo_analysis = None
    st.session_state.audio = None
    st.session_state.transcription = None
    st.session_state.ai_report = None
    st.session_state.final_report = None
    st.session_state.pdf_bytes = None


def render_header():
    """Render application header"""
    st.markdown("""
    <div class="main-header">
        <h1>⚠️ Safety Flash Pro</h1>
        <p>Sistema de Reportes de Incidentes Mineros</p>
    </div>
    """, unsafe_allow_html=True)


def render_step_indicator(current_step: int):
    """Render step progress indicator"""
    steps = ["👤 TAG", "📸 Foto", "🎤 Audio", "✅ Listo"]

    cols = st.columns(len(steps))
    for i, name in enumerate(steps):
        step_num = i + 1
        with cols[i]:
            if step_num < current_step:
                st.markdown(f"<div style='text-align:center'><span style='font-size:1.2em; color:green'>✅</span><br><small>{name}</small></div>", unsafe_allow_html=True)
            elif step_num == current_step:
                st.markdown(f"<div style='text-align:center'><span style='font-size:1.2em'>🔵</span><br><small><b>{name}</b></small></div>", unsafe_allow_html=True)
            else:
                st.markdown(f"<div style='text-align:center; opacity:0.4'><span style='font-size:1.2em'>⚪</span><br><small>{name}</small></div>", unsafe_allow_html=True)


def get_worker_by_tag(tag: str):
    """Buscar trabajador por TAG"""
    db = get_database()
    worker = db.get_worker_by_tag(tag.upper())
    if worker:
        return worker
    for w in DEMO_WORKERS:
        if w["tag_code"].upper() == tag.upper():
            return w
    return None


def render_step_1_tag():
    """Step 1: Worker identification by TAG"""
    st.markdown("### 👤 Identificación del Trabajador")

    col1, col2 = st.columns([2, 1])

    with col1:
        tag_input = st.text_input(
            "Ingresa tu código TAG:",
            placeholder="Ej: MIN-2345",
            max_chars=10,
            key="tag_input"
        ).upper()

    with col2:
        st.markdown("<br>", unsafe_allow_html=True)
        with st.expander("TAGs de prueba"):
            st.caption("MIN-2345, MIN-3456, MIN-4567, MIN-5678, MIN-6789")

    if tag_input and len(tag_input) >= 4:
        worker = get_worker_by_tag(tag_input)
        if worker:
            st.session_state.worker = worker
            st.session_state.location = DEMO_LOCATIONS[0]  # Ubicación por defecto

            st.markdown(f"""
            <div class="worker-card">
                <h4>👤 {worker.get('name', 'N/A')}</h4>
                <p><b>Cargo:</b> {worker.get('cargo', 'N/A')}</p>
                <p><b>Área:</b> {worker.get('area', 'N/A')}</p>
                <p><b>Antigüedad:</b> {worker.get('antiguedad', 'N/A')}</p>
                <p><b>📍 Ubicación:</b> {st.session_state.location.get('name', 'N/A')} - Nivel {st.session_state.location.get('nivel', 'N/A')}</p>
            </div>
            """, unsafe_allow_html=True)

            if st.button("📸 Continuar a Captura de Foto →", type="primary", use_container_width=True):
                st.session_state.step = 2
                st.rerun()
        else:
            st.error("❌ TAG no encontrado. Verifica el código.")


def render_step_2_photo():
    """Step 2: Photo capture"""
    st.markdown("### 📸 Captura del Incidente")

    # Info del trabajador
    if st.session_state.worker:
        st.markdown(f"""
        <div class="info-box">
            👤 <b>{st.session_state.worker['name']}</b> |
            📍 {st.session_state.location.get('name', 'N/A')}
        </div>
        """, unsafe_allow_html=True)

    st.markdown("**Toma una foto clara del incidente o condición insegura:**")

    photo = st.camera_input("Capturar foto", key="camera_input", label_visibility="collapsed")

    if photo:
        photo_bytes = photo.getvalue()
        st.session_state.photo = photo_bytes
        st.success("✅ Foto capturada")

    # Navigation
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Volver a TAG", use_container_width=True):
            st.session_state.step = 1
            st.rerun()
    with col2:
        if st.button("🎤 Continuar a Descripción →", type="primary", use_container_width=True, disabled=not st.session_state.photo):
            st.session_state.step = 3
            st.rerun()

    if not st.session_state.photo:
        st.caption("📸 Captura una foto del incidente para continuar")


def render_step_3_audio():
    """Step 3: Audio recording and description"""
    st.markdown("### 🎤 Describe lo que Viste")

    # Info del trabajador
    if st.session_state.worker:
        st.markdown(f"""
        <div class="info-box">
            👤 <b>{st.session_state.worker['name']}</b> |
            📍 {st.session_state.location.get('name', 'N/A')}
        </div>
        """, unsafe_allow_html=True)

    # Foto capturada (compacta, no ocupa toda la pantalla)
    if st.session_state.photo:
        st.image(st.session_state.photo, caption="Foto capturada", width=250)

    st.markdown("""
    **Describe con tus propias palabras:**
    - ¿Qué viste?  ¿Dónde exactamente?  ¿Hay riesgo inmediato?

    *Habla naturalmente, como le contarías a un compañero.*
    """)

    st.markdown("---")

    # Audio recording
    st.markdown("**🎤 Graba tu descripción:**")
    audio = st.audio_input("Grabar audio", key="audio_recorder", label_visibility="collapsed")

    if audio:
        st.session_state.audio = audio.getvalue()
        st.audio(audio)

        # Transcribir
        with st.spinner("Transcribiendo audio..."):
            try:
                stt = get_speech_to_text()
                transcription = stt.transcribe(audio.getvalue())
                if transcription and not transcription.startswith("[Modo Demo]"):
                    st.session_state.transcription = transcription
                    st.success("✅ Transcripción completada")
                    st.write(f"📝 *\"{transcription}\"*")
            except:
                st.warning("No se pudo transcribir automáticamente. Escribe tu descripción abajo.")

    # Manual input as backup
    st.markdown("---")
    st.markdown("**O escribe tu descripción directamente:**")
    manual_desc = st.text_area(
        "Descripción",
        placeholder="Ej: Encontré un cable pelado cerca de la rampa del nivel 5, estaba echando chispas. El área estaba sin señalizar...",
        height=120,
        key="manual_description",
        label_visibility="collapsed"
    )

    if manual_desc:
        st.session_state.transcription = manual_desc

    # Navigation
    st.markdown("---")
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Volver a Foto", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with col2:
        has_description = st.session_state.transcription and len(st.session_state.transcription.strip()) > 5
        if st.button("🚀 Generar Reporte con IA →", type="primary", use_container_width=True, disabled=not has_description):
            generate_and_send_report()

    if not has_description:
        st.caption("⚠️ Graba o escribe una descripción del incidente para continuar")


def generate_and_send_report():
    """Generate report with AI and send"""
    with st.spinner("🤖 Analizando foto y audio con IA..."):
        try:
            # Analizar imagen con IA
            photo_analysis = None
            if st.session_state.photo and is_vision_available():
                photo_analysis = analyze_image(st.session_state.photo)

            # Generate AI report
            ai_report = generate_professional_report(
                audio_transcription=st.session_state.transcription,
                image_analysis=photo_analysis,
                worker_info=st.session_state.worker,
                location_info=st.session_state.location
            )

            if ai_report:
                # Build final report
                final_report = {
                    **ai_report,
                    'worker_info': st.session_state.worker,
                    'location_info': st.session_state.location,
                    'transcripcion_audio': st.session_state.transcription,
                    'created_at': datetime.now().isoformat(),
                    'final_risk_level': ai_report.get('nivel_riesgo', 'MEDIO'),
                }

                # Save to database
                db = get_database()
                saved = db.create_report(final_report)
                if saved:
                    final_report['id'] = saved.get('id')
                    final_report['report_number'] = saved.get('report_number')

                st.session_state.ai_report = ai_report
                st.session_state.final_report = final_report

                # Generate PDF
                try:
                    pdf_bytes = generate_flash_report_pdf(final_report, st.session_state.photo)
                    st.session_state.pdf_bytes = pdf_bytes
                except Exception as e:
                    st.warning(f"Error generando PDF: {e}")

                # Send notifications
                try:
                    send_report_notifications(final_report, st.session_state.pdf_bytes)
                except:
                    pass

                st.session_state.step = 4
                st.rerun()
            else:
                st.error("Error al generar el reporte. Intenta de nuevo.")
        except Exception as e:
            st.error(f"Error: {e}")


def render_step_4_success():
    """Step 4: Success confirmation"""
    st.balloons()

    report = st.session_state.final_report

    if not report:
        st.error("No hay reporte para mostrar")
        if st.button("← Volver al inicio"):
            reset_report()
            st.rerun()
        return

    risk = report.get('final_risk_level', 'MEDIO')
    risk_config = RISK_LEVELS.get(risk, RISK_LEVELS['MEDIO'])

    st.success("✅ Reporte enviado exitosamente")

    st.markdown(f"""
    ### Reporte #{report.get('report_number', 'N/A')}

    **Nivel de Riesgo:** {risk_config['icon']} {risk}

    **Reportante:** {report.get('worker_info', {}).get('name', 'N/A')}

    **Ubicación:** {report.get('location_info', {}).get('name', 'N/A')}

    ---
    """)

    st.markdown("**📝 Tu descripción original:**")
    st.info(report.get('transcripcion_audio', 'N/A'))

    st.markdown("**🤖 Análisis técnico (IA):**")
    st.write(report.get('descripcion_tecnica', 'N/A'))

    st.markdown("---")

    st.markdown("**⚡ Acciones inmediatas recomendadas:**")
    acciones = report.get('acciones_inmediatas', [])
    if isinstance(acciones, list):
        for a in acciones:
            st.write(f"• {a}")
    else:
        st.write(acciones)

    st.markdown("---")

    # PDF Download
    if st.session_state.pdf_bytes:
        filename = get_pdf_filename(report)
        st.download_button(
            label="📥 Descargar Reporte PDF",
            data=st.session_state.pdf_bytes,
            file_name=filename,
            mime="application/pdf",
            type="primary",
            use_container_width=True
        )

    st.markdown("---")

    # New report button
    if st.button("➕ Crear Nuevo Reporte", type="primary", use_container_width=True):
        reset_report()
        st.rerun()


def render_sidebar():
    """Render sidebar"""
    with st.sidebar:
        st.markdown("### ℹ️ Información")

        db = get_database()
        if db.is_demo_mode():
            st.warning("🔧 **Modo Demo**")
        else:
            st.success("✅ **Conectado**")

        st.markdown("---")

        st.markdown("### 🔧 Sistema")

        if is_vision_available():
            st.write("🟢 Análisis de Imágenes")
        else:
            st.write("🔴 Análisis de Imágenes")

        if is_transcription_available():
            st.write("🟢 Transcripción de Audio")
        else:
            st.write("🔴 Transcripción de Audio")

        st.markdown("---")

        if st.button("🔄 Reiniciar", use_container_width=True):
            reset_report()
            st.rerun()

        st.markdown("---")
        st.caption("Safety Flash Pro v2.0")
        st.caption(f"📅 {datetime.now().strftime('%d/%m/%Y %H:%M')}")


def main():
    """Main application entry point"""
    init_session_state()
    init_ai()

    render_header()
    render_sidebar()
    render_step_indicator(st.session_state.step)

    st.markdown("---")

    if st.session_state.step == 1:
        render_step_1_tag()
    elif st.session_state.step == 2:
        render_step_2_photo()
    elif st.session_state.step == 3:
        render_step_3_audio()
    elif st.session_state.step == 4:
        render_step_4_success()


if __name__ == "__main__":
    main()
