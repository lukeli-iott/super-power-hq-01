#!/usr/bin/env python3
"""Regenerate the Architecture section of README.md from the repo's own code.

This performs lightweight static analysis of the repository (application
entrypoint, requirements, Dockerfile, GitHub Actions workflows) to keep the
Mermaid "System Design" and "CI/CD Flow" diagrams in README.md in sync with
the actual code. No AI/LLM calls are involved -- everything is derived
directly from files already in the repo.

Run manually with:
    python scripts/generate_architecture_diagram.py [--check]

--check exits non-zero if README.md would change, without writing it. This
is what .github/workflows/update-architecture-diagram.yml uses to decide
whether a commit is needed.
"""

from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

import yaml

REPO_ROOT = Path(__file__).resolve().parent.parent
README_PATH = REPO_ROOT / "README.md"
START_MARKER = "<!-- ARCHITECTURE-DIAGRAM:START -->"
END_MARKER = "<!-- ARCHITECTURE-DIAGRAM:END -->"


def _node_id(raw: str) -> str:
    """Turn a job/step name into a safe Mermaid node id."""
    safe = re.sub(r"[^A-Za-z0-9]", "_", raw).strip("_")
    return safe or "node"


def find_app_entrypoint() -> Path | None:
    for candidate in ("app.py", "main.py", "server.py"):
        path = REPO_ROOT / candidate
        if path.exists():
            return path
    return None


def detect_framework(requirements: str) -> str:
    lowered = requirements.lower()
    if "streamlit" in lowered:
        return "Streamlit App"
    if "flask" in lowered:
        return "Flask App"
    if "fastapi" in lowered:
        return "FastAPI App"
    return "Application"


def detect_database(app_source: str) -> str | None:
    if "sqlite3" in app_source:
        match = re.search(r"""DB_PATH\s*=.*?["']?([\w.]+\.db)["']?""", app_source)
        db_name = match.group(1) if match else "database.db"
        return f"SQLite {db_name}"
    if "psycopg2" in app_source or "postgresql" in app_source.lower():
        return "PostgreSQL"
    return None


def detect_env_auth(app_source: str) -> str | None:
    env_vars = sorted(set(re.findall(r"""os\.environ(?:\.get)?\(["'](\w*PASSWORD\w*|\w*SECRET\w*|\w*TOKEN\w*)["']""", app_source)))
    if env_vars:
        return ", ".join(env_vars)
    return None


def detect_deploy_target(workflows_text: str) -> str | None:
    match = re.search(r"huggingface\.co/spaces/([\w-]+/[\w-]+)", workflows_text)
    if match:
        return f"HuggingFace Space<br/>{match.group(1)}"
    return None


def read_workflows_text() -> str:
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    if not workflows_dir.exists():
        return ""
    return "\n".join(wf.read_text() for wf in sorted(workflows_dir.glob("*.yml")))


def build_system_design_diagram() -> str:
    app_path = find_app_entrypoint()
    app_source = app_path.read_text() if app_path else ""
    requirements_path = REPO_ROOT / "requirements.txt"
    requirements = requirements_path.read_text() if requirements_path.exists() else ""
    dockerfile_exists = (REPO_ROOT / "Dockerfile").exists()

    entrypoint_label = detect_framework(requirements)
    if app_path:
        entrypoint_label = f"{entrypoint_label} {app_path.name}"

    database = detect_database(app_source)
    auth_env_vars = detect_env_auth(app_source)
    deploy_target = detect_deploy_target(read_workflows_text())

    lines = [
        "flowchart LR",
        f"    User[Hero / Admin User] -->|HTTPS| App[{entrypoint_label}]",
    ]
    if database:
        lines.append(f"    App -->|reads/writes| DB[({database})]")
    if auth_env_vars:
        lines.append(f"    App -->|checks {auth_env_vars} env var| Auth[Admin Auth]")

    host_node = "App"
    if dockerfile_exists:
        lines.append("    App -->|runs inside| Docker[Docker Container]")
        host_node = "Docker"
    if deploy_target:
        lines.append(f"    {host_node} -->|hosted on| HF[{deploy_target}]")

    return "\n".join(lines)


_SUMMARY_KEYWORDS = ("deploy", "push", "test", "valid", "check", "build")


def _job_summary(job: dict) -> str:
    """Pick the most descriptive step name, skipping generic setup steps."""
    step_names = [
        step["name"]
        for step in (job.get("steps", []) or [])
        if isinstance(step, dict) and step.get("name")
    ]
    for name in step_names:
        if any(keyword in name.lower() for keyword in _SUMMARY_KEYWORDS):
            return name
    return step_names[-1] if step_names else "run steps"


def _job_trigger_note(job: dict) -> str | None:
    condition = job.get("if")
    if not condition:
        return None
    if "main" in condition:
        return "push to main only"
    return "conditional"


def build_cicd_diagram() -> str | None:
    workflows_dir = REPO_ROOT / ".github" / "workflows"
    if not workflows_dir.exists():
        return None

    for wf_path in sorted(workflows_dir.glob("*.yml")):
        data = yaml.safe_load(wf_path.read_text()) or {}
        jobs = data.get("jobs") or {}
        if not jobs:
            continue

        lines = ["flowchart TD", "    Dev[Push / PR to GitHub]"]
        job_labels = {
            job_id: f"{job_id.title()} Job:<br/>{_job_summary(job)}"
            for job_id, job in jobs.items()
        }

        for job_id, job in jobs.items():
            node = f"{_node_id(job_id)}[{job_labels[job_id]}]"
            needs = job.get("needs")
            needs_list = [needs] if isinstance(needs, str) else list(needs or [])
            note = _job_trigger_note(job)
            edge = f"-->|{note}|" if note else "-->"

            if needs_list:
                for dep in needs_list:
                    dep_node = f"{_node_id(dep)}[{job_labels.get(dep, dep)}]"
                    lines.append(f"    {dep_node} {edge} {node}")
            else:
                lines.append(f"    Dev {edge} {node}")

        lines.append(f"    {_node_id(list(jobs)[-1])} --> Live[Live App Updated]")
        return "\n".join(lines)

    return None


def render_architecture_block() -> str:
    system_diagram = build_system_design_diagram()
    cicd_diagram = build_cicd_diagram()

    parts = [
        START_MARKER,
        "### System Design",
        "",
        "```mermaid",
        system_diagram,
        "```",
        "",
    ]
    if cicd_diagram:
        parts += [
            "### CI/CD Flow",
            "",
            "```mermaid",
            cicd_diagram,
            "```",
            "",
        ]
    parts += [
        (
            "*Diagrams above are auto-generated from the repo's code and CI workflow "
            "-- see [`scripts/generate_architecture_diagram.py`](scripts/generate_architecture_diagram.py).*"
        ),
        END_MARKER,
    ]
    return "\n".join(parts)


def apply_to_readme(check_only: bool) -> bool:
    """Returns True if README.md is (or would be) changed."""
    original = README_PATH.read_text()
    if START_MARKER not in original or END_MARKER not in original:
        print(
            f"error: could not find {START_MARKER} / {END_MARKER} markers in README.md",
            file=sys.stderr,
        )
        sys.exit(1)

    before, rest = original.split(START_MARKER, 1)
    _, after = rest.split(END_MARKER, 1)
    updated = before + render_architecture_block() + after

    changed = updated != original
    if changed and not check_only:
        README_PATH.write_text(updated)
    return changed


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="Exit with status 1 if README.md would change, without writing it.",
    )
    args = parser.parse_args()

    changed = apply_to_readme(check_only=args.check)
    if args.check:
        if changed:
            print("README.md architecture diagrams are out of date.")
            sys.exit(1)
        print("README.md architecture diagrams are up to date.")
    else:
        print("README.md architecture diagrams updated." if changed else "No changes needed.")


if __name__ == "__main__":
    main()
