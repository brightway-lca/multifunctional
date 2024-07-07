from pprint import pformat
from typing import Dict, List

from bw2data import get_node
from bw2data.backends import Exchange
from bw2data.backends.schema import ExchangeDataset
from bw2data.errors import UnknownObject
from loguru import logger


def allocation_before_writing(data: Dict[tuple, dict], strategy_label: str) -> Dict[tuple, dict]:
    """Utility to perform allocation on datasets and expand `data` with allocated processes."""
    from . import allocation_strategies

    datasets = []
    func = allocation_strategies[strategy_label]
    for key, ds in data.items():
        ds["database"] = key[0]
        ds["code"] = key[1]

        if sum(1 for exc in ds.get("exchanges", []) if exc.get("functional")) > 1:
            datasets.extend(func(ds))
        else:
            datasets.append(ds)

    return {(ds.pop("database"), ds.pop("code")): ds for ds in datasets}


def label_multifunctional_nodes(data: dict) -> dict:
    """Add type `multifunctional` to nodes with more than one functional exchange"""
    for key, ds in data.items():
        if sum(1 for exc in ds.get("exchanges", []) if exc.get("functional")) > 1:
            ds["type"] = "multifunctional"
    return data


def add_exchange_input_if_missing(data: dict) -> dict:
    """Add `input` values to each functional exchange if not already present.

    Needed because multifunctional processes don't normally link to themselves, but rather to
    specific products; however, due to limitations in our data schema we *must* have an `input`
    value even if it doesn't make sense."""
    for key, ds in data.items():
        for exc in ds.get("exchanges", []):
            if not exc.get("functional"):
                continue
            if exc.get("input"):
                if "code" in exc and exc["code"] != exc["input"][1]:
                    logger.critical(
                        "Mismatch in exchange: given 'code' is '{c}' but 'input' code is '{i}' in exchange:\n{e}",
                        c=exc["code"],
                        i=exc["input"][1],
                        e=pformat(exc),
                    )
                    exc["code"] = exc["input"][1]
            else:
                exc["input"] = key
                exc["mf_artificial_code"] = True
    return data


def update_datasets_from_allocation_results(data: List[dict]) -> None:
    """Given data from allocation, create or update datasets as needed from `data`."""
    from .node_classes import ReadOnlyProcessWithReferenceProduct

    for ds in data:
        exchanges = ds.pop("exchanges")
        try:
            node = get_node(database=ds["database"], code=ds["code"])
            node._data.update(**ds)
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
            exc.update(**exc_data)
            exc.output = node
            exc.save()
