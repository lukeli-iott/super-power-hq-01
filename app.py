import csv
import io
import os
import re
import threading
from pathlib import Path

from flask import Flask, Response, redirect, render_template, request, session, url_for
from sqlalchemy import (
    Column,
    Integer,
    MetaData,
    Table,
    Text,
    create_engine,
    select,
)
from sqlalchemy.engine import URL, Engine, make_url

BASE_DIR = Path(__file__).parent
DB_PATH = BASE_DIR / "heroes.db"
EMAIL_RE = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DB_INIT_LOCK = threading.Lock()

metadata = MetaData()
submissions = Table(
    "submissions",
    metadata,
    Column("id", Integer, primary_key=True, autoincrement=True),
    Column("hero_name", Text),
    Column("powers", Text),
    Column("age", Text),
    Column("location", Text),
    Column("email", Text),
)


def create_database_engine(database_url=None):
    database_url = database_url or os.environ.get("DATABASE_URL")
    if database_url:
        parsed_url = make_url(database_url)
        if parsed_url.drivername in {"postgres", "postgresql"} or parsed_url.drivername.startswith(
            "postgresql+"
        ):
            parsed_url = parsed_url.set(drivername="postgresql+psycopg")
        elif os.environ.get("VERCEL"):
            raise RuntimeError("DATABASE_URL must point to a persistent PostgreSQL database on Vercel.")
        return create_engine(parsed_url, pool_pre_ping=True)
    if os.environ.get("VERCEL"):
        raise RuntimeError("Set DATABASE_URL to a persistent PostgreSQL database on Vercel.")
    return create_engine(
        URL.create("sqlite", database=str(DB_PATH)),
        connect_args={"check_same_thread": False},
    )


def validate_signup(data):
    errors = {}
    cleaned_data = {
        field: data.get(field, "").strip()
        for field in ("hero_name", "powers", "age", "location", "email")
    }

    if not cleaned_data["hero_name"]:
        errors["hero_name"] = "Hero name is required."
    elif len(cleaned_data["hero_name"]) > 200:
        errors["hero_name"] = "Hero name is too long."

    if not cleaned_data["powers"]:
        errors["powers"] = "Powers are required."
    elif len(cleaned_data["powers"]) > 500:
        errors["powers"] = "Powers description is too long."

    age = cleaned_data["age"]
    if not age:
        errors["age"] = "Age is required."
    elif not age.isdigit() or not (0 < int(age) <= 150):
        errors["age"] = "Age must be a number between 1 and 150."

    if not cleaned_data["location"]:
        errors["location"] = "Location is required."
    elif len(cleaned_data["location"]) > 200:
        errors["location"] = "Location is too long."

    email = cleaned_data["email"]
    if not email:
        errors["email"] = "Email is required."
    elif not EMAIL_RE.fullmatch(email):
        errors["email"] = "Please enter a valid email address."
    elif len(email) > 200:
        errors["email"] = "Email is too long."

    return errors, cleaned_data


def create_app(database_url=None):
    flask_app = Flask(__name__)
    flask_app.config["SECRET_KEY"] = os.environ.get("SECRET_KEY")
    flask_app.config["DATABASE_URL"] = database_url
    flask_app.extensions["database_engine"] = None
    flask_app.extensions["database_initialized"] = False

    @flask_app.before_request
    def initialize_database():
        if not flask_app.extensions["database_initialized"]:
            with DB_INIT_LOCK:
                if not flask_app.extensions["database_initialized"]:
                    engine = flask_app.extensions["database_engine"]
                    if engine is None:
                        if os.environ.get("VERCEL") and not (
                            flask_app.config["DATABASE_URL"]
                            or os.environ.get("DATABASE_URL")
                        ):
                            raise RuntimeError(
                                "Set DATABASE_URL to a persistent PostgreSQL database on Vercel."
                            )
                        engine = create_database_engine(
                            flask_app.config["DATABASE_URL"]
                        )
                        flask_app.extensions["database_engine"] = engine
                    metadata.create_all(engine)
                    flask_app.extensions["database_initialized"] = True

    @flask_app.get("/")
    def index():
        values = {field: "" for field in ("hero_name", "powers", "age", "location", "email")}
        return render_template(
            "index.html",
            success=request.args.get("success") == "1",
            errors={},
            **values,
        )

    @flask_app.post("/")
    def submit_application():
        form_data = request.form.to_dict()
        errors, cleaned_data = validate_signup(form_data)
        if errors:
            return (
                render_template(
                    "index.html",
                    success=False,
                    errors=errors,
                    **cleaned_data,
                ),
                400,
            )

        engine: Engine = flask_app.extensions["database_engine"]
        with engine.begin() as connection:
            connection.execute(submissions.insert().values(**cleaned_data))
        return redirect(url_for("index", success=1), code=303)

    @flask_app.route("/admin", methods=["GET", "POST"])
    def admin():
        error = None
        admin_password = os.environ.get("ADMIN_PASSWORD")

        if request.method == "POST":
            action = request.form.get("action")
            if action == "logout":
                session.pop("admin_authenticated", None)
                return redirect(url_for("admin"))
            if not flask_app.config["SECRET_KEY"]:
                error = "Admin access is not configured. Set SECRET_KEY."
            elif not admin_password:
                error = "Admin access is not configured. Set ADMIN_PASSWORD."
            elif request.form.get("password", "") == admin_password:
                session["admin_authenticated"] = True
                return redirect(url_for("admin"))
            else:
                error = "Incorrect password."

        authenticated = session.get("admin_authenticated", False)
        if authenticated:
            engine: Engine = flask_app.extensions["database_engine"]
            with engine.connect() as connection:
                rows = connection.execute(
                    select(submissions).order_by(submissions.c.id.desc())
                ).mappings().all()
        else:
            rows = []

        return render_template(
            "admin.html",
            rows=rows,
            authenticated=authenticated,
            error=error,
        )

    @flask_app.get("/admin/export")
    def export_applications():
        if not session.get("admin_authenticated", False):
            return redirect(url_for("admin"))

        engine: Engine = flask_app.extensions["database_engine"]
        with engine.connect() as connection:
            rows = connection.execute(
                select(submissions).order_by(submissions.c.id.desc())
            ).mappings().all()

        output = io.StringIO()
        writer = csv.DictWriter(
            output,
            fieldnames=("id", "hero_name", "powers", "age", "location", "email"),
        )
        writer.writeheader()
        writer.writerows(dict(row) for row in rows)
        return Response(
            output.getvalue(),
            mimetype="text/csv",
            headers={"Content-Disposition": "attachment; filename=hero_applications.csv"},
        )

    return flask_app


app = create_app()
