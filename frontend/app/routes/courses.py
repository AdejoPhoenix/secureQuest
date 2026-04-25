import requests
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from functools import wraps

courses_bp = Blueprint("courses", __name__, url_prefix="/courses")


def _api(path):
    return f"{current_app.config['BACKEND_URL']}/api/v1{path}"


def _headers():
    return {"Authorization": f"Bearer {session.get('token', '')}"}


def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if not session.get("token"):
            flash("Please log in to continue.", "warning")
            return redirect(url_for("auth.login"))
        return f(*args, **kwargs)
    return decorated


@courses_bp.route("/")
@login_required
def catalog():
    try:
        resp = requests.get(_api("/courses/"), headers=_headers(), timeout=10)
        courses = resp.json() if resp.status_code == 200 else []
    except requests.RequestException:
        courses = []
    return render_template("courses/catalog.html", courses=courses)


@courses_bp.route("/<int:course_id>")
@login_required
def detail(course_id):
    try:
        c_resp = requests.get(_api(f"/courses/{course_id}"), headers=_headers(), timeout=10)
        course = c_resp.json() if c_resp.status_code == 200 else None
        # Try to get progress (only if enrolled)
        p_resp = requests.get(_api(f"/courses/{course_id}/progress"), headers=_headers(), timeout=10)
        progress = p_resp.json() if p_resp.status_code == 200 else None
    except requests.RequestException:
        course, progress = None, None
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("courses.catalog"))
    return render_template("courses/detail.html", course=course, progress=progress)


@courses_bp.route("/<int:course_id>/enroll", methods=["POST"])
@login_required
def enroll(course_id):
    try:
        resp = requests.post(_api(f"/courses/{course_id}/enroll"), headers=_headers(), timeout=10)
        if resp.status_code in (200, 201):
            flash("You're enrolled! Start learning.", "success")
        else:
            flash(resp.json().get("detail", "Could not enroll"), "danger")
    except requests.RequestException:
        flash("Server error.", "danger")
    return redirect(url_for("courses.learn", course_id=course_id))


@courses_bp.route("/<int:course_id>/learn")
@login_required
def learn(course_id):
    try:
        c_resp = requests.get(_api(f"/courses/{course_id}"), headers=_headers(), timeout=10)
        p_resp = requests.get(_api(f"/courses/{course_id}/progress"), headers=_headers(), timeout=10)
        course   = c_resp.json() if c_resp.status_code == 200 else None
        progress = p_resp.json() if p_resp.status_code == 200 else None
    except requests.RequestException:
        course, progress = None, None
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("courses.catalog"))
    if not progress:
        # Enroll automatically and reload
        try:
            requests.post(_api(f"/courses/{course_id}/enroll"), headers=_headers(), timeout=10)
            p_resp = requests.get(_api(f"/courses/{course_id}/progress"), headers=_headers(), timeout=10)
            progress = p_resp.json() if p_resp.status_code == 200 else {"module_progress": [], "completed_modules": 0, "total_modules": len(course.get("modules", []))}
        except requests.RequestException:
            progress = {"module_progress": [], "completed_modules": 0, "total_modules": 0}
    return render_template("courses/learn.html", course=course, progress=progress)


@courses_bp.route("/<int:course_id>/modules/<int:module_id>/complete", methods=["POST"])
@login_required
def complete_module(course_id, module_id):
    data = {"score": int(request.json.get("score", 100))}
    try:
        resp = requests.post(
            _api(f"/courses/{course_id}/modules/{module_id}/complete"),
            json=data, headers=_headers(), timeout=10,
        )
        return jsonify(resp.json() if resp.status_code == 200 else {"error": resp.text})
    except requests.RequestException:
        return jsonify({"error": "Server error"}), 500
