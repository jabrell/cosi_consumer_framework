from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING


from sqlmodel import SQLModel
from pydantic import ConfigDict

if TYPE_CHECKING:
    from cosi_consumer_framework import Environment


class AgentPerception(SQLModel, ABC):
    """Abstract class for perceptions of an agent. Perceptions take place in two steps:
    1. The agent perceives the environment and creates a perception object.
    2. The perception object can be distorted to simulate noise in the perception.

    To use this class, you need to implement the `get_information_from_environment`
    method to extract the relevant information from the environment and instantiate the
    perception. You also need to implement the `distort_information` method to simulate
    noise in the perception of the agent.

    The `AgentPerception` class is used by calling class methods "perceive"
    which automatically calls the `get_information_from_environment` method
    and then distorts the information using the `distort_information` method.
    """

    model_config = ConfigDict(extra="forbid", validate_assignment=True)  # type: ignore

    @classmethod
    def perceive(cls, agent: Any, environment: "Environment") -> Any:
        """Create a perception from the environment.

        Args:
            environment: The environment in which the household is located.

        Returns:
            A HouseholdPerception object containing the relevant information.
        """
        information = cls.get_information_from_environment(
            agent=agent, environment=environment
        )
        info = cls(**information)
        info.distort_information(agent=agent)
        return info

    @classmethod
    @abstractmethod
    def get_information_from_environment(
        cls, agent: Any, environment: "Environment"
    ) -> dict:
        """Get information from the environment and instantiate the perception.

        args:
            agent: The agent that is perceiving the environment.
            environment: The environment in which the agent is located.

        Returns:
            Instance of AgentPerception containing the relevant information.
        """
        raise NotImplementedError(
            "This method should be implemented in a subclass of AgentPerception."
        )

    @abstractmethod
    def distort_information(self, agent: Any) -> None:
        """Distort the information in the perception.

        This method is used to distort the information in the perception.
        It can be used to simulate noise in the perception of the agent.

        Args:
            agent: The agent that is perceiving the environment.
        """
        raise NotImplementedError(
            "This method should be implemented in a subclass of AgentPerception."
        )
