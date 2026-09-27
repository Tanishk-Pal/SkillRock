"""
SkillSwap Campus — AI Service Layer
Powered by real Google Gemini API (gemini-2.5-flash).
Features a 10-Slot API Key Pool with automatic failover rotation.
If one key hits a rate-limit (429), quota issue, or transient error,
SkillBot automatically and seamlessly shifts to the next key.
Does NOT use fake responses when all keys are missing or exhausted.
"""

import os
import json
import logging
from pathlib import Path
from dotenv import load_dotenv

# Ensure environment variables are loaded
BASE_DIR = Path(__file__).resolve().parent.parent
load_dotenv(BASE_DIR / ".env")

logger = logging.getLogger(__name__)

# Tracks active key index in the pool for round-robin / failover
_current_key_idx = 0


def get_gemini_api_keys():
    """
    Retrieves all configured, non-empty Gemini API keys from:
    1. GEMINI_API_KEY_1 through GEMINI_API_KEY_10 (10 dedicated slots)
    2. Legacy GEMINI_API_KEY fallback
    Strips accidental quotes and ignores default placeholders.
    """
    keys = []
    for i in range(1, 11):
        raw = os.getenv(f"GEMINI_API_KEY_{i}", "").strip()
        if raw.startswith('"') and raw.endswith('"'):
            raw = raw[1:-1].strip()
        elif raw.startswith("'") and raw.endswith("'"):
            raw = raw[1:-1].strip()
        if raw and "YOUR_GEMINI" not in raw and raw not in keys:
            keys.append(raw)

    fallback = os.getenv("GEMINI_API_KEY", "").strip()
    if fallback.startswith('"') and fallback.endswith('"'):
        fallback = fallback[1:-1].strip()
    elif fallback.startswith("'") and fallback.endswith("'"):
        fallback = fallback[1:-1].strip()
    if fallback and "YOUR_GEMINI" not in fallback and fallback not in keys:
        keys.insert(0, fallback)

    return keys


def is_gemini_configured():
    """Checks whether at least one valid GEMINI_API_KEY has been set."""
    return len(get_gemini_api_keys()) > 0


def execute_gemini_call(call_func):
    """
    Executes a Gemini API call function with automatic failover across all configured API keys (up to 10 slots).
    If a key hits a rate limit (429), quota exhaustion, or temporary API error,
    it automatically logs and shifts to the next available key in the pool.
    """
    global _current_key_idx
    keys = get_gemini_api_keys()
    if not keys:
        raise ValueError("No Gemini API keys configured. Please add GEMINI_API_KEY_1..10 in .env.")

    from google import genai

    total_keys = len(keys)
    attempts = 0
    last_error = None

    while attempts < total_keys:
        active_idx = _current_key_idx % total_keys
        api_key = keys[active_idx]
        slot_label = f"Key Slot #{active_idx + 1}"

        try:
            client = genai.Client(api_key=api_key)
            result = call_func(client)
            return result
        except Exception as e:
            err_text = str(e)
            last_error = e
            logger.warning(
                f"[SkillBot Key Pool] {slot_label} failed with error: {err_text[:120]}... "
                f"Auto-shifting to next key in pool."
            )
            # Advance key index to next slot
            _current_key_idx = (_current_key_idx + 1) % total_keys
            attempts += 1

    # If all keys failed
    raise last_error or Exception("All configured Gemini API keys exhausted.")


def normalize_skill(raw_name):
    """
    Normalizes a skill name using standard aliases.
    """
    if not raw_name:
        return ""
    clean = raw_name.strip()
    aliases = {
        "py": "Python",
        "python3": "Python",
        "python 3": "Python",
        "js": "JavaScript",
        "ts": "TypeScript",
        "cpp": "C++",
        "c plus plus": "C++",
        "ui/ux": "UI/UX",
        "ui ux": "UI/UX",
        "ui/ux design": "UI/UX",
        "uiux": "UI/UX",
        "reactjs": "React",
        "react.js": "React",
        "ml": "Machine Learning",
        "dl": "Deep Learning",
        "ds": "Data Science",
        "html/css": "HTML & CSS",
        "html css": "HTML & CSS",
        "git": "Git & GitHub",
        "github": "Git & GitHub",
        "premiere": "Video Editing",
        "premiere pro": "Video Editing",
    }
    low = clean.lower()
    if low in aliases:
        return aliases[low]
    return clean.title()


def chat_with_skillbot(message, user_context=None):
    """
    Sends message to Google Gemini API for student skill advice.
    Uses multi-key failover pool. If all keys fail or missing, informs the student.
    """
    msg = message.strip()
    if not msg:
        return "Please ask a question about skills, roadmaps, or career paths."

    if not is_gemini_configured():
        return (
            "**SkillBot AI is currently offline.**\n\n"
            "MANUAL CONFIGURATION REQUIRED:\n"
            "To enable live AI answers and roadmaps, please set your `GEMINI_API_KEY_1` in `.env`.\n\n"
            "👉 **Steps to enable:**\n"
            "1. Get free API keys at [Google AI Studio](https://aistudio.google.com/)\n"
            "2. Open your `.env` file and set: `GEMINI_API_KEY_1=your_key_here`\n"
            "3. You can set up to 10 keys (`GEMINI_API_KEY_1` to `GEMINI_API_KEY_10`) for instant auto-failover!"
        )

    context_str = ""
    if user_context:
        teaching = user_context.get("teaching", [])
        learning = user_context.get("learning", [])
        name = user_context.get("name", "Student")
        context_str = f"Student Name: {name}. Skills they can teach: {', '.join(teaching)}. Skills they want to learn: {', '.join(learning)}."

    system_instruction = (
        "You are SkillBot, a helpful AI guide for SkillSwap Campus (a student peer-to-peer skill exchange platform). "
        "Help students with skill learning roadmaps, peer matching strategies, study tips, and tech career advice. "
        "Keep responses clear, concise, motivating, structured with bullet points where appropriate, and formatted in clean markdown. "
        "Do NOT write excessively long essays."
    )

    prompt = f"{system_instruction}\nContext: {context_str}\nStudent Question: {msg}"

    def _call(client):
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )
        return response.text

    try:
        return execute_gemini_call(_call)
    except Exception as e:
        logger.error(f"Gemini API request failed across all keys: {e}")
        return f"Unable to reach Google Gemini API (all configured keys in pool were tried). Error: {str(e)[:150]}. Please check your keys or quota."


def generate_skill_roadmap(skill_name):
    """
    Generates a personalized study roadmap for a skill using Google Gemini.
    Uses multi-key failover pool.
    """
    skill = skill_name.strip()
    if not skill:
        return {"error": "Skill name is required"}

    if not is_gemini_configured():
        return {
            "title": f"{skill} Roadmap (AI Offline)",
            "description": "SkillBot requires a Gemini API key to generate custom roadmaps.",
            "steps": [
                "MANUAL CONFIGURATION REQUIRED: Set GEMINI_API_KEY_1..10 in your .env file to enable custom roadmaps.",
                "Visit https://aistudio.google.com/ to generate a free Gemini API key.",
                "Restart the server once configured."
            ],
            "estimated_time": "Configuration Required"
        }

    prompt = (
        f"Generate a beginner-to-intermediate study roadmap for learning '{skill}'. "
        "Return ONLY a valid JSON object with the following keys:\n"
        "{\n"
        '  "title": "Title of the roadmap",\n'
        '  "description": "Short 1-2 sentence overview",\n'
        '  "steps": ["Step 1: ...", "Step 2: ...", "Step 3: ...", "Step 4: ...", "Step 5: ..."],\n'
        '  "estimated_time": "e.g. 4 Weeks"\n'
        "}\n"
        "Do not include markdown code block backticks around the JSON."
    )

    def _call(client):
        response = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt
        )
        raw_text = response.text.strip()
        if raw_text.startswith("```json"):
            raw_text = raw_text[7:]
        if raw_text.startswith("```"):
            raw_text = raw_text[3:]
        if raw_text.endswith("```"):
            raw_text = raw_text[:-3]
        return json.loads(raw_text.strip())

    try:
        return execute_gemini_call(_call)
    except Exception as e:
        logger.error(f"Gemini roadmap generation failed across all keys: {e}")
        return {
            "title": f"{skill} Roadmap",
            "description": f"Failed to generate roadmap via Gemini API: {str(e)[:120]}",
            "steps": ["Please check your GEMINI_API_KEY_1..10 in .env and try again."],
            "estimated_time": "N/A"
        }


# Aliases for route compatibility
get_learning_roadmap = generate_skill_roadmap


def get_skill_recommendations(query, current_skills=None):
    """Provides skill recommendations using Gemini failover pool."""
    if not is_gemini_configured():
        return {
            "recommendations": [],
            "message": "Gemini API key is required. Set GEMINI_API_KEY_1 in .env."
        }

    prompt = (
        f"Given interest in '{query}' and current skills '{current_skills or []}', "
        'suggest 3-5 high-value complementary skills to learn as JSON list of strings: ["Skill 1", "Skill 2"]'
    )

    def _call(client):
        res = client.models.generate_content(model="gemini-3.8-flash", contents=prompt)
        text = res.text.strip().replace("```json", "").replace("```", "").strip()
        return {"recommendations": json.loads(text)}

    try:
        return execute_gemini_call(_call)
    except Exception:
        return {"recommendations": []}
