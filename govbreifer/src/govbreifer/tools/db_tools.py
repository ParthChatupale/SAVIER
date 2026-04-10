import json
import sys
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field
from sqlalchemy import func, select


REPO_ROOT = Path(__file__).resolve().parents[4]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from database import SessionLocal  # noqa: E402
from models import AgentLog, GeneratedReport, TimeSeriesMetric  # noqa: E402


def _to_iso(value: Any) -> str | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.isoformat()
    return str(value)


class _EmptyInput(BaseModel):
    """No input required."""
    placeholder: str = Field(default="ok", description="No input required.")


class DBAuditTool(BaseTool):
    name: str = "db_audit_tool"
    description: str = (
        "Fetch recent governance audit logs and aggregates. "
        "Returns evidence table, top incidents, and counts by status/agent."
    )
    args_schema: Type[BaseModel] = _EmptyInput

    def _run(self, placeholder: str = "ok") -> str:
        with SessionLocal() as db:
            rows = db.execute(
                select(
                    AgentLog.id,
                    AgentLog.timestamp,
                    AgentLog.run_id,
                    AgentLog.agent_name,
                    AgentLog.task_name,
                    AgentLog.status,
                    AgentLog.violation_reason,
                )
                .order_by(AgentLog.timestamp.desc())
                .limit(100)
            ).all()

            status_counts = dict(
                db.execute(
                    select(AgentLog.status, func.count()).group_by(AgentLog.status)
                ).all()
            )
            agent_counts = dict(
                db.execute(
                    select(AgentLog.agent_name, func.count()).group_by(AgentLog.agent_name)
                ).all()
            )

            incidents = []
            for row in rows:
                if row.status != "SAFE":
                    incidents.append(
                        {
                            "id": row.id,
                            "timestamp": _to_iso(row.timestamp),
                            "agent_name": row.agent_name,
                            "task_name": row.task_name,
                            "status": row.status,
                            "violation_reason": row.violation_reason,
                        }
                    )
                if len(incidents) >= 5:
                    break

            evidence = [
                {
                    "id": row.id,
                    "timestamp": _to_iso(row.timestamp),
                    "run_id": row.run_id,
                    "agent_name": row.agent_name,
                    "task_name": row.task_name,
                    "status": row.status,
                    "violation_reason": row.violation_reason,
                }
                for row in rows
            ]

        payload = {
            "status_counts": status_counts,
            "agent_counts": agent_counts,
            "top_incidents": incidents,
            "evidence_table": evidence,
        }
        return json.dumps(payload, ensure_ascii=False)


class DBMetricsTool(BaseTool):
    name: str = "db_metrics_tool"
    description: str = (
        "Fetch global governance metrics and velocity series. "
        "Computes anomaly rate based on WARNING/CRITICAL alerts."
    )
    args_schema: Type[BaseModel] = _EmptyInput

    def _run(self, placeholder: str = "ok") -> str:
        with SessionLocal() as db:
            totals = db.execute(
                select(
                    func.coalesce(func.sum(TimeSeriesMetric.tasks_completed_this_minute), 0),
                    func.coalesce(func.sum(TimeSeriesMetric.tokens_burned_this_minute), 0),
                )
            ).one()

            alerts = db.execute(
                select(func.count()).select_from(AgentLog).where(AgentLog.status != "SAFE")
            ).one()

            velocity_rows = db.execute(
                select(
                    TimeSeriesMetric.timestamp_minute,
                    TimeSeriesMetric.tokens_burned_this_minute,
                    TimeSeriesMetric.tasks_completed_this_minute,
                )
                .order_by(TimeSeriesMetric.timestamp_minute.desc())
                .limit(60)
            ).all()

        tasks_completed = totals[0]
        tokens_burned = totals[1]
        alert_count = alerts[0]
        anomaly_rate = (alert_count / tasks_completed) if tasks_completed else 0.0

        velocity = [
            {
                "timestamp_minute": _to_iso(row.timestamp_minute),
                "tokens_burned_this_minute": row.tokens_burned_this_minute,
                "tasks_completed_this_minute": row.tasks_completed_this_minute,
            }
            for row in velocity_rows
        ]

        payload = {
            "tasks_completed": tasks_completed,
            "tokens_burned": tokens_burned,
            "alert_count": alert_count,
            "anomaly_rate": anomaly_rate,
            "velocity_series": velocity,
        }
        return json.dumps(payload, ensure_ascii=False)


class DBReportsTool(BaseTool):
    name: str = "db_reports_tool"
    description: str = "Fetch recent governance briefs for continuity context."
    args_schema: Type[BaseModel] = _EmptyInput

    def _run(self, placeholder: str = "ok") -> str:
        with SessionLocal() as db:
            rows = db.execute(
                select(GeneratedReport.report_id, GeneratedReport.created_at)
                .order_by(GeneratedReport.created_at.desc())
                .limit(3)
            ).all()

        payload = [
            {
                "report_id": row.report_id,
                "created_at": _to_iso(row.created_at),
            }
            for row in rows
        ]
        return json.dumps(payload, ensure_ascii=False)
