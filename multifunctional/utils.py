from typing import List

from bw2data import get_node
from bw2data.backends import Exchange
from bw2data.backends.schema import ExchangeDataset
from bw2data.errors import UnknownObject


def prepare_multifunctional_for_writing(data: dict) -> dict:
    """Add `input` values to each functional exchange if not already present."""
    for key, ds in data.items():
        for exc in ds.get("exchanges", []):
            if exc.get("functional") and "input" not in exc:
                exc["input"] = key
    return data


def update_datasets_from_allocation_results(data: List[dict]) -> None:
    """Given data from allocation, create or update datasets as needed from `data`."""
    from .node_classes import ReadOnlyProcessWithReferenceProduct

    for ds in data:
        exchanges = ds.pop("exchanges")
        try:
            node = get_node(database=ds["database"], code=ds["code"])
            node._data.update(**data)
        except UnknownObject:
            node = ReadOnlyProcessWithReferenceProduct(**ds)

        node.save()

        # Delete existing edges. Much easier than trying to find the right one to update.
        ExchangeDataset.delete().where(
            ExchangeDataset.output_code == ds["code"],
            ExchangeDataset.output_database == ds["database"],
        ).execute()

        for exc_data in exchanges:
            exc = Exchange()
            exc.output = node
            exc.update(**exc_data)
            exc.save()
