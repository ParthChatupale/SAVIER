#!/usr/bin/env python
import os
import sys
import warnings

from datetime import datetime
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[3]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from analyzesys.crew import Analyzesys
from agent_governance_sdk import monitor_crew

warnings.filterwarnings("ignore", category=SyntaxWarning, module="pysbd")

# This main file is intended to be a way for you to run your
# crew locally, so refrain from adding unnecessary logic into this file.
# Replace with inputs you want to test with, it will automatically
# interpolate any tasks and agents information

SDK_BACKEND_URL = os.getenv("AGENT_GOVERNANCE_BACKEND_URL", "http://localhost:8000/ingest")
SDK_PROJECT_NAME = os.getenv("AGENT_GOVERNANCE_PROJECT_NAME", "analyzesys")
SDK_DEBUG = os.getenv("AGENT_GOVERNANCE_DEBUG", "true").lower() == "true"
SDK_TIMEOUT_SEC = float(os.getenv("AGENT_GOVERNANCE_TIMEOUT_SEC", "10"))

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
        'topic': 'AI LLMs',
        'current_year': str(datetime.now().year)
    }

    try:
        result = Analyzesys().crew().kickoff(inputs=inputs)
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
        Analyzesys().crew().train(n_iterations=int(sys.argv[1]), filename=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while training the crew: {e}")

def replay():
    """
    Replay the crew execution from a specific task.
    """
    try:
        Analyzesys().crew().replay(task_id=sys.argv[1])

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
        Analyzesys().crew().test(n_iterations=int(sys.argv[1]), eval_llm=sys.argv[2], inputs=inputs)

    except Exception as e:
        raise Exception(f"An error occurred while testing the crew: {e}")

@monitor_crew(
    backend_url=SDK_BACKEND_URL,
    project_name=SDK_PROJECT_NAME,
    debug=SDK_DEBUG,
    timeout_sec=SDK_TIMEOUT_SEC,
)
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
        result = Analyzesys().crew().kickoff(inputs=inputs)
        return result
    except Exception as e:
        raise Exception(f"An error occurred while running the crew with trigger: {e}")

def run_with_trigger_cli():
    """
    CLI entrypoint: print the result and exit cleanly.
    """
    result = run_with_trigger()
    if result is not None:
        print(result)
    return 0
