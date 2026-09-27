"""
SkillSwap Campus — XP, Gamification & Rating Service
MongoDB-backed business logic:
- Accept swap: +20 XP (both students, strictly once)
- Complete teaching session: +20 XP (teacher, strictly once)
- Complete learning session: +10 XP (learner, strictly once)
- Receive 5-star rating: +5 XP (reviewee, strictly once)
- Starting XP: 0
- Level progression & badge awards
- Single-award guarantee to prevent duplicate XP
"""

import logging
from models import User, Badge, Connection, Session

logger = logging.getLogger(__name__)

XP_ACCEPT_SWAP = 20
XP_TEACH_SESSION = 20
XP_LEARN_SESSION = 10
XP_FIVE_STAR_RATING = 5

def add_xp_to_user(user, amount, reason=""):
    """Safely adds XP to a user in MongoDB and evaluates badge awards."""
    if not user or amount <= 0:
        return
    user.xp = (user.xp or 0) + amount
    user.save()
    check_and_award_badges(user)
    return user.xp

def award_swap_accepted_xp(swap_request):
    """Awards +20 XP to both students upon swap acceptance (strictly once)."""
    if not swap_request or swap_request.xp_awarded:
        return False
    
    sender = swap_request.sender
    receiver = swap_request.receiver
    if sender:
        add_xp_to_user(sender, XP_ACCEPT_SWAP, "Skill swap accepted")
    if receiver:
        add_xp_to_user(receiver, XP_ACCEPT_SWAP, "Skill swap accepted")

    swap_request.xp_awarded = True
    swap_request.save()
    return True

def award_session_completed_xp(session):
    """Awards +20 XP to teacher and +10 XP to learner upon session completion (strictly once)."""
    if not session or session.xp_awarded:
        return False

    teacher = session.teacher
    learner = session.learner
    skill_name = session.skill.name if session.skill else "Session"

    if teacher:
        add_xp_to_user(teacher, XP_TEACH_SESSION, f"Taught {skill_name}")
    if learner:
        add_xp_to_user(learner, XP_LEARN_SESSION, f"Learned {skill_name}")

    session.xp_awarded = True
    session.save()
    return True

def award_rating_xp(rating):
    """Awards +5 XP to reviewee if rating is 5 stars (strictly once)."""
    if not rating or rating.xp_awarded:
        return False

    if rating.score == 5:
        reviewee = rating.reviewee
        if reviewee:
            add_xp_to_user(reviewee, XP_FIVE_STAR_RATING, "5-star rating received")
        rating.xp_awarded = True
        rating.save()
        return True
    return False

def check_and_award_badges(user):
    """Checks badge criteria and assigns badges to the user in MongoDB."""
    if not user:
        return []

    newly_awarded = []
    user_badges_slugs = set(user._data.get("badges", []))

    # 1. First Swap: at least 1 accepted connection
    if "first-swap" not in user_badges_slugs:
        conns_count = Connection.count({
            "$or": [{"user1_id": str(user.id)}, {"user2_id": str(user.id)}]
        })
        if conns_count >= 1:
            user.add_badge("first-swap")
            newly_awarded.append("first-swap")
            user_badges_slugs.add("first-swap")

    # 2. Knowledge Sharer: taught >= 5 completed sessions
    if "knowledge-sharer" not in user_badges_slugs:
        taught_count = Session.count({"teacher_id": str(user.id), "status": "completed"})
        if taught_count >= 5:
            user.add_badge("knowledge-sharer")
            newly_awarded.append("knowledge-sharer")
            user_badges_slugs.add("knowledge-sharer")

    # 3. Fast Learner: completed >= 5 learning sessions
    if "fast-learner" not in user_badges_slugs:
        learned_count = Session.count({"learner_id": str(user.id), "status": "completed"})
        if learned_count >= 5:
            user.add_badge("fast-learner")
            newly_awarded.append("fast-learner")
            user_badges_slugs.add("fast-learner")

    # 4. Community Builder: >= 10 accepted connections
    if "community-builder" not in user_badges_slugs:
        conns_count = Connection.count({
            "$or": [{"user1_id": str(user.id)}, {"user2_id": str(user.id)}]
        })
        if conns_count >= 10:
            user.add_badge("community-builder")
            newly_awarded.append("community-builder")
            user_badges_slugs.add("community-builder")

    # 5. Skill Mentor: >= 1000 XP
    if "skill-mentor" not in user_badges_slugs:
        if (user.xp or 0) >= 1000:
            user.add_badge("skill-mentor")
            newly_awarded.append("skill-mentor")
            user_badges_slugs.add("skill-mentor")

    return newly_awarded

def update_user_rating(user, new_score):
    """Calculates updated rolling average rating for a user without fake bias."""
    if not user:
        return
    old_count = user.rating_count or 0
    old_rating = user.rating or 0.0
    new_count = old_count + 1

    if old_count == 0:
        updated_rating = float(new_score)
    else:
        updated_rating = ((old_rating * old_count) + new_score) / new_count

    user.rating = round(updated_rating, 1)
    user.rating_count = new_count
    user.save()
