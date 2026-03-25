"""
Safety_Flash Pro - Database Module
Conexión a Supabase con fallback a datos demo
"""

import streamlit as st
from typing import Optional, List, Dict
from datetime import datetime
import uuid

from core.config import (
    DEMO_WORKERS,
    DEMO_LOCATIONS,
    INCIDENT_CATEGORIES,
    get_secrets,
)

# Try to import supabase
try:
    from supabase import create_client, Client
    SUPABASE_AVAILABLE = True
except ImportError:
    SUPABASE_AVAILABLE = False
    Client = None


class Database:
    """Database handler with Supabase connection and demo mode fallback"""

    def __init__(self):
        self.client: Optional[Client] = None
        self.demo_mode = True
        self._demo_reports: List[Dict] = []
        self._connect()

    def _connect(self):
        """Initialize database connection"""
        secrets = get_secrets()

        if SUPABASE_AVAILABLE and secrets["SUPABASE_URL"] and secrets["SUPABASE_KEY"]:
            try:
                self.client = create_client(
                    secrets["SUPABASE_URL"],
                    secrets["SUPABASE_KEY"]
                )
                self.demo_mode = False
            except Exception as e:
                st.warning(f"No se pudo conectar a Supabase. Usando modo demo. Error: {e}")
                self.demo_mode = True
        else:
            self.demo_mode = True

    def is_demo_mode(self) -> bool:
        """Check if running in demo mode"""
        return self.demo_mode

    # Worker Methods
    def get_worker_by_tag(self, tag_code: str) -> Optional[Dict]:
        """Get worker by TAG code"""
        if self.demo_mode:
            for worker in DEMO_WORKERS:
                if worker["tag_code"].upper() == tag_code.upper():
                    return worker
            return None

        try:
            response = self.client.table("sf_workers").select("*").eq("tag_code", tag_code).single().execute()
            return response.data
        except Exception:
            return None

    def get_all_workers(self) -> List[Dict]:
        """Get all active workers"""
        if self.demo_mode:
            return [w for w in DEMO_WORKERS if w["status"] == "active"]

        try:
            response = self.client.table("sf_workers").select("*").eq("status", "active").execute()
            return response.data
        except Exception:
            return DEMO_WORKERS

    # Location Methods
    def get_all_locations(self) -> List[Dict]:
        """Get all locations"""
        if self.demo_mode:
            return DEMO_LOCATIONS

        try:
            response = self.client.table("sf_locations").select("*").eq("status", "active").execute()
            return response.data
        except Exception:
            return DEMO_LOCATIONS

    def get_niveles(self) -> List[str]:
        """Get all mine levels"""
        locations = self.get_all_locations()
        niveles = list(set([loc["nivel"] for loc in locations]))
        return sorted(niveles, reverse=True)

    def get_sectores_by_nivel(self, nivel: str) -> List[str]:
        """Get sectors for a specific level"""
        locations = self.get_all_locations()
        sectores = list(set([loc["sector"] for loc in locations if loc["nivel"] == nivel]))
        return sorted(sectores)

    def get_locations_by_nivel_sector(self, nivel: str, sector: str) -> List[Dict]:
        """Get locations for specific level and sector"""
        locations = self.get_all_locations()
        return [loc for loc in locations if loc["nivel"] == nivel and loc["sector"] == sector]

    def get_location_by_id(self, location_id: str) -> Optional[Dict]:
        """Get location by ID"""
        if self.demo_mode:
            for loc in DEMO_LOCATIONS:
                if loc["id"] == location_id:
                    return loc
            return None

        try:
            response = self.client.table("sf_locations").select("*").eq("id", location_id).single().execute()
            return response.data
        except Exception:
            return None

    # Category Methods
    def get_all_categories(self) -> Dict:
        """Get all incident categories"""
        return INCIDENT_CATEGORIES

    def get_category_by_code(self, code: str) -> Optional[Dict]:
        """Get category by code"""
        return INCIDENT_CATEGORIES.get(code)

    # Report Methods
    def create_report(self, report_data: Dict) -> Optional[Dict]:
        """Create a new incident report"""
        report_id = str(uuid.uuid4())
        report_number = len(self._demo_reports) + 1001

        report = {
            "id": report_id,
            "report_number": report_number,
            "created_at": datetime.now().isoformat(),
            "status": "pending",
            **report_data
        }

        if self.demo_mode:
            self._demo_reports.append(report)
            return report

        # Columnas válidas en sf_reports
        VALID_COLUMNS = {
            "worker_id", "location_id", "category_id",
            "photo_url", "audio_url", "audio_transcription",
            "ai_image_analysis", "ai_description", "ai_risk_level", "ai_immediate_actions",
            "final_description", "final_risk_level", "final_actions",
            "status", "created_at", "approved_at", "metadata"
        }
        db_data = {k: v for k, v in report_data.items() if k in VALID_COLUMNS}

        try:
            response = self.client.table("sf_reports").insert(db_data).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al crear reporte: {e}")
            # Fallback to demo storage
            self._demo_reports.append(report)
            return report

    def update_report(self, report_id: str, update_data: Dict) -> Optional[Dict]:
        """Update an existing report"""
        if self.demo_mode:
            for i, report in enumerate(self._demo_reports):
                if report["id"] == report_id:
                    self._demo_reports[i].update(update_data)
                    return self._demo_reports[i]
            return None

        try:
            response = self.client.table("sf_reports").update(update_data).eq("id", report_id).execute()
            return response.data[0] if response.data else None
        except Exception as e:
            st.error(f"Error al actualizar reporte: {e}")
            return None

    def get_report_by_id(self, report_id: str) -> Optional[Dict]:
        """Get report by ID"""
        if self.demo_mode:
            for report in self._demo_reports:
                if report["id"] == report_id:
                    return report
            return None

        try:
            response = self.client.table("sf_reports").select("*").eq("id", report_id).single().execute()
            return response.data
        except Exception:
            return None

    def get_recent_reports(self, limit: int = 10) -> List[Dict]:
        """Get recent reports"""
        if self.demo_mode:
            return sorted(self._demo_reports, key=lambda x: x["created_at"], reverse=True)[:limit]

        try:
            response = self.client.table("sf_reports").select("*").order("created_at", desc=True).limit(limit).execute()
            return response.data
        except Exception:
            return []

    # Notification Log Methods
    def log_notification(self, notification_data: Dict) -> Optional[Dict]:
        """Log a sent notification"""
        notification = {
            "id": str(uuid.uuid4()),
            "sent_at": datetime.now().isoformat(),
            **notification_data
        }

        if self.demo_mode:
            return notification

        try:
            response = self.client.table("sf_notifications").insert(notification_data).execute()
            return response.data[0] if response.data else None
        except Exception:
            return notification


# Singleton instance (sin cache para permitir reinicialización)
def get_database() -> Database:
    """Get or create database instance"""
    if "database" not in st.session_state:
        st.session_state.database = Database()
    return st.session_state.database
