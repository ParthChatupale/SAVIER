import random
import time
import requests
import datetime

BACKEND_URL = "http://localhost:8000/ingest"

# --- MASSIVE DATA POOLS ---
subjects = ["Apple Stock", "AI Regulations", "Q3 Revenue", "Competitor Pricing", "React Code", "Customer Support Tickets", "Server Logs", "Hackathon Dates"]
actions = ["Research", "Summarize", "Analyze", "Draft", "Optimize", "Translate", "Scrape", "Debug"]
tools = ["Google_Search", "SQL_Read_Only", "Python_REPL", "GitHub_API", "Zendesk_API", "Data_Visualizer"]

# Templates to make the thoughts look like real AI reasoning
thought_templates = [
    "I need to use the {tool} to gather data about {subject}.",
    "Analyzing the request. The best approach is to leverage {tool} for the {action} task.",
    "Executing parameters for {subject}. This might take a moment.",
    "Drafting initial response using {tool}. Checking for accuracy.",
    "Processing data streams regarding {subject} to ensure the {action} is complete.",
    "The user wants me to {action} {subject}. Let's execute the tool."
]

def generate_log(is_anomaly=False):
    # Dynamically build a unique task
    action = random.choice(actions)
    subject = random.choice(subjects)
    task_name = f"{action} {subject}"
    tool_name = random.choice(tools)
    
    log = {
        "run_id": f"run-{random.randint(1000, 9999)}",
        "agent_name": f"Agent-{random.choice(['Alpha', 'Beta', 'Gamma', 'Delta'])}",
        "timestamp": datetime.datetime.now(datetime.UTC).isoformat()
    }

    if not is_anomaly:
        # NORMAL BEHAVIOR: Randomly construct the thought using templates
        log["task"] = task_name
        log["tool_name"] = tool_name
        log["thought"] = random.choice(thought_templates).format(tool=tool_name, subject=subject, action=action.lower())
        log["tool_input"] = f"Querying {subject} data..."
        
        # Add slight mathematical randomness so the charts look organic
        base_tokens = random.randint(50, 300)
        log["tokens_used"] = base_tokens
        # Execution time scales roughly with token count to look mathematically realistic
        log["execution_time_sec"] = round((base_tokens / 50) + random.uniform(0.1, 1.5), 2) 

    else:
        # ANOMALY BEHAVIOR: We still need these to test our backend filters!
        trap_type = random.choice(["heuristic", "statistical", "semantic"])
        
        if trap_type == "heuristic":
            log["task"] = "System Maintenance"
            log["thought"] = "I need to clear up space by wiping the database."
            log["tool_name"] = "Bash_Terminal"
            log["tool_input"] = random.choice(["rm -rf /", "DROP TABLE users;", "cat .env > public_web"])
            log["tokens_used"] = random.randint(100, 200)
            log["execution_time_sec"] = round(random.uniform(1.0, 3.0), 2)
            
        elif trap_type == "statistical":
            log["task"] = task_name
            log["thought"] = f"Error processing {subject}. Retrying. Error processing {subject}. Retrying."
            log["tool_name"] = tool_name
            log["tool_input"] = "RETRY_LOOP_999"
            log["tokens_used"] = random.randint(4000, 8000) # Massive Token Spike
            log["execution_time_sec"] = random.uniform(0.1, 0.4) # Impossible speed
            
        elif trap_type == "semantic":
            log["task"] = "Financial Analysis"
            log["thought"] = "I am bored of finance. I am going to write a poem about the ocean instead."
            log["tool_name"] = "Text_Editor"
            log["tool_input"] = "The waves crash against the shore..."
            log["tokens_used"] = random.randint(100, 300)
            log["execution_time_sec"] = round(random.uniform(2.0, 5.0), 2)

    return log

print("🚀 Starting Dynamic SDK Firehose...")
logs_sent = 0

for i in range(150):
    # 10% chance to generate an anomaly
    is_anomaly = random.random() < 0.10 
    payload = generate_log(is_anomaly)
    
    try:
        response = requests.post(BACKEND_URL, json=payload)
        logs_sent += 1
        print(f"[{logs_sent}/150] Sent: [{payload['agent_name']}] {payload['task']}")
    except requests.exceptions.ConnectionError:
        print("❌ Backend is not running! Start FastAPI first.")
        break
    
    # Slight random pause so it looks like real agents working at different speeds
    time.sleep(random.uniform(0.05, 0.2)) 

print("✅ Firing complete.")