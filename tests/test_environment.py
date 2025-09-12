import pytest

from cosi_consumer_framework import Asset, Environment
from .conftest import SampleAgent, SampleAsset


def test_dependency_check():
    """Test that dependencies are checked when registering assets."""
    env = Environment()

    class House(Asset):
        """
        A sample house
        """

        pass

    class Household(SampleAgent):
        """
        A sample household
        """

        house_id: str

    house = House(id="house1")
    env.add(house)
    # fails as wrong id type
    with pytest.raises(ValueError):
        household = Household(id="household1", house_id=house.id[:-2])
        env._check_references(household)
    # with the correct id, it should pass
    household.house_id = house.id
    env._check_references(household)
    household.destroy()
    house.destroy()


def test_asset_dependency():
    """Test that asset dependencies are checked."""
    env = Environment()

    class House(Asset):
        heatingSystem_id: str

    class HeatingSystem(Asset):
        pass

    house = House(id="house1", heatingSystem_id="heating1")

    # fails as HeatingSystem is not registered
    with pytest.raises(ValueError):
        env.add(house)

    # passes as HeatingSystem is registered
    heating_system = HeatingSystem(id="heating1")
    env.add(heating_system)
    house.heatingSystem_id = heating_system.id
    env.add(house)

    # clean up
    house.destroy()
    heating_system.destroy()


def test_asset_agent_dependency():
    """Test that asset-agent dependencies are checked."""
    env = Environment()

    class House(Asset):
        owner_id: str

    class Owner(SampleAgent):
        pass

    house = House(id="house1", owner_id="Owner.owner1")

    # fails as Owner is not registered
    with pytest.raises(ValueError):
        env.add(house)
    # passes as Owner is registered
    owner = Owner(id="owner1")

    # clean up
    env.add(owner)
    house.owner_id = owner.id


def test_agent_dependency():
    """Test that agent dependencies are checked."""
    env = Environment()

    class House(Asset):
        pass

    class MyAgent(SampleAgent):
        house_id: str

    house = House(id="house1")
    env.add(house)

    my_agent = MyAgent(id="agent1", house_id="false_id")
    # fails as wrong id
    with pytest.raises(ValueError):
        env.add(my_agent)

    # passes as House is registered
    my_agent.house_id = house.id
    env.add(my_agent)

    # clean up
    house.destroy()


def test_add_twice(agent1: SampleAgent):
    """Test that adding the same agent twice raises an error."""
    id_ = agent1.id.split(".")[-1]
    with pytest.raises(ValueError):
        SampleAgent(id=id_)


def test_get_list(asset_list: list[SampleAsset]):
    """Test that the get_asset_list method returns the correct assets."""
    env = Environment()
    env.add(asset_list)
    assert env.get_list(SampleAsset) == asset_list
    assert env.get_list("SampleAsset") == asset_list
    # also get it without filter as the only registered assets
    assert env.get_list() == asset_list


def test_get_list_empty():
    """Test that the get_asset_list method returns an empty list if no assets are registered."""
    env = Environment()
    assert env.get_list() == []


def test_get_item(asset1: Asset):
    """Test that the get_item method returns the correct asset."""
    env = Environment()
    env.add(asset1)
    assert env.get(asset1.id) == asset1

    # get a non-existing asset
    with pytest.raises(ValueError):
        env.get("Fuel.non_existing")


def test_year():
    model = Environment(year=2000)
    for _ in range(10):
        model.step()
    assert model.year == 2010


def test_reporting(asset1: SampleAsset, agent1: SampleAgent):
    """Test that reporting works correctly."""
    env = Environment()
    asset1.is_reporting = False
    env.add(asset1)
    env.add(agent1)
    env.report()

    assert len(env.reports) == 1
    assert len(env.reports[agent1.class_name]) == 1
    assert asset1.class_name not in env.reports


def test_step():
    """Test that the step method works correctly."""
    env = Environment(year=2020)

    class TestAgent(SampleAgent):
        def act(self, environment: Environment):
            _ = environment  # Use environment parameter to avoid diagnostic warning
            self.report()

    agent = TestAgent(id="agent1")
    env.add(agent)
    env.step()
    assert env.year == 2021  # Initial year is 2020 plus one step
    assert len(env.reports[agent.class_name]) == 1

    # clean up
    agent.destroy()


def test_delete_single_asset(asset1: SampleAsset):
    """Test that a single asset can be deleted using the delete method."""
    env = Environment()
    env.add(asset1)
    assert env.is_in(asset1)

    env.delete(asset1)
    assert not env.is_in(asset1)


def test_delete_single_agent(agent1: SampleAgent):
    """Test that a single agent can be deleted using the delete method."""
    env = Environment()
    env.add(agent1)
    assert env.is_in(agent1)

    env.delete(agent1)
    assert not env.is_in(agent1)


def test_delete_asset_list(asset_list: list[SampleAsset]):
    """Test that a list of assets can be deleted using the delete method."""
    env = Environment()
    env.add(asset_list)
    for asset in asset_list:
        assert env.is_in(asset)

    env.delete(asset_list)
    for asset in asset_list:
        assert not env.is_in(asset)


def test_delete_agent_list(agent_list: list[SampleAgent]):
    """Test that a list of agents can be deleted using the delete method."""
    env = Environment()
    env.add(agent_list)
    for agent in agent_list:
        assert env.is_in(agent)

    env.delete(agent_list)
    for agent in agent_list:
        assert not env.is_in(agent)


def test_delete_mixed_objects(asset1: SampleAsset, agent1: SampleAgent):
    """Test that mixed assets and agents can be deleted together using the delete method."""
    env = Environment()
    env.add([asset1, agent1])
    assert env.is_in(asset1)
    assert env.is_in(agent1)

    env.delete([asset1, agent1])
    assert not env.is_in(asset1)
    assert not env.is_in(agent1)


def test_delete_mixed_object_list(
    asset_list: list[SampleAsset], agent_list: list[SampleAgent]
):
    """Test that mixed lists of assets and agents can be deleted together using the delete method."""
    env = Environment()
    mixed_objects = asset_list + agent_list
    env.add(mixed_objects)

    for asset in asset_list:
        assert env.is_in(asset)
    for agent in agent_list:
        assert env.is_in(agent)

    env.delete(mixed_objects)

    for asset in asset_list:
        assert not env.is_in(asset)
    for agent in agent_list:
        assert not env.is_in(agent)


def test_delete_non_existent_object():
    """Test that deleting a non-existent object raises a KeyError."""
    env = Environment()
    asset = SampleAsset(id="non_existent_asset")

    with pytest.raises(KeyError):
        env.delete(asset)

    asset.destroy()


def test_delete_already_deleted_object(asset1: SampleAsset):
    """Test that deleting an already deleted object raises a KeyError."""
    env = Environment()
    env.add(asset1)
    env.delete(asset1)

    with pytest.raises(KeyError):
        env.delete(asset1)


def test_add_nested_lists(asset_list: list[SampleAsset], agent_list: list[SampleAgent]):
    """Test that nested lists of objects can be added using the add method."""
    env = Environment()
    nested_objects = [asset_list, agent_list]
    env.add(nested_objects)

    for asset in asset_list:
        assert env.is_in(asset)
    for agent in agent_list:
        assert env.is_in(agent)


def test_delete_nested_lists(
    asset_list: list[SampleAsset], agent_list: list[SampleAgent]
):
    """Test that nested lists of objects can be deleted using the delete method."""
    env = Environment()
    nested_objects = [asset_list, agent_list]
    env.add(nested_objects)

    # Verify objects are registered
    for asset in asset_list:
        assert env.is_in(asset)
    for agent in agent_list:
        assert env.is_in(agent)

    # Delete using nested lists
    env.delete(nested_objects)

    # Verify objects are deleted
    for asset in asset_list:
        assert not env.is_in(asset)
    for agent in agent_list:
        assert not env.is_in(agent)


def test_add_mixed_nested_lists():
    """Test adding nested lists with mixed object types."""
    env = Environment()

    asset1 = SampleAsset(id="nested_asset1")
    asset2 = SampleAsset(id="nested_asset2")
    agent1 = SampleAgent(id="nested_agent1")
    agent2 = SampleAgent(id="nested_agent2")

    nested_mixed = [[asset1, agent1], [asset2, agent2]]
    env.add(nested_mixed)

    assert env.is_in(asset1)
    assert env.is_in(asset2)
    assert env.is_in(agent1)
    assert env.is_in(agent2)

    # Clean up
    env.delete([asset1, asset2, agent1, agent2])
    asset1.destroy()
    asset2.destroy()
    agent1.destroy()
    agent2.destroy()


def test_add_invalid_type():
    """Test that adding an invalid type raises a TypeError."""
    env = Environment()

    with pytest.raises(TypeError):
        env.add("invalid_type")

    with pytest.raises(TypeError):
        env.add(12345)

    with pytest.raises(TypeError):
        env.add(None)
