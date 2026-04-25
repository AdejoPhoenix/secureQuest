import requests
from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


def _api(path):
    return f"{current_app.config['BACKEND_URL']}/api/v1{path}"


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    if session.get("token"):
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        data = {"email": request.form["email"], "password": request.form["password"]}
        try:
            resp = requests.post(_api("/auth/login"), json=data, timeout=10)
            if resp.status_code == 200:
                payload = resp.json()
                session["token"] = payload["access_token"]
                session["user"] = payload["user"]
                flash("Welcome back!", "success")
                if payload["user"]["role"] == "admin":
                    return redirect(url_for("admin.dashboard"))
                return redirect(url_for("main.dashboard"))
            else:
                flash(resp.json().get("detail", "Login failed"), "danger")
        except requests.RequestException:
            flash("Could not reach the server. Please try again.", "danger")

    return render_template("auth/login.html")


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    if session.get("token"):
        return redirect(url_for("main.dashboard"))

    if request.method == "POST":
        data = {
            "email": request.form["email"],
            "username": request.form["username"],
            "password": request.form["password"],
        }
        try:
            resp = requests.post(_api("/auth/register"), json=data, timeout=10)
            if resp.status_code == 201:
                payload = resp.json()
                session["token"] = payload["access_token"]
                session["user"] = payload["user"]
                flash("Account created! Welcome aboard.", "success")
                return redirect(url_for("main.dashboard"))
            else:
                flash(resp.json().get("detail", "Registration failed"), "danger")
        except requests.RequestException:
            flash("Could not reach the server. Please try again.", "danger")

    return render_template("auth/register.html")


@auth_bp.route("/google")
def google_login():
    backend_url = current_app.config["BACKEND_URL"]
    return redirect(f"{backend_url}/api/v1/auth/google")


@auth_bp.route("/logout")
def logout():
    session.clear()
    flash("You have been logged out.", "info")
    return redirect(url_for("auth.login"))
