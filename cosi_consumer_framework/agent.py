from abc import ABC, abstractmethod
from typing import Any, TYPE_CHECKING

from .registrable import Registrable

if TYPE_CHECKING:
    from .agent_perception import AgentPerception  # pragma: no cover
    from .environment import Environment  # pragma: no cover
    from .choice_set import ChoiceSet  # pragma: no cover


class Agent(Registrable, ABC):
    """An abstract base class for any object that can perform actions
    during a simulation step."""

    def act(self, environment: "Environment") -> None:
        """Perform a step in the simulation. This contains of several steps:
        1. Perceive the environment to get the current state.
        2. Trigger a choice set based on the perception.
        3. Evaluate the options in the choice set.
        4. Make a choice based on the evaluation.

        Args:
            environment: The environment in which the household is located.
                If not provided, the household's environment is used.
        """
        # get information from the environment
        perception = self.perceive(environment=environment)
        # trigger choice sets
        options = self.trigger_choice(perception=perception)
        # evaluate the choice set
        options.evaluate()
        # make choice based on the evaluation
        self.choose(options=options, perception=perception)

    @abstractmethod
    def perceive(self, environment: "Environment") -> "AgentPerception":
        """Perceive the environment and return an AgentPerception object.

        Args:
            environment (Environment): The environment in which the agent operates.

        Returns:
            AgentPerception: An object containing the agent's perception of the environment.
        """
        pass

    @abstractmethod
    def trigger_choice(self, perception: Any) -> "ChoiceSet":
        """Given the agent's perception, determine the set of available options

        Args:
            perception (AgentPerception): The agent's perception of the environment.

        Returns:
            ChoiceSet: A choice set containing the available options for the agent.
        """
        pass

    @abstractmethod
    def choose(self, options: Any, perception: Any) -> None:
        """Make a choice based on the available options. This requires that agent
        has evaluated the options in the choice set. This is typically done
        automatically in the pre-defined step method.

        Args:
            options (ChoiceSet): The choice set containing the available options.
            perception (AgentPerception): The agent's perception of the environment.
        """
        pass
