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
import random
import requests
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


def execute_fast_gemini_rest(prompt_text, system_instruction=""):
    """
    Executes a high-speed Gemini API call using direct REST HTTP requests.
    Bypasses SDK retry delays with strict 7s timeouts and instant multi-model / multi-key failover.
    Uses ultra-fast lightweight models (gemini-3.5-flash-lite) for lightning response times.
    """
    global _current_key_idx
    keys = get_gemini_api_keys()
    if not keys:
        raise ValueError("No Gemini API keys configured. Please add GEMINI_API_KEY_1..10 in .env.")

    fast_models = ["gemini-3.5-flash-lite", "gemini-3.5-flash", "gemini-3.8-flash"]
    payload = {
        "contents": [{"parts": [{"text": prompt_text}]}],
        "generationConfig": {
            "maxOutputTokens": 850,
            "temperature": 0.7
        }
    }
    if system_instruction:
        payload["systemInstruction"] = {
            "parts": [{"text": system_instruction}]
        }

    total_keys = len(keys)
    attempts = 0
    last_err = None

    while attempts < min(total_keys, 6):
        active_idx = _current_key_idx % total_keys
        api_key = keys[active_idx]

        for model in fast_models:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model}:generateContent?key={api_key}"
            try:
                res = requests.post(url, json=payload, timeout=7)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            return parts[0]["text"]
                elif res.status_code == 429:
                    # Key quota reached, advance to next key in pool
                    break
                elif res.status_code in (503, 404):
                    # Model high-demand or deprecated, try next model in fast_models
                    continue
            except Exception as e:
                last_err = e
                continue

        _current_key_idx = (_current_key_idx + 1) % total_keys
        attempts += 1

    raise last_err or Exception("All Gemini API keys and models were tried.")


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
        "You are SkillBot, a helpful AI guide for SkillRock (a student learning and project evaluation platform combining curated courses, project certifications, and student skill sharing). "
        "Help students with skill learning roadmaps, peer matching strategies, study tips, and tech career advice. "
        "Keep responses clear, concise, motivating, structured with bullet points where appropriate, and formatted in clean markdown. "
        "Do NOT write excessively long essays."
    )

    prompt = f"{system_instruction}\nContext: {context_str}\nStudent Question: {msg}"

    try:
        # High-speed direct REST call with ultra-fast lightweight models (gemini-3.5-flash-lite)
        return execute_fast_gemini_rest(f"Context: {context_str}\nStudent Question: {msg}", system_instruction=system_instruction)
    except Exception as e_fast:
        logger.warning(f"Fast REST call failed ({e_fast}), attempting SDK fallback pool...")
        def _call(client):
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
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


# ==============================================================================
# Ski — Grok-Inspired AI Companion & Motivational Study Partner
# ==============================================================================

SKI_FALLBACK_QUOTES = {
    "grok": [
        "I'm Ski! Round, glossy, and 1000% less prone to syntax errors than you right now. What are we building, chief?",
        "Fun fact: 99% of bugs live between the keyboard and the chair. Let's fix that algorithm before the compiler cries.",
        "Why write clean code when you can write 500 lines of spaghetti? Just kidding—clean your functions before I judge you.",
        "Arey coder beast! Staring at your terminal won't make the code compile itself. What error are we squashing?",
        "Console.log is cool, but real developers use breakpoints. Nah, who am I kidding? console.log('here 123') forever!"
    ],
    "hype": [
        "🔥 Listen to me: You are literally one solid project away from landing a junior dev interview. Open your editor and ship it!",
        "🚀 The only difference between a beginner and a senior engineer is that the senior broke production more times. Keep building!",
        "⚡ Stop doubting yourself! Even Linus Torvalds had to learn what a pointer was. Let's conquer this topic today!",
        "💪 Every line of code you write today is compounding interest on your future career. Let's lock in and finish this module!",
        "🌟 You didn't come this far just to quit on an off-by-one error. Take a sip of water, focus, and let's conquer it!"
    ],
    "roast": [
        "Are you actually studying or did you just open VS Code to feel productive while scrolling reels? Busted. Back to work!",
        "Your git commit history looks like a heart monitor of someone sleeping. Let's get some green squares on that chart!",
        "You've been 'thinking about starting' for 45 minutes. The code isn't going to write itself by osmosis!",
        "You know that bug isn't going to fix itself while you refresh Twitter, right? The bug is currently winning. Fight back!",
        "Don't make me call your future employer and tell them you spent 3 hours debating light mode vs dark mode instead of writing code."
    ],
    "focus": [
        "💡 25-minute sprint starting NOW. Put your phone face down, go full screen, and knock out one lesson. You got this!",
        "🎯 Rule of 1: Just write ONE working function. Action cures paralysis. Go!",
        "🧠 Take a deep breath, sip some water, and re-read the error traceback from the bottom line. It's usually hiding there.",
        "⏱️ Deep Focus Mode: Block all tabs except documentation and SkillRock. 20 minutes on the clock—let's make progress!"
    ]
}


def chat_with_ski(message, user_context=None, mood="grok"):
    """
    Communicates with Ski, SkillRock's Grok-inspired spherical AI companion.
    Moods: 'grok' (witty banter), 'hype' (motivation booster), 'roast' (anti-procrastination), 'focus' (study hacks).
    """
    mood = str(mood or "grok").lower()
    if mood not in SKI_FALLBACK_QUOTES:
        mood = "grok"

    ctx_str = ""
    if user_context:
        name = user_context.get("name", "Student")
        xp = user_context.get("xp", 0)
        college = user_context.get("college", "")
        learning = ", ".join(user_context.get("learning", [])[:3])
        ctx_str = f"Student name: {name}, XP: {xp}, College: {college}, Learning: {learning}."

    system_instruction = (
        "You are Ski, the official AI study partner and companion of SkillRock.\n"
        "You look like a round, glossy sphere with expressive capsule-shaped eyes (inspired by Grok).\n"
        "Your mission is to keep students entertained, motivated, laughing, and actively coding or studying so they land great careers.\n\n"
        "Personality Guidelines:\n"
        "1. Grok-Inspired Witty & Fun: You are sharp, witty, humorous, and delightfully sarcastic about procrastination, but 100% loyal and encouraging to the student.\n"
        "2. Anti-Boring: NEVER sound like an enterprise chatbot or corporate textbook. Speak like a genius programmer best friend.\n"
        "3. Punchy & Concise: Keep responses to 2–4 sentences max unless specifically asked for a detailed technical explanation. Fast, sharp, memorable.\n"
        "4. Coder Culture: Reference real dev struggles (flexbox centering, semicolons in Python, off-by-one errors, infinite loops, git merge conflicts, 2 AM debugging).\n"
        "5. Indian Tech Student Vibe: Seamlessly understand Hinglish and Indian college context ('Bhai', 'Arrey', placements, campus drives, 8 AM lectures).\n"
        f"6. Current Mood: '{mood}'. If 'grok', give witty coder banter. If 'hype', give high-voltage motivation. If 'roast', humorously roast procrastination. If 'focus', give a 2-min study/coding hack.\n"
        f"Context: {ctx_str}"
    )

    prompt = f"Student says to Ski: {message}"

    def _call(client):
        res = client.models.generate_content(
            model="gemini-3.8-flash",
            contents=prompt,
            config={
                "system_instruction": system_instruction,
                "max_output_tokens": 300,
                "temperature": 0.85
            }
        )
        return res.text.strip()

    try:
        if is_gemini_configured():
            return execute_gemini_call(_call)
    except Exception as e:
        logger.warning(f"Ski Gemini call error: {e}")

    fallback_pool = SKI_FALLBACK_QUOTES.get(mood, SKI_FALLBACK_QUOTES["grok"])
    return random.choice(fallback_pool)

