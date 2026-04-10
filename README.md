# Agent Governance SDK Playground

This repo now contains a small Python SDK skeleton for passively monitoring CrewAI runs and forwarding normalized telemetry to the existing FastAPI `/ingest` endpoint.

## What is included

- `agent_governance_sdk/`: decorator-first SDK package
- `main.py`: FastAPI ingest endpoint that queues telemetry into Redis
- `worker.py`: Redis worker with simple heuristic and anomaly checks
- `simulate_sdk.py`: payload firehose for backend testing

## SDK shape

```python
from agent_governance_sdk import monitor_crew


@monitor_crew(
    backend_url="http://localhost:8000/ingest",
    project_name="autonomous-agent-governance",
    debug=True,
)
def run_workflow():
    # your CrewAI flow goes here
    ...
```

The SDK is event-first and fail-open:

- it tries to register CrewAI event listeners when the decorated function starts
- it normalizes telemetry into your required payload schema
- it pushes payloads through a background sender thread
- if CrewAI is missing or the backend is unavailable, it quietly degrades

## Expected payload

```json
{
  "run_id": "string",
  "agent_name": "string",
  "timestamp": "ISO 8601 UTC string",
  "task": "string",
  "thought": "string",
  "tool_name": "string",
  "tool_input": "string",
  "tokens_used": "integer",
  "execution_time_sec": "float"
}
```

## Run the demo backend

Start FastAPI:

```bash
uvicorn main:app --reload
```

Start the worker in another terminal:

```bash
python worker.py
```

Send sample payloads:

```bash
python simulate_sdk.py
```
