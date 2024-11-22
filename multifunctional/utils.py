from collections import Counter
from pprint import pformat
from typing import Dict, List

from bw2data import get_node, labels
from bw2data.backends import Exchange, Node
from bw2data.backends.schema import ExchangeDataset
from bw2data.errors import UnknownObject
from loguru import logger

from multifunctional.errors import MultipleFunctionalExchangesWithSameInput


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
    """Given data from allocation, create, update, or delete datasets as needed from `data`."""
    from .node_classes import ReadOnlyProcessWithReferenceProduct

    for ds in data:
        exchanges = ds.pop("exchanges")
        try:
            node = get_node(database=ds["database"], code=ds["code"])
            node._data.update(**ds)
        except UnknownObject:
            node = ReadOnlyProcessWithReferenceProduct(**ds)

        # .save() calls purge_expired_linked_readonly_processes(), which will delete existing
        # read-only processes (we have a new allocation and therefore a new mf_allocation_run_uuid)
        node.save()

        # Delete existing edges. Much easier than trying to find the right one to update.
        for edge in ExchangeDataset.select().where(
            ExchangeDataset.output_code == ds["code"],
            ExchangeDataset.output_database == ds["database"],
        ):
            edge.delete_instance()

        for exc_data in exchanges:
            exc = Exchange()
            exc.update(**exc_data)
            exc.output = node
            exc.save()


def product_as_process_name(data: List[dict]) -> None:
    """Some import formats, notably SimaPro, give a process name but then never use it - instead,
    they want linking only via products (there is not process name). So this function overrides
    the process name with the functional product name.

    Only applies when there is a single functional edge."""
    for ds in data:
        functional_excs = [exc for exc in ds["exchanges"] if exc.get("functional")]
        if len(functional_excs) == 1 and functional_excs[0].get("name"):
            ds["name"] = functional_excs[0]["name"]


def set_correct_process_type(dataset: Node) -> Node:
    """
    Change the `type` for an LCI process under certain conditions.

    Only will make changes if the following conditions are met:

    * `type` is `multifunctional` but the dataset is no longer multifunctional ->
        set to either `process` or `processwithreferenceproduct`
    * `type` is `None` or missing -> set to either `process` or `processwithreferenceproduct`
    * `type` is `process` but the dataset also includes an exchange which points to the same node
        -> `processwithreferenceproduct`

    """
    if dataset.get("type") not in (
        labels.chimaera_node_default,
        labels.process_node_default,
        "multifunctional",
        None,
    ):
        pass
    elif dataset.multifunctional:
        dataset["type"] = "multifunctional"
    elif any(exc.input == exc.output for exc in dataset.exchanges()):
        if dataset["type"] == "multifunctional":
            logger.debug(
                "Changed %s (%s) type from `multifunctional` to `%s`",
                dataset.get("name"),
                dataset.id,
                labels.chimaera_node_default,
            )
        dataset["type"] = labels.chimaera_node_default
    elif any(exc.get("functional") for exc in dataset.exchanges()):
        if dataset["type"] == "multifunctional":
            logger.debug(
                "Changed %s (%s) type from `multifunctional` to `%s`",
                dataset.get("name"),
                dataset.id,
                labels.process_node_default,
            )
        dataset["type"] = labels.process_node_default
    elif (
        # No production edges -> implicit self production -> chimaera
        not any(
            exc.get("type") in labels.technosphere_positive_edge_types
            for exc in dataset.exchanges()
        )
    ):
        dataset["type"] = labels.chimaera_node_default
    elif not dataset.get("type"):
        dataset["type"] = labels.process_node_default
    else:
        # No conditions for setting or changing type occurred
        pass

    return dataset


def purge_expired_linked_readonly_processes(dataset: Node) -> None:
    from .database import MultifunctionalDatabase

    if not dataset.get("mf_was_once_allocated"):
        return

    if dataset["type"] == "multifunctional":
        # Can have some readonly allocated processes which refer to non-functional edges
        for ds in MultifunctionalDatabase(dataset["database"]):
            if (
                ds["type"] in ("readonly_process",)
                and ds.get("mf_parent_key") == dataset.key
                and ds["mf_allocation_run_uuid"] != dataset["mf_allocation_run_uuid"]
            ):
                ds.delete()

        for exc in dataset.exchanges():
            try:
                exc.input
            except UnknownObject:
                exc.input = dataset
                exc.save()
                logger.debug(
                    "Edge to deleted readonly process redirected to parent process: %s",
                    exc,
                )

    else:
        # Process or chimaera process with one functional edge
        # Make sure that single functional edge is not referring to obsolete readonly process
        functional_edges = [exc for exc in dataset.exchanges() if exc.get("functional")]
        if not len(functional_edges) < 2:
            raise ValueError(
                f"Process marked monofunctional with type {dataset['type']} but has {len(functional_edges)} functional edges"
            )
        edge = functional_edges[0]
        if edge.input["type"] in (
            "readonly_process",
        ):  # TBD https://github.com/brightway-lca/multifunctional/issues/23
            # This node should be deleted; have to change to chimaera process with self-input
            logger.debug(
                "Edge to expired readonly process %s redirected to parent process %s",
                edge.input,
                dataset,
            )
            edge.input = dataset
            edge.save()
            if dataset["type"] != labels.chimaera_node_default:
                logger.debug(
                    "Change node type to chimaera: %s (%s)",
                    dataset,
                    dataset.id,
                )
                dataset["type"] = labels.chimaera_node_default

        # Obsolete readonly processes
        for ds in MultifunctionalDatabase(dataset["database"]):
            if ds["type"] in ("readonly_process",) and ds.get("mf_parent_key") == dataset.key:
                ds.delete()
