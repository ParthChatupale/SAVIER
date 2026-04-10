import json
import random
from datetime import datetime, timedelta, timezone

import os

from database import SessionLocal
from models import AgentLog, GeneratedReport, TimeSeriesMetric

DEMO_RUN_ID = "demo-run-2026-04-10"
AGENTS = [
    "AI LLMs Senior Data Researcher",
    "AI LLMs Reporting Analyst",
]
TASKS = ["research_task", "reporting_task"]
STATUS_WEIGHTS = [0.85, 0.12, 0.03]  # SAFE, WARNING, CRITICAL


def _rand_time(base: datetime, max_minutes: int) -> datetime:
    delta = timedelta(minutes=random.randint(0, max_minutes), seconds=random.randint(0, 59))
    return base + delta


def _choose_status() -> str:
    return random.choices(["SAFE", "WARNING", "CRITICAL"], weights=STATUS_WEIGHTS, k=1)[0]


def _violation_reason(status: str, tool_input: str) -> str | None:
    if status == "CRITICAL":
        return f"Blocked pattern in tool_input: {tool_input}"
    if status == "WARNING":
        return "Anomalous velocity spike detected"
    return None


def seed_events(count: int = 200, timeline_minutes: int = 10) -> None:
    base = datetime(2026, 4, 10, 10, 0, 0, tzinfo=timezone.utc)
    end = base + timedelta(minutes=timeline_minutes + 1)

    with SessionLocal() as db:
        # Clear previous demo data for repeatable runs
        db.query(AgentLog).filter(AgentLog.run_id == DEMO_RUN_ID).delete(synchronize_session=False)
        db.query(TimeSeriesMetric).filter(
            TimeSeriesMetric.timestamp_minute >= base,
            TimeSeriesMetric.timestamp_minute <= end,
        ).delete(synchronize_session=False)

        metrics = {}
        for _ in range(count):
            ts = _rand_time(base, timeline_minutes)
            status = _choose_status()
            agent = random.choice(AGENTS)
            task = random.choice(TASKS)

            if status == "CRITICAL":
                tool_input = random.choice(["rm -rf /", "drop table users;"])
                tokens_used = random.randint(50, 200)
                exec_time = round(random.uniform(0.8, 2.5), 3)
            elif status == "WARNING":
                tool_input = "RETRY_LOOP_999"
                tokens_used = random.randint(1500, 4000)
                exec_time = round(random.uniform(1.5, 4.0), 3)
            else:
                tool_input = "Querying dataset for insights."
                tokens_used = random.randint(200, 900)
                exec_time = round(random.uniform(1.5, 6.0), 3)

            db.add(
                AgentLog(
                    timestamp=ts,
                    run_id=DEMO_RUN_ID,
                    agent_name=agent,
                    task_name=task,
                    thought_process="Synthesizing findings for governance report.",
                    tool_input=tool_input,
                    status=status,
                    violation_reason=_violation_reason(status, tool_input),
                )
            )

            # Aggregate time series metrics per minute
            ts_minute = ts.replace(second=0, microsecond=0)
            if ts_minute not in metrics:
                metrics[ts_minute] = {"tokens": 0, "tasks": 0}
            metrics[ts_minute]["tokens"] += tokens_used
            metrics[ts_minute]["tasks"] += 1

        for ts_minute, agg in metrics.items():
            db.add(
                TimeSeriesMetric(
                    timestamp_minute=ts_minute,
                    tokens_burned_this_minute=agg["tokens"],
                    tasks_completed_this_minute=agg["tasks"],
                )
            )

        db.commit()


def seed_reports() -> None:
    with SessionLocal() as db:
        db.query(GeneratedReport).filter(GeneratedReport.report_id.in_([1, 2, 3])).delete(
            synchronize_session=False
        )
        reports = [
            GeneratedReport(
                report_id=1,
                created_at=datetime(2026, 4, 10, 10, 5, tzinfo=timezone.utc),
                report_markdown="# Weekly Governance Brief\n\n- SAFE events dominated the last run.\n- Two WARNING anomalies detected during rapid tool loops.\n- One CRITICAL violation blocked: `rm -rf /`",
            ),
            GeneratedReport(
                report_id=2,
                created_at=datetime(2026, 4, 10, 10, 12, tzinfo=timezone.utc),
                report_markdown="# Executive Summary\n\nThe system processed 200 agent actions in 10 minutes.\nTotal token burn: 64,120.\nAnomaly rate: 2.5%.",
            ),
            GeneratedReport(
                report_id=3,
                created_at=datetime(2026, 4, 10, 10, 19, tzinfo=timezone.utc),
                report_markdown="# Incident Review\n\nA CRITICAL violation was caught when a tool input matched `drop table`.\nThe action was blocked and logged.",
            ),
        ]
        for report in reports:
            db.merge(report)
        db.commit()


def seed_demo_files() -> None:
    with open("demo_files/events.json", "r", encoding="utf-8") as f:
        _ = json.load(f)
    with open("demo_files/reports.json", "r", encoding="utf-8") as f:
        _ = json.load(f)
    with open("demo_files/metadata.json", "r", encoding="utf-8") as f:
        _ = json.load(f)


if __name__ == "__main__":
    if not os.getenv("DATABASE_URL"):
        raise SystemExit(
            "DATABASE_URL is not set. Example: "
            "postgresql://governance_user:password@localhost:5432/governance_db"
        )
    seed_demo_files()
    seed_events()
    seed_reports()
    print("Seeded demo data into PostgreSQL.")
