"""
Safety_Flash Pro - Speech-to-Text Module
Transcripción de audio usando Gemini (sin OpenAI)
"""

import streamlit as st
from typing import Optional

from core.config import MINING_VOCABULARY, get_secrets

# Try to import Gemini
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


# Chilean mining vocabulary for better transcription
TRANSCRIPTION_CONTEXT = f"""Transcripción de reporte de incidente en mina subterránea chilena.
{MINING_VOCABULARY}

Términos adicionales:
- Fortificación: malla electrosoldada, pernos de anclaje, shotcrete, marcos metálicos
- Equipos LHD: scooptram, cargador frontal subterráneo
- Perforación: jumbo de perforación, barra de perforación, bit
- Tronadura: polvorín, explosivos, cordón detonante, fulminante
- EPP: casco minero, lámpara, autorrescatador, arnés de seguridad
"""


class SpeechToText:
    """Speech to Text handler using Gemini"""

    def __init__(self):
        self.client = None
        self.available = False
        self._initialize()

    def _initialize(self):
        """Initialize Gemini client for audio transcription"""
        secrets = get_secrets()

        if GEMINI_AVAILABLE and secrets.get("GEMINI_API_KEY"):
            try:
                self.client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
                self.available = True
            except Exception as e:
                st.warning(f"Error inicializando Gemini para audio: {e}")
                self.available = False
        else:
            self.available = False

    def transcribe(self, audio_bytes: bytes, language: str = "es") -> Optional[str]:
        """
        Transcribe audio to text using Gemini

        Args:
            audio_bytes: Audio file content in bytes
            language: Language code (default: Spanish)

        Returns:
            Transcribed text or None if failed
        """
        if not self.available or not self.client:
            return self._mock_transcription()

        try:
            audio_part = types.Part.from_bytes(
                data=audio_bytes,
                mime_type="audio/wav"
            )

            prompt = f"""Transcribe el siguiente audio de un trabajador minero chileno reportando un incidente de seguridad.

Contexto para mejorar la transcripción:
{TRANSCRIPTION_CONTEXT}

IMPORTANTE:
- Transcribe exactamente lo que dice el trabajador
- Mantén el lenguaje natural (puede incluir jerga chilena)
- Si hay ruido de fondo o partes inaudibles, indica [inaudible]
- Responde SOLO con la transcripción, sin explicaciones adicionales"""

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, audio_part]
            )

            return response.text.strip()

        except Exception as e:
            st.warning(f"Error en transcripción: {e}")
            return self._mock_transcription()

    def _mock_transcription(self) -> str:
        """Return mock transcription for demo mode"""
        return "[Modo Demo] Ingrese la descripción del incidente manualmente en el campo de texto."


# Singleton instance (sin cache para permitir reinicialización)
def get_speech_to_text() -> SpeechToText:
    """Get or create SpeechToText instance"""
    if "speech_to_text" not in st.session_state:
        st.session_state.speech_to_text = SpeechToText()
    return st.session_state.speech_to_text


def process_audio_input(audio_value) -> Optional[str]:
    """
    Process audio input from Streamlit audio_input widget

    Args:
        audio_value: Value from st.audio_input()

    Returns:
        Transcribed text or None
    """
    if audio_value is None:
        return None

    stt = get_speech_to_text()

    if stt.available:
        return stt.transcribe(audio_value.getvalue())
    else:
        return stt._mock_transcription()


def is_transcription_available() -> bool:
    """Check if audio transcription is available"""
    stt = get_speech_to_text()
    return stt.available
