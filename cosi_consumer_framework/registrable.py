from typing import ClassVar, Any
import pandas as pd
from pydantic import field_validator, PrivateAttr
from sqlmodel import SQLModel
from pydantic import ConfigDict, Field


class Registrable(SQLModel):
    """
    A class that allows registration in the environment.

    The id provided to the constructor is automatically prefixed with the class
    name to ensure uniqueness across different classes.
    """

    # This class is used as a base class for all objects that can be registered
    # in the environment
    model_config = ConfigDict(extra="forbid", validate_assignment=True)  # type: ignore

    id: str  # The ID of the object, can be a string or an integer.
    _is_active: bool = PrivateAttr(default=True)
    is_reporting: bool = Field(
        default=True,
        exclude=True,
        description="Flag to indicate if the object is reporting.",
    )
    _used_ids: ClassVar[set[str]]

    def model_post_init(self, __context):
        self._used_ids.add(self.id)

    def __init_subclass__(cls, **kwargs: Any) -> None:
        """
        This method is called when a new subclass (e.g., Building) is created.
        """
        super().__init_subclass__(**kwargs)
        # Attach a fresh, unique set for used IDs to each subclass.
        cls._used_ids = set()

    @field_validator("id", mode="before")
    @classmethod
    def _validate_id_uniqueness(cls, v: str) -> str:
        """Pydantic validator to ensure the ID is globally unique at creation."""
        if not isinstance(v, int) and not v.strip():
            raise ValueError("id must be a non-empty string or integer.")

        # convert id to qualified ID
        v_new = f"{cls.__name__}.{v}"

        if v_new in cls._used_ids:
            raise ValueError(f"ID '{v}' is already in use and must be unique by class.")

        return v_new

    @property
    def class_name(self) -> str:
        """
        Get the class name of the object.

        Returns:
            The class name as a string.
        """
        return self.__class__.__name__

    @property
    def is_active(self) -> bool:
        """
        Check if the object is active.

        Returns:
            True if the object is active, False otherwise.
        """
        return self._is_active

    def destroy(self):
        """
        Delete the object and remove its ID from the used IDs set.
        """
        self._used_ids.remove(self.id)
        self._is_active = False

    def report(self) -> dict[str, dict[str, Any]]:
        """
        Report the object as a dictionary.

        Returns:
            A dictionary with the key as the class name and the value as a
            dictionary of the object's attributes
        """
        report = {self.class_name: self.model_dump()}
        return report

    @classmethod
    def create_from_dataframe(cls, df: pd.DataFrame) -> list["Registrable"]:
        """
        Create an instance of the class from a DataFrame.

        Args:
            df: A DataFrame containing the data to create the instance.

        Returns:
            List of instances of the class created from the DataFrame.
        """
        df.columns = df.columns.map(str)
        instances = [cls(**row) for row in df.to_dict(orient="records")]  # type: ignore
        return instances
