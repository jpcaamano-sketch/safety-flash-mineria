# Safety Flash Pro ⚠️

Sistema de Reportes de Incidentes Mineros - Una aplicación profesional para reportar incidentes de seguridad en minería subterránea.

## Características

- **Identificación Rápida**: Ingreso por código TAG del trabajador
- **Captura de Evidencia**: Foto del incidente con análisis automático por IA
- **Descripción por Voz**: Grabación de audio con transcripción automática
- **Generación Inteligente**: IA genera reportes profesionales desde descripciones coloquiales
- **Notificaciones Automáticas**: Alertas por email/SMS según nivel de riesgo
- **PDF Profesional**: Descarga de reportes en formato PDF

## Flujo de Usuario

```
1. IDENTIFICACIÓN (2 seg)    → Escanear TAG o ingresar código
2. UBICACIÓN (3 seg)         → Seleccionar nivel/sector/punto
3. EVIDENCIA (5 seg)         → Capturar foto del incidente
4. DESCRIPCIÓN (15 seg)      → Grabar audio describiendo el problema
5. GENERACIÓN (3 seg)        → IA procesa y genera reporte
6. REVISIÓN (10 seg)         → Revisar, editar y aprobar
7. DISTRIBUCIÓN (automático) → PDF + Notificaciones
```

## Instalación

### 1. Clonar o copiar el proyecto

```bash
cd Safety_Flash
```

### 2. Crear entorno virtual

```bash
python -m venv venv
source venv/bin/activate  # En Windows: venv\Scripts\activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar credenciales

```bash
cp .streamlit/secrets.toml.example .streamlit/secrets.toml
# Editar secrets.toml con tus credenciales
```

### 5. Ejecutar la aplicación

```bash
streamlit run app.py
```

## Configuración

### Variables de Entorno

Copia `.streamlit/secrets.toml.example` a `.streamlit/secrets.toml` y configura:

| Variable | Descripción | Requerido |
|----------|-------------|-----------|
| `SUPABASE_URL` | URL del proyecto Supabase | Opcional* |
| `SUPABASE_KEY` | API Key de Supabase | Opcional* |
| `GEMINI_API_KEY` | API Key de Google Gemini | Recomendado |
| `OPENAI_API_KEY` | API Key de OpenAI (Whisper) | Recomendado |
| `SMTP_*` | Configuración de email | Opcional |

*La app funciona en modo demo sin base de datos

### Base de Datos (Supabase)

1. Crear proyecto en [Supabase](https://supabase.com)
2. Ejecutar el script `database_schema.sql` en el SQL Editor
3. Copiar las credenciales a `secrets.toml`

## Estructura del Proyecto

```
Safety_Flash/
├── app.py                    # App principal Streamlit
├── core/
│   ├── config.py            # Configuración y constantes
│   ├── database.py          # Conexión Supabase
│   ├── ai_client.py         # Cliente IA (Gemini/OpenAI)
│   ├── speech.py            # Speech-to-text (Whisper)
│   ├── vision.py            # Análisis de imágenes
│   └── notifications.py     # Email/WhatsApp/SMS
├── components/
│   ├── tag_reader.py        # Identificación por TAG
│   ├── location_selector.py # Selector de ubicación
│   ├── camera.py            # Captura de foto
│   ├── audio_recorder.py    # Grabación de audio
│   └── report_editor.py     # Editor de reporte
├── utils/
│   ├── pdf_generator.py     # Generación de PDF
│   └── validators.py        # Validaciones
├── .streamlit/
│   ├── config.toml          # Configuración Streamlit
│   └── secrets.toml         # Credenciales (no commitear)
├── database_schema.sql      # Schema SQL para Supabase
└── requirements.txt         # Dependencias Python
```

## Categorías de Incidentes

| Código | Categoría | Icono | Ejemplos |
|--------|-----------|-------|----------|
| GEO | Geomecánico | 🪨 | Derrumbe, planchón, malla dañada |
| EQU | Equipos | 🚜 | Falla scoop, fuga hidráulica |
| ENE | Energía | ⚡ | Cable dañado, cortocircuito |
| CON | Conducta | 👷 | Sin EPP, procedimiento no seguido |
| AMB | Ambiente | 🌫️ | Ventilación deficiente, gases |

## Niveles de Riesgo

| Nivel | Color | Notificación |
|-------|-------|--------------|
| 🟢 BAJO | Verde | Email a supervisor |
| 🟡 MEDIO | Amarillo | Email a supervisor + jefe turno |
| 🟠 ALTO | Naranja | Email + SMS a jefe turno + prevencionista |
| 🔴 CRÍTICO | Rojo | Email + SMS + WhatsApp a gerencia |

## Modo Demo

Sin configurar credenciales, la app funciona en modo demo con:
- 5 trabajadores de prueba (TAGs: MIN-2345 a MIN-6789)
- 8 ubicaciones predefinidas
- Simulación de notificaciones

## Despliegue

### Streamlit Cloud

1. Subir el código a GitHub
2. Conectar en [share.streamlit.io](https://share.streamlit.io)
3. Configurar secrets en la interfaz web

### Docker (Opcional)

```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 8501
CMD ["streamlit", "run", "app.py"]
```

## Tecnologías

- **Frontend**: Streamlit
- **Backend**: Python 3.11+
- **Database**: Supabase (PostgreSQL)
- **AI**: Google Gemini (Vision + LLM), OpenAI Whisper
- **PDF**: ReportLab
- **Notifications**: SMTP, Twilio (opcional)

## Licencia

MIT License - Uso libre para proyectos comerciales y personales.
