import os

from crewai import Agent, Crew, LLM, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
# If you want to run a snippet of code before or after the crew starts,
# you can use the @before_kickoff and @after_kickoff decorators
# https://docs.crewai.com/concepts/crews#example-crew-class-with-decorators

from govbreifer.tools import DBAuditTool, DBMetricsTool, DBReportsTool


FAST_MODEL = os.getenv("GOVBREIFER_MODEL_FAST", "nvidia_nim/google/gemma-4-31b-it")
FINAL_MODEL = os.getenv("GOVBREIFER_MODEL_FINAL", "nvidia_nim/openai/gpt-oss-120b")

DEFAULT_NIM_KEY = os.getenv("NVIDIA_NIM_API_KEY")
FAST_NIM_KEY = os.getenv("GOVBREIFER_NIM_API_KEY_FAST", DEFAULT_NIM_KEY)
FINAL_NIM_KEY = os.getenv("GOVBREIFER_NIM_API_KEY_FINAL", DEFAULT_NIM_KEY)

FAST_LLM = LLM(model=FAST_MODEL, api_key=FAST_NIM_KEY)
FINAL_LLM = LLM(model=FINAL_MODEL, api_key=FINAL_NIM_KEY)


@CrewBase
class Govbreifer():
    """Govbreifer crew"""

    agents: list[BaseAgent]
    tasks: list[Task]

    # Learn more about YAML configuration files here:
    # Agents: https://docs.crewai.com/concepts/agents#yaml-configuration-recommended
    # Tasks: https://docs.crewai.com/concepts/tasks#yaml-configuration-recommended
    
    # If you would like to add tools to your agents, you can learn more about it here:
    # https://docs.crewai.com/concepts/agents#agent-tools
    @agent
    def governance_researcher(self) -> Agent:
        return Agent(
            config=self.agents_config['governance_researcher'], # type: ignore[index]
            verbose=True,
            tools=[DBAuditTool(), DBMetricsTool()],
            llm=FAST_LLM,
        )

    @agent
    def risk_compliance_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['risk_compliance_analyst'], # type: ignore[index]
            verbose=True,
            tools=[DBAuditTool(), DBReportsTool()],
            llm=FAST_LLM,
        )

    @agent
    def metrics_roi_analyst(self) -> Agent:
        return Agent(
            config=self.agents_config['metrics_roi_analyst'], # type: ignore[index]
            verbose=True,
            tools=[DBMetricsTool()],
            llm=FAST_LLM,
        )

    @agent
    def briefing_editor(self) -> Agent:
        return Agent(
            config=self.agents_config['briefing_editor'], # type: ignore[index]
            verbose=True,
            llm=FINAL_LLM,
        )

    # To learn more about structured task outputs,
    # task dependencies, and task callbacks, check out the documentation:
    # https://docs.crewai.com/concepts/tasks#overview-of-a-task
    @task
    def evidence_harvest(self) -> Task:
        return Task(
            config=self.tasks_config['evidence_harvest'], # type: ignore[index]
        )

    @task
    def risk_posture(self) -> Task:
        return Task(
            config=self.tasks_config['risk_posture'], # type: ignore[index]
        )

    @task
    def metrics_roi(self) -> Task:
        return Task(
            config=self.tasks_config['metrics_roi'], # type: ignore[index]
        )

    @task
    def executive_brief(self) -> Task:
        return Task(
            config=self.tasks_config['executive_brief'], # type: ignore[index]
            output_file='report.md'
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Govbreifer crew"""
        # To learn how to add knowledge sources to your crew, check out the documentation:
        # https://docs.crewai.com/concepts/knowledge#what-is-knowledge

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
