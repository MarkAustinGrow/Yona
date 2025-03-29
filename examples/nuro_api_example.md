# Nuro API Integration Examples

This document provides examples of how to use the Nuro API integration in the Yona project.

## Using the Sonic API (Original)

The Sonic API is the original API used by the Yona project. It's still fully supported and can be used as follows:

```bash
# Basic usage with the Sonic API (default)
python src/generate_song.py "Create a happy pop song about summer adventures"

# With additional Sonic API parameters
python src/generate_song.py "Create a happy pop song about summer adventures" \
  --override-style "pop, upbeat, summer" \
  --override-negative-tags "sad, melancholic" \
  --override-instrumental \
  --override-mv "sonic-v4" \
  --override-description "A cheerful summer pop song with upbeat vibes"
```

## Using the Nuro API (New)

The Nuro API provides additional parameters for more control over song generation:

```bash
# Basic usage with the Nuro API
python src/generate_song.py "Create a happy pop song about summer adventures" --api nuro

# With additional Nuro API parameters
python src/generate_song.py "Create a happy pop song about summer adventures" \
  --api nuro \
  --gender "Female" \
  --genre "Pop" \
  --mood "Happy" \
  --timbre "Bright" \
  --duration 180
```

## Nuro API Parameter Options

The Nuro API supports the following parameter options:

### Gender
- `Female`
- `Male`

### Genre
- `Folk`
- `Pop`
- `Rock`
- `Chinese Style`
- `Hip Hop/Rap`
- `R&B/Soul`
- `Punk`
- `Electronic`
- `Jazz`
- `Reggae`
- `DJ`
- `Pop Punk`
- `Disco`
- `Future Bass`
- `Pop Rap`
- `Trap Rap`
- `R&B Rap`
- `Chinoiserie Electronic`
- `GuFeng Music`
- `Pop Rock`
- `Jazz Pop`
- `Bossa Nova`
- `Contemporary R&B`

### Mood
- `Happy`
- `Dynamic/Energetic`
- `Sentimental/Melancholic/Lonely`
- `Inspirational/Hopeful`
- `Nostalgic/Memory`
- `Excited`
- `Sorrow/Sad`
- `Chill`
- `Romantic`
- `Miss`
- `Groovy/Funky`
- `Dreamy/Ethereal`
- `Calm/Relaxing`

### Timbre
- `Warm`
- `Bright`
- `Husky`
- `Electrified voice`
- `Sweet_AUDIO_TIMBRE`
- `Cute_AUDIO_TIMBRE`
- `Loud and sonorous`
- `Powerful`
- `Sexy/Lazy`

### Duration
- Integer value between 30 and 240 seconds (default is 120 seconds)

## Comparing the APIs

The two APIs have different strengths:

- **Sonic API**: Good for general song creation with style tags and negative tags
- **Nuro API**: Better for fine-tuning specific aspects like gender, genre, mood, and timbre

You can experiment with both APIs to see which one produces better results for your specific needs.

## Automatic Fallback Mechanism

The system includes an automatic fallback mechanism that switches to the Nuro API if the Sonic API is under maintenance:

1. When the Sonic API returns a maintenance error, the system automatically falls back to the Nuro API
2. The system maps Sonic API parameters to Nuro API parameters:
   - `voice_gender` → `gender` (Female/Male)
   - `style_tags` → `genre` and `mood` (using intelligent mapping)
3. The fallback is logged for transparency
4. The song is created using the Nuro API with the mapped parameters
5. All subsequent status checks use the Nuro API methods

This ensures continuous operation even when one API is unavailable, making the system more resilient.

Example log output when fallback occurs:
```
WARNING:__main__:Sonic API is under maintenance, falling back to Nuro API
INFO:__main__:Falling back to Nuro API with genre=Pop, mood=Happy, gender=Female
```

## Robust Status Checking

The system includes robust status checking logic that handles differences between the Sonic and Nuro APIs:

1. For the Sonic API, it checks the 'state' field in the response
2. For the Nuro API, it checks both 'state' and 'status' fields (Nuro API uses 'status')
3. The system also considers a song successful if:
   - The status is "succeeded"
   - The progress is 100%
   - An audio_url is available, even if the status is still "pending"

This ensures that songs are properly detected as complete regardless of which API is used or how the API reports status.

Example log output during status checking:
```
INFO:src.music_api:Nuro song status: succeeded, state: succeeded
INFO:__main__:Song status: succeeded
INFO:__main__:Song creation completed successfully!
```
