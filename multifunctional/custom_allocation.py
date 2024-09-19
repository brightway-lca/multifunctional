import logging
from copy import copy
from dataclasses import dataclass
from enum import Enum
from numbers import Number
from typing import List, Union, Optional

from blinker import signal
from bw2data import Database, databases
from bw2data.backends import Exchange, Node
from bw2data.project import ProjectDataset, projects

from . import allocation_strategies
from .allocation import property_allocation

DEFAULT_ALLOCATIONS = set(allocation_strategies)


class MessageType(Enum):
    NONNUMERIC_PRODUCT_PROPERTY = "Non-numeric product property"
    NONNUMERIC_EDGE_PROPERTY = "Non-numeric edge property"
    NONNUMERIC_PROPERTY = "Non-numeric property"
    MISSING_PRODUCT_PROPERTY = "Missing product property"
    MISSING_EDGE_PROPERTY = "Missing edge property"
    MISSING_PROPERTY = "Missing property"
    ALL_VALID = "All properties found and have correct type"


@dataclass
class PropertyMessage:
    level: int  # logging levels WARNING and CRITICAL
    process_id: int  # Can get object with bw2data.get_node(id=process_id)
    product_id: int  # Can get object with bw2data.get_node(id=product_id)
    message_type: MessageType  # Computer-readable error message type
    message: str  # Human-readable error message


def _get_unified_properties(edge: Exchange):
    try:
        properties = copy(edge.input["properties"])
    except KeyError:
        properties = {}
    if "properties" in edge:
        properties.update(edge["properties"])
    return properties


def list_available_properties(database_label: str, target_process: Optional[Node] = None):
    """
    Get a list of all properties in a database, and check their suitability for use.

    `database_label`: String label of an existing database.
    `target_process`: Optional. If provided, property checks are done only for this process.
                      If not provided, checks are done for the whole database.

    Returns a list of tuples like `(label: str, message: MessageType)`. Note that
    `NONNUMERIC_PROPERTY` is worse than `MISSING_PROPERTY` as missing properties can be assumed to
    be zero, but non-numeric ones break everything.
    """
    if database_label not in databases:
        raise ValueError(f"Database `{database_label}` not defined in this project")
    if target_process is not None and target_process.get("database") != database_label:
        raise ValueError(f"Target process must be also in database `{database_label}`")

    results = []
    all_properties = set()

    for ds in filter(
        lambda x: x["type"] == "multifunctional", Database(database_label)
    ):
        for edge in filter(lambda x: x.get("functional"), ds.exchanges()):
            for key in _get_unified_properties(edge):
                all_properties.add(key)

    for label in all_properties:
        if target_process is None:
            check_results = check_property_for_allocation(database_label, label)
        else:
            check_results = check_property_for_process_allocation(target_process, label)
        if check_results is True:
            results.append((label, MessageType.ALL_VALID))
        elif any(
            msg.message_type
            in (
                MessageType.NONNUMERIC_PRODUCT_PROPERTY,
                MessageType.NONNUMERIC_EDGE_PROPERTY,
            )
            for msg in check_results
        ):
            results.append((label, MessageType.NONNUMERIC_PROPERTY))
        else:
            results.append((label, MessageType.MISSING_PROPERTY))

    return results


def check_property_for_process_allocation(
    process: Node, property_label: str, messages: Optional[List[PropertyMessage]] = None
) -> Union[bool, List[PropertyMessage]]:
    """
    Check that the given property is present for all functional edges in a given process.

    `process`: Multifunctional process `Node`.
    `property_label`: String label of the property to be used for allocation.

    If all the needed data is present, returns `True`.

    If there is missing data, returns a list of `PropertyMessage` objects.
    """
    if messages is None:
        messages = []

    if process['type'] != "multifunctional":
        return True

    for edge in filter(lambda x: x.get("functional"), process.exchanges()):
        properties = _get_unified_properties(edge)
        if (
            property_label not in properties
            and edge.input["type"] != "readonly_process"
        ):
            messages.append(
                PropertyMessage(
                    level=logging.WARNING,
                    process_id=process.id,
                    product_id=edge.input.id,
                    message_type=MessageType.MISSING_PRODUCT_PROPERTY,
                    message=f"""Product is missing a property value for `{property_label}`.
Missing values are treated as zeros.
Please define this property for the product:
    {edge.input}
Referenced by multifunctional process:
    {process}

""",
                )
            )
        elif property_label not in properties:
            messages.append(
                PropertyMessage(
                    level=logging.WARNING,
                    process_id=process.id,
                    product_id=edge.input.id,
                    message_type=MessageType.MISSING_EDGE_PROPERTY,
                    message=f"""Functional edge is missing a property value for `{property_label}`.
Missing values are treated as zeros.
Please define this property for the edge:
    {edge}
Found in multifunctional process:
    {process}

""",
                )
            )
        elif (
            not isinstance(properties[property_label], Number)
            or isinstance(properties[property_label], bool)
            and edge.input["type"] != "readonly_process"
        ):
            messages.append(
                PropertyMessage(
                    level=logging.CRITICAL,
                    process_id=process.id,
                    product_id=edge.input.id,
                    message_type=MessageType.NONNUMERIC_PRODUCT_PROPERTY,
                    message=f"""Found non-numeric value `{properties[property_label]}` in property `{property_label}`.
Please redefine this property for the product:
    {edge.input}
Referenced by multifunctional process:
    {process}

""",
                )
            )
        elif not isinstance(properties[property_label], Number) or isinstance(
            properties[property_label], bool
        ):
            messages.append(
                PropertyMessage(
                    level=logging.CRITICAL,
                    process_id=process.id,
                    product_id=edge.input.id,
                    message_type=MessageType.NONNUMERIC_EDGE_PROPERTY,
                    message=f"""Found non-numeric value `{properties[property_label]}` in property `{property_label}`.
Please redefine this property for the edge:
    {edge}
Found in multifunctional process:
    {process}

""",
                )
            )

    return messages or True


def check_property_for_allocation(
    database_label: str, property_label: str
) -> Union[bool, List[PropertyMessage]]:
    """
    Check that the given property is present for all functional edges in `multifunctional`
    processes.

    `database_label`: String label of an existing database.
    `property_label`: String label of the property to be used for allocation.

    If all the needed data is present, returns `True`.

    If there is missing data, returns a list of `PropertyMessage` objects.
    """
    if database_label not in databases:
        raise ValueError(f"Database `{database_label}` not defined in this project")

    db = Database(database_label)
    messages = []

    for ds in filter(lambda x: x["type"] == "multifunctional", db):
        check_property_for_process_allocation(ds, property_label, messages)

    return messages or True


def add_custom_property_allocation_to_project(
    property_label: str, normalize_by_production_amount: bool = True
) -> None:
    """
    Add a new property-based allocation method to `allocation_strategies`, and persist to a  project
    dataset.

    Note that this function **does not** mark the created function as the default allocation
    anywhere.

    `property_label` is a string giving a label in the functional products `properties` dictionary.
    You should probably use `check_property_for_allocation` to make sure this will work for the
    given database.

    `normalize_by_production_amount` is a bool flag for converting calculated allocation factors so
    that they sum to one.
    """
    if property_label in allocation_strategies:
        raise KeyError(f"`{property_label}` already defined in `allocation_strategies`")

    allocation_strategies[property_label] = property_allocation(
        property_label=property_label,
        normalize_by_production_amount=normalize_by_production_amount,
    )

    if "multifunctional.custom_allocations" not in projects.dataset.data:
        projects.dataset.data["multifunctional.custom_allocations"] = {}

    projects.dataset.data["multifunctional.custom_allocations"][property_label] = {
        "property_label": property_label,
        "normalize_by_production_amount": normalize_by_production_amount,
    }
    projects.dataset.save()


def update_allocation_strategies_on_project_change(
    project_dataset: ProjectDataset,
) -> None:
    """Fix the single dict `allocation_strategies` to reflect custom data for this project."""
    for obsolete in set(allocation_strategies).difference(DEFAULT_ALLOCATIONS):
        del allocation_strategies[obsolete]

    for key, value in project_dataset.data.get(
        "multifunctional.custom_allocations", {}
    ).items():
        allocation_strategies[key] = property_allocation(**value)


signal("bw2data.project_changed").connect(
    update_allocation_strategies_on_project_change
)
