from flask import Blueprint, render_template, request, jsonify
from flask_login import current_user
from services.ai_service import chat_with_skillbot, get_skill_recommendations, get_learning_roadmap, normalize_skill
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
