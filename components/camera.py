"""
Safety_Flash Pro - Camera Component
Captura y manejo de fotos de incidentes
"""

import streamlit as st
from typing import Optional, Tuple
from PIL import Image
import io


def render_camera_capture() -> Optional[bytes]:
    """
    Render camera capture component

    Returns:
        Image bytes if captured, None otherwise
    """
    st.subheader("📸 Foto del Incidente")

    # Camera input
    photo = st.camera_input(
        "Toma una foto del incidente",
        key="incident_camera",
        help="Captura una imagen clara del incidente o situación de riesgo"
    )

    if photo:
        # Show captured image
        st.image(photo, caption="Foto capturada", use_container_width=True)

        # Get image bytes
        return photo.getvalue()

    # Alternative: File upload
    st.markdown("---")
    st.caption("O sube una imagen existente:")

    uploaded = st.file_uploader(
        "Subir imagen",
        type=["jpg", "jpeg", "png"],
        key="incident_upload",
        label_visibility="collapsed"
    )

    if uploaded:
        st.image(uploaded, caption="Imagen subida", use_container_width=True)
        return uploaded.getvalue()

    return None


def render_camera_with_preview() -> Tuple[Optional[bytes], Optional[dict]]:
    """
    Render camera with image preview and basic info

    Returns:
        Tuple of (image_bytes, image_info)
    """
    photo_bytes = render_camera_capture()

    if photo_bytes:
        # Get image info
        try:
            img = Image.open(io.BytesIO(photo_bytes))
            info = {
                "width": img.width,
                "height": img.height,
                "format": img.format,
                "size_kb": len(photo_bytes) / 1024
            }

            st.caption(f"📐 {info['width']}x{info['height']} | 📁 {info['size_kb']:.1f} KB")

            return photo_bytes, info

        except Exception:
            return photo_bytes, None

    return None, None


def compress_image(image_bytes: bytes, max_size_kb: int = 500, quality: int = 85) -> bytes:
    """
    Compress image to reduce size

    Args:
        image_bytes: Original image bytes
        max_size_kb: Maximum size in KB
        quality: JPEG quality (1-100)

    Returns:
        Compressed image bytes
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))

        # Convert to RGB if necessary
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        # Compress
        output = io.BytesIO()
        img.save(output, format='JPEG', quality=quality, optimize=True)

        # Check size and reduce quality if needed
        while output.tell() > max_size_kb * 1024 and quality > 20:
            quality -= 10
            output = io.BytesIO()
            img.save(output, format='JPEG', quality=quality, optimize=True)

        return output.getvalue()

    except Exception:
        return image_bytes


def resize_image(image_bytes: bytes, max_dimension: int = 1920) -> bytes:
    """
    Resize image maintaining aspect ratio

    Args:
        image_bytes: Original image bytes
        max_dimension: Maximum width or height

    Returns:
        Resized image bytes
    """
    try:
        img = Image.open(io.BytesIO(image_bytes))

        # Calculate new size
        ratio = min(max_dimension / img.width, max_dimension / img.height)

        if ratio < 1:
            new_size = (int(img.width * ratio), int(img.height * ratio))
            img = img.resize(new_size, Image.Resampling.LANCZOS)

        # Convert and save
        if img.mode in ('RGBA', 'P'):
            img = img.convert('RGB')

        output = io.BytesIO()
        img.save(output, format='JPEG', quality=90)

        return output.getvalue()

    except Exception:
        return image_bytes


def render_multiple_photos() -> list:
    """
    Render component for capturing multiple photos

    Returns:
        List of image bytes
    """
    st.subheader("📸 Fotos del Incidente")
    st.caption("Puedes capturar múltiples fotos")

    photos = []

    # Initialize photo count in session state
    if "photo_count" not in st.session_state:
        st.session_state.photo_count = 1

    for i in range(st.session_state.photo_count):
        col1, col2 = st.columns([4, 1])

        with col1:
            photo = st.camera_input(
                f"Foto {i + 1}",
                key=f"photo_{i}"
            )
            if photo:
                photos.append(photo.getvalue())

        with col2:
            if i == st.session_state.photo_count - 1:
                if st.button("➕", key=f"add_photo_{i}"):
                    st.session_state.photo_count += 1
                    st.rerun()

    # Show captured photos
    if photos:
        st.write("**Fotos capturadas:**")
        cols = st.columns(min(len(photos), 3))
        for idx, photo in enumerate(photos):
            with cols[idx % 3]:
                st.image(photo, caption=f"Foto {idx + 1}", use_container_width=True)

    return photos
