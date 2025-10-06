from collections import defaultdict
from typing import Any

from .agent import Agent
from .environment import Environment
from .object_registry import ObjectRegistry
from .registrable import Registrable

__all__ = ["ConsumerModel"]


class ConsumerModel:
    """The consumer model orchestrates the simulation by managing agents and their
    interactions with the environment. Agents exist outside the environment and act upon it.
    """

    def __init__(
        self,
        environment: Environment | None = None,
        year: int = 2020,
    ):
        """Initialize the consumer model.

        Args:
            environment: The environment for the simulation. If not provided, a new
                environment is created.
            year: The year in which the simulation starts (only used if environment is None)
                default: 2020
        """
        self._environment = (
            environment if environment is not None else Environment(year=year)
        )

        # separate registry for agents
        self._agent_registry: ObjectRegistry[Agent] = ObjectRegistry()

        # track classnames of agents
        self._agent_classnames: set[str] = set()

        # agent reports are stored separately
        self._agent_reports: dict[str, list[dict[str, Any]]] = defaultdict(list)

    @property
    def environment(self) -> Environment:
        """The environment in which the simulation takes place."""
        return self._environment

    @property
    def year(self) -> int:
        """The current year of the simulation."""
        return self._environment.year

    @property
    def agents(self) -> dict[str, Agent]:
        """Dictionary of all registered agents in the model with their
        IDs as keys."""
        agents = {}
        for class_name in self._agent_classnames:
            agents.update(self._agent_registry._objects_by_class.get(class_name, {}))
        return agents

    @property
    def reports(self) -> dict[str, list[dict[str, Any]]]:
        """Get the reports of all registered objects (both agents and environment assets).

        Returns:
            A dictionary with object IDs as keys and lists of dictionaries
            containing the report data as values.
        """
        # Combine environment and agent reports
        all_reports = dict(self._environment.reports)
        all_reports.update(self._agent_reports)
        return all_reports

    def add_agents(self, agents: Agent | list[Agent] | list[list[Agent]]):
        """Register agents within the model.

        Args:
            agents: A single agent, list of agents, or nested list of agents to be registered.
        """
        # Flatten nested lists
        if isinstance(agents, list) and agents and isinstance(agents[0], list):
            flattened = []
            for sublist in agents:
                if isinstance(sublist, list):
                    flattened.extend(sublist)
            agents = flattened
        elif not isinstance(agents, list):
            agents = [agents]

        for agent in agents:
            if not isinstance(agent, Agent):
                raise TypeError(f"Expected Agent, got {type(agent).__name__} instead.")

            # check for dependencies (agents may reference assets in the environment)
            self._check_agent_references(agent)

            # add to agent registry
            self._agent_registry.add(agent)

            # track classnames
            self._agent_classnames.add(agent.__class__.__name__)

    def delete_agents(self, agents: Agent | list[Agent] | list[list[Agent]]):
        """Delete agents from the model.

        Args:
            agents: A single agent, list of agents, or nested list of agents to be deleted.
        """
        # Flatten nested lists
        agents_to_delete: list[Agent]
        if isinstance(agents, list) and agents and isinstance(agents[0], list):
            flattened: list[Agent] = []
            for sublist in agents:
                if isinstance(sublist, list):
                    flattened.extend(sublist)
            agents_to_delete = flattened
        elif not isinstance(agents, list):
            agents_to_delete = [agents]
        else:
            agents_to_delete = agents  # type: ignore

        self._agent_registry.delete(agents_to_delete)  # type: ignore

    def get_agent(self, id: str) -> Agent:
        """Get an agent from the model by ID.

        Args:
            id: The ID of the agent to retrieve.

        Returns:
            The agent with the specified ID.
        """
        return self._agent_registry.get_item(id)

    def agent_is_in(self, obj: Registrable | str) -> bool:
        """Check if an agent is registered in the model.

        Args:
            obj: The agent to check, can be an Agent or a string representing the id.

        Returns:
            True if the agent is registered, False otherwise.
        """
        return self._agent_registry.object_is_registered(obj)

    def get_agent_list(self, class_name: str | type | None = None) -> list[Agent]:
        """Get all registered agents of a certain type.

        Args:
            class_name: The class name of the agents to retrieve.

        Returns:
            A list of all registered agents of the specified type.
        """
        if class_name is None:
            return list(self.agents.values())
        return self._agent_registry.list_objects(class_name)

    def step(self):
        """Advance the simulation by one step. Agents act on the environment,
        then reports are generated, and finally time is advanced."""
        # Agents act on the environment
        for agent in self.agents.values():
            agent.act(environment=self._environment)

        # Generate reports for both agents and environment
        self._report_agents()
        self._environment.report()

        # Advance time
        self._environment.advance_time()

    def _report_agents(self) -> None:
        """Generate reports for all agents that have reporting enabled."""
        all_reporters: list[Agent] = [
            a for a in self.get_agent_list() if a.is_reporting
        ]

        for agent in all_reporters:
            report = agent.report()
            if report:
                for k, r in report.items():
                    r["year"] = self.year
                    self._agent_reports[k].append(r)

    def _check_agent_references(self, agent: Agent) -> None:
        """Check if the agent has references to assets in the environment.

        Dependencies are identified by attributes ending with '_id'. Dependencies
        are public attributes, i.e., not starting with an underscore. The dependency
        id has to be a qualified id, i.e., the class name and the id of the object
        (e.g., MyBuilding.1).

        Args:
            agent: The agent to check for dependencies.
        Raises:
            ValueError: If a dependency is not registered in the environment.
        """
        references = [
            attr
            for attr in agent.__dict__
            if attr.endswith("_id") and not attr.startswith("_")
        ]
        for ref in references:
            ref_id = getattr(agent, ref)
            # check whether the referenced object is registered in the environment
            if not self._environment.is_in(ref_id):
                raise ValueError(
                    f"Agent '{agent.__class__.__name__}' with id '{agent.id}'"
                    f" has a reference '{ref}' with id '{ref_id}' which is not"
                    " registered in the environment."
                )
