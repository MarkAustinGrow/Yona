# Yona K-pop Star System - Database Migration Guide

This document explains the database schema changes and migration process for the Yona K-pop Star System.

## Schema Changes

We've updated the database schema to store song parameters in dedicated columns instead of just in the JSONB `params_used` field. This change allows for better querying and filtering of songs based on specific parameters.

### New Columns Added

The following columns have been added to both the `songs` and `song_versions` tables:

- `style` (TEXT): Music style/tags
- `mv` (TEXT): Music model (sonic-v3-5 or sonic-v4)
- `negative_tags` (TEXT): Elements to avoid in the song
- `make_instrumental` (BOOLEAN): Whether it's an instrumental version
- `gpt_description` (TEXT): Description for the GPT model
- `image_url` (TEXT): URL to the generated image
- `video_url` (TEXT): URL to the generated video
- `duration` (NUMERIC): Duration in seconds

The original `params_used` JSONB field is still maintained for backward compatibility and to store any additional parameters not covered by the dedicated columns.

## Migration Process

To apply these schema changes to your Supabase database, follow these steps:

1. Log in to your Supabase dashboard
2. Go to the SQL Editor
3. Copy the contents of the `migration.sql` file
4. Paste the SQL into the editor
5. Run the SQL script

The SQL script will:
- Add the new columns to the `songs` and `song_versions` tables
- Create indexes for better performance
- Migrate existing data from the `params_used` JSONB field to the dedicated columns

## Code Changes

The following files have been updated to support the new schema:

1. `src/supabase_client.py`: Updated to store song parameters in both the dedicated columns and the `params_used` field
2. `src/list_songs.py`: Updated to display the dedicated columns instead of extracting them from `params_used`

## Benefits of the New Schema

- **Better Querying**: You can now query songs directly by style, model, or other parameters
- **Improved Performance**: Dedicated columns with indexes provide faster filtering and sorting
- **Better Data Integrity**: Explicit columns enforce data types and constraints
- **Backward Compatibility**: The original `params_used` field is still maintained

## Testing the Migration

After running the migration, you can test it by listing the songs with the updated script:

```
python src/list_songs.py --show-details
```

This will display all songs with their dedicated parameter columns. 