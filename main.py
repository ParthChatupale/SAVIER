from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json
import logging

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_governance_backend")

# Connect to your local Ubuntu Redis server
# decode_responses=True ensures we get normal strings, not raw bytes
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)

class AgentLog(BaseModel):
    run_id: str
    agent_name: str
    timestamp: str
    task: str
    thought: str
    tool_name: str
    tool_input: str
    tokens_used: int
    execution_time_sec: float

@app.post("/ingest")
async def ingest_log(log: AgentLog):
    # 1. Convert the validated Pydantic object back to a JSON string
    log_json = log.model_dump_json()

    # 2. Push it into a high-speed Redis queue named "incoming_logs"
    try:
        redis_client.lpush("incoming_logs", log_json)
    except Exception as exc:
        logger.exception("Failed to enqueue telemetry to Redis")
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc

    # 3. Instantly return success!
    queue_len = redis_client.llen("incoming_logs")
    return {"status": "queued", "queue_len": queue_len}


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/health/redis")
async def health_redis():
    try:
        redis_client.ping()
    except Exception as exc:
        logger.exception("Redis ping failed")
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc
    return {"status": "ok"}


@app.get("/debug/queue")
async def debug_queue():
    try:
        return {"incoming_logs": redis_client.llen("incoming_logs")}
    except Exception as exc:
        logger.exception("Redis queue length failed")
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc
