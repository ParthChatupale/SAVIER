from sqlalchemy import Column, DateTime, Integer, String, Text

from database import Base


class AgentLog(Base):
    __tablename__ = "agent_logs"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, index=True, nullable=False)
    run_id = Column(String, index=True, nullable=False)
    agent_name = Column(String, nullable=False)
    task_name = Column(String, nullable=False)
    thought_process = Column(Text, nullable=False)
    tool_input = Column(Text, nullable=False)
    status = Column(String, nullable=False)
    violation_reason = Column(String, nullable=True)


class TimeSeriesMetric(Base):
    __tablename__ = "time_series_metrics"

    timestamp_minute = Column(DateTime, primary_key=True)
    tokens_burned_this_minute = Column(Integer, default=0, nullable=False)
    tasks_completed_this_minute = Column(Integer, default=0, nullable=False)


class GeneratedReport(Base):
    __tablename__ = "generated_reports"

    report_id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, nullable=False)
    report_markdown = Column(Text, nullable=False)
