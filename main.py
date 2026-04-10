from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import redis
import json
import logging
from sqlalchemy import func, select

from database import Base, SessionLocal, engine
from models import AgentLog as AgentLogModel, GeneratedReport, TimeSeriesMetric

app = FastAPI()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("agent_governance_backend")

# Connect to your local Ubuntu Redis server
# decode_responses=True ensures we get normal strings, not raw bytes
redis_client = redis.Redis(host='localhost', port=6379, db=0, decode_responses=True)
QUEUE_LIST = "incoming_logs"
HISTORY_LIST = "incoming_logs_history"
HISTORY_LIMIT = 1000


@app.on_event("startup")
def startup() -> None:
    Base.metadata.create_all(bind=engine)

class AgentLogIn(BaseModel):
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
async def ingest_log(log: AgentLogIn):
    # 1. Convert the validated Pydantic object back to a JSON string
    log_json = log.model_dump_json()

    # 2. Push it into a high-speed Redis queue named "incoming_logs"
    try:
        redis_client.lpush(QUEUE_LIST, log_json)
        redis_client.lpush(HISTORY_LIST, log_json)
        redis_client.ltrim(HISTORY_LIST, 0, HISTORY_LIMIT - 1)
    except Exception as exc:
        logger.exception("Failed to enqueue telemetry to Redis")
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc

    # 3. Instantly return success!
    queue_len = redis_client.llen(QUEUE_LIST)
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
        return {
            "incoming_logs": redis_client.llen(QUEUE_LIST),
            "incoming_logs_history": redis_client.llen(HISTORY_LIST),
        }
    except Exception as exc:
        logger.exception("Redis queue length failed")
        raise HTTPException(status_code=503, detail="Redis unavailable") from exc


@app.get("/api/audit-logs")
async def api_audit_logs(agent_name: str | None = None, status: str | None = None):
    with SessionLocal() as db:
        stmt = select(
            AgentLogModel.timestamp,
            AgentLogModel.run_id,
            AgentLogModel.agent_name,
            AgentLogModel.task_name,
            AgentLogModel.status,
        ).order_by(AgentLogModel.timestamp.desc()).limit(100)

        if agent_name:
            stmt = stmt.where(AgentLogModel.agent_name == agent_name)
        if status:
            stmt = stmt.where(AgentLogModel.status == status)

        rows = db.execute(stmt).all()
        return [
            {
                "timestamp": row.timestamp,
                "run_id": row.run_id,
                "agent_name": row.agent_name,
                "task_name": row.task_name,
                "status": row.status,
            }
            for row in rows
        ]


@app.get("/api/metrics/global")
async def api_metrics_global():
    with SessionLocal() as db:
        totals = db.execute(
            select(
                func.coalesce(func.sum(TimeSeriesMetric.tasks_completed_this_minute), 0),
                func.coalesce(func.sum(TimeSeriesMetric.tokens_burned_this_minute), 0),
            )
        ).one()
        alerts = db.execute(
            select(func.count())
            .select_from(AgentLogModel)
            .where(AgentLogModel.status != "SAFE")
        ).one()

        return {
            "tasks_completed": totals[0],
            "tokens_burned": totals[1],
            "alerts": alerts[0],
        }


@app.get("/api/metrics/velocity")
async def api_metrics_velocity():
    with SessionLocal() as db:
        rows = db.execute(
            select(
                TimeSeriesMetric.timestamp_minute,
                TimeSeriesMetric.tokens_burned_this_minute,
            )
            .order_by(TimeSeriesMetric.timestamp_minute.desc())
            .limit(60)
        ).all()

        return [
            {
                "timestamp_minute": row.timestamp_minute,
                "tokens_burned_this_minute": row.tokens_burned_this_minute,
            }
            for row in rows
        ]


@app.get("/api/reports")
async def api_reports():
    with SessionLocal() as db:
        rows = db.execute(
            select(GeneratedReport.report_id, GeneratedReport.created_at).order_by(
                GeneratedReport.created_at.desc()
            )
        ).all()

        return [
            {"report_id": row.report_id, "created_at": row.created_at} for row in rows
        ]
