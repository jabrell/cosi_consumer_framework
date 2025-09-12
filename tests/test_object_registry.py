import pytest

from cosi_consumer_framework import ObjectRegistry, Registrable

from .conftest import SampleAsset


def test_register_object(asset1: Registrable):
    registry = ObjectRegistry()
    registry.add(asset1)
    assert registry.objects[asset1.id] == asset1


def test_register_object_duplicated(asset1: Registrable):
    registry = ObjectRegistry()
    registry.add(asset1)
    with pytest.raises(ValueError):
        registry.add(asset1)


def test_objects_property(asset_list: list[Registrable]):
    registry = ObjectRegistry()
    registry.add(asset_list)
    objects = registry.objects
    assert isinstance(objects, dict)
    assert len(objects) == len(asset_list)


def test_register_not_registrable():
    registry = ObjectRegistry()

    class TestObj:
        def __init__(self):
            pass  # No id attribute

    obj1 = TestObj()
    with pytest.raises(TypeError):
        registry.add(obj1)


def test_register_objects_list(asset_list: list[SampleAsset]):
    registry = ObjectRegistry()
    registry.add(asset_list)
    for obj in asset_list:
        assert registry.objects[obj.id] == obj


def test_delete_object(asset_list: list[SampleAsset]):
    registry = ObjectRegistry()
    registry.add(asset_list)
    obj1 = asset_list[0]
    assert obj1.id in registry.objects
    registry.delete(obj1)
    assert obj1.id not in registry.objects


def test_object_is_registered(asset_list: list[SampleAsset]):
    registry = ObjectRegistry()
    registry.add(asset_list)
    obj1 = asset_list[0]
    assert registry.object_is_registered(obj1)

    class Foo:
        def __init__(self):
            pass

    assert not registry.object_is_registered(Foo())


def test_delete_non_existent_object(asset_list: list[SampleAsset]):
    registry = ObjectRegistry()
    registry.add(asset_list)
    obj1 = asset_list[0]
    registry.delete(obj1)
    with pytest.raises(KeyError):
        registry.delete(obj1)  # Attempt to delete an already deleted object


def test_add_non_active_object(asset1: SampleAsset):
    registry = ObjectRegistry()
    asset1._is_active = False  # Set the object to non-active
    with pytest.raises(ValueError):
        registry.add(asset1)  # Attempt to add a non-active object
    asset1._is_active = True  # Reset to active for further tests


def test_is_active_not_registered(asset1: SampleAsset):
    registry = ObjectRegistry()
    registry.add(asset1)  # Add the object to the registry
    asset1._is_active = False
    assert not registry.object_is_registered(asset1)  # Check if it is registered
    asset1._is_active = True  # Reset to active for further tests


def test_list_objects_by_class_name(asset_list: list[SampleAsset]):
    registry = ObjectRegistry()
    registry.add(asset_list)
    class_name = SampleAsset.__name__
    objects = registry.list_objects(class_name)
    assert isinstance(objects, list)
    assert all(isinstance(obj, SampleAsset) for obj in objects)
    assert len(objects) == len(asset_list)
    # as we only have one registered object class, we should get the same
    # results without specifying the class name
    assert registry.list_objects() == objects

    # test with class instead of string
    objects = registry.list_objects("SampleAsset")
    assert isinstance(objects, list)
    assert all(isinstance(obj, SampleAsset) for obj in objects)
    assert len(objects) == len(asset_list)

    # Test with a non-existent class name
    non_existent_class_name = "NonExistentClass"
    objects = registry.list_objects(non_existent_class_name)
    assert objects == []  # Should return an empty list for non-existent class names


def test_get_item(asset_list: list[SampleAsset]):
    registry = ObjectRegistry()
    registry.add(asset_list)
    obj1 = asset_list[0]

    # by id
    retrieved_obj = registry.get_item(
        id=obj1.id,
    )
    assert retrieved_obj == obj1

    # non-existent ID
    with pytest.raises(ValueError):
        registry.get_item(id="non_existent_id")

    # non-existent but valid class name
    with pytest.raises(ValueError):
        registry.get_item(id="nonExistant.id")


def test_get_object_name_from_id(asset1: SampleAsset):
    registry = ObjectRegistry()
    assert registry._get_class_name_from_id(asset1.id) == asset1.class_name
    with pytest.raises(ValueError):
        registry._get_class_name_from_id("invalid_id")
