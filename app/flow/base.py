from abc import ABC, abstractmethod
from enum import Enum
from typing import Dict, List, Optional, Union

from pydantic import BaseModel

from app.agent.base import BaseAgent


class FlowType(str, Enum):
    PLANNING = "planning"


class BaseFlow(BaseModel, ABC):
    """Base class for execution flows supporting multiple agents"""

    agents: Dict[str, BaseAgent]
    tools: Optional[List] = None
    primary_agent_key: Optional[str] = None

    class Config:
        arbitrary_types_allowed = True

    def __init__(
        self, agents: Union[BaseAgent, List[BaseAgent], Dict[str, BaseAgent]], **data
    ):
        # Handle different ways of providing agents
        if isinstance(agents, BaseAgent):
            agents_dict = {"default": agents}
        elif isinstance(agents, list):
            agents_dict = {f"agent_{i}": agent for i, agent in enumerate(agents)}
        else:
            agents_dict = agents

        # If primary agent not specified, use first agent
        primary_key = data.get("primary_agent_key")
        if not primary_key and agents_dict:
            primary_key = next(iter(agents_dict))
            data["primary_agent_key"] = primary_key

        # Set the agents dictionary
        data["agents"] = agents_dict

        # Initialize using BaseModel's init
        super().__init__(**data)

    @property
    def primary_agent(self) -> Optional[BaseAgent]:
        """Get the primary agent for the flow"""
        return self.agents.get(self.primary_agent_key)

    def get_agent(self, key: str) -> Optional[BaseAgent]:
        """Get a specific agent by key"""
        return self.agents.get(key)

    def add_agent(self, key: str, agent: BaseAgent) -> None:
        """Add a new agent to the flow"""
        self.agents[key] = agent

    @abstractmethod
    async def execute(self, input_text: str) -> str:
        """Execute the flow with given input"""


class PlanStepStatus(str, Enum):
    """Enum class defining possible statuses of a plan step"""

    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    BLOCKED = "blocked"

    @classmethod
    def get_all_statuses(cls) -> list[str]:
        """Return a list of all possible step status values"""
        return [status.value for status in cls]

    @classmethod
    def get_active_statuses(cls) -> list[str]:
        """Return a list of values representing active statuses (not started or in progress)"""
        return [cls.NOT_STARTED.value, cls.IN_PROGRESS.value]

    @classmethod
    def get_status_marks(cls) -> Dict[str, str]:
        """Return a mapping of statuses to their marker symbols"""
        return {
            cls.COMPLETED.value: "[✓]",
            cls.IN_PROGRESS.value: "[→]",
            cls.BLOCKED.value: "[!]",
            cls.NOT_STARTED.value: "[ ]",
        }
