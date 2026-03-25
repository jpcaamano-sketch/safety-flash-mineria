"""
Safety_Flash Pro - Versión Móvil
Flujo: TAG → Foto → Audio → IA genera reporte
"""

import streamlit as st
from datetime import datetime

from core.config import RISK_LEVELS, DEMO_WORKERS, DEMO_LOCATIONS
from core.database import get_database
from core.ai_client import init_ai, analyze_image, generate_professional_report
from core.speech import get_speech_to_text
from utils.pdf_generator import generate_flash_report_pdf
from core.notifications import send_report_notifications

st.set_page_config(
    page_title="Safety Flash",
    page_icon="⚠️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

st.markdown("""
<style>
    #MainMenu, footer, header {visibility: hidden;}
    .block-container {padding: 0.5rem; max-width: 100%;}
    .stButton>button {
        width: 100%;
        height: 70px;
        font-size: 1.3em;
        border-radius: 15px;
        margin: 10px 0;
    }
    .stTextInput>div>div>input {
        font-size: 1.8em !important;
        text-align: center;
        letter-spacing: 4px;
        text-transform: uppercase;
        height: 60px;
    }
    .header-mini {
        text-align: center;
        background: linear-gradient(135deg, #ff4b4b, #ff6b6b);
        color: white;
        padding: 10px;
        border-radius: 10px;
        margin-bottom: 10px;
    }
    .step-badge {
        background: #333;
        color: white;
        padding: 5px 15px;
        border-radius: 20px;
        font-size: 0.9em;
    }
    .worker-info {
        background: #f0f2f6;
        padding: 10px;
        border-radius: 10px;
        margin: 10px 0;
    }
</style>
""", unsafe_allow_html=True)


def init_session():
    """Inicializar estado"""
    defaults = {
        "step": 1,
        "tag": "",
        "worker": None,
        "location": None,
        "photo": None,
        "photo_analysis": None,
        "transcription": None,
        "report": None,
        "pdf": None,
    }
    for key, value in defaults.items():
        if key not in st.session_state:
            st.session_state[key] = value


def reset_all():
    """Reiniciar todo"""
    for key in ["step", "tag", "worker", "location", "photo", "photo_analysis", "transcription", "report", "pdf"]:
        if key == "step":
            st.session_state[key] = 1
        elif key == "tag":
            st.session_state[key] = ""
        else:
            st.session_state[key] = None


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


def step_1_tag():
    """Paso 1: Ingresar TAG"""
    st.markdown('<div class="header-mini"><h2>⚠️ Safety Flash</h2></div>', unsafe_allow_html=True)
    st.markdown('<center><span class="step-badge">Paso 1 de 3: Tu TAG</span></center>', unsafe_allow_html=True)

    tag = st.text_input("", placeholder="MIN-2345", max_chars=10, key="tag_input", label_visibility="collapsed")

    with st.expander("TAGs demo", expanded=False):
        st.caption("MIN-2345, MIN-3456, MIN-4567, MIN-5678, MIN-6789")

    if tag and len(tag) >= 4:
        worker = get_worker_by_tag(tag)
        if worker:
            st.session_state.tag = tag.upper()
            st.session_state.worker = worker
            # Ubicación por defecto del trabajador
            st.session_state.location = DEMO_LOCATIONS[0]

            st.markdown('<div class="worker-info">', unsafe_allow_html=True)
            st.write(f"👤 **{worker.get('name', 'N/A')}**")
            st.write(f"📋 {worker.get('cargo', 'N/A')}")
            st.write(f"📍 {st.session_state.location.get('name', 'N/A')}")
            st.markdown('</div>', unsafe_allow_html=True)

            if st.button("📸 Tomar Foto →", type="primary"):
                st.session_state.step = 2
                st.rerun()
        else:
            st.error("TAG no encontrado")


def step_2_photo():
    """Paso 2: Capturar foto"""
    st.markdown('<div class="header-mini"><h3>📸 Foto del Incidente</h3></div>', unsafe_allow_html=True)
    st.markdown('<center><span class="step-badge">Paso 2 de 3: Captura</span></center>', unsafe_allow_html=True)

    # Info del trabajador
    if st.session_state.worker:
        st.caption(f"👤 {st.session_state.worker.get('name', '')} | 📍 {st.session_state.location.get('name', '')}")

    photo = st.camera_input("", key="camera", label_visibility="collapsed")

    if photo:
        st.session_state.photo = photo.getvalue()
        st.success("✅ Foto capturada")
        st.session_state.step = 3
        st.rerun()

    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Volver", use_container_width=True):
            st.session_state.step = 1
            st.rerun()


def step_3_audio():
    """Paso 3: Grabar descripción de audio"""
    st.markdown('<div class="header-mini"><h3>🎤 Describe qué pasó</h3></div>', unsafe_allow_html=True)
    st.markdown('<center><span class="step-badge">Paso 3 de 3: Tu relato</span></center>', unsafe_allow_html=True)

    # Mostrar foto capturada
    if st.session_state.photo:
        st.image(st.session_state.photo, width=200)

    st.markdown("**Habla con tus palabras, como le contarías a un compañero:**")

    audio = st.audio_input("", key="audio_rec", label_visibility="collapsed")

    transcription = None

    if audio:
        st.audio(audio)
        with st.spinner("Transcribiendo..."):
            try:
                stt = get_speech_to_text()
                transcription = stt.transcribe(audio.getvalue())
                if transcription and not transcription.startswith("[Modo Demo]"):
                    st.session_state.transcription = transcription
                    st.success("Transcripción lista")
                    st.write(f"📝 *\"{transcription}\"*")
            except Exception as e:
                st.warning("No se pudo transcribir. Escribe tu descripción abajo.")

    # Input manual como respaldo
    st.markdown("---")
    st.caption("O escribe directamente:")
    manual = st.text_area("", placeholder="Ej: Encontré un cable pelado cerca de la rampa, estaba echando chispas...", height=100, key="manual_input", label_visibility="collapsed")

    if manual:
        st.session_state.transcription = manual

    # Botones
    col1, col2 = st.columns(2)
    with col1:
        if st.button("← Foto", use_container_width=True):
            st.session_state.step = 2
            st.rerun()
    with col2:
        has_desc = st.session_state.transcription and len(st.session_state.transcription.strip()) > 5
        if st.button("🚀 Generar Reporte", type="primary", use_container_width=True, disabled=not has_desc):
            process_and_send()

    if not has_desc:
        st.caption("⚠️ Graba o escribe una descripción para continuar")


def process_and_send():
    """Procesar con IA y generar reporte"""
    with st.spinner("🤖 Analizando foto y audio con IA..."):
        try:
            # Analizar imagen con IA
            photo_analysis = None
            if st.session_state.photo:
                try:
                    photo_analysis = analyze_image(st.session_state.photo)
                except:
                    pass

            # Generar reporte con IA
            report = generate_professional_report(
                audio_transcription=st.session_state.transcription,
                image_analysis=photo_analysis,
                worker_info=st.session_state.worker,
                location_info=st.session_state.location
            )

            if report:
                # Completar datos del reporte
                report['worker_info'] = st.session_state.worker
                report['location_info'] = st.session_state.location
                report['transcripcion_audio'] = st.session_state.transcription  # Guardar transcripción original
                report['created_at'] = datetime.now().isoformat()
                report['final_risk_level'] = report.get('nivel_riesgo', 'MEDIO')

                # Guardar en BD
                db = get_database()
                saved = db.create_report(report)
                if saved:
                    report['report_number'] = saved.get('report_number')
                    report['id'] = saved.get('id')

                st.session_state.report = report

                # Generar PDF
                try:
                    pdf = generate_flash_report_pdf(report, st.session_state.photo)
                    st.session_state.pdf = pdf
                except Exception as e:
                    st.warning(f"Error generando PDF: {e}")

                # Enviar notificaciones
                try:
                    send_report_notifications(report, st.session_state.pdf)
                except:
                    pass

                st.session_state.step = 4
                st.rerun()
            else:
                st.error("Error generando reporte. Intenta de nuevo.")
        except Exception as e:
            st.error(f"Error: {e}")


def step_4_done():
    """Paso 4: Reporte completado"""
    report = st.session_state.report

    if not report:
        st.error("Error: No hay reporte")
        if st.button("Reiniciar"):
            reset_all()
            st.rerun()
        return

    st.balloons()

    risk = report.get('final_risk_level', 'MEDIO')
    risk_config = RISK_LEVELS.get(risk, RISK_LEVELS['MEDIO'])

    st.markdown(f"""
    <div style="text-align:center; padding:20px;">
        <h1>✅</h1>
        <h2>Reporte Enviado</h2>
        <p style="font-size:1.3em">{risk_config['icon']} Riesgo: <b>{risk}</b></p>
        <p>Reporte #{report.get('report_number', 'N/A')}</p>
    </div>
    """, unsafe_allow_html=True)

    # Mostrar resumen del reporte
    with st.expander("📋 Ver Reporte Generado", expanded=True):
        st.markdown("**Tu descripción original:**")
        st.info(report.get('transcripcion_audio', 'N/A'))

        st.markdown("**Análisis técnico (IA):**")
        st.write(report.get('descripcion_tecnica', 'N/A'))

        if report.get('acciones_inmediatas'):
            st.markdown("**Acciones inmediatas:**")
            for a in report['acciones_inmediatas']:
                st.write(f"• {a}")

    # Descargar PDF
    if st.session_state.pdf:
        st.download_button(
            "📥 Descargar PDF",
            data=st.session_state.pdf,
            file_name=f"ReporteFlash_{report.get('report_number', 'R')}.pdf",
            mime="application/pdf",
            use_container_width=True,
            type="primary"
        )

    st.markdown("---")

    if st.button("➕ Nuevo Reporte", use_container_width=True):
        reset_all()
        st.rerun()


def main():
    init_session()
    init_ai()

    # Indicador de pasos
    steps = ["1️⃣ TAG", "2️⃣ Foto", "3️⃣ Audio", "✅"]
    current = st.session_state.step
    cols = st.columns(4)
    for i, (col, step) in enumerate(zip(cols, steps)):
        with col:
            if i + 1 < current:
                st.markdown(f"<center style='color:green'>✓</center>", unsafe_allow_html=True)
            elif i + 1 == current:
                st.markdown(f"<center><b>{step}</b></center>", unsafe_allow_html=True)
            else:
                st.markdown(f"<center style='opacity:0.4'>{step}</center>", unsafe_allow_html=True)

    st.markdown("---")

    if st.session_state.step == 1:
        step_1_tag()
    elif st.session_state.step == 2:
        step_2_photo()
    elif st.session_state.step == 3:
        step_3_audio()
    elif st.session_state.step == 4:
        step_4_done()


if __name__ == "__main__":
    main()
