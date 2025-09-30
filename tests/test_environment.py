import pytest

from cosi_consumer_framework import Asset, Environment
from .conftest import SampleAgent, SampleAsset


def test_environment_only_accepts_assets(agent1: SampleAgent):
    """Test that environment only accepts assets, not agents."""
    env = Environment()
    
    with pytest.raises(TypeError, match="Expected Asset.*Agents should be added to ConsumerModel"):
        env.add(agent1)


def test_dependency_check():
    """Test that dependencies are checked when registering assets."""
    env = Environment()

    class House(Asset):
        """A sample house"""
        pass

    house = House(id="house1")
    env.add(house)
    
    # Test with wrong id type
    class HeatingSystem(Asset):
        house_id: str

    heating_system = HeatingSystem(id="heating1", house_id=house.id[:-2])
    with pytest.raises(ValueError):
        env._check_references(heating_system)
    
    # With the correct id, it should pass
    heating_system.house_id = house.id
    env._check_references(heating_system)
    
    # Clean up
    heating_system.destroy()
    house.destroy()


def test_asset_dependency():
    """Test that asset dependencies are checked."""
    env = Environment()

    class House(Asset):
        heatingSystem_id: str

    class HeatingSystem(Asset):
        pass

    house = House(id="house1", heatingSystem_id="HeatingSystem.heating1")

    # Fails as HeatingSystem is not registered
    with pytest.raises(ValueError):
        env.add(house)

    # Passes as HeatingSystem is registered
    heating_system = HeatingSystem(id="heating1")
    env.add(heating_system)
    house.heatingSystem_id = heating_system.id
    env.add(house)

    # Clean up
    house.destroy()
    heating_system.destroy()


def test_get_list(asset_list: list[SampleAsset]):
    """Test that the get_list method returns the correct assets."""
    env = Environment()
    env.add(asset_list)
    assert env.get_list(SampleAsset) == asset_list
    assert env.get_list("SampleAsset") == asset_list
    # Also get it without filter as the only registered assets
    assert env.get_list() == asset_list


def test_get_list_empty():
    """Test that the get_list method returns an empty list if no assets are registered."""
    env = Environment()
    assert env.get_list() == []


def test_get_item(asset1: Asset):
    """Test that the get method returns the correct asset."""
    env = Environment()
    env.add(asset1)
    assert env.get(asset1.id) == asset1

    # Get a non-existing asset
    with pytest.raises(ValueError):
        env.get("SampleAsset.non_existing")


def test_year():
    """Test that the year property and advance_time method work correctly."""
    env = Environment(year=2000)
    assert env.year == 2000
    for _ in range(10):
        env.advance_time()
    assert env.year == 2010


def test_reporting(asset1: SampleAsset):
    """Test that reporting works correctly for assets."""
    env = Environment()
    asset1.is_reporting = False
    env.add(asset1)
    env.report()

    # Asset has reporting disabled, so no reports should be generated
    assert len(env.reports) == 0

    # Enable reporting
    asset1.is_reporting = True
    env.report()
    assert len(env.reports) == 1
    assert len(env.reports[asset1.class_name]) == 1


def test_delete_single_asset(asset1: SampleAsset):
    """Test that a single asset can be deleted using the delete method."""
    env = Environment()
    env.add(asset1)
    assert env.is_in(asset1)

    env.delete(asset1)
    assert not env.is_in(asset1)


def test_delete_asset_list(asset_list: list[SampleAsset]):
    """Test that a list of assets can be deleted using the delete method."""
    env = Environment()
    env.add(asset_list)
    for asset in asset_list:
        assert env.is_in(asset)

    env.delete(asset_list)
    for asset in asset_list:
        assert not env.is_in(asset)


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


def test_add_nested_lists(asset_list: list[SampleAsset]):
    """Test that nested lists of assets can be added using the add method."""
    env = Environment()
    
    # Create a second list for nesting
    asset_list2 = [SampleAsset(id=f"nested_obj{i}") for i in range(3)]
    
    nested_objects = [asset_list, asset_list2]
    env.add(nested_objects)

    for asset in asset_list:
        assert env.is_in(asset)
    for asset in asset_list2:
        assert env.is_in(asset)
    
    # Clean up
    for asset in asset_list2:
        asset.destroy()


def test_delete_nested_lists(asset_list: list[SampleAsset]):
    """Test that nested lists of assets can be deleted using the delete method."""
    env = Environment()
    
    # Create a second list for nesting
    asset_list2 = [SampleAsset(id=f"nested_obj{i}") for i in range(3)]
    
    nested_objects = [asset_list, asset_list2]
    env.add(nested_objects)

    # Verify objects are registered
    for asset in asset_list:
        assert env.is_in(asset)
    for asset in asset_list2:
        assert env.is_in(asset)

    # Delete using nested lists
    env.delete(nested_objects)

    # Verify objects are deleted
    for asset in asset_list:
        assert not env.is_in(asset)
    for asset in asset_list2:
        assert not env.is_in(asset)
    
    # Clean up
    for asset in asset_list2:
        asset.destroy()


def test_add_invalid_type():
    """Test that adding an invalid type raises a TypeError."""
    env = Environment()

    with pytest.raises(TypeError):
        env.add("invalid_type")

    with pytest.raises(TypeError):
        env.add(12345)

    with pytest.raises(TypeError):
        env.add(None)
