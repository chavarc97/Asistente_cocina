-- ==============================================
-- CHEF BOT - DATABASE INITIALIZATION
-- Sistema de Asistente de Recetas de Cocina
-- ==============================================

-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- ==============================================
-- TIPOS ENUMERADOS
-- ==============================================

CREATE TYPE dietary_filter AS ENUM ('none', 'vegetarian', 'vegan', 'gluten_free');
CREATE TYPE favorite_status AS ENUM ('active', 'removed');

-- ==============================================
-- TABLA: users
-- Almacena información de usuarios de Telegram
-- ==============================================

CREATE TABLE IF NOT EXISTS users (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    telegram_id BIGINT UNIQUE NOT NULL,
    username VARCHAR(100),
    first_name VARCHAR(100),
    last_name VARCHAR(100),
    dietary_filter dietary_filter DEFAULT 'none',
    language_code VARCHAR(10) DEFAULT 'es',
    is_active BOOLEAN DEFAULT true,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_active TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para users
CREATE INDEX idx_users_telegram_id ON users(telegram_id);
CREATE INDEX idx_users_last_active ON users(last_active);

-- ==============================================
-- TABLA: favorites
-- Recetas favoritas de cada usuario (máximo 10)
-- ==============================================

CREATE TABLE IF NOT EXISTS favorites (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    recipe_id VARCHAR(50) NOT NULL,  -- ID de TheMealDB
    recipe_name VARCHAR(255) NOT NULL,
    recipe_image TEXT,  -- URL de imagen
    recipe_category VARCHAR(100),
    status favorite_status DEFAULT 'active',
    added_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    removed_at TIMESTAMP WITH TIME ZONE,
    
    -- Constraint: máximo 10 favoritos activos por usuario
    CONSTRAINT unique_user_recipe UNIQUE(user_id, recipe_id)
);

-- Índices para favorites
CREATE INDEX idx_favorites_user_id ON favorites(user_id);
CREATE INDEX idx_favorites_recipe_id ON favorites(recipe_id);
CREATE INDEX idx_favorites_status ON favorites(status);

-- ==============================================
-- TABLA: search_history
-- Historial de búsquedas (últimas 20 por usuario)
-- ==============================================

CREATE TABLE IF NOT EXISTS search_history (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    search_query TEXT NOT NULL,
    ingredients JSONB DEFAULT '[]',  -- Array de ingredientes buscados
    dietary_filter dietary_filter,   -- Filtro activo al momento de buscar
    results_count INTEGER DEFAULT 0,
    searched_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para search_history
CREATE INDEX idx_search_history_user_id ON search_history(user_id);
CREATE INDEX idx_search_history_searched_at ON search_history(searched_at);
CREATE INDEX idx_search_history_ingredients ON search_history USING GIN(ingredients);

-- ==============================================
-- TABLA: recipe_cache
-- Caché de recetas de TheMealDB (TTL: 7 días)
-- ==============================================

CREATE TABLE IF NOT EXISTS recipe_cache (
    recipe_id VARCHAR(50) PRIMARY KEY,
    recipe_data JSONB NOT NULL,  -- Datos completos de la receta
    category VARCHAR(100),
    area VARCHAR(100),
    tags TEXT[],
    cached_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '7 days'),
    access_count INTEGER DEFAULT 0,
    last_accessed TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
);

-- Índices para recipe_cache
CREATE INDEX idx_recipe_cache_expires_at ON recipe_cache(expires_at);
CREATE INDEX idx_recipe_cache_category ON recipe_cache(category);
CREATE INDEX idx_recipe_cache_tags ON recipe_cache USING GIN(tags);

-- ==============================================
-- TABLA: user_sessions
-- Sesiones activas y estado de conversación
-- ==============================================

CREATE TABLE IF NOT EXISTS user_sessions (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    user_id UUID NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    current_recipe_id VARCHAR(50),  -- Receta que está viendo
    current_step INTEGER DEFAULT 0,  -- Paso actual de la receta
    session_data JSONB DEFAULT '{}',  -- Datos adicionales de sesión
    started_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    last_interaction TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    expires_at TIMESTAMP WITH TIME ZONE DEFAULT (CURRENT_TIMESTAMP + INTERVAL '24 hours')
);

-- Índices para user_sessions
CREATE INDEX idx_user_sessions_user_id ON user_sessions(user_id);
CREATE INDEX idx_user_sessions_expires_at ON user_sessions(expires_at);

-- ==============================================
-- TABLA: conversion_units
-- Unidades de conversión para medidas
-- ==============================================

CREATE TABLE IF NOT EXISTS conversion_units (
    id SERIAL PRIMARY KEY,
    from_unit VARCHAR(50) NOT NULL,
    to_unit VARCHAR(50) NOT NULL,
    factor DECIMAL(10, 4) NOT NULL,
    category VARCHAR(50),  -- 'volume', 'weight', etc.
    CONSTRAINT unique_conversion UNIQUE(from_unit, to_unit)
);

-- ==============================================
-- FUNCIONES Y TRIGGERS
-- ==============================================

-- Función para actualizar updated_at automáticamente
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = CURRENT_TIMESTAMP;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para users
CREATE TRIGGER update_users_updated_at
    BEFORE UPDATE ON users
    FOR EACH ROW
    EXECUTE FUNCTION update_updated_at_column();

-- Función para limitar favoritos a 10 por usuario
CREATE OR REPLACE FUNCTION check_favorites_limit()
RETURNS TRIGGER AS $$
BEGIN
    IF (SELECT COUNT(*) FROM favorites WHERE user_id = NEW.user_id AND status = 'active') >= 10 THEN
        RAISE EXCEPTION 'Maximum 10 favorites allowed per user';
    END IF;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para limitar favoritos
CREATE TRIGGER enforce_favorites_limit
    BEFORE INSERT ON favorites
    FOR EACH ROW
    EXECUTE FUNCTION check_favorites_limit();

-- Función para limpiar historial viejo (mantener últimas 20)
CREATE OR REPLACE FUNCTION cleanup_search_history()
RETURNS TRIGGER AS $$
BEGIN
    DELETE FROM search_history
    WHERE user_id = NEW.user_id
    AND id NOT IN (
        SELECT id FROM search_history
        WHERE user_id = NEW.user_id
        ORDER BY searched_at DESC
        LIMIT 20
    );
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Trigger para limpiar historial
CREATE TRIGGER cleanup_old_searches
    AFTER INSERT ON search_history
    FOR EACH ROW
    EXECUTE FUNCTION cleanup_search_history();

-- Función para limpiar caché expirado
CREATE OR REPLACE FUNCTION cleanup_expired_cache()
RETURNS void AS $$
BEGIN
    DELETE FROM recipe_cache WHERE expires_at < CURRENT_TIMESTAMP;
    DELETE FROM user_sessions WHERE expires_at < CURRENT_TIMESTAMP;
END;
$$ LANGUAGE plpgsql;

-- ==============================================
-- DATOS INICIALES - CONVERSIONES
-- ==============================================

INSERT INTO conversion_units (from_unit, to_unit, factor, category) VALUES
-- Volumen
('taza', 'ml', 236.588, 'volume'),
('tazas', 'ml', 236.588, 'volume'),
('cup', 'ml', 236.588, 'volume'),
('cups', 'ml', 236.588, 'volume'),
('cucharada', 'ml', 14.787, 'volume'),
('cucharadas', 'ml', 14.787, 'volume'),
('tbsp', 'ml', 14.787, 'volume'),
('cucharadita', 'ml', 4.929, 'volume'),
('cucharaditas', 'ml', 4.929, 'volume'),
('tsp', 'ml', 4.929, 'volume'),
('litro', 'ml', 1000, 'volume'),
('litros', 'ml', 1000, 'volume'),
('oz', 'ml', 29.574, 'volume'),
('onza', 'ml', 29.574, 'volume'),
('onzas', 'ml', 29.574, 'volume'),
-- Peso
('lb', 'g', 453.592, 'weight'),
('libra', 'g', 453.592, 'weight'),
('libras', 'g', 453.592, 'weight'),
('oz', 'g', 28.35, 'weight'),
('kg', 'g', 1000, 'weight'),
('kilogramo', 'g', 1000, 'weight'),
('kilogramos', 'g', 1000, 'weight');

-- ==============================================
-- VISTAS ÚTILES
-- ==============================================

-- Vista de usuarios con sus estadísticas
CREATE OR REPLACE VIEW user_stats AS
SELECT 
    u.id,
    u.telegram_id,
    u.username,
    u.dietary_filter,
    u.last_active,
    COUNT(DISTINCT f.id) FILTER (WHERE f.status = 'active') as favorites_count,
    COUNT(DISTINCT sh.id) as total_searches,
    MAX(sh.searched_at) as last_search
FROM users u
LEFT JOIN favorites f ON u.id = f.user_id
LEFT JOIN search_history sh ON u.id = sh.user_id
GROUP BY u.id;

-- Vista de recetas populares en favoritos
CREATE OR REPLACE VIEW popular_recipes AS
SELECT 
    recipe_id,
    recipe_name,
    recipe_image,
    COUNT(*) as favorites_count
FROM favorites
WHERE status = 'active'
GROUP BY recipe_id, recipe_name, recipe_image
ORDER BY favorites_count DESC;

-- ==============================================
-- PERMISOS
-- ==============================================

-- Otorgar permisos al usuario de la aplicación
GRANT ALL PRIVILEGES ON ALL TABLES IN SCHEMA public TO chef_user;
GRANT ALL PRIVILEGES ON ALL SEQUENCES IN SCHEMA public TO chef_user;
GRANT ALL PRIVILEGES ON ALL FUNCTIONS IN SCHEMA public TO chef_user;

-- ==============================================
-- MENSAJE DE ÉXITO
-- ==============================================

DO $$
BEGIN
    RAISE NOTICE '✅ Chef Bot Database initialized successfully!';
    RAISE NOTICE '📊 Tables created: users, favorites, search_history, recipe_cache, user_sessions, conversion_units';
    RAISE NOTICE '🔧 Functions and triggers configured';
    RAISE NOTICE '📈 Views created: user_stats, popular_recipes';
END $$;