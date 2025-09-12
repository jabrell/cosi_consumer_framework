from abc import ABC
from .registrable import Registrable


class Asset(Registrable, ABC):
    """An abstract base class for any object that can be registered as an asset
    in the environment. Assets can be used to represent various entities in the
    simulation, such as buildings, heating systems, or other components."""

    pass
