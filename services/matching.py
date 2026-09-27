"""
SkillSwap Campus — Skill Matching Engine
Calculates clean, transparent compatibility scores based on exact business logic:
- Mutual direct match: 70 points
- One-way match: 45 points
- Related skill: 30 points
- Same college: +10 points
- Same branch: +5 points
- Same year: +5 points
- Maximum: 100%
"""

from bson import ObjectId

SKILL_CLUSTERS = {
    "web_development": {"javascript", "react", "html", "css", "node.js", "nodejs", "flask", "django", "rest apis", "typescript", "vue", "tailwind"},
    "core_programming": {"python", "c++", "cpp", "c", "java", "data structures", "algorithms", "git", "github", "linux"},
    "data_ai": {"python", "machine learning", "deep learning", "sql", "data science", "pandas", "numpy", "tensorflow", "pytorch", "power bi"},
    "design_uiux": {"ui/ux", "ui ux", "figma", "photoshop", "canva", "illustrator", "wireframing", "graphic design"},
    "media_creative": {"video editing", "photography", "premiere pro", "after effects", "content writing", "copywriting", "audio editing"},
    "communication_softskills": {"public speaking", "communication", "presentation skills", "english speaking", "leadership", "interview prep"},
    "productivity_tools": {"excel", "advanced excel", "notion", "project management", "prompt engineering"}
}

def normalize_skill_name(name):
    """Normalize skill name for robust string and alias comparison."""
    if not name:
        return ""
    clean = name.strip().lower()
    clean = clean.replace("++", "pp").replace("/", " ").replace("-", " ")
    aliases = {
        "ui ux": "ui/ux",
        "ui/ux design": "ui/ux",
        "cpp": "c++",
        "python 3": "python",
        "python programming": "python",
        "js": "javascript",
        "reactjs": "react",
        "react.js": "react",
        "ms excel": "excel",
    }
    return aliases.get(clean, clean)

def are_skills_related(skill_a, skill_b):
    """Checks if two skill strings belong to the same cluster."""
    norm_a = normalize_skill_name(skill_a)
    norm_b = normalize_skill_name(skill_b)

    if norm_a == norm_b:
        return True

    for cluster_skills in SKILL_CLUSTERS.values():
        has_a = any(norm_a in s or s in norm_a for s in cluster_skills)
        has_b = any(norm_b in s or s in norm_b for s in cluster_skills)
        if has_a and has_b:
            return True

    return False

def calculate_match_score(user_a, user_b):
    """
    Calculates exact compatibility score between User A (active user) and User B (target user).
    
    Exact Rules:
    - Mutual direct match: 70
    - One-way match: 45
    - Related skill: 30
    - Same college: +10
    - Same branch: +5
    - Same year: +5
    - Capped at 100%
    """
    if str(user_a.id) == str(user_b.id):
        return {
            "score": 0,
            "reasons": ["Same user"],
            "b_teaches_a_wants": [],
            "a_teaches_b_wants": [],
            "mutual_pairs": []
        }

    a_teaches = [s.name for s in user_a.teaching_skills]
    a_wants = [s.name for s in user_a.learning_skills]

    b_teaches = [s.name for s in user_b.teaching_skills]
    b_wants = [s.name for s in user_b.learning_skills]

    # Find skill intersections
    b_teaches_a_wants = []
    for s_w in a_wants:
        for s_t in b_teaches:
            if s_w.lower() == s_t.lower() or normalize_skill_name(s_w) == normalize_skill_name(s_t):
                b_teaches_a_wants.append((s_t, s_w))

    a_teaches_b_wants = []
    for s_t in a_teaches:
        for s_w in b_wants:
            if s_t.lower() == s_w.lower() or normalize_skill_name(s_t) == normalize_skill_name(s_w):
                a_teaches_b_wants.append((s_t, s_w))

    score = 0
    reasons = []
    mutual_pairs = []

    # 1. Mutual Direct Match (70 pts)
    if b_teaches_a_wants and a_teaches_b_wants:
        score = 70
        reasons.append(f"{user_b.name} can teach {b_teaches_a_wants[0][0]}, and you want to learn it.")
        reasons.append(f"You can teach {a_teaches_b_wants[0][0]}, and {user_b.name} wants to learn it.")
        mutual_pairs.append((a_teaches_b_wants[0][0], b_teaches_a_wants[0][0]))
    # 2. One-Way Match (45 pts)
    elif b_teaches_a_wants:
        score = 45
        reasons.append(f"{user_b.name} teaches {b_teaches_a_wants[0][0]}, which you want to learn.")
    elif a_teaches_b_wants:
        score = 45
        reasons.append(f"You teach {a_teaches_b_wants[0][0]}, which {user_b.name} wants to learn.")
    else:
        # 3. Related Skill (30 pts)
        related_pair = None
        for s_w in a_wants:
            for s_t in b_teaches:
                if are_skills_related(s_w, s_t):
                    related_pair = (s_t, s_w)
                    break
            if related_pair:
                break

        if not related_pair:
            for s_t in a_teaches:
                for s_w in b_wants:
                    if are_skills_related(s_t, s_w):
                        related_pair = (s_t, s_w)
                        break
                if related_pair:
                    break

        if related_pair:
            score = 30
            reasons.append(f"Related skills: {related_pair[0]} and {related_pair[1]}.")

    # Additional campus compatibility points
    if user_a.college and user_b.college and user_a.college.strip().lower() == user_b.college.strip().lower():
        score += 10
        reasons.append(f"Same college: {user_a.college}.")

    if user_a.branch and user_b.branch and user_a.branch.strip().lower() == user_b.branch.strip().lower():
        score += 5
        reasons.append(f"Same branch: {user_a.branch}.")

    if user_a.year and user_b.year and user_a.year.strip().lower() == user_b.year.strip().lower():
        score += 5
        reasons.append(f"Same year: {user_a.year}.")

    final_score = min(100, max(0, score))

    return {
        "score": final_score,
        "reasons": reasons,
        "b_teaches_a_wants": [pair[0] for pair in b_teaches_a_wants],
        "a_teaches_b_wants": [pair[0] for pair in a_teaches_b_wants],
        "mutual_pairs": mutual_pairs
    }

def get_top_matches_for_user(user, limit=3):
    """Retrieves top recommended students from MongoDB sorted by compatibility score."""
    from models import User
    from models.mongo import _to_obj_id

    query = {}
    if user.id:
        query = {"_id": {"$ne": _to_obj_id(user.id)}}
    other_users = User.find_all(query)
    results = []

    for other in other_users:
        match_info = calculate_match_score(user, other)
        can_teach_them = match_info["a_teaches_b_wants"][0] if match_info["a_teaches_b_wants"] else (user.teaching_skills[0].name if user.teaching_skills else "Knowledge")
        can_learn_from_them = match_info["b_teaches_a_wants"][0] if match_info["b_teaches_a_wants"] else (other.teaching_skills[0].name if other.teaching_skills else "Skills")

        results.append({
            "user": other,
            "score": match_info["score"],
            "reasons": match_info["reasons"],
            "can_teach_them": can_teach_them,
            "can_learn_from_them": can_learn_from_them,
            "b_teaches_a_wants": match_info["b_teaches_a_wants"],
            "a_teaches_b_wants": match_info["a_teaches_b_wants"]
        })

    results.sort(key=lambda x: x["score"], reverse=True)
    return results[:limit]
