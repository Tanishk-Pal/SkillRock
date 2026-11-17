from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
import random
from services.ai_service import (
    chat_with_skillbot,
    get_skill_recommendations,
    get_learning_roadmap,
    normalize_skill,
    chat_with_ski,
    SKI_FALLBACK_QUOTES,
)
from models import Skill

ai_bp = Blueprint("ai", __name__)

@ai_bp.route("/ai/assistant")
def assistant_page():
    all_skills = Skill.find_all()
    user_context = None
    if current_user.is_authenticated:
        user_context = {
            "name": current_user.name,
            "college": current_user.college,
            "branch": current_user.branch,
            "teaching": [s.name for s in current_user.teaching_skills],
            "learning": [s.name for s in current_user.learning_skills],
            "xp": current_user.xp,
            "level": current_user.level_name
        }
    return render_template("ai_assistant.html", all_skills=all_skills, user_context=user_context)


@ai_bp.route("/api/ai/chat", methods=["POST"])
def api_chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    if not message:
        return jsonify({"error": "Message is required."}), 400

    user_context = None
    if current_user.is_authenticated:
        user_context = {
            "name": current_user.name,
            "college": current_user.college,
            "branch": current_user.branch,
            "teaching": [s.name for s in current_user.teaching_skills],
            "learning": [s.name for s in current_user.learning_skills],
            "xp": current_user.xp
        }

    response_text = chat_with_skillbot(message, user_context=user_context)
    return jsonify({
        "success": True,
        "reply": response_text
    })


@ai_bp.route("/api/ai/recommend-skills", methods=["POST"])
def api_recommend_skills():
    data = request.get_json(silent=True) or {}
    query = data.get("query", "").strip()
    
    current_skills = []
    if current_user.is_authenticated:
        current_skills = [s.name for s in current_user.teaching_skills] + [s.name for s in current_user.learning_skills]

    result = get_skill_recommendations(query or "software development", current_skills)
    return jsonify(result)


@ai_bp.route("/api/ai/roadmap", methods=["GET", "POST"])
def api_roadmap():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        skill_name = data.get("skill", "").strip()
    else:
        skill_name = request.args.get("skill", "").strip()

    if not skill_name:
        return jsonify({"error": "Skill name is required."}), 400

    roadmap = get_learning_roadmap(skill_name)
    return jsonify(roadmap)


@ai_bp.route("/api/ai/normalize", methods=["POST"])
def api_normalize():
    data = request.get_json(silent=True) or {}
    raw_skill = data.get("skill", "").strip()
    normalized = normalize_skill(raw_skill)
    return jsonify({"original": raw_skill, "normalized": normalized})


# ==============================================================================
# Ski — Grok-Inspired AI Companion & Motivational Study Partner Routes
# ==============================================================================

@ai_bp.route("/ski")
def ski_hub():
    """
    Ski — SkillRock's Grok-Inspired AI Study Partner & Motivation Mascot.
    Full interactive companion hub with 3D sphere avatar, moods, sound, and quick quests.
    """
    user_context = None
    if current_user.is_authenticated:
        user_context = {
            "name": current_user.name,
            "college": current_user.college,
            "branch": current_user.branch,
            "xp": current_user.xp,
            "level": current_user.level_name
        }
    return render_template("ski.html", user_context=user_context)


@ai_bp.route("/api/ski/chat", methods=["POST"])
def api_ski_chat():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "").strip()
    mood = data.get("mood", "grok").strip()
    current_url = data.get("current_url", "").strip()
    if not message:
        return jsonify({"error": "Message is required."}), 400

    user_context = None
    if current_user.is_authenticated:
        user_context = {
            "name": current_user.name,
            "college": current_user.college,
            "branch": current_user.branch,
            "xp": current_user.xp,
            "level": current_user.level_name
        }

    res_data = chat_with_ski(message, user_context=user_context, mood=mood, current_url=current_url)
    if isinstance(res_data, str):
        res_data = {
            "reply": res_data,
            "redirect_url": None,
            "action": "chat",
            "thinking_steps": ["Processed query with Ski."],
            "bot_name": "Ski"
        }

    res_data["success"] = True
    res_data["mood"] = mood
    return jsonify(res_data)


@ai_bp.route("/api/ski/quote", methods=["GET"])
def api_ski_quote():
    mood = request.args.get("mood", "grok").lower()
    pool = SKI_FALLBACK_QUOTES.get(mood, SKI_FALLBACK_QUOTES["grok"])
    return jsonify({
        "success": True,
        "quote": random.choice(pool),
        "mood": mood
    })

