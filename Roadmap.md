# Project Roadmap

## Overview

**Goal**: Build an **agentic AI K-pop star** system named **Yona** that:
1. Uses **ChatGPT as the brain** for Yona, enabling natural language processing and decision-making.
2. Creates K-pop songs via [MusicAPI.ai](https://www.musicapi.ai) using Yona’s persona.
3. Saves all song creation inputs in **Supabase** for future reference and adjustments.

This framework is designed as an **agentic system**, meaning that Yona operates autonomously within a structured environment, making calls to external APIs and storing historical data for continuous improvement.

---

## Phases

1. **Initialize the Project**  
2. **Create Supabase Database**  
3. **Design DB Schema**  
4. **Integrate Yona & MusicAPI.ai**  
5. **Store Song Inputs & Outputs**  
6. **Iteration & Refinement**

---

## 1. Initialize the Project

1. **Set Up Repo**  
   - Create a new repository (e.g., GitHub or GitLab) to manage your application code, including:
     - `roadmap.md` (this document)
     - Scripts for creating personas and generating music
     - Code for integrating with Supabase

2. **Establish Local Dev Environment**  
   - Ensure you have Python (or Node.js, if that’s your preference) set up.  
   - Decide on a framework (Cursor, LangChain, or a plain script approach).

3. **Install Required Dependencies**  
   - For Python:
     ```bash
     pip install httpx psycopg2 supabase
     ```
   - For Node.js:
     ```bash
     npm install @supabase/supabase-js axios
     ```
   - Adjust based on your chosen stack and environment.

---

## 2. Create Supabase Database

1. **Sign Up / Log In**  
   - Go to [Supabase.io](https://supabase.io/), create an account, and set up a new project.

2. **Configure Project Settings**  
   - Retrieve your API credentials from the Supabase Dashboard (`Project API Keys`).  
   - Make sure you store these credentials securely (e.g., environment variables).

3. **Database Setup**  
   - Supabase manages a Postgres database under the hood, so your next step is to define a schema that tracks all relevant data.

---

## 3. Design DB Schema

A possible schema includes at least one table (e.g., `songs`) to store:

| Field Name    | Type        | Description                                  |
|--------------|------------|----------------------------------------------|
| `id` (PK)    | `uuid`      | Unique ID, primary key (auto-generated)     |
| `title`      | `text`      | Song title                                  |
| `persona_id` | `text`      | Reference to Yona’s persona ID              |
| `lyrics`     | `text`      | Full or partial lyrics                      |
| `audio_url`  | `text`      | URL of the generated track                  |
| `params_used`| `jsonb`     | JSON object storing all input parameters    |
| `created_at` | `timestamp` | Timestamp for record creation               |

**Implementation Steps**  
1. **Create the table** in Supabase (via SQL or the Dashboard). Example SQL:
   ```sql
   create table if not exists songs (
     id uuid default uuid_generate_v4() primary key,
     title text,
     persona_id text,
     lyrics text,
     audio_url text,
     params_used jsonb,
     created_at timestamp default current_timestamp
   );
   ```

2. **Enable `uuid_generate_v4()`**  
   - Use Supabase’s built-in UUID generator for unique IDs.

---

## 4. Integrate Yona & MusicAPI.ai

### Yona as an AI Agent

Yona is an **agentic AI system** that uses **ChatGPT as its brain**. Yona:
- Takes user prompts and transforms them into structured **song generation requests**.
- Calls **MusicAPI.ai** to create music based on these requests.
- Stores metadata and past interactions in **Supabase** for continuous learning and improvement.

### Persona Creation

```python
import http.client, json

conn = http.client.HTTPSConnection("api.musicapi.ai")
payload = json.dumps({
    "name": "Yona",
    "description": "Energetic K-pop idol persona with bright EDM influences, occasionally rapping segments.",
    "continue_clip_id": "a2632456-62b0-405c-9de8-2ba509cf24fe"
})
headers = {'Content-Type': 'application/json'}
conn.request("POST", "/api/v1/sonic/persona", payload, headers)
res = conn.getresponse()
data = json.loads(res.read())
print(data)
```

### Song Creation

```python
import http.client, json

conn = http.client.HTTPSConnection("api.musicapi.ai")
create_song_payload = {
    "persona_id": "REPLACE_WITH_YONA_PERSONA_ID",
    "prompt": "Compose an energetic K-pop track about friendship and summer fun",
    "style": "kpop",
    "parameters": {
        "tempo": 120,
        "duration": 180
    }
}
payload = json.dumps(create_song_payload)
headers = {'Content-Type': 'application/json'}
conn.request("POST", "/api/v1/sonic/music", payload, headers)
res = conn.getresponse()
data = json.loads(res.read())
print(data)
```

---

## 5. Store Song Inputs & Outputs

1. **Connect to Supabase**  
   ```python
   from supabase import create_client

   url = "https://YOUR_SUPABASE_PROJECT_URL"
   key = "YOUR_SUPABASE_ANON_KEY"
   supabase = create_client(url, key)
   ```

2. **Insert the Record**  
   ```python
   response = supabase.table("songs").insert({
       "title": "Summer Friendship",
       "persona_id": "REPLACE_WITH_YONA_PERSONA_ID",
       "audio_url": "REPLACE_WITH_AUDIO_URL",
       "params_used": create_song_payload
   }).execute()
   print(response)
   ```

---

## 6. Iteration & Refinement

1. **Refine Prompt & Parameters**  
   - Use the stored `params_used` to iterate on improvements.

2. **Version Control**  
   - Each song iteration should be stored as a new record with a `parent_id` reference (if applicable).

3. **Automated Feedback Loop**  
   - Store and analyze listener feedback in **Supabase** to adjust Yona’s song creation process dynamically.

4. **Orchestration & Expansion**  
   - Introduce additional **agents** for song publishing and audience engagement.

---

## Summary

This roadmap details how to:
1. Set up an **agentic AI framework** where **ChatGPT serves as the brain** for Yona.
2. Store music creation history in **Supabase** to refine future outputs.
3. Integrate Yona with **MusicAPI.ai** for K-pop song generation.

By following these steps, you'll create a dynamic, evolving AI K-pop star capable of autonomously generating and improving music over time.

---

## 7. Nuro API Integration

### Overview
Integrate the new Nuro API from MusicAPI.ai to provide an alternative song creation method with enhanced parameters and functionality. This will allow Yona to create songs using either the original Sonic API or the new Nuro API based on specific needs and success rates.

### Implementation Steps

1. **Update Configuration**  
   - Add a new constant `NURO_BASE_URL` in `src/config/config.py` pointing to the Nuro API endpoint
   - Example: `NURO_BASE_URL = "https://api.musicapi.ai/api/v1/nuro"`

2. **Add New Methods to MusicAPI Class**  
   - Create a dedicated method for the Nuro API:
     ```python
     def create_song_nuro(
         self,
         lyrics: str,
         gender: Optional[str] = None,  # "Female" or "Male"
         genre: Optional[str] = None,   # From the list of allowed genres
         mood: Optional[str] = None,    # From the list of allowed moods
         timbre: Optional[str] = None,  # From the list of allowed timbres
         duration: Optional[int] = None # Between 30-240 seconds
     ) -> Dict[str, Any]:
         # Implementation here
     ```
   - Add a status checking method for Nuro songs:
     ```python
     def check_song_status_nuro(self, task_id: str) -> Dict[str, Any]:
         # Implementation here
     ```

3. **Update Higher-Level Code**  
   - Modify scripts like `generate_song.py` to provide an option to choose which API to use
   - Add command-line flags or configuration settings to select the API

4. **Parameter Handling**  
   - Create utility functions to map between parameter sets if needed
   - Document the different parameter options for each API

5. **Testing and Validation**  
   - Create test cases specifically for the Nuro API
   - Compare results between the two APIs to determine optimal use cases

### Benefits

- **Enhanced Functionality**: Access to additional parameters (gender, genre, mood, timbre, duration) for more control over song generation
- **Resilience**: Multiple API options provide redundancy if one service is unavailable
- **Experimentation**: Ability to compare results between APIs to determine which produces better songs for different inputs
- **Future-Proofing**: Prepared for potential API deprecation or changes

### Example Usage

```python
# Using the original Sonic API
song_sonic = music_api.create_song(
    prompt="Lyrics about summer adventures",
    title="Summer Days",
    style="kpop, upbeat",
    voice_gender="female"
)

# Using the new Nuro API
song_nuro = music_api.create_song_nuro(
    lyrics="Lyrics about summer adventures",
    gender="Female",
    genre="Pop",
    mood="Happy",
    timbre="Bright",
    duration=180
)
```

This integration will expand Yona's capabilities by providing more options for song creation and greater control over the generated music.
