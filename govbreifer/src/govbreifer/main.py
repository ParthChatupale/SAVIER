#!/usr/bin/env python
import os
import sys
import warnings

from datetime import datetime, timezone
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from govbreifer.crew import Govbreifer
from agent_governance_sdk import monitor_crew
from database import SessionLocal
from models import GeneratedReport

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

SDK_BACKEND_URL = os.getenv("AGENT_GOVERNANCE_BACKEND_URL", "http://localhost:8000/ingest")
SDK_PROJECT_NAME = os.getenv("AGENT_GOVERNANCE_PROJECT_NAME", "govbreifer")
SDK_DEBUG = os.getenv("AGENT_GOVERNANCE_DEBUG", "true").lower() == "true"
SDK_TIMEOUT_SEC = float(os.getenv("AGENT_GOVERNANCE_TIMEOUT_SEC", "10"))

REPORT_PATH = Path(__file__).resolve().parents[2] / "report.md"


def _normalize_output(result: object) -> str:
    if isinstance(result, str):
        return result
    for attr in ("raw", "output", "final", "result"):
        if hasattr(result, attr):
            value = getattr(result, attr)
            if isinstance(value, str):
                return value
    return str(result)


def _persist_report(markdown: str) -> None:
    with SessionLocal() as db:
        db.add(
            GeneratedReport(
                created_at=datetime.now(timezone.utc),
                report_markdown=markdown,
            )
        )
        db.commit()


def _write_report(markdown: str) -> None:
    REPORT_PATH.write_text(markdown, encoding="utf-8")

@monitor_crew(
    backend_url=SDK_BACKEND_URL,
    project_name=SDK_PROJECT_NAME,
    debug=SDK_DEBUG,
    timeout_sec=SDK_TIMEOUT_SEC,
)
def run():
    """
    Run the crew.
    """
    inputs = {
        "topic": "AI Governance",
        'current_year': str(datetime.now().year)
    }

    try:
        result = Govbreifer().crew().kickoff(inputs=inputs)
        if result:
            markdown = _normalize_output(result)
            _write_report(markdown)
            _persist_report(markdown)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew: {e}")

def run_cli():
    """
    CLI entrypoint: print the result and exit cleanly.
    """
    result = run()
    if result is not None:
        print(result)
    return 0


def train():
    """
    Train the crew for a given number of iterations.
    """
    inputs = {
        "topic": "AI LLMs",
        'current_year': str(datetime.now().year)
    }
    try:
        Govbreifer().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Govbreifer().crew().replay(task_id=sys.argv[1])

    except Exception as e:
        raise Exception(f"An error occurred while replaying the crew: {e}")

def test():
    """
    Test the crew execution and returns the results.
    """
    inputs = {
        "topic": "AI LLMs",
        "current_year": str(datetime.now().year)
    }

    try:
        Govbreifer().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

def run_with_trigger():
    """
    Run the crew with trigger payload.
    """
    import json

    if len(sys.argv) < 2:
        raise Exception("No trigger payload provided. Please provide JSON payload as argument.")

    try:
        trigger_payload = json.loads(sys.argv[1])
    except json.JSONDecodeError:
        raise Exception("Invalid JSON payload provided as argument")

    inputs = {
        "crewai_trigger_payload": trigger_payload,
        "topic": "",
        "current_year": ""
    }

    try:
        result = Govbreifer().crew().kickoff(inputs=inputs)
        if result:
            _write_report(result)
            _persist_report(result)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")
