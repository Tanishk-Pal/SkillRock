"""
SkillSwap Campus — MongoDB Database Initialization Script
Initializes MongoDB collections, unique indexes, and standard skills/badges.
Does NOT create fake users, demo credentials, or fake sessions.
"""

import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from models.mongo import get_db, init_indexes, Skill, Badge

STANDARD_SKILLS = [
    {"name": "Python", "category": "Programming", "icon": "terminal", "description": "Backend development, scripting, and automation"},
    {"name": "C++", "category": "Programming", "icon": "cpu", "description": "High performance computing, STL, and DSA"},
    {"name": "Java", "category": "Programming", "icon": "coffee", "description": "OOP, enterprise systems, and Android development"},
    {"name": "JavaScript", "category": "Programming", "icon": "code", "description": "Modern frontend, DOM, and full-stack JS"},
    {"name": "React", "category": "Programming", "icon": "layers", "description": "Modern component architecture and state management"},
    {"name": "HTML & CSS", "category": "Programming", "icon": "layout", "description": "Responsive layout design, Flexbox, and CSS Grid"},
    {"name": "SQL", "category": "Programming", "icon": "database", "description": "Relational database queries, indexing, and joins"},
    {"name": "Git & GitHub", "category": "Programming", "icon": "git-branch", "description": "Version control, branching workflows, and PR collaboration"},
    {"name": "Machine Learning", "category": "Data Science", "icon": "activity", "description": "Data preprocessing, Scikit-learn, and model training"},
    {"name": "UI/UX", "category": "Design", "icon": "pen-tool", "description": "User research, wireframing, and design thinking"},
    {"name": "Figma", "category": "Design", "icon": "figma", "description": "Auto-layout, responsive component systems, and interactive prototypes"},
    {"name": "Photoshop", "category": "Design", "icon": "image", "description": "Digital composites, photo retouching, and asset export"},
    {"name": "Video Editing", "category": "Media & Creative", "icon": "video", "description": "Pacing, cutting, audio mixing, and color grading in Premiere Pro"},
    {"name": "Public Speaking", "category": "Soft Skills", "icon": "mic", "description": "Stage presence, speech delivery, and presentation clarity"},
    {"name": "Communication", "category": "Soft Skills", "icon": "message-circle", "description": "Interpersonal clarity, active listening, and interview prep"},
    {"name": "Excel", "category": "Productivity", "icon": "table", "description": "Formulas, VLOOKUP/XLOOKUP, Pivot Tables, and analysis"}
]

def init_database():
    print("[1/3] Connecting to MongoDB and verifying collections...")
    db = get_db()
    init_indexes(db)
    print("      -> MongoDB indexes and uniqueness constraints verified.")

    print("[2/3] Seeding standard campus skills...")
    for s_data in STANDARD_SKILLS:
        Skill.create_or_get(
            name=s_data["name"],
            category=s_data["category"],
            icon=s_data["icon"],
            description=s_data["description"]
        )
    print(f"      -> {len(STANDARD_SKILLS)} standard skills ready.")

    print("[3/3] Seeding system badges...")
    badges = Badge.get_all()
    print(f"      -> {len(badges)} system achievement badges initialized.")

    print("\n[SUCCESS] Production MongoDB database initialized!")
    print("Zero fake users or demo accounts present. Ready for real student signups.\n")

if __name__ == "__main__":
    init_database()
