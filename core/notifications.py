"""
Safety_Flash Pro - Notifications Module
Sistema de notificaciones por email, SMS y WhatsApp según nivel de riesgo
"""

import streamlit as st
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from typing import Optional, List, Dict
from datetime import datetime

from core.config import RISK_LEVELS, INCIDENT_CATEGORIES, get_secrets
from core.database import get_database


class NotificationService:
    """Notification service for incident alerts"""

    def __init__(self):
        self.db = get_database()
        self.smtp_config = self._get_smtp_config()

    def _get_smtp_config(self) -> Dict:
        """Get SMTP configuration from secrets"""
        try:
            return {
                "server": st.secrets["SMTP_SERVER"],
                "port": int(st.secrets["SMTP_PORT"]),
                "email": st.secrets["SMTP_EMAIL"],
                "password": st.secrets["SMTP_PASSWORD"],
            }
        except Exception as e:
            return {
                "server": "smtp.gmail.com",
                "port": 587,
                "email": "",
                "password": "",
            }

    def get_recipients_for_report(self, report: Dict) -> List[Dict]:
        """
        Get notification recipients based on risk level and category

        Risk-based escalation:
        - BAJO: Supervisor directo
        - MEDIO: Supervisor + Jefe de turno
        - ALTO: Supervisor + Jefe de turno + Prevencionista
        - CRITICO: Todos + Gerencia
        """
        # TEST MODE: Enviar todo a email de prueba
        TEST_MODE = True
        TEST_EMAIL = "jpcaamano@gmail.com"

        recipients = []
        risk_level = report.get("final_risk_level") or report.get("ai_risk_level", "MEDIO")
        category_code = report.get("categoria_codigo", "GEO")

        # Get category configuration
        category = INCIDENT_CATEGORIES.get(category_code, INCIDENT_CATEGORIES["GEO"])
        notify_roles = category.get("notify_roles", ["jefe_turno"])

        # Get worker's supervisor
        worker = report.get("worker_info", {})

        # Siempre agregar supervisor
        recipients.append({
            "email": TEST_EMAIL if TEST_MODE else worker.get("supervisor_email", "supervisor@minera.cl"),
            "role": "supervisor_directo",
            "name": "Supervisor Directo",
            "channels": ["email"]
        })

        # Add based on risk level
        if risk_level in ["MEDIO", "ALTO", "CRITICO"]:
            recipients.append({
                "email": TEST_EMAIL if TEST_MODE else "jefeturno@minera.cl",
                "role": "jefe_turno",
                "name": "Jefe de Turno",
                "channels": ["email"]
            })

        if risk_level in ["ALTO", "CRITICO"]:
            recipients.append({
                "email": TEST_EMAIL if TEST_MODE else "prevencionista@minera.cl",
                "role": "prevencionista",
                "name": "Prevencionista",
                "channels": ["email"]
            })

        if risk_level == "CRITICO":
            recipients.append({
                "email": TEST_EMAIL if TEST_MODE else "gerencia@minera.cl",
                "role": "gerencia",
                "name": "Gerencia Operaciones",
                "channels": ["email"]
            })

        # En modo test, eliminar duplicados (todos van al mismo email)
        if TEST_MODE:
            seen_roles = set()
            unique_recipients = []
            for r in recipients:
                if r["role"] not in seen_roles:
                    seen_roles.add(r["role"])
                    unique_recipients.append(r)
            return unique_recipients

        return recipients

    def send_notifications(self, report: Dict, pdf_bytes: Optional[bytes] = None) -> List[Dict]:
        """
        Send notifications for an incident report

        Returns list of notification results
        """
        recipients = self.get_recipients_for_report(report)
        results = []

        for recipient in recipients:
            for channel in recipient.get("channels", ["email"]):
                result = None

                if channel == "email":
                    result = self.send_email(recipient, report, pdf_bytes)
                elif channel == "sms":
                    result = self.send_sms(recipient, report)
                elif channel == "whatsapp":
                    result = self.send_whatsapp(recipient, report)

                if result:
                    # Log notification
                    self.db.log_notification({
                        "report_id": report.get("id"),
                        "channel": channel,
                        "recipient": recipient.get("email") or recipient.get("phone"),
                        "status": result.get("status"),
                        "error_message": result.get("error")
                    })
                    results.append(result)

        return results

    def send_email(self, recipient: Dict, report: Dict, pdf_bytes: Optional[bytes] = None) -> Dict:
        """Send email notification"""
        if not self.smtp_config.get("email") or not self.smtp_config.get("password"):
            return {
                "channel": "email",
                "recipient": recipient.get("email"),
                "status": "simulated",
                "message": f"[DEMO] Email enviado a {recipient.get('email')}"
            }

        try:
            risk_level = report.get("final_risk_level") or report.get("ai_risk_level", "MEDIO")
            risk_config = RISK_LEVELS.get(risk_level, RISK_LEVELS["MEDIO"])

            # Create email
            msg = MIMEMultipart()
            msg["From"] = self.smtp_config["email"]
            msg["To"] = recipient["email"]
            msg["Subject"] = f"{risk_config['icon']} FLASH REPORT [{risk_level}] - {report.get('report_number', 'N/A')}"

            # Email body
            body = self._create_email_body(report, recipient)
            msg.attach(MIMEText(body, "html"))

            # Attach PDF if available
            if pdf_bytes:
                pdf_attachment = MIMEApplication(pdf_bytes, _subtype="pdf")
                pdf_attachment.add_header(
                    "Content-Disposition",
                    "attachment",
                    filename=f"FlashReport_{report.get('report_number', 'N')}.pdf"
                )
                msg.attach(pdf_attachment)

            # Send email
            with smtplib.SMTP(self.smtp_config["server"], self.smtp_config["port"]) as server:
                server.starttls()
                server.login(self.smtp_config["email"], self.smtp_config["password"])
                server.send_message(msg)

            return {
                "channel": "email",
                "recipient": recipient["email"],
                "status": "sent",
                "message": "Email enviado correctamente"
            }

        except Exception as e:
            return {
                "channel": "email",
                "recipient": recipient.get("email"),
                "status": "error",
                "error": str(e)
            }

    def _create_email_body(self, report: Dict, recipient: Dict) -> str:
        """Create HTML email body"""
        risk_level = report.get("final_risk_level") or report.get("ai_risk_level", "MEDIO")
        risk_config = RISK_LEVELS.get(risk_level, RISK_LEVELS["MEDIO"])
        worker = report.get("worker_info", {})
        location = report.get("location_info", {})

        return f"""
<!DOCTYPE html>
<html>
<head>
    <style>
        body {{ font-family: Arial, sans-serif; margin: 0; padding: 20px; }}
        .header {{ background-color: {risk_config['color']}; color: white; padding: 20px; text-align: center; }}
        .content {{ padding: 20px; }}
        .section {{ margin-bottom: 20px; }}
        .label {{ font-weight: bold; color: #333; }}
        .risk-badge {{ display: inline-block; padding: 5px 15px; border-radius: 20px;
                      background-color: {risk_config['color']}; color: white; font-weight: bold; }}
        .actions {{ background-color: #f5f5f5; padding: 15px; border-left: 4px solid {risk_config['color']}; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>{risk_config['icon']} FLASH REPORT - NIVEL {risk_level}</h1>
        <p>Reporte #{report.get('report_number', 'N/A')}</p>
    </div>

    <div class="content">
        <div class="section">
            <p class="label">Fecha/Hora:</p>
            <p>{datetime.now().strftime('%d/%m/%Y %H:%M')}</p>
        </div>

        <div class="section">
            <p class="label">Reportante:</p>
            <p>{worker.get('name', 'N/A')} - {worker.get('cargo', 'N/A')}</p>
        </div>

        <div class="section">
            <p class="label">Ubicación:</p>
            <p>{location.get('name', 'N/A')} - Nivel {location.get('nivel', 'N/A')}</p>
        </div>

        <div class="section">
            <p class="label">Categoría:</p>
            <p>{report.get('categoria_nombre', report.get('ai_classification', 'N/A'))}</p>
        </div>

        <div class="section">
            <p class="label">Nivel de Riesgo:</p>
            <span class="risk-badge">{risk_level}</span>
        </div>

        <div class="section">
            <p class="label">Descripción:</p>
            <p>{report.get('final_description') or report.get('ai_description', 'N/A')}</p>
        </div>

        <div class="section actions">
            <p class="label">Acciones Inmediatas:</p>
            <p>{report.get('final_actions') or report.get('ai_immediate_actions', 'N/A')}</p>
        </div>

        <hr>
        <p style="color: #666; font-size: 12px;">
            Este es un mensaje automático del sistema Safety Flash Pro.
            Por favor, revise el incidente y tome las acciones necesarias.
        </p>
    </div>
</body>
</html>
"""

    def send_sms(self, recipient: Dict, report: Dict) -> Dict:
        """Send SMS notification (simulated - integrate Twilio for production)"""
        risk_level = report.get("final_risk_level") or report.get("ai_risk_level", "MEDIO")
        risk_config = RISK_LEVELS.get(risk_level, RISK_LEVELS["MEDIO"])

        message = f"""
{risk_config['icon']} FLASH REPORT [{risk_level}]
Reporte #{report.get('report_number', 'N/A')}
Ubicación: {report.get('location_info', {}).get('name', 'N/A')}
Categoría: {report.get('categoria_nombre', 'N/A')}
Acción requerida inmediata.
"""

        # In production, integrate with Twilio:
        # from twilio.rest import Client
        # client = Client(account_sid, auth_token)
        # message = client.messages.create(body=message, from_='+1...', to=recipient['phone'])

        return {
            "channel": "sms",
            "recipient": recipient.get("phone", recipient.get("email")),
            "status": "simulated",
            "message": f"[DEMO] SMS enviado: {message[:50]}..."
        }

    def send_whatsapp(self, recipient: Dict, report: Dict) -> Dict:
        """Send WhatsApp notification (simulated - integrate WhatsApp Business API for production)"""
        risk_level = report.get("final_risk_level") or report.get("ai_risk_level", "MEDIO")
        risk_config = RISK_LEVELS.get(risk_level, RISK_LEVELS["MEDIO"])

        message = f"""
{risk_config['icon']} *FLASH REPORT - NIVEL {risk_level}*

📋 Reporte #{report.get('report_number', 'N/A')}
📍 {report.get('location_info', {}).get('name', 'N/A')}
🏷️ {report.get('categoria_nombre', 'N/A')}

{report.get('final_description') or report.get('ai_description', 'Ver reporte adjunto')}

⚠️ *Acción requerida inmediata*
"""

        # In production, integrate with WhatsApp Business API
        # or use Twilio WhatsApp integration

        return {
            "channel": "whatsapp",
            "recipient": recipient.get("phone", recipient.get("email")),
            "status": "simulated",
            "message": f"[DEMO] WhatsApp enviado: {message[:50]}..."
        }


# Singleton instance
@st.cache_resource
def get_notification_service() -> NotificationService:
    """Get or create NotificationService instance"""
    return NotificationService()


def send_report_notifications(report: Dict, pdf_bytes: Optional[bytes] = None) -> List[Dict]:
    """Helper to send notifications for a report"""
    service = get_notification_service()
    return service.send_notifications(report, pdf_bytes)


def get_notification_preview(report: Dict) -> List[Dict]:
    """Get preview of who will be notified"""
    service = get_notification_service()
    return service.get_recipients_for_report(report)
