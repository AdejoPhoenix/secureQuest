import requests
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app, jsonify
from functools import wraps

main_bp = Blueprint("main", __name__)


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


@main_bp.route("/")
def index():
    if session.get("token"):
        return redirect(url_for("main.dashboard"))
    return redirect(url_for("auth.login"))


@main_bp.route("/dashboard")
@login_required
def dashboard():
    try:
        tournaments_resp = requests.get(_api("/tournaments/"), headers=_headers(), timeout=10)
        leaderboard_resp = requests.get(_api("/leaderboard/global"), headers=_headers(), timeout=10)
        tournaments = tournaments_resp.json() if tournaments_resp.status_code == 200 else []
        leaderboard = leaderboard_resp.json() if leaderboard_resp.status_code == 200 else []
    except requests.RequestException:
        tournaments, leaderboard = [], []
        flash("Could not load data from the server.", "warning")
    return render_template("main/dashboard.html", tournaments=tournaments, leaderboard=leaderboard)


@main_bp.route("/tournaments")
@login_required
def tournaments():
    try:
        resp = requests.get(_api("/tournaments/"), headers=_headers(), timeout=10)
        data = resp.json() if resp.status_code == 200 else []
    except requests.RequestException:
        data = []
    return render_template("main/tournaments.html", tournaments=data)


@main_bp.route("/tournaments/<int:tournament_id>")
@login_required
def tournament_detail(tournament_id):
    try:
        t_resp = requests.get(_api(f"/tournaments/{tournament_id}"), headers=_headers(), timeout=10)
        lb_resp = requests.get(_api(f"/tournaments/{tournament_id}/leaderboard"), headers=_headers(), timeout=10)
        tournament = t_resp.json() if t_resp.status_code == 200 else None
        leaderboard = lb_resp.json() if lb_resp.status_code == 200 else []
    except requests.RequestException:
        tournament, leaderboard = None, []
    if not tournament:
        flash("Tournament not found.", "danger")
        return redirect(url_for("main.tournaments"))
    return render_template("main/tournament_detail.html", tournament=tournament, leaderboard=leaderboard)


@main_bp.route("/tournaments/<int:tournament_id>/join", methods=["POST"])
@login_required
def join_tournament(tournament_id):
    try:
        resp = requests.post(_api(f"/tournaments/{tournament_id}/join"), headers=_headers(), timeout=10)
        if resp.status_code == 201:
            flash("You have joined the tournament!", "success")
        else:
            flash(resp.json().get("detail", "Could not join tournament"), "danger")
    except requests.RequestException:
        flash("Server error.", "danger")
    return redirect(url_for("main.play", tournament_id=tournament_id))


@main_bp.route("/tournaments/<int:tournament_id>/play")
@login_required
def play(tournament_id):
    try:
        t_resp = requests.get(_api(f"/tournaments/{tournament_id}"), headers=_headers(), timeout=10)
        c_resp = requests.get(_api(f"/tournaments/{tournament_id}/challenges"), headers=_headers(), timeout=10)
        tournament = t_resp.json() if t_resp.status_code == 200 else None
        challenges = c_resp.json() if c_resp.status_code == 200 else []
    except requests.RequestException:
        tournament, challenges = None, []

    if not tournament:
        flash("Tournament not found or you have not joined.", "danger")
        return redirect(url_for("main.tournaments"))

    return render_template("main/play.html", tournament=tournament, challenges=challenges)


@main_bp.route("/tournaments/<int:tournament_id>/submit", methods=["POST"])
@login_required
def submit_answer(tournament_id):
    data = {
        "challenge_id": int(request.form["challenge_id"]),
        "response": request.form["response"],
        "time_taken_seconds": int(request.form.get("time_taken_seconds", 0)),
    }
    try:
        resp = requests.post(_api(f"/tournaments/{tournament_id}/submit"), json=data, headers=_headers(), timeout=10)
        result = resp.json()
    except requests.RequestException:
        result = {"error": "Server error"}
    return jsonify(result)


@main_bp.route("/pitch")
def pitch():
    return render_template("pitch.html")


@main_bp.route("/leaderboard")
@login_required
def leaderboard():
    try:
        resp = requests.get(_api("/leaderboard/global"), headers=_headers(), timeout=10)
        data = resp.json() if resp.status_code == 200 else []
    except requests.RequestException:
        data = []
    return render_template("main/leaderboard.html", leaderboard=data)
