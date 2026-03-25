"""
Safety_Flash Pro - Vision Module
Análisis de imágenes de incidentes usando Gemini Vision
"""

import streamlit as st
import json
import re
from typing import Optional, Dict, List

from core.config import INCIDENT_CATEGORIES, get_secrets

# Try to import new Gemini package
try:
    from google import genai
    from google.genai import types
    GEMINI_AVAILABLE = True
except ImportError:
    GEMINI_AVAILABLE = False


class VisionAnalyzer:
    """Image analysis for mining incidents"""

    def __init__(self):
        self.client = None
        self.available = False
        self._initialize()

    def _initialize(self):
        """Initialize Gemini Vision client"""
        secrets = get_secrets()

        if GEMINI_AVAILABLE and secrets.get("GEMINI_API_KEY"):
            try:
                self.client = genai.Client(api_key=secrets["GEMINI_API_KEY"])
                self.available = True
            except Exception as e:
                st.warning(f"Error inicializando Gemini Vision: {e}")
                self.available = False
        else:
            self.available = False

    def analyze_incident(self, image_bytes: bytes) -> Optional[Dict]:
        """
        Analyze incident image

        Args:
            image_bytes: Image content in bytes (JPEG/PNG)

        Returns:
            Analysis result with description, hazards, category, urgency
        """
        if not self.available or not self.client:
            return self._mock_analysis()

        try:
            categories_text = "\n".join([
                f"- {code}: {cat['name']} - Palabras clave: {', '.join(cat['keywords'][:5])}"
                for code, cat in INCIDENT_CATEGORIES.items()
            ])

            prompt = f"""Eres un experto en seguridad minera analizando una imagen de un posible incidente en mina subterránea.

CATEGORÍAS DISPONIBLES:
{categories_text}

ANALIZA LA IMAGEN E IDENTIFICA:
1. Descripción detallada de lo que se observa
2. Peligros o riesgos potenciales visibles
3. Categoría del incidente (usa el código)
4. Nivel de urgencia basado en el riesgo observado

CRITERIOS DE URGENCIA:
- BAJO: Situación menor, no representa peligro inmediato
- MEDIO: Requiere atención pero no es urgente
- ALTO: Peligro significativo, requiere acción pronta
- CRITICO: Peligro grave e inminente, requiere acción inmediata

Responde ÚNICAMENTE con JSON válido:
{{
    "descripcion_visual": "Descripción detallada de lo observado en la imagen",
    "peligros_detectados": ["Peligro 1", "Peligro 2", "Peligro 3"],
    "elementos_visibles": ["Elemento 1", "Elemento 2"],
    "categoria_sugerida": "GEO",
    "categoria_nombre": "Geomecánico",
    "urgencia": "MEDIO",
    "justificacion_urgencia": "Explicación del nivel de urgencia",
    "confianza": 0.85,
    "recomendaciones_inmediatas": ["Acción 1", "Acción 2"]
}}"""

            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg"
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, image_part]
            )

            return self._parse_response(response.text)

        except Exception as e:
            st.warning(f"Error en análisis de imagen: {e}")
            return self._mock_analysis()

    def detect_hazards(self, image_bytes: bytes) -> List[Dict]:
        """
        Detect specific hazards in image

        Returns list of detected hazards with locations and severity
        """
        if not self.available or not self.client:
            return []

        try:
            prompt = """Analiza esta imagen de mina subterránea e identifica TODOS los peligros visibles.

Para cada peligro encontrado, indica:
1. Tipo de peligro
2. Ubicación en la imagen (arriba/abajo/izquierda/derecha/centro)
3. Severidad (1-5)
4. Descripción breve

Responde con JSON:
{
    "hazards": [
        {
            "type": "tipo de peligro",
            "location": "ubicación en imagen",
            "severity": 3,
            "description": "descripción"
        }
    ]
}"""

            image_part = types.Part.from_bytes(
                data=image_bytes,
                mime_type="image/jpeg"
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, image_part]
            )

            result = self._parse_response(response.text)
            return result.get("hazards", []) if result else []

        except Exception:
            return []

    def compare_before_after(self, before_bytes: bytes, after_bytes: bytes) -> Optional[Dict]:
        """
        Compare before/after images of an incident area

        Returns comparison analysis
        """
        if not self.available or not self.client:
            return None

        try:
            prompt = """Compara estas dos imágenes de un área de mina subterránea.
La primera imagen es el ANTES y la segunda es el DESPUÉS.

Identifica:
1. Cambios visibles entre ambas imágenes
2. Mejoras en seguridad (si las hay)
3. Nuevos riesgos (si los hay)
4. Estado de resolución del incidente

Responde con JSON:
{
    "cambios_detectados": ["cambio 1", "cambio 2"],
    "mejoras": ["mejora 1"],
    "nuevos_riesgos": [],
    "estado_resolucion": "completo/parcial/sin_cambios",
    "recomendaciones": ["recomendación 1"]
}"""

            before_part = types.Part.from_bytes(
                data=before_bytes,
                mime_type="image/jpeg"
            )
            after_part = types.Part.from_bytes(
                data=after_bytes,
                mime_type="image/jpeg"
            )

            response = self.client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[prompt, before_part, after_part]
            )

            return self._parse_response(response.text)

        except Exception as e:
            st.warning(f"Error en comparación de imágenes: {e}")
            return None

    def _parse_response(self, text: str) -> Optional[Dict]:
        """Parse JSON from model response"""
        text = text.strip()

        # Remove markdown code blocks
        if text.startswith("```"):
            text = re.sub(r'^```(?:json)?\n?', '', text)
            text = re.sub(r'\n?```$', '', text)

        try:
            return json.loads(text)
        except json.JSONDecodeError:
            # Try to find JSON in text
            json_match = re.search(r'\{[\s\S]*\}', text)
            if json_match:
                try:
                    return json.loads(json_match.group())
                except json.JSONDecodeError:
                    pass
        return None

    def _mock_analysis(self) -> Dict:
        """Return mock analysis for demo mode"""
        return {
            "descripcion_visual": "Imagen capturada en ambiente de mina subterránea. Se requiere API de Gemini para análisis detallado.",
            "peligros_detectados": ["Requiere análisis con IA para detectar peligros específicos"],
            "elementos_visibles": ["Ambiente minero"],
            "categoria_sugerida": "GEO",
            "categoria_nombre": "Geomecánico",
            "urgencia": "MEDIO",
            "justificacion_urgencia": "Nivel por defecto hasta completar análisis con IA",
            "confianza": 0.3,
            "recomendaciones_inmediatas": ["Completar descripción manual del incidente"]
        }


# Singleton instance (sin cache para permitir reinicialización con nuevas API keys)
def get_vision_analyzer() -> VisionAnalyzer:
    """Get or create VisionAnalyzer instance"""
    if "vision_analyzer" not in st.session_state:
        st.session_state.vision_analyzer = VisionAnalyzer()
    return st.session_state.vision_analyzer


def quick_analyze_image(image_bytes: bytes) -> Optional[Dict]:
    """Quick helper to analyze an image"""
    analyzer = get_vision_analyzer()
    return analyzer.analyze_incident(image_bytes)


def is_vision_available() -> bool:
    """Check if vision analysis is available"""
    analyzer = get_vision_analyzer()
    return analyzer.available
