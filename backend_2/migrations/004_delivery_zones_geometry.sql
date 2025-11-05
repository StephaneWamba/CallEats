-- Migration: 004 - Delivery Zones Geometry Support
-- Adds PostGIS geometry support for spatial queries and map integration
-- Enables point-in-zone checks and GeoJSON boundary storage

-- Enable PostGIS extension (if available)
-- Note: If this fails, enable PostGIS via Supabase Dashboard > Database > Extensions
CREATE EXTENSION IF NOT EXISTS postgis;

-- Add geometry column for zone boundaries
ALTER TABLE delivery_zones
ADD COLUMN IF NOT EXISTS boundary GEOMETRY(POLYGON, 4326);

-- Add center point for quick reference (optional, can be computed from boundary)
ALTER TABLE delivery_zones
ADD COLUMN IF NOT EXISTS center_point GEOMETRY(POINT, 4326);

-- Create spatial index for efficient spatial queries
CREATE INDEX IF NOT EXISTS idx_delivery_zones_boundary 
ON delivery_zones USING GIST(boundary);

CREATE INDEX IF NOT EXISTS idx_delivery_zones_center 
ON delivery_zones USING GIST(center_point);

-- Comments for documentation
COMMENT ON COLUMN delivery_zones.boundary IS 'Polygon boundary in WGS84 (SRID 4326) for zone coverage';
COMMENT ON COLUMN delivery_zones.center_point IS 'Center point of zone for quick distance calculations';

-- ============================================================================
-- SPATIAL FUNCTIONS
-- ============================================================================

-- Function to set boundary from GeoJSON
CREATE OR REPLACE FUNCTION set_zone_boundary(
    p_zone_id UUID,
    p_restaurant_id UUID,
    p_geojson JSONB
) RETURNS JSONB AS $$
DECLARE
    geometry_type TEXT;
    geometry_json JSONB;
BEGIN
    -- Validate zone belongs to restaurant
    IF NOT EXISTS (
        SELECT 1 FROM delivery_zones 
        WHERE id = p_zone_id AND restaurant_id = p_restaurant_id
    ) THEN
        RAISE EXCEPTION 'Zone not found or access denied';
    END IF;
    
    -- Extract geometry type
    geometry_type := p_geojson->>'type';
    geometry_json := p_geojson;
    
    -- Handle Feature or Geometry
    IF geometry_type = 'Feature' THEN
        geometry_json := p_geojson->'geometry';
        geometry_type := geometry_json->>'type';
    END IF;
    
    -- Validate type
    IF geometry_type NOT IN ('Polygon', 'MultiPolygon') THEN
        RAISE EXCEPTION 'Geometry must be Polygon or MultiPolygon';
    END IF;
    
    -- Convert GeoJSON to PostGIS geometry and update
    UPDATE delivery_zones
    SET boundary = ST_SetSRID(
            ST_GeomFromGeoJSON(geometry_json::text), 
            4326
        ),
        center_point = ST_Centroid(
            ST_SetSRID(
                ST_GeomFromGeoJSON(geometry_json::text), 
                4326
            )
        )
    WHERE id = p_zone_id;
    
    -- Return updated zone with GeoJSON boundary
    RETURN (
        SELECT jsonb_build_object(
            'id', id,
            'zone_name', zone_name,
            'boundary', ST_AsGeoJSON(boundary)::jsonb,
            'center', ST_AsGeoJSON(center_point)::jsonb
        )
        FROM delivery_zones
        WHERE id = p_zone_id
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to check if point is in any zone
CREATE OR REPLACE FUNCTION check_delivery_zone(
    p_restaurant_id UUID,
    p_longitude DOUBLE PRECISION,
    p_latitude DOUBLE PRECISION
) RETURNS TABLE (
    id UUID,
    zone_name TEXT,
    description TEXT,
    delivery_fee DECIMAL(10,2),
    min_order DECIMAL(10,2),
    boundary_geojson JSONB
) AS $$
BEGIN
    RETURN QUERY
    SELECT 
        dz.id,
        dz.zone_name,
        dz.description,
        dz.delivery_fee,
        dz.min_order,
        ST_AsGeoJSON(dz.boundary)::jsonb as boundary_geojson
    FROM delivery_zones dz
    WHERE dz.restaurant_id = p_restaurant_id
    AND dz.boundary IS NOT NULL
    AND ST_Within(
        ST_SetSRID(ST_MakePoint(p_longitude, p_latitude), 4326),
        dz.boundary
    )
    LIMIT 1;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Function to get zone boundary as GeoJSON Feature
CREATE OR REPLACE FUNCTION get_zone_boundary_geojson(
    p_zone_id UUID,
    p_restaurant_id UUID
) RETURNS JSONB AS $$
BEGIN
    RETURN (
        SELECT jsonb_build_object(
            'type', 'Feature',
            'properties', jsonb_build_object(
                'zone_id', id,
                'zone_name', zone_name
            ),
            'geometry', ST_AsGeoJSON(boundary)::jsonb
        )
        FROM delivery_zones
        WHERE id = p_zone_id 
        AND restaurant_id = p_restaurant_id
        AND boundary IS NOT NULL
    );
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

-- Grant execute permissions
GRANT EXECUTE ON FUNCTION set_zone_boundary TO service_role;
GRANT EXECUTE ON FUNCTION set_zone_boundary TO anon;
GRANT EXECUTE ON FUNCTION set_zone_boundary TO authenticated;

GRANT EXECUTE ON FUNCTION check_delivery_zone TO service_role;
GRANT EXECUTE ON FUNCTION check_delivery_zone TO anon;
GRANT EXECUTE ON FUNCTION check_delivery_zone TO authenticated;

GRANT EXECUTE ON FUNCTION get_zone_boundary_geojson TO service_role;
GRANT EXECUTE ON FUNCTION get_zone_boundary_geojson TO anon;
GRANT EXECUTE ON FUNCTION get_zone_boundary_geojson TO authenticated;

