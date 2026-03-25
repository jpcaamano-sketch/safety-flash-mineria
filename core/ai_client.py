"""
Safety_Flash Pro - AI Client Module
Cliente de IA para análisis de imágenes, transcripción y generación de reportes
"""

import streamlit as st
import json
import re
import tempfile
import os
import base64
from datetime import datetime
from typing import Optional, Dict

from core.config import MINING_VOCABULARY, INCIDENT_CATEGORIES, get_secrets

# Try to import AI libraries - new google.genai package
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False

# OpenAI removed - using only Gemini for all AI functionality

# Global client
_gemini_client = None


def init_ai() -> bool:
    """Initialize AI clients"""
    global _gemini_client
    secrets = get_secrets()
    initialized = False

    if GEMINI_AVAILABLE and secrets.get("GEMINI_API_KEY"):
        try:
            _gemini_client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
            initialized = True
        except Exception as e:
            st.warning(f"Error inicializando Gemini: {e}")

    return initialized


def get_gemini_client():
    """Get or create Gemini client"""
    global _gemini_client
    if _gemini_client is None:
        init_ai()
    return _gemini_client


def parse_json_response(text: str) -> Optional[Dict]:
    """Parse JSON from AI response, handling markdown code blocks"""
    # Remove markdown code blocks if present
    text = text.strip()
    if text.startswith("```"):
        # Remove opening ```json or ```
        text = re.sub(r'^```(?:json)?\n?', '', text)
        # Remove closing ```
        text = re.sub(r'\n?```$', '', text)

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        # Try to find JSON in the text
        json_match = re.search(r'\{[\s\S]*\}', text)
        if json_match:
            try:
                return json.loads(json_match.group())
            except json.JSONDecodeError:
                pass
    return None


def analyze_image(image_bytes: bytes) -> Optional[Dict]:
    """
    Analyze incident image using Gemini Vision
    Returns: description, detected hazards, urgency level
    """
    secrets = get_secrets()
    client = get_gemini_client()

    if not GEMINI_AVAILABLE or not client or not secrets.get("GEMINI_API_KEY"):
        return _mock_image_analysis()

    try:
        prompt = """Eres un experto en seguridad minera. Analiza esta imagen de un incidente en mina subterránea.

Identifica:
1. ¿Qué se observa en la imagen?
2. ¿Qué peligros o riesgos detectas?
3. ¿Qué categoría de incidente es? (Geomecánico, Equipos, Energía, Conducta, Ambiente)
4. Nivel de urgencia (BAJO, MEDIO, ALTO, CRITICO)

Responde SOLO con JSON válido, sin texto adicional:
{
    "descripcion_visual": "descripción detallada de lo observado",
    "peligros_detectados": ["peligro 1", "peligro 2"],
    "categoria_sugerida": "GEO/EQU/ENE/CON/AMB",
    "categoria_nombre": "nombre de la categoría",
    "urgencia": "BAJO/MEDIO/ALTO/CRITICO",
    "confianza": 0.85
}"""

        # Create image part for the new API
        image_part = types.Part.from_bytes(
            data=image_bytes,
            mime_type="image/jpeg"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[prompt, image_part]
        )

        result = parse_json_response(response.text)
        if result:
            return result
        else:
            st.warning("No se pudo parsear la respuesta de análisis de imagen")
            return _mock_image_analysis()

    except Exception as e:
        st.warning(f"Error en análisis de imagen: {e}")
        return _mock_image_analysis()


def _mock_image_analysis() -> Dict:
    """Mock image analysis for demo mode"""
    return {
        "descripcion_visual": "Se observa una situación en ambiente de mina subterránea que requiere evaluación",
        "peligros_detectados": ["Requiere inspección visual directa", "Evaluación de condiciones del área"],
        "categoria_sugerida": "GEO",
        "categoria_nombre": "Geomecánico",
        "urgencia": "MEDIO",
        "confianza": 0.5
    }


def transcribe_audio(audio_bytes: bytes) -> Optional[str]:
    """
    Transcribe audio using Gemini
    Optimized for Chilean mining jargon
    """
    return _transcribe_with_gemini(audio_bytes)


def _transcribe_with_gemini(audio_bytes: bytes) -> Optional[str]:
    """Fallback transcription using Gemini"""
    secrets = get_secrets()
    client = get_gemini_client()

    if not GEMINI_AVAILABLE or not client or not secrets.get("GEMINI_API_KEY"):
        return _mock_transcription()

    try:
        audio_part = types.Part.from_bytes(
            data=audio_bytes,
            mime_type="audio/wav"
        )

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=[
                f"Transcribe el siguiente audio de un trabajador minero chileno reportando un incidente. Contexto: {MINING_VOCABULARY}",
                audio_part
            ]
        )

        return response.text
    except Exception as e:
        st.warning(f"Error en transcripción con Gemini: {e}")
        return _mock_transcription()


def _mock_transcription() -> str:
    """Mock transcription for demo mode"""
    return "[Modo Demo] Ingrese la descripción del incidente manualmente en el campo de texto."


def generate_professional_report(
    audio_transcription: str,
    image_analysis: Optional[Dict],
    worker_info: Dict,
    location_info: Dict,
    manual_description: str = ""
) -> Optional[Dict]:
    """
    Generate professional report from:
    - Audio transcription (colloquial language)
    - Image analysis
    - Worker and location information
    """
    secrets = get_secrets()
    client = get_gemini_client()

    # Use manual description if transcription is mock
    description = manual_description if manual_description else audio_transcription

    if not GEMINI_AVAILABLE or not client or not secrets.get("GEMINI_API_KEY"):
        return _mock_report(description, image_analysis, worker_info, location_info)

    try:
        image_analysis_text = json.dumps(image_analysis, indent=2, ensure_ascii=False) if image_analysis else "No disponible"

        prompt = f"""Eres un experto en seguridad minera redactando un Flash Report oficial.

CONTEXTO:
- Reportante: {worker_info.get('name', 'N/A')} ({worker_info.get('cargo', 'N/A')})
- Ubicación: {location_info.get('name', 'N/A')} - Nivel {location_info.get('nivel', 'N/A')}
- Fecha/Hora: {datetime.now().strftime('%d/%m/%Y %H:%M')}

DESCRIPCIÓN DEL TRABAJADOR (puede incluir lenguaje coloquial):
"{description}"

ANÁLISIS DE IMAGEN:
{image_analysis_text}

TU TAREA:
1. Redacta una DESCRIPCIÓN TÉCNICA profesional (3-4 oraciones) basada en lo que el trabajador describió. Usa lenguaje técnico formal, mantén los hechos.

2. Evalúa el NIVEL DE RIESGO (BAJO/MEDIO/ALTO/CRITICO) considerando:
   - Potencial de daño a personas
   - Probabilidad de ocurrencia
   - Gravedad de consecuencias

3. Lista las ACCIONES INMEDIATAS (3-5 pasos) según protocolo de seguridad minera.

4. Clasifica la CATEGORÍA del incidente usando los códigos: GEO (Geomecánico), EQU (Equipos), ENE (Energía), CON (Conducta), AMB (Ambiente).

Responde SOLO con JSON válido:
{{
    "descripcion_tecnica": "Descripción profesional del incidente...",
    "nivel_riesgo": "ALTO",
    "justificacion_riesgo": "Explicación del nivel de riesgo asignado...",
    "acciones_inmediatas": ["1. Primera acción", "2. Segunda acción", "3. Tercera acción"],
    "categoria_codigo": "GEO",
    "categoria_nombre": "Geomecánico",
    "palabras_clave": ["palabra1", "palabra2", "palabra3"]
}}"""

        response = client.models.generate_content(
            model="gemini-2.5-flash",
            contents=prompt
        )
        result = parse_json_response(response.text)

        if result:
            return result
        else:
            st.warning("No se pudo parsear la respuesta del reporte")
            return _mock_report(description, image_analysis, worker_info, location_info)

    except Exception as e:
        st.warning(f"Error generando reporte: {e}")
        return _mock_report(description, image_analysis, worker_info, location_info)


def _mock_report(description: str, image_analysis: Optional[Dict], worker_info: Dict, location_info: Dict) -> Dict:
    """Generate mock report for demo mode"""
    # Detect category from description
    description_lower = description.lower() if description else ""
    detected_category = "GEO"
    detected_category_name = "Geomecánico"

    for code, cat in INCIDENT_CATEGORIES.items():
        for keyword in cat["keywords"]:
            if keyword in description_lower:
                detected_category = code
                detected_category_name = cat["name"]
                break

    return {
        "descripcion_tecnica": f"Se reporta incidente en {location_info.get('name', 'ubicación no especificada')}, Nivel {location_info.get('nivel', 'N/A')}. {description if description else 'Descripción pendiente de completar.'}",
        "nivel_riesgo": image_analysis.get("urgencia", "MEDIO") if image_analysis else "MEDIO",
        "justificacion_riesgo": "Nivel de riesgo asignado en base a la información disponible. Se requiere evaluación en terreno para confirmación.",
        "acciones_inmediatas": [
            "1. Delimitar y señalizar el área afectada",
            "2. Informar a supervisor de turno",
            "3. Evaluar condiciones de seguridad antes de intervenir",
            "4. Documentar con fotografías adicionales",
            "5. Completar formulario de seguimiento"
        ],
        "categoria_codigo": detected_category,
        "categoria_nombre": detected_category_name,
        "palabras_clave": ["incidente", "seguridad", "mina"]
    }


def classify_category(text: str) -> str:
    """Classify incident category based on text"""
    text_lower = text.lower()

    for code, cat in INCIDENT_CATEGORIES.items():
        for keyword in cat["keywords"]:
            if keyword in text_lower:
                return code

    return "GEO"  # Default to Geomechanical
