-- Add new columns to the songs table
ALTER TABLE songs ADD COLUMN IF NOT EXISTS style TEXT;
ALTER TABLE songs ADD COLUMN IF NOT EXISTS mv TEXT;
ALTER TABLE songs ADD COLUMN IF NOT EXISTS negative_tags TEXT;
ALTER TABLE songs ADD COLUMN IF NOT EXISTS make_instrumental BOOLEAN;
ALTER TABLE songs ADD COLUMN IF NOT EXISTS gpt_description TEXT;
ALTER TABLE songs ADD COLUMN IF NOT EXISTS image_url TEXT;
ALTER TABLE songs ADD COLUMN IF NOT EXISTS video_url TEXT;
ALTER TABLE songs ADD COLUMN IF NOT EXISTS duration NUMERIC;

-- Add new columns to the song_versions table
ALTER TABLE song_versions ADD COLUMN IF NOT EXISTS style TEXT;
ALTER TABLE song_versions ADD COLUMN IF NOT EXISTS mv TEXT;
ALTER TABLE song_versions ADD COLUMN IF NOT EXISTS negative_tags TEXT;
ALTER TABLE song_versions ADD COLUMN IF NOT EXISTS make_instrumental BOOLEAN;
ALTER TABLE song_versions ADD COLUMN IF NOT EXISTS gpt_description TEXT;
ALTER TABLE song_versions ADD COLUMN IF NOT EXISTS image_url TEXT;
ALTER TABLE song_versions ADD COLUMN IF NOT EXISTS video_url TEXT;
ALTER TABLE song_versions ADD COLUMN IF NOT EXISTS duration NUMERIC;

-- Create indexes for better performance
CREATE INDEX IF NOT EXISTS idx_songs_style ON songs(style);
CREATE INDEX IF NOT EXISTS idx_songs_mv ON songs(mv);
CREATE INDEX IF NOT EXISTS idx_song_versions_song_id ON song_versions(song_id);

-- Migrate existing data from params_used to dedicated columns
DO $$
DECLARE
  song_record RECORD;
  params JSONB;
BEGIN
  FOR song_record IN SELECT id, params_used FROM songs LOOP
    params := song_record.params_used;
    
    IF params IS NOT NULL THEN
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
    END IF;
  END LOOP;
END;
$$; 