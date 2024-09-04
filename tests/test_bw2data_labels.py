from bw2data import labels
from bw2data.subclass_mapping import (
    DATABASE_BACKEND_MAPPING,
    NODE_PROCESS_CLASS_MAPPING,
)
from bw2data.tests import bw2test


@bw2test
def test_labels_updated():
    assert "readonly_process" in labels.process_node_types
    assert "readonly_process" in labels.node_types


@bw2test
def test_mappings_updated():
    assert "multifunctional" in DATABASE_BACKEND_MAPPING
    assert "multifunctional" in NODE_PROCESS_CLASS_MAPPING
