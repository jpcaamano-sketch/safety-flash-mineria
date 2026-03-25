"""
Safety_Flash Pro - Audio Recorder Component
Grabación y transcripción de descripciones de incidentes
"""

import streamlit as st
from typing import Optional, Tuple

from core.speech import get_speech_to_text, is_transcription_available


def render_audio_recorder() -> Tuple[Optional[bytes], Optional[str]]:
    """
    Render audio recording component with transcription

    Returns:
        Tuple of (audio_bytes, transcription_text)
    """
    st.subheader("🎤 Descripción del Incidente")

    # Check if transcription is available
    transcription_available = is_transcription_available()

    if transcription_available:
        st.caption("Graba una descripción del incidente. Habla naturalmente, la IA convertirá tu descripción a lenguaje técnico.")
    else:
        st.caption("Graba o escribe una descripción del incidente.")
        st.warning("⚠️ Transcripción automática no disponible. Ingresa la descripción manualmente.")

    # Audio recording
    audio = st.audio_input(
        "Grabar descripción",
        key="incident_audio",
        help="Presiona para grabar y describe el incidente"
    )

    transcription = None

    if audio:
        # Show audio player
        st.audio(audio, format="audio/wav")

        # Transcribe if available
        if transcription_available:
            with st.spinner("🤖 Transcribiendo audio..."):
                stt = get_speech_to_text()
                transcription = stt.transcribe(audio.getvalue())

            if transcription:
                st.success("✅ Transcripción completada")
                st.text_area(
                    "Transcripción",
                    transcription,
                    key="transcription_display",
                    disabled=True,
                    height=100
                )
            else:
                st.warning("No se pudo transcribir el audio. Por favor, ingresa la descripción manualmente.")

    # Manual description input (always available as fallback)
    st.markdown("---")
    manual_description = st.text_area(
        "O escribe la descripción manualmente:",
        placeholder="Describe qué pasó, dónde, cuándo y cualquier detalle relevante...",
        key="manual_description",
        height=100
    )

    # Return audio and best available transcription
    audio_bytes = audio.getvalue() if audio else None
    final_transcription = transcription or manual_description or None

    return audio_bytes, final_transcription


def render_compact_audio_recorder() -> Tuple[Optional[bytes], Optional[str]]:
    """
    Compact audio recorder for streamlined workflow

    Returns:
        Tuple of (audio_bytes, transcription_text)
    """
    col1, col2 = st.columns([2, 3])

    with col1:
        audio = st.audio_input(
            "🎤 Grabar",
            key="compact_audio"
        )

    transcription = None

    if audio:
        with col2:
            st.audio(audio, format="audio/wav")

        if is_transcription_available():
            with st.spinner("Transcribiendo..."):
                stt = get_speech_to_text()
                transcription = stt.transcribe(audio.getvalue())

            if transcription:
                st.caption(f"📝 {transcription[:100]}..." if len(transcription) > 100 else f"📝 {transcription}")

    # Fallback text input
    if not transcription:
        transcription = st.text_input(
            "Descripción",
            placeholder="Describe el incidente...",
            key="compact_description",
            label_visibility="collapsed"
        )

    audio_bytes = audio.getvalue() if audio else None

    return audio_bytes, transcription


def render_description_input_only() -> str:
    """
    Render text-only description input

    Returns:
        Description text
    """
    return st.text_area(
        "Descripción del incidente",
        placeholder="Describe detalladamente:\n- ¿Qué observaste?\n- ¿Dónde exactamente?\n- ¿Hay personas o equipos en riesgo?\n- ¿Qué acciones tomaste?",
        key="description_only",
        height=150
    )


def get_description_tips():
    """Return tips for good incident descriptions"""
    return """
    **Tips para una buena descripción:**
    - 📍 Sé específico sobre la ubicación exacta
    - ⏰ Menciona cuándo ocurrió o fue detectado
    - 👁️ Describe lo que viste, no suposiciones
    - ⚠️ Indica si hay peligro inmediato
    - 👷 Menciona si hay personas afectadas o en riesgo
    - 🔧 Describe qué acciones tomaste (si alguna)
    """
