-- Fresh volumes get pgvector before the answer service creates tables.
-- Dimension is chosen at runtime (BGE-M3 is 1024, local fallback may differ),
-- so units/kb_meta are created by psb_vectors.py, not here.
CREATE EXTENSION IF NOT EXISTS vector;
