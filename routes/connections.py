"""
SkillSwap Campus — Connections Routes
Lists real active connections from MongoDB.
"""

from flask import Blueprint, render_template
from flask_login import login_required, current_user
from models import Connection, Skill

connections_bp = Blueprint("connections", __name__)

@connections_bp.route("/connections")
@login_required
def connections_list():
    conns = Connection.find_by_user(current_user.id)

    connection_data = []
    for conn in conns:
        partner = conn.get_partner(current_user.id)
        if not partner:
            continue

        swap_req = conn.swap_request
        partner_teaches = partner.teaching_skills
        my_teaches = current_user.teaching_skills

        connection_data.append({
            "connection": conn,
            "partner": partner,
            "swap_request": swap_req,
            "partner_teaches": partner_teaches,
            "my_teaches": my_teaches,
            "sessions_count": conn.sessions.count()
        })

    all_skills = Skill.find_all()

    return render_template(
        "connections.html",
        connections=connection_data,
        all_skills=all_skills
    )
