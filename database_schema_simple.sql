-- Safety_Flash Pro - Schema Simplificado (sin conflictos)
-- Solo tablas nuevas para Safety_Flash

-- Tabla de trabajadores mineros
CREATE TABLE IF NOT EXISTS sf_workers (
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
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de ubicaciones de la mina
CREATE TABLE IF NOT EXISTS sf_locations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  nivel VARCHAR(50),
  sector VARCHAR(100),
  tipo VARCHAR(50),
  status VARCHAR(20) DEFAULT 'active',
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de categorías de incidentes
CREATE TABLE IF NOT EXISTS sf_categories (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  code VARCHAR(50) UNIQUE NOT NULL,
  name VARCHAR(100) NOT NULL,
  icon VARCHAR(10),
  color VARCHAR(7),
  keywords TEXT[],
  notify_roles TEXT[],
  created_at TIMESTAMPTZ DEFAULT NOW()
);

-- Tabla de reportes de incidentes
CREATE TABLE IF NOT EXISTS sf_reports (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_number SERIAL,
  worker_id UUID REFERENCES sf_workers(id),
  location_id UUID REFERENCES sf_locations(id),
  category_id UUID REFERENCES sf_categories(id),
  photo_url TEXT,
  audio_url TEXT,
  audio_transcription TEXT,
  ai_image_analysis JSONB,
  ai_description TEXT,
  ai_risk_level VARCHAR(20),
  ai_immediate_actions TEXT,
  final_description TEXT,
  final_risk_level VARCHAR(20),
  final_actions TEXT,
  status VARCHAR(20) DEFAULT 'pending',
  created_at TIMESTAMPTZ DEFAULT NOW(),
  approved_at TIMESTAMPTZ,
  metadata JSONB DEFAULT '{}'::jsonb
);

-- Tabla de notificaciones
CREATE TABLE IF NOT EXISTS sf_notifications (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  report_id UUID REFERENCES sf_reports(id),
  channel VARCHAR(20),
  recipient VARCHAR(100),
  status VARCHAR(20),
  sent_at TIMESTAMPTZ DEFAULT NOW(),
  error_message TEXT
);

-- Índices
CREATE INDEX IF NOT EXISTS idx_sf_reports_date ON sf_reports(created_at DESC);
CREATE INDEX IF NOT EXISTS idx_sf_reports_status ON sf_reports(status);
CREATE INDEX IF NOT EXISTS idx_sf_workers_tag ON sf_workers(tag_code);

-- Datos iniciales: Categorías
INSERT INTO sf_categories (code, name, icon, color, keywords, notify_roles) VALUES
('GEO', 'Geomecánico', '🪨', '#8B4513', ARRAY['roca', 'derrumbe', 'planchón', 'malla', 'shotcrete'], ARRAY['jefe_turno', 'geomecanico']),
('EQU', 'Equipos', '🚜', '#FF8C00', ARRAY['scoop', 'jumbo', 'camión', 'fuga', 'falla'], ARRAY['jefe_turno', 'mantenimiento']),
('ENE', 'Energía', '⚡', '#FFD700', ARRAY['eléctrico', 'cable', 'voltaje', 'cortocircuito'], ARRAY['jefe_turno', 'electrico']),
('CON', 'Conducta', '👷', '#4169E1', ARRAY['epp', 'casco', 'procedimiento', 'conducta'], ARRAY['jefe_turno', 'supervisor']),
('AMB', 'Ambiente', '🌫️', '#708090', ARRAY['ventilación', 'polvo', 'gases', 'agua'], ARRAY['jefe_turno', 'ventilacion'])
ON CONFLICT (code) DO NOTHING;

-- Datos iniciales: Trabajadores demo
INSERT INTO sf_workers (tag_code, name, rut, cargo, area, turno, empresa, supervisor_email, phone) VALUES
('MIN-2345', 'Juan Pérez González', '12.345.678-9', 'Operador Scoop', 'Producción', 'A', 'Minera Demo S.A.', 'supervisor@minera.cl', '+56912345678'),
('MIN-3456', 'Carlos Muñoz Silva', '13.456.789-0', 'Operador Jumbo', 'Desarrollo', 'B', 'Minera Demo S.A.', 'supervisor@minera.cl', '+56923456789'),
('MIN-4567', 'Pedro Soto Rojas', '14.567.890-1', 'Fortificador', 'Geomecánica', 'A', 'Minera Demo S.A.', 'geomecanico@minera.cl', '+56934567890'),
('MIN-5678', 'Miguel Fernández López', '15.678.901-2', 'Electricista', 'Mantenimiento', 'B', 'Minera Demo S.A.', 'mantenimiento@minera.cl', '+56945678901'),
('MIN-6789', 'Roberto Díaz Martínez', '16.789.012-3', 'Jefe de Turno', 'Operaciones', 'A', 'Minera Demo S.A.', 'gerencia@minera.cl', '+56956789012')
ON CONFLICT (tag_code) DO NOTHING;

-- Datos iniciales: Ubicaciones demo
INSERT INTO sf_locations (code, name, nivel, sector, tipo) VALUES
('N-1400-GAL-01', 'Galería Principal', '1400', 'Norte', 'galeria'),
('N-1400-RAM-01', 'Rampa de Acceso', '1400', 'Norte', 'rampa'),
('N-1350-GAL-01', 'Galería Producción', '1350', 'Norte', 'galeria'),
('N-1350-EST-01', 'Estocada 1', '1350', 'Norte', 'estocada'),
('S-1400-GAL-01', 'Galería Sur', '1400', 'Sur', 'galeria'),
('S-1350-PIQ-01', 'Pique Principal', '1350', 'Sur', 'pique'),
('C-1300-GAL-01', 'Galería Central', '1300', 'Central', 'galeria'),
('C-1300-RAM-01', 'Rampa Central', '1300', 'Central', 'rampa')
ON CONFLICT (code) DO NOTHING;
