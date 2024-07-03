from typing import Optional, Union

from bw2data import databases, get_node, labels
from bw2data.backends.proxies import Activity
from loguru import logger

from .edge_classes import ReadOnlyExchanges
from .errors import NoAllocationNeeded


class MaybeMultifunctionalProcess(Activity):
    """Default node class for nodes in `MultifunctionalDatabase`.

    Sets flag on save if multifunctional."""

    def functional_edges(self):
        return (edge for edge in self.exchanges if edge.get("functional"))

    def nonfunctional_edges(self):
        return (edge for edge in self.exchanges if not edge.get("functional"))

    @property
    def has_multiple_functional_edges(self):
        return len(list(self.functional_edges)) > 1

    def save(self):
        if self.has_multiple_functional_edges:
            self["type"] = "multifunctional"
            logger.info(
                "Process {p} is multifunctional - please reload with `get_node(id={i})`",
                p=repr(self),
                i=self.id,
            )
        else:
            self["type"] = "process"
        super().save()


class MultifunctionalProcess(MaybeMultifunctionalProcess):
    def allocate(
        self, strategy_label: Optional[str] = None
    ) -> Union[None, NoAllocationNeeded]:
        from . import allocation_strategies

        if strategy_label is None:
            if self.get("default_allocation"):
                strategy_label = self.get("default_allocation")
            else:
                strategy_label = databases[self["database"]].get("default_allocation")

        if not strategy_label:
            raise ValueError(
                "Can't find `default_allocation` in input arguments, or process/database metadata."
            )
        elif strategy_label not in allocation_strategies:
            raise KeyError(
                f"Given strategy label {strategy_label} not in `allocation_strategies`"
            )

        if self.get("skip_allocation"):
            return NoAllocationNeeded
        elif not self.has_multiple_functional_edges:
            return NoAllocationNeeded

        logger.debug(
            "Allocating {p} (id: {i}) with strategy {s}",
            p=repr(self),
            i=self.id,
            s=strategy_label,
        )

    def rp_exchange(self):
        raise ValueError("Multifunctional processes have no reference product")

    def save(self):
        if self.has_multiple_functional_edges:
            self["type"] = "multifunctional"
        else:
            self["type"] = "process"
        super().save()


class ReadOnlyProcessWithReferenceProduct(MaybeMultifunctionalProcess):
    def __setitem__(self, key, value):
        raise NotImplemented(
            "This node is read only. Update the corresponding multifunctional process."
        )

    def parent(self):
        """Return the `MultifunctionalProcess` which generated this node object"""
        return get_node(id=self["multifunctional_parent_id"])

    def save(self):
        self["type"] = "readonly_process"
        if not self.get("multifunctional_parent_id"):
            raise ValueError("Must specify `multifunctional_parent_id`")
        super().save()

    def copy(self, *args, **kwargs):
        raise NotImplemented(
            "This node is read only. Update the corresponding multifunctional process."
        )

    def new_edge(self, **kwargs):
        raise NotImplemented(
            "This node is read only. Update the corresponding multifunctional process."
        )

    def delete(self):
        raise NotImplemented(
            "This node is read only. Update the corresponding multifunctional process."
        )

    def exchanges(self):
        return super().exchanges(exchanges_class=ReadOnlyExchanges)

    def technosphere(self):
        return super().technosphere(exchanges_class=ReadOnlyExchanges)

    def biosphere(self):
        return super().biosphere(exchanges_class=ReadOnlyExchanges)

    def production(self, include_substitution=False):
        return super().production(
            include_substitution=include_substitution, exchanges_class=ReadOnlyExchanges
        )

    def substitution(self):
        return super().substitution(exchanges_class=ReadOnlyExchanges)

    def upstream(self, kinds=labels.technosphere_negative_edge_types):
        return super().upstream(kinds=kinds, exchanges_class=ReadOnlyExchanges)