-- Enable UUID extension
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Create songs table
CREATE TABLE IF NOT EXISTS songs (
  id UUID DEFAULT uuid_generate_v4() PRIMARY KEY,
  title TEXT NOT NULL,
  persona_id TEXT NOT NULL,
  lyrics TEXT,
  audio_url TEXT,
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
CREATE INDEX IF NOT EXISTS idx_song_versions_song_id ON song_versions(song_id);
CREATE INDEX IF NOT EXISTS idx_feedback_song_id ON feedback(song_id);
CREATE INDEX IF NOT EXISTS idx_personas_external_id ON personas(external_id); 