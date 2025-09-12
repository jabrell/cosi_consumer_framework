import pytest

import pandas as pd
from pydantic import ValidationError

from .conftest import SampleAsset
from cosi_consumer_framework import Registrable


def test_registrable_objects(asset_list: list[SampleAsset]):
    for obj in asset_list:
        assert isinstance(obj, SampleAsset)
        assert obj.id in SampleAsset._used_ids
    assert SampleAsset._used_ids == {o.id for o in asset_list}


def test_register_object_empty_id():
    with pytest.raises(ValidationError):
        SampleAsset(id="")  # Attempt to create an object with an empty ID


def test_registrable_duplicated(asset1: SampleAsset):
    original_id_obj1 = ".".join(asset1.id.split(".")[1:])
    with pytest.raises(ValidationError):
        SampleAsset(id=original_id_obj1)  # Attempt to create a duplicate ID


def test_registrable_destroy():
    my_id = "test_destroy"
    obj_test_destroy = SampleAsset(id=my_id)
    obj_test_destroy.destroy()
    assert my_id not in SampleAsset._used_ids
    assert not obj_test_destroy.is_active


def test_registrable_unique_by_class_id():
    class U1(Registrable):
        pass

    class U2(Registrable):
        pass

    # does not raise an error as IDs are unique by class
    _ = U1(id="unique1")
    _ = U2(id="unique1")


def test_report(asset1: Registrable):
    report = asset1.report()
    assert report[asset1.class_name] == asset1.model_dump()


def test_create_from_dataframe():
    asset_data = [
        {"id": "dataframe_asset1"},
        {"id": "dataframe_asset2"},
        {"id": "dataframe_asset3"},
    ]
    df_assets = pd.DataFrame(asset_data)

    assets = SampleAsset.create_from_dataframe(df_assets)
    assert len(assets) == len(asset_data)
    for i, a in enumerate(assets):
        id_ = asset_data[i]["id"]
        assert isinstance(a, SampleAsset)
        assert a.id == f"SampleAsset.{id_}"
        a.destroy()
