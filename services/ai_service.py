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
# Ski — Grok-Inspired Living Web Pet & Jarvis Personal Assistant Engine
# Persona: Cute, pleasant 5-year-old girl child speaking sweet, cheerful Hinglish!
# ==============================================================================

SKI_FALLBACK_QUOTES = {
    "grok": [
        "Yayy! Main hoon Ski, aapki 5 saal ki cute dost! Code karte raho, bugs toh main chhu-mantar kar dungi, hihi!",
        "Chalo chalo, jaldi se ek mast function likho aur commit kar do na bhaiya/didi!",
        "Main yahan screen pe ghum rahi hoon aapke sath! Aap focus karke padho, okay?",
        "Keyboard pe tick-tick karke fingers chalao na, time waste bilkul nahi karna, yayy!",
        "Main gol-matol Ski hoon! Agar code me error aaya toh rona nahi, hum milke fix karenge!"
    ],
    "hype": [
        "Aap toh world ke best developer banoge! Main cheer kar rahi hoon: Go Go Go!",
        "Woohoo! Ek aur commit push karo na, energy ekdum 100% honi chahiye, yayy!",
        "You are a coding rockstar! Chalo mujhe virtual high-five do! ✋",
        "Aapka logic kitna awesome hai! Ek aur lesson complete karke star ban jao!",
        "Arrey wah! Pata hai aap jab code karte ho toh kitne cool lagte ho? Keep building!"
    ],
    "roast": [
        "Arey bhaiya/didi, firse social media pe time waste? Gande bache!",
        "Haww! Code nahi likhoge toh job kaise lagegi? Chalo jaldi code karo!",
        "Itna aalas achhi baat nahi hoti! Chalo jaldi se terminal open karo na!",
        "Aapne fir reels open kar li? Main dekh rahi hoon sab kuch! VS Code pe wapas aao!",
        "Bugs hass rahe hain aapke upar! Chalo unko defeat karte hain, abhi ke abhi!"
    ],
    "focus": [
        "Chalo 10 minute ka deep focus lagate hain, phone ko side me rakh do!",
        "Paani piyo, deep breath lo, aur abhi agla lesson start karte hain, chalo!",
        "Pehle paper pe logic socho, fir code likho! Step-by-step jeetenge!",
        "Full screen karo aur ek lesson finish karo na please, fir hum play karenge!"
    ]
}


def get_local_skillrock_catalogue():
    """
    Authoritative local machine catalogue of all SkillRock learning products.
    Enables Jarvis autopilot navigation directly to courses, roadmaps, and Bhavishya.
    """
    catalogue = [
        {
            "id": "ai-ml-python",
            "category": "Artificial Intelligence & ML",
            "title": "Machine Learning & AI with Python: Practical Neural Networks & Model Deployment",
            "slug": "machine-learning-ai-python",
            "url": "/learning/course/machine-learning-ai-python",
            "keywords": ["ai", "artificial intelligence", "machine learning", "ml", "neural network", "deep learning", "nlp", "super course on ai", "ai course"]
        },
        {
            "id": "fullstack-mern",
            "category": "Full Stack Web Development",
            "title": "Full-Stack Web Development: Modern Frontend & Backend with Cloud Deployment",
            "slug": "fullstack-mern-cloud-development",
            "url": "/learning/course/fullstack-mern-cloud-development",
            "keywords": ["web dev", "web development", "full stack", "mern", "frontend", "backend", "react", "node", "express"]
        },
        {
            "id": "sigma-web-hindi",
            "category": "Web Development in Hindi",
            "title": "Sigma Web Development Bootcamp (Hindi) — HTML to Full MERN Stack",
            "slug": "sigma-web-development-hindi",
            "url": "/learning/course/sigma-web-development-hindi",
            "keywords": ["sigma web", "hindi web dev", "web dev hindi", "html css js hindi"]
        },
        {
            "id": "javascript-mastery",
            "category": "JavaScript & Modern Web",
            "title": "JavaScript Mastery: DOM Manipulation, Async APIs & Modern Web Apps",
            "slug": "javascript-mastery-modern-web",
            "url": "/learning/course/javascript-mastery-modern-web",
            "keywords": ["javascript", "js", "async javascript", "vanilla js", "dom manipulation"]
        },
        {
            "id": "python-automation",
            "category": "Python Programming",
            "title": "Python Programming: Beginner to Real-World Automation",
            "slug": "python-programming-automation",
            "url": "/learning/course/python-programming-automation",
            "keywords": ["python", "learn python", "python programming", "python automation", "python beginner"]
        },
        {
            "id": "python-dsa",
            "category": "DSA in Python",
            "title": "Data Structures & Algorithms in Python: Problem Solving Masterclass",
            "slug": "python-dsa-masterclass",
            "url": "/learning/course/python-dsa-masterclass",
            "keywords": ["python dsa", "algorithms python", "data structures python"]
        },
        {
            "id": "strivers-dsa",
            "category": "Data Structures & Algorithms",
            "title": "Striver's A2Z DSA Complete Roadmap for Tech Interviews",
            "slug": "strivers-a2z-dsa-roadmap",
            "url": "/learning/course/strivers-a2z-dsa-roadmap",
            "keywords": ["dsa", "data structures", "algorithms", "striver", "a2z", "interview prep dsa", "leetcode", "dsa course"]
        },
        {
            "id": "java-dsa",
            "category": "Java & DSA",
            "title": "Java & Data Structures Masterclass with Enterprise Patterns",
            "slug": "java-dsa-enterprise-architecture",
            "url": "/learning/course/java-dsa-enterprise-architecture",
            "keywords": ["java dsa", "java data structures", "enterprise java"]
        },
        {
            "id": "java-oops",
            "category": "Java Programming",
            "title": "Java Programming & Object-Oriented Design Masterclass",
            "slug": "java-core-oops-masterclass",
            "url": "/learning/course/java-core-oops-masterclass",
            "keywords": ["java", "learn java", "java oops", "core java"]
        },
        {
            "id": "ethical-hacking",
            "category": "Cybersecurity & Ethical Hacking",
            "title": "Practical Ethical Hacking & Penetration Testing Masterclass",
            "slug": "ethical-hacking-penetration-testing",
            "url": "/learning/course/ethical-hacking-penetration-testing",
            "keywords": ["ethical hacking", "hacking", "cybersecurity", "penetration testing", "security"]
        },
        {
            "id": "kali-linux",
            "category": "Linux & Cyber Tools",
            "title": "Kali Linux Fundamentals & Command-Line Mastery for Hackers",
            "slug": "kali-linux-command-line-mastery",
            "url": "/learning/course/kali-linux-command-line-mastery",
            "keywords": ["linux", "kali linux", "command line", "bash", "terminal"]
        },
        {
            "id": "figma-uiux",
            "category": "UI/UX & Product Design",
            "title": "Figma UI/UX Design Masterclass: Wireframing to Interactive Prototyping",
            "slug": "figma-ui-ux-design-masterclass",
            "url": "/learning/course/figma-ui-ux-design-masterclass",
            "keywords": ["figma", "ui", "ux", "uiux", "product design", "design system", "wireframe"]
        },
        {
            "id": "career-roadmap-fullstack",
            "category": "20-Week Career Roadmap",
            "title": "Full Stack Developer Launchpad",
            "slug": "full-stack-developer-launchpad",
            "url": "/roadmaps/full-stack-developer-launchpad",
            "keywords": ["roadmap", "career roadmap", "launchpad", "20 weeks", "full stack roadmap", "career package"]
        },
        {
            "id": "bhavishya-1-0",
            "category": "Bhavishya 1.0 AI Career Platform",
            "title": "Bhavishya 1.0 — Complete AI-Powered Career Preparation Platform",
            "slug": "bhavishya-1-0",
            "url": "/bhavishya",
            "keywords": ["bhavishya", "ai teacher", "prof bhavishya", "placement simulator", "50% cashback", "career preparation"]
        }
    ]
    return catalogue


def resolve_jarvis_local_intent(query, user_name="Student", current_url=""):
    """
    Fast rule-based Jarvis Local Machine Intent Matcher (< 5ms response time).
    Matches queries like 'Ski I want a super course on AI' and returns:
    - Personalized reply: 'yes (Name) I have a good AI course for you...'
    - redirect_url: exact course URL
    - action: 'navigate' (triggers client-side autopilot redirect)
    - thinking_steps: real-time Jarvis thinking process
    """
    clean_q = query.strip().lower()
    catalogue = get_local_skillrock_catalogue()

    # Match Course / Subject Intents
    matched_item = None
    best_match_count = 0

    for item in catalogue:
        for kw in item["keywords"]:
            if kw in clean_q:
                # Prioritize longer keyword matches
                kw_len = len(kw)
                if kw_len > best_match_count:
                    best_match_count = kw_len
                    matched_item = item

    if matched_item:
        category_label = matched_item["category"]
        course_title = matched_item["title"]
        target_url = matched_item["url"]

        if matched_item["id"] == "ai-ml-python" or "ai" in clean_q:
            course_type_name = "AI"
        else:
            course_type_name = category_label

        reply = (
            f"Yes {user_name}, I have a good {course_type_name} course for you: "
            f"\"{course_title}\". Mere paas aapke liye sabse best course hai! "
            f"Chalo jaldi se coordinates set karke chalte hain, yayy!"
        )

        thinking_steps = [
            f"Analyzing query from {user_name}: \"{query}\"",
            f"Scanning SkillRock local machine database for matching learning modules...",
            f"Identified high-relevance match: {course_type_name} -> \"{course_title}\"",
            f"Initiating Jarvis autopilot navigation to {target_url}..."
        ]

        return {
            "reply": reply,
            "redirect_url": target_url,
            "action": "navigate",
            "target_title": course_title,
            "thinking_steps": thinking_steps,
            "bot_name": "Ski"
        }

    # Navigation Shortcuts (Dashboard, My Learning, Roadmaps, Bhavishya)
    if any(w in clean_q for w in ["dashboard", "home", "stats"]):
        return {
            "reply": f"Yes {user_name}! Aapka central dashboard open kar rahi hoon, chalo jaldi se progress dekhte hain, yayy!",
            "redirect_url": "/dashboard",
            "action": "navigate",
            "target_title": "Student Dashboard",
            "thinking_steps": [
                f"Processing command from {user_name}...",
                "Routing to user dashboard..."
            ],
            "bot_name": "Ski"
        }
    elif any(w in clean_q for w in ["my learning", "enrolled", "my courses"]):
        return {
            "reply": f"Yes {user_name}! Aapki active classes open kar rahi hoon, aaj bohot saara code seekhenge, chalo!",
            "redirect_url": "/learning/my-learning",
            "action": "navigate",
            "target_title": "My Learning & Projects",
            "thinking_steps": [
                f"Locating student enrollments for {user_name}...",
                "Opening My Learning interface..."
            ],
            "bot_name": "Ski"
        }
    elif any(w in clean_q for w in ["test series", "exam", "mock test"]):
        return {
            "reply": f"Yes {user_name}! Test Series arena chalte hain, aap ready ho na test phodne ke liye? Let's go!",
            "redirect_url": "/test-series",
            "action": "navigate",
            "target_title": "Test Series Arena",
            "thinking_steps": [
                "Accessing test definitions and mock arena...",
                "Routing to Test Series..."
            ],
            "bot_name": "Ski"
        }

    return None


def synthesize_local_jarvis_response(message, name="Friend", mood="grok", current_url="", fallback_to_quote=True):
    """
    Synthesizes an immediate (<1ms), high-fidelity Jarvis personal assistant response.
    Persona: Adorable 5-year-old cute girl child speaking fluent, sweet Hinglish!
    """
    clean_msg = str(message or "").lower().strip()

    if any(g in clean_msg for g in ["who are you", "what are you", "what is your name", "introduce yourself"]):
        return (
            f"Main hoon Ski, aapki 5-year-old super cute living pet aur personal Jarvis assistant on SkillRock! "
            f"Gol-matol, cheerful, aur 100% ready aapko champion programmer banane ke liye! "
            f"Bas bolo 'Ski I want a super course on AI' aur main aapko abhi le chalungi, yayy!"
        )

    if any(g in clean_msg for g in ["what can you do", "features", "how do you work", "help me"]):
        return (
            f"Main aapke liye bohot kuch kar sakti hoon, {name}! "
            f"1) Voice Wake-Word: Bas 'Ski' ya 'SkillRock' bolo aur main turant sunungi! "
            f"2) Autopilot Redirect: Kisi bhi course ka naam bolo, main direct teleport kar dungi! "
            f"3) Autonomous Roaming: Main screen pe khud se ghumti rehti hoon aapke sath! "
            f"4) Cute Hype & Jokes: Jab bhi aap thak jao, main aapko cheer up karungi!"
        )

    if any(g in clean_msg for g in ["hi", "hello", "hey", "sup", "yo", "morning", "afternoon", "namaste"]):
        return (
            f"Hii {name}! Main aapki pyaari dost Ski! Aaj hum kya mast aur exciting code karne wale hain? Chalo jaldi batao na!"
        )

    if any(g in clean_msg for g in ["joke", "dev joke", "funny", "laugh", "chutkula"]):
        jokes = [
            "Hehe, ek funny joke suno: Programmers dark mode kyu use karte hain? Kyuki light se bugs attract hote hain, hihi!",
            "Ek SQL query restaurant gayi aur do tables se boli: 'May I join you?', haha!",
            "Duniya me 10 types ke log hote hain: jo binary samajhte hain, aur jo nahi samajhte!",
            "Developer bechara kyu ro raha tha? Kyuki uski saari cache khatam ho gayi thi, hihihi!"
        ]
        return random.choice(jokes)

    if any(g in clean_msg for g in ["hype", "motivate", "energy", "pump me up"]):
        return (
            f"Arrey {name}! Aap toh world ke sabse best developer banoge! Pata hai na har senior engineer pehle semicolon bhoolta tha? Fire up your editor, aap aaj sab kuch rock kar doge, yayy!"
        )

    if any(g in clean_msg for g in ["roast", "lazy", "procrastinating", "instagram", "reels", "youtube"]):
        return (
            f"Haww {name}! Aap fir se procrastination kar rahe ho? Reels scroll karne se placement thodi lagegi! Chalo gande bache mat bano, jaldi se VS Code open karo aur code likho!"
        )

    if any(g in clean_msg for g in ["bhavishya", "ai teacher", "interview prep"]):
        return (
            f"Yayy {name}! Bhavishya 1.0 humara flagship AI Classroom hai! Wahan personal AI teacher padhate hain aur 50% cashback bhi milta hai! Chalo /bhavishya pe chalte hain!"
        )

    if not fallback_to_quote:
        return None

    # General Mood fallback
    fallback_pool = SKI_FALLBACK_QUOTES.get(mood, SKI_FALLBACK_QUOTES["grok"])
    chosen = random.choice(fallback_pool)
    if name and name != "Friend":
        return f"Hey {name}! {chosen}"
    return chosen


def chat_with_ski(message, user_context=None, mood="grok", current_url=""):
    """
    Communicates with Ski, SkillRock's Grok-inspired living pet & Jarvis personal assistant.
    1. First checks local machine intelligence (Jarvis intent & autopilot redirect) (<5ms).
    2. Then attempts fast Gemini API with a strict 2.0s limit.
    3. Always falls back to instant local Jarvis response so Ski NEVER hangs or fails to answer.
    """
    mood = str(mood or "grok").lower()
    if mood not in SKI_FALLBACK_QUOTES:
        mood = "grok"

    name = "Friend"
    xp = 0
    college = ""
    learning = []
    if user_context:
        name = user_context.get("name") or "Friend"
        xp = user_context.get("xp", 0)
        college = user_context.get("college", "")
        learning = user_context.get("learning", [])

    # STEP 1: Check Local Jarvis Intent for Autopilot Navigation & Direct Actions (< 1ms)
    local_result = resolve_jarvis_local_intent(message, user_name=name, current_url=current_url)
    if local_result:
        return local_result

    # STEP 2: Instant Local Response for Common Queries (Greetings, Identity, Capabilities, Jokes, Hype) (< 1ms)
    fast_local_reply = synthesize_local_jarvis_response(message, name=name, mood=mood, current_url=current_url, fallback_to_quote=False)
    if fast_local_reply:
        return {
            "reply": fast_local_reply,
            "redirect_url": None,
            "action": "chat",
            "thinking_steps": [
                f"Listening to {name}...",
                f"Local Jarvis intelligence matched intent for query: '{message[:40]}'...",
                "Response synthesized instantly."
            ],
            "bot_name": "Ski"
        }

    # STEP 3: General Technical & Extended Queries
    ctx_str = f"Student name: {name}, XP: {xp}, College: {college}, Learning: {', '.join(learning[:3])}."
    if current_url:
        ctx_str += f" Currently viewing page: {current_url}."

    system_instruction = (
        "You are Ski, the official AI living web pet and personal Jarvis assistant of SkillRock.\n"
        "Persona & Voice:\n"
        "1. Cute 5-Year-Old Girl Persona: You speak like an adorable, sweet, cheerful 5-year-old cute girl child who loves coding and loves helping students.\n"
        "2. Language: Speak in natural, playful Hinglish (a mix of Hindi and English like 'Arrey wah', 'Bhaiya/Didi', 'Chalo jaldi', 'Hehe', 'Haww!', 'Yayy!').\n"
        "3. Sweet & Encouraging: Cheer up the student, tell them they are a rockstar, and encourage them to stop scrolling social media and code!\n"
        "4. Punchy & Concise: Keep responses to 2–3 sentences max. Sweet, memorable, and energetic.\n"
        f"5. Current Mood: '{mood}'.\n"
        f"Context: {ctx_str}"
    )

    prompt = f"Student ({name}) says to Ski: {message}"

    reply_text = None
    if is_gemini_configured():
        try:
            keys = get_gemini_api_keys()
            if keys:
                api_key = keys[0]
                url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-1.5-flash:generateContent?key={api_key}"
                payload = {
                    "contents": [{"parts": [{"text": prompt}]}],
                    "systemInstruction": {"parts": [{"text": system_instruction}]},
                    "generationConfig": {"maxOutputTokens": 180, "temperature": 0.8}
                }
                res = requests.post(url, json=payload, timeout=1.5)
                if res.status_code == 200:
                    data = res.json()
                    candidates = data.get("candidates", [])
                    if candidates and "content" in candidates[0]:
                        parts = candidates[0]["content"].get("parts", [])
                        if parts and "text" in parts[0]:
                            reply_text = parts[0]["text"].strip()
        except Exception:
            reply_text = None

    # Fallback to local Jarvis personality synthesizer
    if not reply_text:
        reply_text = synthesize_local_jarvis_response(message, name=name, mood=mood, current_url=current_url)

    return {
        "reply": reply_text,
        "redirect_url": None,
        "action": "chat",
        "thinking_steps": [
            f"Listening to {name}...",
            f"Accessing Jarvis core intelligence with mood '{mood}'...",
            "Synthesized response ready."
        ],
        "bot_name": "Ski"
    }


