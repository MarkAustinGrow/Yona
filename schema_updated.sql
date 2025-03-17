-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create songs table with expanded columns for all parameters
CREATE TABLE IF NOT EXISTS songs (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  title TEXT NOT NULL,
  persona_id TEXT NOT NULL,
  lyrics TEXT,
  audio_url TEXT,
  
  -- New dedicated columns for important parameters
  style TEXT,                     -- Music style/tags
  mv TEXT,                        -- Music model (sonic-v3-5 or sonic-v4)
  negative_tags TEXT,             -- Elements to avoid in the song
  make_instrumental BOOLEAN,      -- Whether it's an instrumental version
  gpt_description TEXT,           -- Description for the GPT model
  image_url TEXT,                 -- URL to the generated image
  video_url TEXT,                 -- URL to the generated video
  duration NUMERIC,               -- Duration in seconds
  
  -- Keep the original JSONB field for backward compatibility and any additional parameters
  params_used JSONB,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create song_versions table for tracking iterations
CREATE TABLE IF NOT EXISTS song_versions (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  song_id UUID REFERENCES songs(id),
  version_number INTEGER NOT NULL,
  title TEXT NOT NULL,
  lyrics TEXT,
  audio_url TEXT,
  
  -- New dedicated columns for important parameters
  style TEXT,                     -- Music style/tags
  mv TEXT,                        -- Music model (sonic-v3-5 or sonic-v4)
  negative_tags TEXT,             -- Elements to avoid in the song
  make_instrumental BOOLEAN,      -- Whether it's an instrumental version
  gpt_description TEXT,           -- Description for the GPT model
  image_url TEXT,                 -- URL to the generated image
  video_url TEXT,                 -- URL to the generated video
  duration NUMERIC,               -- Duration in seconds
  
  -- Keep the original JSONB field for backward compatibility and any additional parameters
  params_used JSONB,
  
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create feedback table for storing user feedback
CREATE TABLE IF NOT EXISTS feedback (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  song_id UUID REFERENCES songs(id),
  rating INTEGER CHECK (rating >= 1 AND rating <= 5),
  comments TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create personas table for storing persona information
CREATE TABLE IF NOT EXISTS personas (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  external_id TEXT NOT NULL UNIQUE,
  name TEXT NOT NULL,
  description TEXT,
  created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_songs_persona_id ON songs(persona_id);
CREATE INDEX IF NOT EXISTS idx_songs_style ON songs(style);
CREATE INDEX IF NOT EXISTS idx_songs_mv ON songs(mv);
CREATE INDEX IF NOT EXISTS idx_song_versions_song_id ON song_versions(song_id);
CREATE INDEX IF NOT EXISTS idx_feedback_song_id ON feedback(song_id);
CREATE INDEX IF NOT EXISTS idx_personas_external_id ON personas(external_id);

-- Migration function to populate new columns from params_used
CREATE OR REPLACE FUNCTION migrate_song_params() RETURNS void AS $$
DECLARE
  song_record RECORD;
  params JSONB;
BEGIN
  FOR song_record IN SELECT id, params_used FROM songs LOOP
    params := song_record.params_used;
    
    UPDATE songs SET
      style = params->>'style',
      mv = params->>'mv',
      negative_tags = params->>'negative_tags',
      make_instrumental = (params->>'make_instrumental')::BOOLEAN,
      gpt_description = params->>'gpt_description_prompt',
      image_url = params->>'image_url',
      video_url = params->>'video_url',
      duration = (params->>'duration')::NUMERIC
    WHERE id = song_record.id;
  END LOOP;
END;
$$ LANGUAGE plpgsql; 