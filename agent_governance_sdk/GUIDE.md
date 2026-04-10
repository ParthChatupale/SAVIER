# Agent Governance SDK User Guide

This SDK provides full‑event observability for CrewAI runs and ships normalized telemetry to a backend without blocking agent execution.

## Quick Start (Local Demo)

### 1) Start the backend
From the repo root:

```bash
uvicorn main:app --reload
```

### 2) Start the worker
From the repo root:

```bash
python3 worker.py
```

### 3) Run your CrewAI project
From your CrewAI project folder (example: `analyzesys`):

```bash
AGENT_GOVERNANCE_DEBUG=true uv run run_crew
```

You should see:
- `EVENT` lines for start events
- `SAFE` lines for completed events
- `WARNING` only for true anomalies

## SDK Integration

In your CrewAI `main.py`, wrap your entrypoint with `@monitor_crew`:

```python
from agent_governance_sdk import monitor_crew

@monitor_crew(
    backend_url="http://localhost:8000/ingest",
    project_name="analyzesys",
    debug=True,
)
def run():
    ...
```

## Environment Variables

These variables are read from your CrewAI project `.env`:

```
AGENT_GOVERNANCE_BACKEND_URL=http://localhost:8000/ingest
AGENT_GOVERNANCE_PROJECT_NAME=analyzesys
AGENT_GOVERNANCE_DEBUG=true
```

## Telemetry Schema

Each event is posted with the exact schema below:

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

## Viewing Events in Redis

The backend stores events in two lists:
- `incoming_logs` (live queue for the worker)
- `incoming_logs_history` (persistent history, last 1000)

Use the helper script:

```bash
python3 print_events.py -n 10 --raw
```

To view the live queue:

```bash
python3 print_events.py -n 10 --raw --list incoming_logs
```

## Troubleshooting

**No logs in worker**
- Confirm FastAPI is running: `curl -s http://localhost:8000/health`
- Confirm Redis reachable: `curl -s http://localhost:8000/health/redis`
- Confirm CrewAI run prints SDK debug lines

**Only a few logs**
- Full event logging emits on task/agent/tool/LLM start and completion.
- Calibration phase in the worker prints `EVENT` until enough completed events arrive.

**Redis list is empty**
- The worker consumes `incoming_logs` immediately.
- Use `incoming_logs_history` to see past events.
