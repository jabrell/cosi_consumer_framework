from abc import ABC, abstractmethod
from typing import Any
from pydantic import BaseModel


class ChoiceSet(BaseModel, ABC):
    """
    A class to represent a choice set for an agent in the COSI ABM. A choice set
    contains a list of option that the agent can choose from and performs their
    evaluation. The choice set is initialized using a trigger function that
    determines the available options based on the agent's perception of the
    environment.
    """

    @classmethod
    @abstractmethod
    def trigger(cls, agent: Any, perception: Any) -> "ChoiceSet":
        """Trigger function to determine the available options for the agent.
        This method should be implemented by subclasses to return a choice set
        containing the available options based on the agent's perception of the
        environment.

        Args:
            agent: The agent for which the choice set is created.
            perception: The perception of the agent, which contains information
                about the environment and the agent's state.
        """
        pass

    @abstractmethod
    def evaluate(self) -> None:
        """Evaluate the available options in the choice set.

        This method should be implemented by subclasses to perform the evaluation
        of the options based on the agent's preferences and the environment.
        """
        pass
