-- 1. Enable pgvector extension for semantic search
CREATE EXTENSION IF NOT EXISTS vector;

-- 2. Knowledge Base Table
-- Stores information about programs, events, research, and science topics.
CREATE TABLE IF NOT EXISTS knowledge_base (
    id BIGSERIAL PRIMARY KEY,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    category TEXT, -- e.g., 'research', 'programs', 'science'
    embedding VECTOR(768), -- Dimension 768 is for Gemini 'text-embedding-004'
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 3. Newsletter Subscribers Table
CREATE TABLE IF NOT EXISTS newsletter_subscribers (
    id BIGSERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    area_of_interest TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 4. Program Manager Callback Requests Table
CREATE TABLE IF NOT EXISTS callback_requests (
    id BIGSERIAL PRIMARY KEY,
    full_name TEXT NOT NULL,
    email TEXT NOT NULL,
    phone_number TEXT NOT NULL,
    area_of_interest TEXT,
    preferred_contact_time TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- 5. Semantic Search Function (RPC)
-- This function allows the Edge Function to perform vector similarity searches.
CREATE OR REPLACE FUNCTION match_knowledge (
  query_embedding VECTOR(768),
  match_threshold FLOAT,
  match_count INT
)
RETURNS TABLE (
  id BIGINT,
  content TEXT,
  title TEXT,
  similarity FLOAT
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    knowledge_base.id,
    knowledge_base.content,
    knowledge_base.title,
    1 - (knowledge_base.embedding <=> query_embedding) AS similarity
  FROM knowledge_base
  WHERE 1 - (knowledge_base.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;
