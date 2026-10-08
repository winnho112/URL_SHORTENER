-- Enable the pgcrypto extension for gen_random_uuid()
CREATE EXTENSION IF NOT EXISTS pgcrypto;

-- Create the links table if it doesn't already exist
CREATE TABLE IF NOT EXISTS public.links (
    id              uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id         uuid NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
    original_url    text NOT NULL,
    short_code      text NOT NULL UNIQUE,
    click_count     integer NOT NULL DEFAULT 0,
    created_at      timestamptz NOT NULL DEFAULT now(),
    last_clicked_at timestamptz NULL,
    CONSTRAINT click_count_non_negative CHECK (click_count >= 0)
);

-- Index on user_id for fast lookups by user
CREATE INDEX IF NOT EXISTS idx_links_user_id ON public.links(user_id);

-- Index on short_code for fast lookups when redirecting
CREATE INDEX IF NOT EXISTS idx_links_short_code ON public.links(short_code);