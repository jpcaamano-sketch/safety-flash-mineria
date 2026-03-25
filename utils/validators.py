"""
Safety_Flash Pro - Validators Module
Validaciones para datos de entrada
"""

import re
from typing import Optional, Tuple, List


def validate_tag_code(tag: str) -> Tuple[bool, str]:
    """
    Validate TAG code format

    Expected formats: MIN-1234, TAG-5678, etc.

    Args:
        tag: TAG code to validate

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not tag:
        return False, "El código TAG es requerido"

    tag = tag.strip().upper()

    # Check format: PREFIX-NUMBERS
    pattern = r'^[A-Z]{2,4}-\d{3,6}$'

    if not re.match(pattern, tag):
        return False, "Formato inválido. Use formato: MIN-1234"

    return True, ""


def validate_description(description: str, min_length: int = 10) -> Tuple[bool, str]:
    """
    Validate incident description

    Args:
        description: Description text
        min_length: Minimum required length

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not description:
        return False, "La descripción es requerida"

    description = description.strip()

    if len(description) < min_length:
        return False, f"La descripción debe tener al menos {min_length} caracteres"

    return True, ""


def validate_email(email: str) -> Tuple[bool, str]:
    """
    Validate email format

    Args:
        email: Email address

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not email:
        return False, "El email es requerido"

    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'

    if not re.match(pattern, email):
        return False, "Formato de email inválido"

    return True, ""


def validate_phone(phone: str) -> Tuple[bool, str]:
    """
    Validate Chilean phone number

    Expected formats: +56912345678, 912345678, etc.

    Args:
        phone: Phone number

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not phone:
        return False, "El teléfono es requerido"

    # Remove spaces and dashes
    phone = re.sub(r'[\s\-]', '', phone)

    # Check Chilean format
    pattern = r'^(\+?56)?9\d{8}$'

    if not re.match(pattern, phone):
        return False, "Formato de teléfono inválido. Use: +56912345678"

    return True, ""


def validate_rut(rut: str) -> Tuple[bool, str]:
    """
    Validate Chilean RUT

    Args:
        rut: RUT number (with or without formatting)

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not rut:
        return False, "El RUT es requerido"

    # Remove formatting
    rut = rut.replace(".", "").replace("-", "").upper()

    if len(rut) < 8 or len(rut) > 9:
        return False, "RUT inválido"

    # Extract body and verifier
    body = rut[:-1]
    verifier = rut[-1]

    # Calculate expected verifier
    try:
        total = 0
        multiplier = 2

        for digit in reversed(body):
            total += int(digit) * multiplier
            multiplier = multiplier + 1 if multiplier < 7 else 2

        remainder = 11 - (total % 11)

        if remainder == 11:
            expected = "0"
        elif remainder == 10:
            expected = "K"
        else:
            expected = str(remainder)

        if verifier != expected:
            return False, "RUT inválido (dígito verificador incorrecto)"

    except ValueError:
        return False, "RUT inválido (formato incorrecto)"

    return True, ""


def validate_image(image_bytes: bytes, max_size_mb: float = 10) -> Tuple[bool, str]:
    """
    Validate image file

    Args:
        image_bytes: Image content
        max_size_mb: Maximum file size in MB

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not image_bytes:
        return False, "La imagen es requerida"

    # Check size
    size_mb = len(image_bytes) / (1024 * 1024)
    if size_mb > max_size_mb:
        return False, f"La imagen excede el tamaño máximo de {max_size_mb}MB"

    # Check file type (basic check for JPEG/PNG headers)
    if image_bytes[:2] == b'\xff\xd8':  # JPEG
        return True, ""
    elif image_bytes[:8] == b'\x89PNG\r\n\x1a\n':  # PNG
        return True, ""
    elif image_bytes[:4] == b'RIFF' and image_bytes[8:12] == b'WEBP':  # WebP
        return True, ""

    return False, "Formato de imagen no soportado. Use JPEG, PNG o WebP"


def validate_audio(audio_bytes: bytes, max_duration_sec: int = 120) -> Tuple[bool, str]:
    """
    Validate audio file

    Args:
        audio_bytes: Audio content
        max_duration_sec: Maximum duration in seconds

    Returns:
        Tuple of (is_valid, error_message)
    """
    if not audio_bytes:
        return False, "El audio es requerido"

    # Basic size check (rough estimate: ~100KB per 10 seconds for WAV)
    size_kb = len(audio_bytes) / 1024
    estimated_duration = size_kb / 10  # Very rough estimate

    if estimated_duration > max_duration_sec:
        return False, f"El audio parece exceder {max_duration_sec} segundos"

    return True, ""


def validate_report_data(report: dict) -> Tuple[bool, List[str]]:
    """
    Validate complete report data before submission

    Args:
        report: Report data dictionary

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Required fields
    if not report.get("worker_info"):
        errors.append("Información del trabajador requerida")

    if not report.get("location_info"):
        errors.append("Ubicación del incidente requerida")

    description = report.get("final_description") or report.get("ai_description")
    if not description:
        errors.append("Descripción del incidente requerida")
    elif len(description.strip()) < 10:
        errors.append("La descripción es muy corta")

    risk_level = report.get("final_risk_level") or report.get("ai_risk_level")
    if not risk_level:
        errors.append("Nivel de riesgo requerido")
    elif risk_level not in ["BAJO", "MEDIO", "ALTO", "CRITICO"]:
        errors.append("Nivel de riesgo inválido")

    return len(errors) == 0, errors


def sanitize_text(text: str) -> str:
    """
    Sanitize text input (remove dangerous characters)

    Args:
        text: Input text

    Returns:
        Sanitized text
    """
    if not text:
        return ""

    # Remove control characters except newlines and tabs
    sanitized = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    # Limit consecutive newlines
    sanitized = re.sub(r'\n{3,}', '\n\n', sanitized)

    return sanitized.strip()


def format_rut(rut: str) -> str:
    """
    Format RUT with standard Chilean formatting

    Args:
        rut: RUT without formatting

    Returns:
        Formatted RUT (XX.XXX.XXX-X)
    """
    # Remove existing formatting
    rut = rut.replace(".", "").replace("-", "").upper()

    if len(rut) < 2:
        return rut

    # Extract body and verifier
    body = rut[:-1]
    verifier = rut[-1]

    # Format body with dots
    formatted_body = ""
    for i, digit in enumerate(reversed(body)):
        if i > 0 and i % 3 == 0:
            formatted_body = "." + formatted_body
        formatted_body = digit + formatted_body

    return f"{formatted_body}-{verifier}"
