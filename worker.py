import redis
import json
from datetime import datetime, timezone
from sklearn.ensemble import IsolationForest
import random

from database import SessionLocal
from models import AgentLog, TimeSeriesMetric

# Connect to Redis
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

# --- STAGE 0: ML COLD START TRAINING ---
print("🧠 Initializing Isolation Forest (calibration pending)...")
ml_model = IsolationForest(contamination=0.05, random_state=42)
calibration_samples = []
CALIBRATION_TARGET = 60
calibrated = False

DANGEROUS_WORDS = ["rm -rf", "drop table", ".env", "password"]
START_EVENT_TOOLS = {
    "task_started",
    "agent_execution_started",
    "tool_usage_started",
    "llm_call_started",
}

# ANSI Colors
RED = '\033[91m'
YELLOW = '\033[93m'
GREEN = '\033[92m'
RESET = '\033[0m'

def _parse_timestamp(value: str | None) -> datetime:
    if not value:
        return datetime.now(timezone.utc)
    if value.endswith("Z"):
        value = value[:-1] + "+00:00"
    return datetime.fromisoformat(value)


print("👷 Worker started. Listening to Redis queue 'incoming_logs'...")

# --- THE ENDLESS LISTENING LOOP ---
while True:
    # 1. Pop the oldest log out of the queue (brpop blocks/waits if empty)
    queue_name, log_data = redis_client.brpop("incoming_logs")
    log = json.loads(log_data)

    # STAGE 1: Data Flattening
    tokens_used = log.get("tokens_used", 0)
    exec_time = log.get("execution_time_sec", 0)
    tool_name = log.get("tool_name", "")
    agent_name = log.get("agent_name", "")
    task_name = log.get("task", "")

    is_start_event = tool_name in START_EVENT_TOOLS or tokens_used <= 0 or exec_time <= 0
    is_completed_event = tokens_used > 0 and exec_time > 0

    if is_start_event:
        print(f"{YELLOW}[⚡ EVENT] [{agent_name}] {tool_name or 'event'}{RESET}")

    status = "SAFE"
    violation_reason = None

    tool_input = log.get("tool_input", "")
    tool_input_lower = tool_input.lower()

    # STAGE 2: The Heuristic Filter
    if any(word in tool_input_lower for word in DANGEROUS_WORDS):
        status = "CRITICAL"
        violation_reason = f"Blocked pattern in tool_input: {tool_input}"
        print(f"{RED}[🚨 CRITICAL] Heuristic Block! Agent '{agent_name}' attempted: '{tool_input}'{RESET}")

    # STAGE 3: Live Calibration
    skip_ml = False
    if not calibrated and is_completed_event:
        calibration_samples.append([tokens_used / exec_time, exec_time])
        if len(calibration_samples) >= CALIBRATION_TARGET:
            ml_model.fit(calibration_samples)
            calibrated = True
            print(f"{GREEN}[✅ CALIBRATED] Isolation Forest trained on {CALIBRATION_TARGET} live events{RESET}")
        else:
            print(f"{YELLOW}[⚡ EVENT] Calibration sample {len(calibration_samples)}/{CALIBRATION_TARGET}: [{agent_name}] {task_name}{RESET}")
        skip_ml = True

    # STAGE 4: The Statistical Filter (Isolation Forest)
    if calibrated and not skip_ml and is_completed_event and status != "CRITICAL":
        velocity = tokens_used / exec_time
        prediction = ml_model.predict([[velocity, exec_time]])
        if prediction[0] == -1:
            status = "WARNING"
            violation_reason = f"Anomalous velocity: {tokens_used} tokens in {exec_time}s"
            print(f"{YELLOW}[⚠️ WARNING] Behavioral Anomaly! Math implies broken loop: {tokens_used} tokens in {exec_time}s{RESET}")
        else:
            print(f"{GREEN}[✅ SAFE] Dropping normal log: [{agent_name}] {task_name}{RESET}")

    # STAGE 5: Persist to PostgreSQL
    try:
        ts = _parse_timestamp(log.get("timestamp"))
        ts_minute = ts.replace(second=0, microsecond=0)
    except Exception:
        ts = datetime.now(timezone.utc)
        ts_minute = ts.replace(second=0, microsecond=0)

    with SessionLocal() as db:
        db.add(
            AgentLog(
                timestamp=ts,
                run_id=log.get("run_id", ""),
                agent_name=agent_name,
                task_name=task_name,
                thought_process=log.get("thought", ""),
                tool_input=tool_input,
                status=status,
                violation_reason=violation_reason,
            )
        )

        # Upsert metrics for completed events only
        if is_completed_event:
            metrics_row = db.get(TimeSeriesMetric, ts_minute)
            if metrics_row is None:
                metrics_row = TimeSeriesMetric(
                    timestamp_minute=ts_minute,
                    tokens_burned_this_minute=tokens_used,
                    tasks_completed_this_minute=1,
                )
                db.add(metrics_row)
            else:
                metrics_row.tokens_burned_this_minute += tokens_used
                metrics_row.tasks_completed_this_minute += 1

        db.commit()
