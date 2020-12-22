from .base import BaseMFClassifier


class ProductWasteClassifier(BaseMFClassifier):
    """If a database has exchanges labelled with ``product`` or ``waste``"""
    def find_functional_flows(cls, db_obj):
        pass
