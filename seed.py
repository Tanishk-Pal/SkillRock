"""
SkillSwap Campus - Database Seed Script
Populates demo users, skills, badges, connections, sessions, and ratings.
Demo Account:
  Email: demo@skillswap.local
  Password: Demo@123
"""

from datetime import datetime, timedelta
from app import create_app
from models import db, User, Skill, UserSkill, Badge, UserBadge, SwapRequest, Connection, Session, Rating

import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

def seed_database():
    app = create_app()
    with app.app_context():
        print("[+] Resetting and seeding database...")
        db.drop_all()
        db.create_all()

        # 1. Seed Badges
        badges_data = [
            {
                "name": "First Swap",
                "slug": "first-swap",
                "description": "Completed first skill exchange on campus",
                "icon": "zap",
                "color": "#06b6d4"
            },
            {
                "name": "Knowledge Sharer",
                "slug": "knowledge-sharer",
                "description": "Taught 5 or more peer learning sessions",
                "icon": "book-open",
                "color": "#3b82f6"
            },
            {
                "name": "Fast Learner",
                "slug": "fast-learner",
                "description": "Completed 5 or more student learning sessions",
                "icon": "award",
                "color": "#10b981"
            },
            {
                "name": "Community Builder",
                "slug": "community-builder",
                "description": "Connected and swapped skills with 10+ students",
                "icon": "users",
                "color": "#8b5cf6"
            },
            {
                "name": "Skill Mentor",
                "slug": "skill-mentor",
                "description": "Reached 1000+ XP in skill exchanges",
                "icon": "crown",
                "color": "#f59e0b"
            }
        ]

        badges_dict = {}
        for b_data in badges_data:
            badge = Badge(**b_data)
            db.session.add(badge)
            badges_dict[b_data["slug"]] = badge
        db.session.flush()

        # 2. Seed Skills
        skills_data = [
            {"name": "Python", "category": "Programming", "icon": "terminal", "description": "General programming, backend dev, and scripting"},
            {"name": "C++", "category": "Programming", "icon": "cpu", "description": "High performance computing, STL, and DSA"},
            {"name": "Java", "category": "Programming", "icon": "coffee", "description": "OOP, enterprise apps, and Android dev"},
            {"name": "JavaScript", "category": "Programming", "icon": "code", "description": "Modern frontend, DOM, and fullstack JS"},
            {"name": "React", "category": "Programming", "icon": "layers", "description": "Component-based modern frontend web architecture"},
            {"name": "HTML & CSS", "category": "Programming", "icon": "layout", "description": "Responsive layout design, flexbox, and CSS grid"},
            {"name": "SQL", "category": "Programming", "icon": "database", "description": "Relational queries, database indexing, and joins"},
            {"name": "Git & GitHub", "category": "Programming", "icon": "git-branch", "description": "Version control, branching, PRs, and collaboration"},
            {"name": "Machine Learning", "category": "Data Science", "icon": "activity", "description": "Model training, Scikit-learn, and feature engineering"},
            {"name": "UI/UX", "category": "Design", "icon": "pen-tool", "description": "User experience, visual hierarchy, and prototyping"},
            {"name": "Figma", "category": "Design", "icon": "figma", "description": "Auto-layout, responsive component libraries, and design systems"},
            {"name": "Photoshop", "category": "Design", "icon": "image", "description": "Graphic editing, digital composites, and asset creation"},
            {"name": "Canva", "category": "Design", "icon": "sparkles", "description": "Quick graphic design, posters, and pitch deck decks"},
            {"name": "Video Editing", "category": "Media & Creative", "icon": "video", "description": "Pacing, B-roll cutting, sound mixing, and color grading"},
            {"name": "Photography", "category": "Media & Creative", "icon": "camera", "description": "Composition, lighting, framing, and lightroom edits"},
            {"name": "Content Writing", "category": "Media & Creative", "icon": "file-text", "description": "Technical blogs, storytelling, and copywriting"},
            {"name": "Public Speaking", "category": "Soft Skills", "icon": "mic", "description": "Stage presence, presentations, and TED-style delivery"},
            {"name": "Communication", "category": "Soft Skills", "icon": "message-circle", "description": "Interpersonal clarity, interview skills, and active listening"},
            {"name": "Excel", "category": "Productivity", "icon": "table", "description": "VLOOKUP, XLOOKUP, Pivot tables, and financial formulas"}
        ]

        skills_dict = {}
        for s_data in skills_data:
            skill = Skill(**s_data)
            db.session.add(skill)
            skills_dict[s_data["name"]] = skill
        db.session.flush()

        # 3. Seed Users
        # Main Demo Account
        demo_user = User(
            name="Tanishk Pal",
            email="demo@skillswap.local",
            college="Delhi Technological University (DTU)",
            branch="Computer Science & Engineering",
            year="2nd Year",
            bio="Passionate CSE student looking to exchange Python and Git knowledge for UI/UX and Video Editing skills! Building cool web products.",
            avatar_seed="Tanishk_Pal",
            xp=380,
            rating=4.9,
            rating_count=8
        )
        demo_user.set_password("Demo@123")
        db.session.add(demo_user)
        db.session.flush()

        # Seed other students with complementary skills
        students_info = [
            {
                "name": "Rahul Sharma",
                "email": "rahul.sharma@campus.edu",
                "college": "Delhi Technological University (DTU)",
                "branch": "Computer Science & Engineering",
                "year": "2nd Year",
                "bio": "Competitive programmer & open source enthusiast. Love teaching Python and Git; really eager to learn Figma & UI/UX design.",
                "avatar_seed": "Rahul_Dev",
                "xp": 420,
                "rating": 4.9,
                "rating_count": 9,
                "teaches": ["Python", "Git & GitHub", "C++"],
                "wants": ["UI/UX", "Figma"]
            },
            {
                "name": "Ananya Verma",
                "email": "ananya.verma@campus.edu",
                "college": "Delhi Technological University (DTU)",
                "branch": "Information Technology",
                "year": "3rd Year",
                "bio": "Product designer and design lead at college tech society. Can teach Figma, wireframing and design systems. Looking to learn Python for automation.",
                "avatar_seed": "Ananya_Design",
                "xp": 560,
                "rating": 5.0,
                "rating_count": 12,
                "teaches": ["UI/UX", "Figma", "Canva"],
                "wants": ["Python", "React"]
            },
            {
                "name": "Aman Gupta",
                "email": "aman.gupta@campus.edu",
                "college": "Netaji Subhas University of Technology (NSUT)",
                "branch": "Computer Science & Engineering",
                "year": "2nd Year",
                "bio": "C++ geek preparing for internships. Want to learn video editing for my YouTube coding tutorials.",
                "avatar_seed": "Aman_Coder",
                "xp": 310,
                "rating": 4.8,
                "rating_count": 6,
                "teaches": ["C++", "SQL", "Python"],
                "wants": ["Video Editing", "Content Writing"]
            },
            {
                "name": "Priya Nair",
                "email": "priya.nair@campus.edu",
                "college": "Netaji Subhas University of Technology (NSUT)",
                "branch": "Electronics & Communication",
                "year": "3rd Year",
                "bio": "College media club head. Expert in Premiere Pro, color grading and storytelling. Looking for a tutor in C++ and DSA.",
                "avatar_seed": "Priya_Media",
                "xp": 490,
                "rating": 4.9,
                "rating_count": 11,
                "teaches": ["Video Editing", "Photography", "Canva"],
                "wants": ["C++", "Python"]
            },
            {
                "name": "Arjun Mehta",
                "email": "arjun.mehta@campus.edu",
                "college": "IIT Delhi",
                "branch": "Electrical Engineering",
                "year": "4th Year",
                "bio": "Full-stack developer building SaaS side-projects. Great at modern JavaScript and React. Seeking mentorship in public speaking and pitching.",
                "avatar_seed": "Arjun_JS",
                "xp": 820,
                "rating": 5.0,
                "rating_count": 18,
                "teaches": ["JavaScript", "React", "HTML & CSS"],
                "wants": ["Public Speaking", "Communication"]
            },
            {
                "name": "Neha Kapoor",
                "email": "neha.kapoor@campus.edu",
                "college": "IIT Delhi",
                "branch": "Management & Economics",
                "year": "3rd Year",
                "bio": "Debating society president & TEDx student speaker. Love helping students speak with conviction. Want to learn JavaScript web dev basics.",
                "avatar_seed": "Neha_Speak",
                "xp": 640,
                "rating": 4.9,
                "rating_count": 14,
                "teaches": ["Public Speaking", "Communication", "Content Writing"],
                "wants": ["JavaScript", "Python"]
            },
            {
                "name": "Kavya Patel",
                "email": "kavya.patel@campus.edu",
                "college": "Delhi Technological University (DTU)",
                "branch": "Mathematics & Computing",
                "year": "2nd Year",
                "bio": "Data enthusiast who loves Pandas and SQL. Can teach Excel and Data analysis. Looking to master Machine Learning and Python OOP.",
                "avatar_seed": "Kavya_Data",
                "xp": 35,
                "rating": 0.0,
                "rating_count": 0,
                "teaches": ["Excel", "SQL"],
                "wants": ["Machine Learning", "Python"]
            },
            {
                "name": "Devendra Singh",
                "email": "devendra.singh@campus.edu",
                "college": "Indraprastha Institute of Information Technology (IIIT-D)",
                "branch": "Computer Science & Artificial Intelligence",
                "year": "4th Year",
                "bio": "AI researcher and hackathon winner. Can guide in Machine Learning, Scikit-learn, and Python. Want to learn Photoshop and graphic design.",
                "avatar_seed": "Dev_AI",
                "xp": 1050,
                "rating": 5.0,
                "rating_count": 22,
                "teaches": ["Machine Learning", "Python"],
                "wants": ["Photoshop", "UI/UX"]
            }
        ]

        created_users = {"demo": demo_user}

        # Setup Demo User's Skills
        demo_teach_skills = ["Python", "Git & GitHub"]
        demo_learn_skills = ["UI/UX", "Video Editing"]

        for s_name in demo_teach_skills:
            if s_name in skills_dict:
                db.session.add(UserSkill(user_id=demo_user.id, skill_id=skills_dict[s_name].id, skill_type="teach", proficiency="Advanced"))
        for s_name in demo_learn_skills:
            if s_name in skills_dict:
                db.session.add(UserSkill(user_id=demo_user.id, skill_id=skills_dict[s_name].id, skill_type="learn", proficiency="Beginner"))

        # Setup other students
        for s_info in students_info:
            user = User(
                name=s_info["name"],
                email=s_info["email"],
                college=s_info["college"],
                branch=s_info["branch"],
                year=s_info["year"],
                bio=s_info["bio"],
                avatar_seed=s_info["avatar_seed"],
                xp=s_info["xp"],
                rating=s_info["rating"],
                rating_count=s_info["rating_count"]
            )
            user.set_password("Student@123")
            db.session.add(user)
            db.session.flush()
            created_users[s_info["name"].split()[0].lower()] = user

            # Attach skills
            for ts in s_info["teaches"]:
                if ts in skills_dict:
                    db.session.add(UserSkill(user_id=user.id, skill_id=skills_dict[ts].id, skill_type="teach", proficiency="Advanced"))
            for ws in s_info["wants"]:
                if ws in skills_dict:
                    db.session.add(UserSkill(user_id=user.id, skill_id=skills_dict[ws].id, skill_type="learn", proficiency="Beginner"))

        db.session.flush()

        # 4. Award initial badges to users
        # Demo user badges
        db.session.add(UserBadge(user_id=demo_user.id, badge_id=badges_dict["first-swap"].id))
        db.session.add(UserBadge(user_id=demo_user.id, badge_id=badges_dict["fast-learner"].id))

        # Rahul badges
        rahul = created_users["rahul"]
        db.session.add(UserBadge(user_id=rahul.id, badge_id=badges_dict["first-swap"].id))
        db.session.add(UserBadge(user_id=rahul.id, badge_id=badges_dict["knowledge-sharer"].id))

        # Ananya badges
        ananya = created_users["ananya"]
        db.session.add(UserBadge(user_id=ananya.id, badge_id=badges_dict["first-swap"].id))
        db.session.add(UserBadge(user_id=ananya.id, badge_id=badges_dict["knowledge-sharer"].id))

        # Devendra badge (Mentor >= 1000 XP)
        dev = created_users["devendra"]
        db.session.add(UserBadge(user_id=dev.id, badge_id=badges_dict["first-swap"].id))
        db.session.add(UserBadge(user_id=dev.id, badge_id=badges_dict["skill-mentor"].id))

        # 5. Create Connections & Sample Sessions for Demo Account
        # Connection with Ananya (UI/UX <-> Python)
        swap_req_1 = SwapRequest(
            sender_id=demo_user.id,
            receiver_id=ananya.id,
            teach_skill_id=skills_dict["Python"].id,
            learn_skill_id=skills_dict["UI/UX"].id,
            message="Hi Ananya! I love your design portfolio. Let's swap Python programming for UI/UX Figma skills!",
            status="accepted",
            xp_awarded=True
        )
        db.session.add(swap_req_1)
        db.session.flush()

        conn_1 = Connection(
            user1_id=min(demo_user.id, ananya.id),
            user2_id=max(demo_user.id, ananya.id),
            swap_request_id=swap_req_1.id
        )
        db.session.add(conn_1)
        db.session.flush()

        # Completed session between Demo and Ananya
        past_date = (datetime.utcnow() - timedelta(days=2)).strftime("%Y-%m-%d")
        sess_1 = Session(
            connection_id=conn_1.id,
            teacher_id=ananya.id,
            learner_id=demo_user.id,
            skill_id=skills_dict["UI/UX"].id,
            title="UI/UX Wireframing & Auto-Layout in Figma",
            notes="Covered 8pt grid, spacing tokens, and Figma auto-layout components.",
            scheduled_date=past_date,
            scheduled_time="17:00",
            duration_minutes=60,
            status="completed",
            meeting_link="Google Meet: meet.google.com/xyz-demo",
            completed_at=datetime.utcnow() - timedelta(days=2),
            xp_awarded=True
        )
        db.session.add(sess_1)
        db.session.flush()

        # Rating for session 1
        rating_1 = Rating(
            session_id=sess_1.id,
            reviewer_id=demo_user.id,
            reviewee_id=ananya.id,
            score=5,
            feedback="Ananya was incredibly clear and patient explaining Figma components! Highly recommend swapping skills with her.",
            xp_awarded=True
        )
        db.session.add(rating_1)

        # Upcoming scheduled session with Ananya
        future_date = (datetime.utcnow() + timedelta(days=3)).strftime("%Y-%m-%d")
        sess_2 = Session(
            connection_id=conn_1.id,
            teacher_id=demo_user.id,
            learner_id=ananya.id,
            skill_id=skills_dict["Python"].id,
            title="Python Automation Scripts & API Basics",
            notes="Setting up requests library and writing automated spreadsheet sync scripts.",
            scheduled_date=future_date,
            scheduled_time="19:00",
            duration_minutes=60,
            status="scheduled",
            meeting_link="Campus Library Room 204 / Google Meet"
        )
        db.session.add(sess_2)

        # Connection with Priya (Video Editing <-> Python)
        priya = created_users["priya"]
        swap_req_2 = SwapRequest(
            sender_id=priya.id,
            receiver_id=demo_user.id,
            teach_skill_id=skills_dict["Video Editing"].id,
            learn_skill_id=skills_dict["Python"].id,
            message="Hey Tanishk! I saw you teach Python. Can you help me write Python scripts for video rendering automation? I can teach you Premiere Pro!",
            status="accepted",
            xp_awarded=True
        )
        db.session.add(swap_req_2)
        db.session.flush()

        conn_2 = Connection(
            user1_id=min(demo_user.id, priya.id),
            user2_id=max(demo_user.id, priya.id),
            swap_request_id=swap_req_2.id
        )
        db.session.add(conn_2)
        db.session.flush()

        # Pending swap request from Rahul Sharma
        swap_req_pending = SwapRequest(
            sender_id=rahul.id,
            receiver_id=demo_user.id,
            teach_skill_id=skills_dict["C++"].id,
            learn_skill_id=skills_dict["Git & GitHub"].id,
            message="Hey! Would love to trade advanced C++ STL techniques for mastering Git branching workflows and merge conflict resolution!",
            status="pending"
        )
        db.session.add(swap_req_pending)

        db.session.commit()
        print("[SUCCESS] Database successfully seeded with 9 students, skills, connections, sessions, and badges!")
        print("[INFO] Demo Account: demo@skillswap.local | Password: Demo@123")

if __name__ == "__main__":
    seed_database()
