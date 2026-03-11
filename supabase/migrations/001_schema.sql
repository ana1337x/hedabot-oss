-- hedabot-oss schema
-- Run this once against your Supabase project to set up the tables the bot needs.
-- You can do this in the Supabase dashboard under SQL Editor, or with the Supabase CLI.

-- ---------------------------------------------------------------------------
-- Tables
-- ---------------------------------------------------------------------------

-- One row per Discord server. Created automatically when the bot first runs /join.
CREATE TABLE IF NOT EXISTS servers (
  id          uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
  discord_id  text    UNIQUE NOT NULL,
  name        text    NOT NULL,
  owner_id    text    NOT NULL DEFAULT '',
  bot_installed boolean DEFAULT true,
  created_at  timestamptz DEFAULT now(),
  updated_at  timestamptz DEFAULT now()
);

-- One row per voice channel session.
CREATE TABLE IF NOT EXISTS meetings (
  id                uuid    PRIMARY KEY DEFAULT gen_random_uuid(),
  guild_id          text    NOT NULL,
  channel_id        text    NOT NULL,
  start_time        timestamp NOT NULL,
  end_time          timestamp,
  title             text    NOT NULL DEFAULT '',
  duration          integer DEFAULT 0,
  participant_count integer DEFAULT 0,
  speakers          jsonb   DEFAULT '[]',
  status            text    NOT NULL DEFAULT 'in_progress'
);

-- One row per Discord user who has ever spoken. Updated on each session.
CREATE TABLE IF NOT EXISTS speakers (
  id               uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  discord_user_id  text UNIQUE NOT NULL,
  username         text NOT NULL,
  display_name     text,
  created_at       timestamptz DEFAULT now(),
  updated_at       timestamptz DEFAULT now()
);

-- One row per transcribed line of speech.
CREATE TABLE IF NOT EXISTS transcripts (
  id           uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  meeting_id   uuid REFERENCES meetings(id),
  speaker_id   text NOT NULL,
  content      text NOT NULL,
  "timestamp"  timestamp NOT NULL,
  server_id    uuid REFERENCES servers(id),
  search_vector tsvector
);

-- ---------------------------------------------------------------------------
-- Indexes
-- ---------------------------------------------------------------------------

CREATE INDEX IF NOT EXISTS idx_meetings_guild_id    ON meetings(guild_id);
CREATE INDEX IF NOT EXISTS idx_meetings_start_time  ON meetings(start_time);
CREATE INDEX IF NOT EXISTS idx_transcripts_meeting  ON transcripts(meeting_id);
CREATE INDEX IF NOT EXISTS idx_transcripts_speaker  ON transcripts(speaker_id);
CREATE INDEX IF NOT EXISTS transcripts_search_idx   ON transcripts USING gin(search_vector);

-- ---------------------------------------------------------------------------
-- Full-text search
-- ---------------------------------------------------------------------------

-- Automatically populate search_vector whenever a transcript row is inserted or updated.
-- This lets you run full-text search queries against your transcripts later.
CREATE OR REPLACE FUNCTION generate_transcript_search_vector()
RETURNS trigger AS $$
BEGIN
  NEW.search_vector := to_tsvector('english', COALESCE(NEW.content, ''));
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

DROP TRIGGER IF EXISTS update_transcript_search_vector ON transcripts;
CREATE TRIGGER update_transcript_search_vector
  BEFORE INSERT OR UPDATE ON transcripts
  FOR EACH ROW EXECUTE FUNCTION generate_transcript_search_vector();

-- ---------------------------------------------------------------------------
-- Real-time
-- ---------------------------------------------------------------------------

-- Enable Supabase Realtime on meetings and transcripts so you can build
-- live dashboards or listen for new lines as they come in.
ALTER PUBLICATION supabase_realtime ADD TABLE meetings;
ALTER PUBLICATION supabase_realtime ADD TABLE transcripts;

-- ---------------------------------------------------------------------------
-- Row Level Security
-- ---------------------------------------------------------------------------

-- RLS is enabled but the bot uses the service role key, which bypasses it.
-- These policies let you add user-facing access later without changing the schema.
ALTER TABLE servers     ENABLE ROW LEVEL SECURITY;
ALTER TABLE meetings    ENABLE ROW LEVEL SECURITY;
ALTER TABLE speakers    ENABLE ROW LEVEL SECURITY;
ALTER TABLE transcripts ENABLE ROW LEVEL SECURITY;
