"""
Safety_Flash Pro - Configuration and Constants
Configuración central del sistema de reportes de incidentes mineros
"""

import streamlit as st
from dataclasses import dataclass
from typing import Dict, List

# Risk Level Configuration
RISK_LEVELS = {
    "BAJO": {"color": "#28a745", "icon": "🟢", "priority": 1},
    "MEDIO": {"color": "#ffc107", "icon": "🟡", "priority": 2},
    "ALTO": {"color": "#fd7e14", "icon": "🟠", "priority": 3},
    "CRITICO": {"color": "#dc3545", "icon": "🔴", "priority": 4},
}

# Incident Categories
INCIDENT_CATEGORIES = {
    "GEO": {
        "name": "Geomecánico",
        "icon": "🪨",
        "color": "#8B4513",
        "keywords": ["roca", "derrumbe", "caída", "planchón", "malla", "fortificación", "acuñadura", "shotcrete"],
        "notify_roles": ["jefe_turno", "geomecanico", "prevencionista"],
    },
    "EQU": {
        "name": "Equipos",
        "icon": "🚜",
        "color": "#FF8C00",
        "keywords": ["equipo", "scoop", "jumbo", "camión", "fuga", "hidráulico", "falla", "mecánico"],
        "notify_roles": ["jefe_turno", "mantenimiento"],
    },
    "ENE": {
        "name": "Energía",
        "icon": "⚡",
        "color": "#FFD700",
        "keywords": ["eléctrico", "cable", "tablero", "voltaje", "cortocircuito", "descarga"],
        "notify_roles": ["jefe_turno", "electrico", "prevencionista"],
    },
    "CON": {
        "name": "Conducta",
        "icon": "👷",
        "color": "#4169E1",
        "keywords": ["trabajador", "epp", "casco", "procedimiento", "conducta", "negligencia"],
        "notify_roles": ["jefe_turno", "supervisor_directo"],
    },
    "AMB": {
        "name": "Ambiente",
        "icon": "🌫️",
        "color": "#708090",
        "keywords": ["ventilación", "polvo", "gases", "temperatura", "humedad", "visibilidad", "agua"],
        "notify_roles": ["jefe_turno", "ventilacion", "prevencionista"],
    },
}

# Mining vocabulary for speech-to-text improvement
MINING_VOCABULARY = """
Vocabulario minero chileno para mejorar transcripción:
- Equipos: scoop, jumbo, camión tolva, LHD, dumper, perforadora
- Geomecánica: shotcrete, acuñadura, malla, perno, split set, planchón, cuña
- Infraestructura: galería, rampa, pique, chimenea, estocada, nivel, cruzado
- Ventilación: manga, ventilador, ducto, extractor
- Peligros: derrumbe, emanación, sismo, estallido de roca
- Jerga común: scoop, perno, malla, frente, labores
"""

# Demo Workers Data
DEMO_WORKERS = [
    {
        "id": "w1",
        "tag_code": "MIN-2345",
        "name": "Juan Pérez González",
        "rut": "12.345.678-9",
        "cargo": "Operador Scoop",
        "area": "Producción",
        "turno": "A",
        "antiguedad": "8 años",
        "empresa": "Minera Demo S.A.",
        "supervisor_email": "supervisor@minera.cl",
        "phone": "+56912345678",
        "status": "active",
    },
    {
        "id": "w2",
        "tag_code": "MIN-3456",
        "name": "Carlos Muñoz Silva",
        "rut": "13.456.789-0",
        "cargo": "Operador Jumbo",
        "area": "Desarrollo",
        "turno": "B",
        "antiguedad": "5 años",
        "empresa": "Minera Demo S.A.",
        "supervisor_email": "supervisor@minera.cl",
        "phone": "+56923456789",
        "status": "active",
    },
    {
        "id": "w3",
        "tag_code": "MIN-4567",
        "name": "Pedro Soto Rojas",
        "rut": "14.567.890-1",
        "cargo": "Fortificador",
        "area": "Geomecánica",
        "turno": "A",
        "antiguedad": "12 años",
        "empresa": "Minera Demo S.A.",
        "supervisor_email": "geomecanico@minera.cl",
        "phone": "+56934567890",
        "status": "active",
    },
    {
        "id": "w4",
        "tag_code": "MIN-5678",
        "name": "Miguel Fernández López",
        "rut": "15.678.901-2",
        "cargo": "Electricista",
        "area": "Mantenimiento",
        "turno": "B",
        "antiguedad": "3 años",
        "empresa": "Minera Demo S.A.",
        "supervisor_email": "mantenimiento@minera.cl",
        "phone": "+56945678901",
        "status": "active",
    },
    {
        "id": "w5",
        "tag_code": "MIN-6789",
        "name": "Roberto Díaz Martínez",
        "rut": "16.789.012-3",
        "cargo": "Jefe de Turno",
        "area": "Operaciones",
        "turno": "A",
        "antiguedad": "15 años",
        "empresa": "Minera Demo S.A.",
        "supervisor_email": "gerencia@minera.cl",
        "phone": "+56956789012",
        "status": "active",
    },
]

# Demo Locations Data
DEMO_LOCATIONS = [
    {"id": "l1", "code": "N-1400-GAL-01", "name": "Galería Principal", "nivel": "1400", "sector": "Norte", "tipo": "galeria"},
    {"id": "l2", "code": "N-1400-RAM-01", "name": "Rampa de Acceso", "nivel": "1400", "sector": "Norte", "tipo": "rampa"},
    {"id": "l3", "code": "N-1350-GAL-01", "name": "Galería Producción", "nivel": "1350", "sector": "Norte", "tipo": "galeria"},
    {"id": "l4", "code": "N-1350-EST-01", "name": "Estocada 1", "nivel": "1350", "sector": "Norte", "tipo": "estocada"},
    {"id": "l5", "code": "S-1400-GAL-01", "name": "Galería Sur", "nivel": "1400", "sector": "Sur", "tipo": "galeria"},
    {"id": "l6", "code": "S-1350-PIQ-01", "name": "Pique Principal", "nivel": "1350", "sector": "Sur", "tipo": "pique"},
    {"id": "l7", "code": "C-1300-GAL-01", "name": "Galería Central", "nivel": "1300", "sector": "Central", "tipo": "galeria"},
    {"id": "l8", "code": "C-1300-RAM-01", "name": "Rampa Central", "nivel": "1300", "sector": "Central", "tipo": "rampa"},
]

# Available mine levels
NIVELES = ["1400", "1350", "1300", "1250", "1200"]

# Available sectors
SECTORES = ["Norte", "Sur", "Central", "Este", "Oeste"]

# App Configuration
APP_CONFIG = {
    "page_title": "Safety Flash Pro",
    "page_icon": "⚠️",
    "layout": "centered",
    "initial_sidebar_state": "collapsed",
}


def get_secrets():
    """Get secrets from Streamlit or environment variables"""
    def get_secret(key, default=""):
        try:
            return st.secrets[key]
        except (KeyError, FileNotFoundError):
            return default

    return {
        "SUPABASE_URL": get_secret("SUPABASE_URL"),
        "SUPABASE_KEY": get_secret("SUPABASE_KEY"),
        "GEMINI_API_KEY": get_secret("GEMINI_API_KEY"),
    }
