-- Safety_Flash Pro - Database Schema for Supabase
-- Sistema de Reportes de Incidentes Mineros

-- =============================================================================
-- TABLES
-- =============================================================================

-- Tabla de trabajadores (sincronizada con sistema de TAGs)
CREATE TABLE workers (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  tag_code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  rut VARCHAR(12),
  cargo VARCHAR(100),
  area VARCHAR(100),
  turno VARCHAR(20),
  empresa VARCHAR(100),
  supervisor_email VARCHAR(100),
  phone VARCHAR(20),
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  updated_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de ubicaciones de la mina
CREATE TABLE locations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  nivel VARCHAR(50),
  sector VARCHAR(100),
  tipo VARCHAR(50), -- galeria, rampa, pique, estocada, etc.
  coordenadas JSONB,
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de categorías de incidentes
CREATE TABLE incident_categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  icon VARCHAR(10),
  color VARCHAR(7),
  keywords TEXT[], -- palabras clave para clasificación automática
  protocol TEXT, -- protocolo de respuesta
  notify_roles TEXT[], -- roles a notificar
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de reportes de incidentes
CREATE TABLE incident_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_number SERIAL,
  worker_id UUID REFERENCES workers(id),
  location_id UUID REFERENCES locations(id),
  category_id UUID REFERENCES incident_categories(id),

  -- Datos capturados
  photo_url TEXT,
  audio_url TEXT,
  audio_transcription TEXT,

  -- Generado por IA
  ai_image_analysis JSONB,
  ai_description TEXT,
  ai_risk_level VARCHAR(20), -- BAJO, MEDIO, ALTO, CRITICO
  ai_immediate_actions TEXT,
  ai_classification_confidence FLOAT,

  -- Editado por usuario
  final_description TEXT,
  final_risk_level VARCHAR(20),
  final_actions TEXT,

  -- Metadatos
  status VARCHAR(20) DEFAULT 'pending', -- pending, approved, resolved, closed
  created_at TIMESTAMPTZ DEFAULT NOW(),
  approved_at TIMESTAMPTZ,
  resolved_at TIMESTAMPTZ,

  -- Seguimiento
  assigned_to UUID REFERENCES workers(id),
  resolution_notes TEXT,
  follow_up_date DATE,

  -- Datos adicionales como JSON
  metadata JSONB DEFAULT '{}'::jsonb
);

-- Tabla de notificaciones enviadas
CREATE TABLE notifications_log (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id UUID REFERENCES incident_reports(id),
  channel VARCHAR(20), -- email, sms, whatsapp
  recipient VARCHAR(100),
  status VARCHAR(20), -- sent, delivered, failed, simulated
  sent_at TIMESTAMPTZ DEFAULT NOW(),
  delivered_at TIMESTAMPTZ,
  error_message TEXT
);

-- Tabla de archivos adjuntos
CREATE TABLE attachments (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id UUID REFERENCES incident_reports(id),
  file_type VARCHAR(20), -- photo, audio, pdf, other
  file_url TEXT,
  file_name VARCHAR(255),
  file_size INTEGER,
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- =============================================================================
-- INDEXES
-- =============================================================================

CREATE INDEX idx_reports_date ON incident_reports(created_at DESC);
CREATE INDEX idx_reports_status ON incident_reports(status);
CREATE INDEX idx_reports_risk ON incident_reports(final_risk_level);
CREATE INDEX idx_reports_worker ON incident_reports(worker_id);
CREATE INDEX idx_reports_location ON incident_reports(location_id);
CREATE INDEX idx_workers_tag ON workers(tag_code);
CREATE INDEX idx_workers_status ON workers(status);
CREATE INDEX idx_locations_nivel ON locations(nivel);
CREATE INDEX idx_notifications_report ON notifications_log(report_id);

-- =============================================================================
-- INITIAL DATA - Categories
-- =============================================================================

INSERT INTO incident_categories (code, name, icon, color, keywords, notify_roles) VALUES
('GEO', 'Geomecánico', '🪨', '#8B4513',
 ARRAY['roca', 'derrumbe', 'caída', 'planchón', 'malla', 'fortificación', 'acuñadura', 'shotcrete', 'perno', 'cuña', 'estallido'],
 ARRAY['jefe_turno', 'geomecanico', 'prevencionista']),

('EQU', 'Equipos', '🚜', '#FF8C00',
 ARRAY['equipo', 'scoop', 'jumbo', 'camión', 'fuga', 'hidráulico', 'falla', 'mecánico', 'motor', 'neumático', 'freno'],
 ARRAY['jefe_turno', 'mantenimiento']),

('ENE', 'Energía', '⚡', '#FFD700',
 ARRAY['eléctrico', 'cable', 'tablero', 'voltaje', 'cortocircuito', 'descarga', 'transformador', 'fusible'],
 ARRAY['jefe_turno', 'electrico', 'prevencionista']),

('CON', 'Conducta', '👷', '#4169E1',
 ARRAY['trabajador', 'epp', 'casco', 'procedimiento', 'conducta', 'negligencia', 'seguridad', 'protocolo'],
 ARRAY['jefe_turno', 'supervisor_directo']),

('AMB', 'Ambiente', '🌫️', '#708090',
 ARRAY['ventilación', 'polvo', 'gases', 'temperatura', 'humedad', 'visibilidad', 'agua', 'inundación', 'aire'],
 ARRAY['jefe_turno', 'ventilacion', 'prevencionista']);

-- =============================================================================
-- INITIAL DATA - Demo Workers
-- =============================================================================

INSERT INTO workers (tag_code, name, rut, cargo, area, turno, empresa, supervisor_email, phone) VALUES
('MIN-2345', 'Juan Pérez González', '12.345.678-9', 'Operador Scoop', 'Producción', 'A', 'Minera Demo S.A.', 'supervisor@minera.cl', '+56912345678'),
('MIN-3456', 'Carlos Muñoz Silva', '13.456.789-0', 'Operador Jumbo', 'Desarrollo', 'B', 'Minera Demo S.A.', 'supervisor@minera.cl', '+56923456789'),
('MIN-4567', 'Pedro Soto Rojas', '14.567.890-1', 'Fortificador', 'Geomecánica', 'A', 'Minera Demo S.A.', 'geomecanico@minera.cl', '+56934567890'),
('MIN-5678', 'Miguel Fernández López', '15.678.901-2', 'Electricista', 'Mantenimiento', 'B', 'Minera Demo S.A.', 'mantenimiento@minera.cl', '+56945678901'),
('MIN-6789', 'Roberto Díaz Martínez', '16.789.012-3', 'Jefe de Turno', 'Operaciones', 'A', 'Minera Demo S.A.', 'gerencia@minera.cl', '+56956789012');

-- =============================================================================
-- INITIAL DATA - Demo Locations
-- =============================================================================

INSERT INTO locations (code, name, nivel, sector, tipo) VALUES
('N-1400-GAL-01', 'Galería Principal', '1400', 'Norte', 'galeria'),
('N-1400-RAM-01', 'Rampa de Acceso', '1400', 'Norte', 'rampa'),
('N-1350-GAL-01', 'Galería Producción', '1350', 'Norte', 'galeria'),
('N-1350-EST-01', 'Estocada 1', '1350', 'Norte', 'estocada'),
('S-1400-GAL-01', 'Galería Sur', '1400', 'Sur', 'galeria'),
('S-1350-PIQ-01', 'Pique Principal', '1350', 'Sur', 'pique'),
('C-1300-GAL-01', 'Galería Central', '1300', 'Central', 'galeria'),
('C-1300-RAM-01', 'Rampa Central', '1300', 'Central', 'rampa');

-- =============================================================================
-- ROW LEVEL SECURITY (Optional - for multi-tenant support)
-- =============================================================================

-- Enable RLS on tables
ALTER TABLE workers ENABLE ROW LEVEL SECURITY;
ALTER TABLE incident_reports ENABLE ROW LEVEL SECURITY;
ALTER TABLE notifications_log ENABLE ROW LEVEL SECURITY;

-- Create policies (adjust according to your auth setup)
-- Example: Allow authenticated users to read all workers
CREATE POLICY "Workers are viewable by authenticated users"
  ON workers FOR SELECT
  USING (auth.role() = 'authenticated');

-- Example: Allow authenticated users to create reports
CREATE POLICY "Reports can be created by authenticated users"
  ON incident_reports FOR INSERT
  WITH CHECK (auth.role() = 'authenticated');

-- Example: Allow users to view all reports
CREATE POLICY "Reports are viewable by authenticated users"
  ON incident_reports FOR SELECT
  USING (auth.role() = 'authenticated');

-- =============================================================================
-- FUNCTIONS
-- =============================================================================

-- Function to auto-update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger for workers table
CREATE TRIGGER update_workers_updated_at
    BEFORE UPDATE ON workers
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Function to get next report number
CREATE OR REPLACE FUNCTION get_next_report_number()
RETURNS INTEGER AS $$
DECLARE
    next_num INTEGER;
BEGIN
    SELECT COALESCE(MAX(report_number), 1000) + 1 INTO next_num FROM incident_reports;
    RETURN next_num;
END;
$$ language 'plpgsql';

-- =============================================================================
-- VIEWS (Optional - for reporting)
-- =============================================================================

-- View for recent reports with worker and location info
CREATE OR REPLACE VIEW recent_reports_view AS
SELECT
    ir.id,
    ir.report_number,
    ir.created_at,
    ir.final_risk_level,
    ir.status,
    w.name as worker_name,
    w.cargo as worker_cargo,
    l.name as location_name,
    l.nivel as location_nivel,
    ic.name as category_name,
    ic.icon as category_icon
FROM incident_reports ir
LEFT JOIN workers w ON ir.worker_id = w.id
LEFT JOIN locations l ON ir.location_id = l.id
LEFT JOIN incident_categories ic ON ir.category_id = ic.id
ORDER BY ir.created_at DESC
LIMIT 100;

-- View for report statistics
CREATE OR REPLACE VIEW report_statistics AS
SELECT
    DATE_TRUNC('day', created_at) as report_date,
    COUNT(*) as total_reports,
    COUNT(*) FILTER (WHERE final_risk_level = 'CRITICO') as critical_count,
    COUNT(*) FILTER (WHERE final_risk_level = 'ALTO') as high_count,
    COUNT(*) FILTER (WHERE final_risk_level = 'MEDIO') as medium_count,
    COUNT(*) FILTER (WHERE final_risk_level = 'BAJO') as low_count,
    COUNT(*) FILTER (WHERE status = 'resolved') as resolved_count
FROM incident_reports
GROUP BY DATE_TRUNC('day', created_at)
ORDER BY report_date DESC;
