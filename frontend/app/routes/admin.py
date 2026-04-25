import requests
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from functools import wraps

admin_bp = Blueprint("admin", __name__, url_prefix="/admin")


def _api(path):
    return f"{current_app.config['BACKEND_URL']}/api/v1{path}"


def _headers():
    return {"Authorization": f"Bearer {session.get('token', '')}"}


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        user = session.get("user", {})
        if not session.get("token"):
            return redirect(url_for("auth.login"))
        if user.get("role") != "admin":
            flash("Admin access required.", "danger")
            return redirect(url_for("main.dashboard"))
        return f(*args, **kwargs)
    return decorated


@admin_bp.route("/")
@admin_required
def dashboard():
    try:
        tournaments_resp = requests.get(_api("/admin/tournaments"), headers=_headers(), timeout=10)
        users_resp = requests.get(_api("/admin/users"), headers=_headers(), timeout=10)
        report_resp = requests.get(_api("/admin/reports/users"), headers=_headers(), timeout=10)
        tournaments = tournaments_resp.json() if tournaments_resp.status_code == 200 else []
        users = users_resp.json() if users_resp.status_code == 200 else []
        report = report_resp.json() if report_resp.status_code == 200 else []
    except requests.RequestException:
        tournaments, users, report = [], [], []
    return render_template("admin/dashboard.html", tournaments=tournaments, users=users, report=report)


@admin_bp.route("/tournaments")
@admin_required
def tournaments():
    try:
        resp = requests.get(_api("/admin/tournaments"), headers=_headers(), timeout=10)
        data = resp.json() if resp.status_code == 200 else []
    except requests.RequestException:
        data = []
    return render_template("admin/tournaments.html", tournaments=data)


@admin_bp.route("/tournaments/new", methods=["GET", "POST"])
@admin_required
def create_tournament():
    if request.method == "POST":
        payload = {
            "name": request.form["name"],
            "description": request.form.get("description", ""),
            "difficulty": request.form["difficulty"],
            "timer_seconds": int(request.form.get("timer_seconds", 300)),
            "total_timer_seconds": int(request.form.get("total_timer_seconds", 3600)),
            "max_participants": int(request.form.get("max_participants", 100)),
            "is_active": request.form.get("is_active") == "on",
        }
        start = request.form.get("start_time")
        end = request.form.get("end_time")
        if start:
            payload["start_time"] = start
        if end:
            payload["end_time"] = end
        try:
            resp = requests.post(_api("/admin/tournaments"), json=payload, headers=_headers(), timeout=10)
            if resp.status_code == 201:
                flash("Tournament created!", "success")
                return redirect(url_for("admin.edit_tournament", tournament_id=resp.json()["id"]))
            else:
                flash(resp.json().get("detail", "Failed to create tournament"), "danger")
        except requests.RequestException:
            flash("Server error.", "danger")
    return render_template("admin/create_tournament.html")


@admin_bp.route("/tournaments/<int:tournament_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_tournament(tournament_id):
    try:
        t_resp = requests.get(_api(f"/admin/tournaments/{tournament_id}"), headers=_headers(), timeout=10)
        tournament = t_resp.json() if t_resp.status_code == 200 else None
    except requests.RequestException:
        tournament = None

    if not tournament:
        flash("Tournament not found.", "danger")
        return redirect(url_for("admin.tournaments"))

    if request.method == "POST":
        payload = {
            "name": request.form["name"],
            "description": request.form.get("description", ""),
            "difficulty": request.form["difficulty"],
            "timer_seconds": int(request.form.get("timer_seconds", 300)),
            "total_timer_seconds": int(request.form.get("total_timer_seconds", 3600)),
            "max_participants": int(request.form.get("max_participants", 100)),
            "is_active": request.form.get("is_active") == "on",
        }
        try:
            resp = requests.patch(_api(f"/admin/tournaments/{tournament_id}"), json=payload, headers=_headers(), timeout=10)
            if resp.status_code == 200:
                flash("Tournament updated!", "success")
                tournament = resp.json()
            else:
                flash(resp.json().get("detail", "Update failed"), "danger")
        except requests.RequestException:
            flash("Server error.", "danger")

    return render_template("admin/edit_tournament.html", tournament=tournament)


@admin_bp.route("/tournaments/<int:tournament_id>/delete", methods=["POST"])
@admin_required
def delete_tournament(tournament_id):
    try:
        requests.delete(_api(f"/admin/tournaments/{tournament_id}"), headers=_headers(), timeout=10)
        flash("Tournament deleted.", "info")
    except requests.RequestException:
        flash("Server error.", "danger")
    return redirect(url_for("admin.tournaments"))


@admin_bp.route("/tournaments/<int:tournament_id>/challenges/add", methods=["GET", "POST"])
@admin_required
def add_challenge(tournament_id):
    try:
        t_resp = requests.get(_api(f"/admin/tournaments/{tournament_id}"), headers=_headers(), timeout=10)
        tournament = t_resp.json() if t_resp.status_code == 200 else None
    except requests.RequestException:
        tournament = None

    if request.method == "POST":
        options_raw = {}
        for key in ["a", "b", "c", "d"]:
            val = request.form.get(f"option_{key}", "").strip()
            if val:
                options_raw[key] = val
        hints_raw = [h.strip() for h in request.form.get("hints", "").splitlines() if h.strip()]
        payload = {
            "title": request.form["title"],
            "description": request.form["description"],
            "type": request.form["type"],
            "points": int(request.form.get("points", 10)),
            "difficulty_level": request.form["difficulty_level"],
            "order": int(request.form.get("order", 0)),
            "options": options_raw or None,
            "correct_answer": request.form["correct_answer"],
            "explanation": request.form.get("explanation", ""),
            "hints": hints_raw or None,
        }
        try:
            resp = requests.post(
                _api(f"/admin/tournaments/{tournament_id}/challenges"),
                json=payload, headers=_headers(), timeout=10,
            )
            if resp.status_code == 201:
                flash("Challenge added!", "success")
                return redirect(url_for("admin.edit_tournament", tournament_id=tournament_id))
            else:
                flash(resp.json().get("detail", "Failed"), "danger")
        except requests.RequestException:
            flash("Server error.", "danger")

    return render_template("admin/add_challenge.html", tournament=tournament)


@admin_bp.route("/challenges/<int:challenge_id>/delete", methods=["POST"])
@admin_required
def delete_challenge(challenge_id):
    tournament_id = request.form.get("tournament_id")
    try:
        requests.delete(_api(f"/admin/challenges/{challenge_id}"), headers=_headers(), timeout=10)
        flash("Challenge deleted.", "info")
    except requests.RequestException:
        flash("Server error.", "danger")
    return redirect(url_for("admin.edit_tournament", tournament_id=tournament_id))


@admin_bp.route("/users")
@admin_required
def users():
    try:
        users_resp = requests.get(_api("/admin/users"), headers=_headers(), timeout=10)
        report_resp = requests.get(_api("/admin/reports/users"), headers=_headers(), timeout=10)
        all_users = users_resp.json() if users_resp.status_code == 200 else []
        report = report_resp.json() if report_resp.status_code == 200 else []
    except requests.RequestException:
        all_users, report = [], []
    report_by_id = {r["user_id"]: r for r in report}
    return render_template("admin/users.html", users=all_users, report_by_id=report_by_id)


@admin_bp.route("/reports")
@admin_required
def reports():
    try:
        report_resp = requests.get(_api("/admin/reports/users"), headers=_headers(), timeout=10)
        tournaments_resp = requests.get(_api("/admin/tournaments"), headers=_headers(), timeout=10)
        report = report_resp.json() if report_resp.status_code == 200 else []
        tournaments = tournaments_resp.json() if tournaments_resp.status_code == 200 else []
    except requests.RequestException:
        report, tournaments = [], []
    return render_template("admin/reports.html", report=report, tournaments=tournaments)


@admin_bp.route("/reports/tournaments/<int:tournament_id>")
@admin_required
def tournament_report(tournament_id):
    try:
        resp = requests.get(_api(f"/admin/reports/tournaments/{tournament_id}"), headers=_headers(), timeout=10)
        data = resp.json() if resp.status_code == 200 else {}
    except requests.RequestException:
        data = {}
    return render_template("admin/tournament_report.html", report=data)


# ══════════════════════════════════════════════════════════════════════════════
# COURSES
# ══════════════════════════════════════════════════════════════════════════════

@admin_bp.route("/courses")
@admin_required
def courses():
    try:
        resp = requests.get(_api("/admin/courses/"), headers=_headers(), timeout=10)
        data = resp.json() if resp.status_code == 200 else []
    except requests.RequestException:
        data = []
    return render_template("admin/courses/list.html", courses=data)


@admin_bp.route("/courses/new", methods=["GET", "POST"])
@admin_required
def create_course():
    if request.method == "POST":
        payload = {
            "name": request.form["name"],
            "description": request.form.get("description", ""),
            "category": request.form["category"],
            "difficulty": request.form["difficulty"],
            "thumbnail_color": request.form.get("thumbnail_color", "#ffc107"),
            "xp_reward": int(request.form.get("xp_reward", 100)),
            "is_published": False,
        }
        try:
            resp = requests.post(_api("/admin/courses/"), json=payload, headers=_headers(), timeout=10)
            if resp.status_code == 201:
                flash("Course created! Now add modules.", "success")
                return redirect(url_for("admin.edit_course", course_id=resp.json()["id"]))
            flash(resp.json().get("detail", "Failed to create"), "danger")
        except requests.RequestException:
            flash("Server error.", "danger")
    return render_template("admin/courses/create.html")


@admin_bp.route("/courses/<int:course_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_course(course_id):
    try:
        resp = requests.get(_api(f"/admin/courses/{course_id}"), headers=_headers(), timeout=10)
        course = resp.json() if resp.status_code == 200 else None
    except requests.RequestException:
        course = None
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("admin.courses"))

    if request.method == "POST":
        payload = {
            "name": request.form["name"],
            "description": request.form.get("description", ""),
            "category": request.form["category"],
            "difficulty": request.form["difficulty"],
            "thumbnail_color": request.form.get("thumbnail_color", "#ffc107"),
            "xp_reward": int(request.form.get("xp_reward", 100)),
        }
        try:
            resp = requests.patch(_api(f"/admin/courses/{course_id}"), json=payload, headers=_headers(), timeout=10)
            if resp.status_code == 200:
                flash("Course updated!", "success")
                course = resp.json()
            else:
                flash(resp.json().get("detail", "Update failed"), "danger")
        except requests.RequestException:
            flash("Server error.", "danger")

    return render_template("admin/courses/edit.html", course=course)


@admin_bp.route("/courses/<int:course_id>/publish", methods=["POST"])
@admin_required
def publish_course(course_id):
    action = request.form.get("action", "publish")
    endpoint = "publish" if action == "publish" else "unpublish"
    try:
        resp = requests.post(_api(f"/admin/courses/{course_id}/{endpoint}"), headers=_headers(), timeout=10)
        if resp.status_code == 200:
            flash(f"Course {'published' if action == 'publish' else 'unpublished'}.", "success")
        else:
            flash(resp.json().get("detail", "Failed"), "danger")
    except requests.RequestException:
        flash("Server error.", "danger")
    return redirect(url_for("admin.edit_course", course_id=course_id))


@admin_bp.route("/courses/<int:course_id>/delete", methods=["POST"])
@admin_required
def delete_course(course_id):
    try:
        requests.delete(_api(f"/admin/courses/{course_id}"), headers=_headers(), timeout=10)
        flash("Course deleted.", "info")
    except requests.RequestException:
        flash("Server error.", "danger")
    return redirect(url_for("admin.courses"))


@admin_bp.route("/courses/<int:course_id>/modules/add", methods=["GET", "POST"])
@admin_required
def add_module(course_id):
    try:
        resp = requests.get(_api(f"/admin/courses/{course_id}"), headers=_headers(), timeout=10)
        course = resp.json() if resp.status_code == 200 else None
    except requests.RequestException:
        course = None

    if request.method == "POST":
        module_type = request.form["type"]
        content = _build_module_content(module_type, request.form)
        payload = {
            "title": request.form["title"],
            "type": module_type,
            "content": content,
            "order": int(request.form.get("order", len(course.get("modules", [])) if course else 0)),
            "xp_reward": int(request.form.get("xp_reward", 20)),
            "is_required": request.form.get("is_required") != "false",
            "pass_score": int(request.form.get("pass_score", 70)),
        }
        try:
            resp = requests.post(_api(f"/admin/courses/{course_id}/modules"), json=payload, headers=_headers(), timeout=10)
            if resp.status_code == 201:
                flash("Module added!", "success")
                return redirect(url_for("admin.edit_course", course_id=course_id))
            flash(resp.json().get("detail", "Failed"), "danger")
        except requests.RequestException:
            flash("Server error.", "danger")

    return render_template("admin/courses/add_module.html", course=course)


@admin_bp.route("/courses/<int:course_id>/modules/<int:module_id>/edit", methods=["GET", "POST"])
@admin_required
def edit_module(course_id, module_id):
    try:
        c_resp = requests.get(_api(f"/admin/courses/{course_id}"), headers=_headers(), timeout=10)
        course = c_resp.json() if c_resp.status_code == 200 else None
    except requests.RequestException:
        course = None

    module = next((m for m in (course or {}).get("modules", []) if m["id"] == module_id), None)
    if not module:
        flash("Module not found.", "danger")
        return redirect(url_for("admin.edit_course", course_id=course_id))

    if request.method == "POST":
        module_type = request.form["type"]
        content = _build_module_content(module_type, request.form)
        payload = {
            "title": request.form["title"],
            "type": module_type,
            "content": content,
            "order": int(request.form.get("order", module["order"])),
            "xp_reward": int(request.form.get("xp_reward", module["xp_reward"])),
            "is_required": request.form.get("is_required") != "false",
            "pass_score": int(request.form.get("pass_score", module["pass_score"])),
        }
        try:
            resp = requests.patch(
                _api(f"/admin/courses/{course_id}/modules/{module_id}"),
                json=payload, headers=_headers(), timeout=10,
            )
            if resp.ok:
                flash("Module updated!", "success")
                return redirect(url_for("admin.edit_course", course_id=course_id))
            flash(resp.json().get("detail", "Failed to update"), "danger")
        except requests.RequestException:
            flash("Server error.", "danger")

    return render_template("admin/courses/edit_module.html", course=course, module=module)


@admin_bp.route("/courses/<int:course_id>/preview")
@admin_required
def preview_course(course_id):
    """Admin preview of an unpublished course — bypasses the published check."""
    try:
        resp = requests.get(_api(f"/admin/courses/{course_id}"), headers=_headers(), timeout=10)
        course = resp.json() if resp.status_code == 200 else None
    except requests.RequestException:
        course = None
    if not course:
        flash("Course not found.", "danger")
        return redirect(url_for("admin.courses"))
    # Build a stub progress so the learn template renders
    progress = {
        "course_id": course_id,
        "course_name": course["name"],
        "total_modules": len(course.get("modules", [])),
        "completed_modules": 0,
        "progress_pct": 0,
        "is_completed": False,
        "xp_earned": 0,
        "module_progress": [],
    }
    return render_template("courses/learn.html", course=course, progress=progress, preview_mode=True)


@admin_bp.route("/courses/<int:course_id>/modules/<int:module_id>/delete", methods=["POST"])
@admin_required
def delete_module(course_id, module_id):
    try:
        requests.delete(_api(f"/admin/courses/{course_id}/modules/{module_id}"), headers=_headers(), timeout=10)
        flash("Module deleted.", "info")
    except requests.RequestException:
        flash("Server error.", "danger")
    return redirect(url_for("admin.edit_course", course_id=course_id))


@admin_bp.route("/courses/<int:course_id>/analytics")
@admin_required
def course_analytics(course_id):
    try:
        resp = requests.get(_api(f"/admin/courses/{course_id}/analytics"), headers=_headers(), timeout=10)
        data = resp.json() if resp.status_code == 200 else {}
    except requests.RequestException:
        data = {}
    return render_template("admin/courses/analytics.html", analytics=data)


def _build_module_content(module_type, form):
    """Parse form data into the correct JSON content structure per module type."""
    if module_type == "lesson":
        callouts = []
        for i in range(1, 6):
            ct = form.get(f"callout_type_{i}", "").strip()
            cb = form.get(f"callout_body_{i}", "").strip()
            if ct and cb:
                callouts.append({"type": ct, "text": cb})
        return {"body": form.get("body", ""), "callouts": callouts}

    elif module_type == "quiz":
        questions = []
        i = 1
        while form.get(f"q{i}_text"):
            opts = {}
            for k in ["a", "b", "c", "d"]:
                v = form.get(f"q{i}_opt_{k}", "").strip()
                if v:
                    opts[k] = v
            questions.append({
                "text": form.get(f"q{i}_text", ""),
                "options": opts,
                "correct": form.get(f"q{i}_correct", "a"),
                "explanation": form.get(f"q{i}_explanation", ""),
            })
            i += 1
        return {"questions": questions}

    elif module_type == "scenario":
        choices = []
        i = 1
        while form.get(f"choice{i}_text"):
            choices.append({
                "text": form.get(f"choice{i}_text", ""),
                "outcome": form.get(f"choice{i}_outcome", ""),
                "is_correct": form.get(f"choice{i}_correct") == "true",
            })
            i += 1
        return {
            "description": form.get("scenario_description", ""),
            "choices": choices,
        }

    elif module_type == "dragdrop":
        categories = [c.strip() for c in form.get("categories", "").split(",") if c.strip()]
        items = []
        i = 1
        while form.get(f"item{i}_text"):
            items.append({
                "text": form.get(f"item{i}_text", ""),
                "category": form.get(f"item{i}_category", categories[0] if categories else ""),
            })
            i += 1
        return {
            "instruction": form.get("instruction", ""),
            "categories": categories,
            "items": items,
        }

    return {}
