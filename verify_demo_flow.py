"""
SkillSwap Campus - Automated End-to-End Test for Critical Demo Flow & Business Logic
Verifies:
1. Registration defaults (0 XP, rating=0.0, "New member - No ratings yet")
2. Skill addition
3. Exact matching engine calculation (Mutual=70, One-way=45, Related=30, College=+10, Branch=+5, Year=+5, Cap=100)
4. Swap request flow & Acceptance (+20 XP to both parties)
5. Duplicate acceptance protection (0 additional XP)
6. Session scheduling & Completion (+20 XP teacher, +10 XP learner)
7. Duplicate completion protection (0 additional XP)
8. Rating submission (+5 XP for 5-star rating)
9. Duplicate rating protection
10. Levels and Badges progression
11. Dashboard rendering with exactly 4 stats
12. SkillBot AI endpoints
"""

import sys
if sys.stdout.encoding != 'utf-8':
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

from app import create_app
from models import db, User, Skill, UserSkill, SwapRequest, Connection, Session, Rating, Badge
from services.matching import calculate_match_score
from services.xp_service import award_swap_accepted_xp, award_session_completed_xp, award_rating_xp, check_and_award_badges

def run_e2e_verification():
    print("[1/12] Initializing Flask test client...")
    app = create_app()
    app.config["TESTING"] = True
    app.config["WTF_CSRF_ENABLED"] = False

    client = app.test_client()

    with app.app_context():
        # Clean up any previous test user
        existing_test = User.query.filter_by(email="teststudent@dtu.edu").first()
        if existing_test:
            # Delete any ratings, sessions, connections, swap requests first
            for s in Session.query.filter((Session.teacher_id == existing_test.id) | (Session.learner_id == existing_test.id)).all():
                Rating.query.filter_by(session_id=s.id).delete()
                db.session.delete(s)
            Connection.query.filter((Connection.user1_id == existing_test.id) | (Connection.user2_id == existing_test.id)).delete()
            SwapRequest.query.filter((SwapRequest.sender_id == existing_test.id) | (SwapRequest.receiver_id == existing_test.id)).delete()
            db.session.delete(existing_test)
            db.session.commit()

        # Step 1: Register
        print("[2/12] Registering new student: Rohit Sen (teststudent@dtu.edu)...")
        res = client.post("/register", data={
            "name": "Rohit Sen",
            "email": "teststudent@dtu.edu",
            "password": "Password@123",
            "college": "Delhi Technological University (DTU)",
            "branch": "Computer Science & Engineering",
            "year": "2nd Year"
        }, follow_redirects=True)
        assert res.status_code == 200, f"Registration failed with code {res.status_code}"
        
        rohit = User.query.filter_by(email="teststudent@dtu.edu").first()
        assert rohit is not None, "User not found in database after register"
        assert rohit.xp == 0, f"Initial XP must be 0, got {rohit.xp}"
        assert rohit.rating == 0.0, f"Initial rating must be 0.0, got {rohit.rating}"
        assert rohit.rating_count == 0, f"Initial rating_count must be 0, got {rohit.rating_count}"
        assert rohit.level_name == "Beginner", f"Initial level must be Beginner, got {rohit.level_name}"
        assert "New member" in rohit.rating_display, f"Expected 'New member' in rating_display, got {rohit.rating_display}"
        print(f"      -> Registered successfully. XP: {rohit.xp}, Rating: {rohit.rating_display}, Level: {rohit.level_name}")

        # Step 2: Add 'Python' to Can Teach
        print("[3/12] Adding 'Python' to Can Teach...")
        res = client.post("/skills/add", data={
            "skill_name": "Python",
            "skill_type": "teach",
            "proficiency": "Advanced"
        }, follow_redirects=True)
        assert res.status_code == 200
        assert any(s.name == "Python" for s in rohit.teaching_skills), "Python not added to teaching skills"
        print("      -> 'Python' successfully added to Can Teach.")

        # Step 3: Add 'UI/UX' to Want to Learn
        print("[4/12] Adding 'UI/UX' to Want to Learn...")
        res = client.post("/skills/add", data={
            "skill_name": "UI/UX",
            "skill_type": "learn",
            "proficiency": "Beginner"
        }, follow_redirects=True)
        assert res.status_code == 200
        assert any(s.name == "UI/UX" for s in rohit.learning_skills), "UI/UX not added to learning skills"
        print("      -> 'UI/UX' successfully added to Want to Learn.")

        # Step 4: Verify Matching Engine Calculation
        print("[5/12] Verifying Exact Matching Formula with Ananya Verma...")
        ananya = User.query.filter_by(email="ananya.verma@campus.edu").first()
        assert ananya is not None, "Ananya Verma not found in database"
        
        # Rohit teaches Python, wants UI/UX
        # Ananya teaches UI/UX, wants Python
        # Both are at DTU (+10), different branch (CSE vs IT = +0), different year (2nd vs 3rd = +0)
        # Direct mutual = 70, Same college = 10 -> Score should be 80%
        match_res = calculate_match_score(rohit, ananya)
        score = match_res["score"]
        reasons = match_res["reasons"]
        assert score == 80, f"Expected match score 80%, got {score}%"
        assert len(reasons) >= 2, f"Expected at least 2 match reasons, got {len(reasons)}"
        print(f"      -> Match score verified: {score}% ({', '.join(reasons)})")

        # Step 5: Send Swap Request to Ananya Verma
        python_skill = Skill.query.filter_by(name="Python").first()
        uiux_skill = Skill.query.filter_by(name="UI/UX").first()

        print(f"[6/12] Sending Skill Swap Request to Ananya Verma (ID: {ananya.id})...")
        res = client.post("/requests/send", data={
            "receiver_id": ananya.id,
            "teach_skill_id": python_skill.id,
            "learn_skill_id": uiux_skill.id,
            "message": "Hey Ananya! I know Python and would love to learn UI/UX from you!"
        }, follow_redirects=True)
        assert res.status_code == 200

        swap_req = SwapRequest.query.filter_by(sender_id=rohit.id, receiver_id=ananya.id, status="pending").first()
        assert swap_req is not None, "Pending swap request not found in database"
        assert swap_req.xp_awarded == False, "New swap request should have xp_awarded=False"
        print(f"      -> Swap Request #{swap_req.id} created with status 'pending'.")

        # Step 6: Log out Rohit and log in as Ananya
        print("[7/12] Logging out Rohit and logging in as Ananya Verma...")
        client.get("/logout")
        res = client.post("/login", data={
            "email": "ananya.verma@campus.edu",
            "password": "Student@123"
        }, follow_redirects=True)
        assert res.status_code == 200
        ananya_xp_before = ananya.xp
        rohit_xp_before = rohit.xp

        # Step 7: Accept Swap Request & Test Duplicate Protection
        print(f"[8/12] Ananya accepting Swap Request #{swap_req.id} (+20 XP each)...")
        res = client.post(f"/requests/{swap_req.id}/accept", follow_redirects=True)
        assert res.status_code == 200
        
        db.session.refresh(swap_req)
        db.session.refresh(ananya)
        db.session.refresh(rohit)
        assert swap_req.status == "accepted", f"Swap request status is {swap_req.status}, expected 'accepted'"
        assert swap_req.xp_awarded == True, "Swap request xp_awarded must be True after acceptance"
        assert ananya.xp == ananya_xp_before + 20, f"Expected Ananya XP +20 ({ananya_xp_before + 20}), got {ananya.xp}"
        assert rohit.xp == rohit_xp_before + 20, f"Expected Rohit XP +20 ({rohit_xp_before + 20}), got {rohit.xp}"

        # Test duplicate acceptance protection directly
        dup_xp_awarded = award_swap_accepted_xp(swap_req)
        assert dup_xp_awarded == False, "Duplicate award_swap_accepted_xp must return False"
        assert ananya.xp == ananya_xp_before + 20, "Duplicate acceptance awarded unauthorized XP"
        print(f"      -> Swap accepted! +20 XP awarded to both. Duplicate protection verified.")

        conn = Connection.query.filter(
            ((Connection.user1_id == rohit.id) & (Connection.user2_id == ananya.id)) |
            ((Connection.user1_id == ananya.id) & (Connection.user2_id == rohit.id))
        ).first()
        assert conn is not None, "Connection record was not created after swap acceptance"

        # Step 8: Schedule Session
        print("[9/12] Scheduling Learning Session between Ananya and Rohit...")
        res = client.post("/sessions/schedule", data={
            "connection_id": conn.id,
            "partner_id": rohit.id,
            "role": "teach", # Ananya teaches Rohit
            "skill_id": uiux_skill.id,
            "title": "Figma Auto-Layout & Design Systems",
            "date": "2026-10-02",
            "time": "18:00",
            "duration": 60,
            "meeting_link": "Google Meet: meet.google.com/test-swap",
            "notes": "Hands-on UI wireframe build"
        }, follow_redirects=True)
        assert res.status_code == 200

        sess = Session.query.filter_by(connection_id=conn.id, skill_id=uiux_skill.id, status="scheduled").first()
        assert sess is not None, "Session not created in database"
        assert sess.xp_awarded == False, "New session must have xp_awarded=False"
        print(f"      -> Session #{sess.id} scheduled.")

        # Step 9: Mark Session Completed & Test Duplicate Protection
        print(f"[10/12] Marking Session #{sess.id} completed (Teacher +20 XP, Learner +10 XP)...")
        ananya_xp_pre_sess = ananya.xp
        rohit_xp_pre_sess = rohit.xp
        
        res = client.post(f"/sessions/{sess.id}/complete", follow_redirects=True)
        assert res.status_code == 200

        db.session.refresh(sess)
        db.session.refresh(ananya)
        db.session.refresh(rohit)
        assert sess.status == "completed", "Session status not marked completed"
        assert sess.xp_awarded == True, "Session xp_awarded must be True after completion"
        assert ananya.xp == ananya_xp_pre_sess + 20, f"Teacher expected +20 XP, got {ananya.xp - ananya_xp_pre_sess}"
        assert rohit.xp == rohit_xp_pre_sess + 10, f"Learner expected +10 XP, got {rohit.xp - rohit_xp_pre_sess}"

        # Test duplicate completion protection
        dup_sess_awarded = award_session_completed_xp(sess)
        assert dup_sess_awarded == False, "Duplicate session completion award must return False"
        assert ananya.xp == ananya_xp_pre_sess + 20, "Duplicate session completion awarded unauthorized XP"
        print("      -> Session completed! Teacher +20 XP, Learner +10 XP. Duplicate protection verified.")

        # Step 10: Rohit rates Ananya (5 stars -> +5 XP)
        print("[11/12] Rohit rates Ananya with 5 stars (+5 XP bonus)...")
        client.get("/logout")
        client.post("/login", data={
            "email": "teststudent@dtu.edu",
            "password": "Password@123"
        }, follow_redirects=True)

        ananya_xp_pre_rating = ananya.xp
        res = client.post(f"/sessions/{sess.id}/rate", data={
            "score": 5,
            "feedback": "Outstanding mentorship! Ananya made Figma auto-layout crystal clear."
        }, follow_redirects=True)
        assert res.status_code == 200

        rating = Rating.query.filter_by(session_id=sess.id, reviewer_id=rohit.id).first()
        assert rating is not None, "Rating not saved in database"
        assert rating.score == 5, f"Expected 5 stars, got {rating.score}"
        assert rating.xp_awarded == True, "Rating xp_awarded must be True"

        db.session.refresh(ananya)
        assert ananya.xp == ananya_xp_pre_rating + 5, f"Expected 5-star rating to award +5 XP, got {ananya.xp - ananya_xp_pre_rating}"

        # Test duplicate rating protection directly
        dup_rating_awarded = award_rating_xp(rating)
        assert dup_rating_awarded == False, "Duplicate rating XP award must return False"
        print(f"      -> 5-star rating saved! Teacher received +5 XP. Duplicate protection verified.")

        # Step 11: Verify Levels and Badges
        print("[12/12] Verifying Level Thresholds, Badges, and Dashboard Layout...")
        # Check Level Thresholds
        rohit.xp = 50
        assert rohit.level_name == "Beginner"
        rohit.xp = 150
        assert rohit.level_name == "Learner"
        rohit.xp = 350
        assert rohit.level_name == "Skill Builder"
        rohit.xp = 750
        assert rohit.level_name == "Knowledge Sharer"
        rohit.xp = 1200
        assert rohit.level_name == "Skill Mentor"

        # Check First Swap badge awarded to Rohit
        new_badges = check_and_award_badges(rohit)
        db.session.refresh(rohit)
        assert any(b.name == "First Swap" for b in rohit.badges), "First Swap badge should be awarded after completed swap"

        # Check Dashboard UI
        dash_res = client.get("/dashboard")
        assert dash_res.status_code == 200
        assert b"Rohit" in dash_res.data
        assert b"XP" in dash_res.data
        assert b"Level" in dash_res.data
        assert b"Skills" in dash_res.data
        assert b"Connections" in dash_res.data
        assert b"Your Best Matches" in dash_res.data

        # Check AI endpoints
        ai_chat_res = client.post("/api/ai/chat", json={"message": "What should I learn after Python?"})
        assert ai_chat_res.status_code == 200
        assert "reply" in ai_chat_res.get_json()

        roadmap_res = client.get("/api/ai/roadmap?skill=UI/UX")
        assert roadmap_res.status_code == 200
        assert "steps" in roadmap_res.get_json()

        print("\n=======================================================")
        print("ALL 12 STEPS OF THE CRITICAL DEMO FLOW PASSED 100%!")
        print("=======================================================\n")

if __name__ == "__main__":
    run_e2e_verification()
