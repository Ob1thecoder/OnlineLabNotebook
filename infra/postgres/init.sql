-- Initial SQL run on first container start.
-- Both databases are created by the POSTGRES_DB env var in docker-compose.
-- This file is reserved for any extensions or roles needed at init time.

-- Enable UUID generation
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";
CREATE EXTENSION IF NOT EXISTS "pg_trgm";  -- for full-text search trigrams
