from collections import defaultdict
from typing import Any

from .asset import Asset
from .agent import Agent
from .object_registry import ObjectRegistry
from .registrable import Registrable

__all__ = ["Environment"]


class Environment:
    """The environment in which households are embedded."""

    def __init__(
        self,
        year: int = 2020,
    ):
        """Initialize the environment.

        Args:
            year: The year in which the simulation starts
                default: 2020
        """
        self._year = year

        # single registry for all objects
        self._object_registry: ObjectRegistry[Registrable] = ObjectRegistry()

        # track classnames of agents and assets
        self._agent_classnames: set[str] = set()
        self._asset_classnames: set[str] = set()

        # reports are used to store the reports of the assets and agents for each
        # step of the simulation
        # the report is stored as a dictionary with the object id as and a list
        # of dictionaries containing the report data
        self._reports: dict[str, list[dict[str, Any]]] = defaultdict(list)

    @property
    def year(self) -> int:
        """The current year of the simulation."""
        return self._year

    @property
    def assets(self) -> dict[str, Registrable]:
        """Get all registered assets in the environment.

        Returns:
            A dictionary with asset IDs as keys and asset objects as values.
        """
        assets = {}
        for class_name in self._asset_classnames:
            assets.update(self._object_registry._objects_by_class.get(class_name, {}))
        return assets

    @property
    def agents(self) -> dict[str, Registrable]:
        """Dictionary of all registered agents in the environment with their
        IDs as keys."""
        agents = {}
        for class_name in self._agent_classnames:
            agents.update(self._object_registry._objects_by_class.get(class_name, {}))
        return agents

    @property
    def reports(self) -> dict[str, list[dict[str, Any]]]:
        """Get the reports of all registered objects in the environment.

        Returns:
            A dictionary with object IDs as keys and lists of dictionaries
            containing the report data as values augmented by the current
            year of the environment.
        """
        return dict(self._reports)

    def add(
        self, objects: Asset | Agent | list[Asset | Agent] | list[list[Asset | Agent]]
    ):
        """Register objects (assets or agents) within the environment.

        Args:
            objects: A single object, list of objects, or nested list of objects to be registered.
                    Can be assets, agents, or a mix of both.
        """
        # Flatten nested lists
        if isinstance(objects, list) and objects and isinstance(objects[0], list):
            flattened = []
            for sublist in objects:
                if isinstance(sublist, list):
                    flattened.extend(sublist)
            objects = flattened
        elif not isinstance(objects, list):
            objects = [objects]

        for obj in objects:
            if not isinstance(obj, (Asset, Agent)):
                raise TypeError(
                    f"Expected Asset or Agent, got {type(obj).__name__} instead."
                )

            # check for dependencies
            self._check_references(obj)

            # add to registry
            self._object_registry.add(obj)

            # track classnames
            if isinstance(obj, Asset):
                self._asset_classnames.add(obj.__class__.__name__)
            elif isinstance(obj, Agent):
                self._agent_classnames.add(obj.__class__.__name__)

    def delete(
        self, objects: Asset | Agent | list[Asset | Agent] | list[list[Asset | Agent]]
    ):
        """Delete objects (assets or agents) from the environment.

        Args:
            objects: A single object, list of objects, or nested list of objects to be deleted.
                    Can be assets, agents, or a mix of both.
        """
        # Flatten nested lists
        objects_to_delete: list[Asset | Agent]
        if isinstance(objects, list) and objects and isinstance(objects[0], list):
            flattened: list[Agent | Asset] = []
            for sublist in objects:
                if isinstance(sublist, list):
                    flattened.extend(sublist)
            objects_to_delete = flattened
        elif not isinstance(objects, list):
            objects_to_delete = [objects]
        else:
            objects_to_delete = objects  # type: ignore

        self._object_registry.delete(objects_to_delete)  # type: ignore

    def get(self, id: str) -> Any:
        """Get an object (asset or agent) from the environment by ID.

        Args:
            id: The ID of the object to retrieve.

        Returns:
            The object with the specified ID, or None if not found.
        """
        return self._object_registry.get_item(id)

    def is_in(self, obj: Registrable | str) -> bool:
        """Check if an object is registered in the environment.

        Args:
            obj: The object to check, can be an Asset, Agent, or a string representing the id.

        Returns:
            True if the object is registered, False otherwise.
        """
        return self._object_registry.object_is_registered(obj)

    def get_list(self, class_name: str | type | None = None) -> list[Any]:
        """Get all registered objects of a certain type.

        Args:
            class_name: The class name of the objects to retrieve.

        Returns:
            A list of all registered objects of the specified type.
        """
        if class_name is None:
            return list(self.assets.values()) + list(self.agents.values())
        return self._object_registry.list_objects(class_name)

    def step(self):
        """Advance the environment by one year."""
        for a in self.agents.values():
            a.act(environment=self)
        self.report()

        self._year += 1

    def report(self) -> None:
        # do the reporting
        all_reporters: list[Registrable] = [
            r for r in self.get_list() if r.is_reporting
        ]

        for a in all_reporters:
            report = a.report()
            if report:
                for k, r in report.items():
                    r["year"] = self.year
                    self._reports[k].append(r)

    def _check_references(self, obj: Any) -> None:
        """Check if the object has references. For each reference, we check, whether
        the referenced object is registered in the environment.

        Dependencies are identified by attributes ending with '_id'. Dependencies
        are public attributes, i.e., not starting with an underscore. The dependency
        id has to be a qualified id, i.e., the class name and the id of the object
        (e.g., MyBuilding.1).

        Currently, we only allow to references to assets, i.e., references to agents
        will raise an error.

        Args:
            obj: The object to check for dependencies.
        Raises:
            ValueError: If a dependency is not registered in the environment.
        """
        # dependencies are identified by ending with _id
        # go through all attributes of the object and check if they are registered
        references = [
            attr
            for attr in obj.__dict__
            if attr.endswith("_id") and not attr.startswith("_")
        ]
        for ref in references:
            ref_id = getattr(obj, ref)
            # check whether the referenced object is registered
            if not self._object_registry.object_is_registered(ref_id):
                raise ValueError(
                    f"Object '{obj.__class__.__name__}' with id '{obj.id}'"
                    f" has a reference '{ref}'  with id '{ref_id}' which is not"
                    " registered in the environment."
                )
