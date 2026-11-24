"""
SkillRock — Career Roadmap Blueprint (Discontinued).
All legacy roadmap routes permanently redirect (HTTP 301) to the new Monthly Challenge platform.
"""

from flask import Blueprint, redirect, url_for

roadmap_bp = Blueprint("roadmap", __name__, url_prefix="/roadmaps")


@roadmap_bp.route("", strict_slashes=False)
@roadmap_bp.route("/", strict_slashes=False)
def catalog():
    """Permanent redirect from discontinued /roadmaps to /challenge."""
    return redirect("/challenge", code=301)


@roadmap_bp.route("/<slug>", strict_slashes=False)
def detail(slug):
    """Permanent redirect from legacy roadmap detail to monthly challenge."""
    return redirect("/challenge", code=301)


@roadmap_bp.route("/<slug>/dashboard", strict_slashes=False)
def dashboard(slug):
    """Permanent redirect from legacy roadmap dashboard to monthly challenge."""
    return redirect("/challenge", code=301)


@roadmap_bp.route("/<slug>/player", strict_slashes=False)
def player(slug):
    return redirect("/challenge", code=301)


@roadmap_bp.route("/<slug>/cashback", strict_slashes=False)
def cashback(slug):
    return redirect("/challenge", code=301)


@roadmap_bp.route("/<path:subpath>", strict_slashes=False)
def catch_all(subpath):
    return redirect("/challenge", code=301)
