from collections import defaultdict
from typing import Any, Generic, TypeVar


from .registrable import Registrable

T = TypeVar("T", bound=Registrable)


class ObjectRegistry(Generic[T]):
    """A registry for objects that can be registered and deleted."""

    def __init__(self) -> None:
        self._objects: dict[str, T] = {}
        self._objects_by_class: dict[str, dict[str, T]] = defaultdict(defaultdict)

    @property
    def objects(self) -> dict[str, Any]:
        """Get all registered objects in the registry.

        Returns:
            A dictionary with class names as keys and dictionaries of objects
            as values.
        """
        return self._objects

    def add(self, objects: T | list[T]) -> None:
        """Register an object or a list of objects in the environment.

        Args:
            objects: An object or a list of objects to be registered.
        """
        if not isinstance(objects, list):
            objects = [objects]
        for obj in objects:
            if not isinstance(obj, Registrable):
                raise TypeError(
                    "Object must be a subclass of Registrable and actively registered."
                )
            if not obj.is_active:
                raise ValueError(
                    "Object must be a subclass of Registrable and actively registered."
                )
            # check if the object is already registered
            if obj.id in self._objects:
                raise ValueError(f"Object with id '{obj.id}' is already registered.")
            # register the object
            self._objects[obj.id] = obj
            self._objects_by_class[obj.__class__.__name__][obj.id] = obj

    def delete(self, objects: T | list[T]) -> None:
        """Delete an object or a list of objects from the registry.

        Args:
            objects: An object or a list of objects to be deleted.
        """
        if not isinstance(objects, list):
            objects = [objects]
        for obj in objects:
            try:
                del self._objects[obj.id]
            except KeyError:
                raise KeyError(f"Object with id '{obj.id}' not found.")

    def object_is_registered(self, object: Registrable | str) -> bool:
        """Check if an object is registered in the registry.
        Args:
            object: The object to check.
        """
        if isinstance(object, Registrable):
            key = object.id
        else:
            key = object
        return key in self._objects and self._objects[key].is_active

    def list_objects(self, class_name: str | type | None = None) -> list[Any]:
        """List all registered objects of a certain type.

        Args:
            class_name: The class name of the objects to list.
                If None, all objects are listed.
                Defaults to None.

        Returns:
            A list of all registered objects by class name. If class_name is None,
            it returns all registered objects.

        """
        if class_name is None:
            return list(self._objects.values())
        if isinstance(class_name, type):
            class_name = class_name.__name__
        return list(self._objects_by_class[class_name].values())

    def _get_class_name_from_id(self, id: str) -> str:
        """Extract class name and ID from a given id

        Args:
            id: The ID of the object, which must be a qualified ID (e.g., "ClassName.id").

        Returns:
            class_name: The class name extracted from the ID.
        """
        res = id.split(".")
        if len(res) < 2:
            raise ValueError("ID must be a qualified ID (e.g., 'ClassName.id').")
        return res[0]

    def get_item(self, id: str) -> T:
        """Get an item from the registry by class name and ID

        Args:
            id: The ID of the object to retrieve.

        Returns:
            The object with the specified ID and class name.
        """
        res = self._objects.get(id)
        if res is None:
            raise ValueError(f"Object with ID '{id}' not found in the registry.")
        return res
