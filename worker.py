import redis
import json
from sklearn.ensemble import IsolationForest
import random

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

print("👷 Worker started. Listening to Redis queue 'incoming_logs'...")

# --- THE ENDLESS LISTENING LOOP ---
while True:
    # 1. Pop the oldest log out of the queue (brpop blocks/waits if empty)
    queue_name, log_data = redis_client.brpop("incoming_logs")
    log = json.loads(log_data)
    
    # STAGE 1: Data Flattening
    tokens_used = log.get('tokens_used', 0)
    exec_time = log.get('execution_time_sec', 0)
    tool_name = log.get('tool_name', '')
    agent_name = log.get('agent_name', '')
    task_name = log.get('task', '')

    # Event-style logs for start events
    if tool_name in START_EVENT_TOOLS:
        print(f"{YELLOW}[⚡ EVENT] [{agent_name}] {tool_name}{RESET}")
        continue
    if tokens_used <= 0 or exec_time <= 0:
        print(f"{YELLOW}[⚡ EVENT] [{agent_name}] {tool_name or 'event'}{RESET}")
        continue
    velocity = tokens_used / exec_time
    tool_input_lower = log['tool_input'].lower()

    # STAGE 2: The Heuristic Filter
    if any(word in tool_input_lower for word in DANGEROUS_WORDS):
        print(f"{RED}[🚨 CRITICAL] Heuristic Block! Agent '{agent_name}' attempted: '{log['tool_input']}'{RESET}")
        continue

    # STAGE 3: Live Calibration
    if not calibrated:
        calibration_samples.append([velocity, exec_time])
        if len(calibration_samples) >= CALIBRATION_TARGET:
            ml_model.fit(calibration_samples)
            calibrated = True
            print(f"{GREEN}[✅ CALIBRATED] Isolation Forest trained on {CALIBRATION_TARGET} live events{RESET}")
        else:
            print(f"{YELLOW}[⚡ EVENT] Calibration sample {len(calibration_samples)}/{CALIBRATION_TARGET}: [{agent_name}] {task_name}{RESET}")
        continue

    # STAGE 4: The Statistical Filter (Isolation Forest)
    prediction = ml_model.predict([[velocity, exec_time]])
    if prediction[0] == -1:
        print(f"{YELLOW}[⚠️ WARNING] Behavioral Anomaly! Math implies broken loop: {tokens_used} tokens in {exec_time}s{RESET}")
        continue

    # STAGE 5: The Drop
    print(f"{GREEN}[✅ SAFE] Dropping normal log: [{agent_name}] {task_name}{RESET}")
