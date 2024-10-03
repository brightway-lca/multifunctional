import bw2data as bd
from bw2data.tests import bw2test

from multifunctional import MultifunctionalDatabase


@bw2test
def test_node_creation():
    db = MultifunctionalDatabase("test database")
    db.register(default_allocation="price")

    node = db.new_node()
    node['name'] = 'foo'
    node['type'] = 'product'
    node.save()

    for node in db:
        assert node['name'] == 'foo'
        assert node['database'] == "test database"
        assert node['code']
        assert node['type'] == 'product'


@bw2test
def test_node_creation_default_label():
    db = MultifunctionalDatabase("test database")
    db.register(default_allocation="price")

    node = db.new_node()
    node['name'] = 'foo'
    node.save()

    for node in db:
        assert node['name'] == 'foo'
        assert node['database'] == "test database"
        assert node['code']
        assert node['type'] == bd.labels.process_node_default


@bw2test
def test_node_creation_multifunctional():
    db = MultifunctionalDatabase("test database")
    db.register(default_allocation="price")

    node = db.new_node()
    node['name'] = 'foo'
    node['unit'] = 'bar'
    node.new_edge(input=node, functional=True, amount=0.1, type="technosphere").save()
    node.new_edge(input=node, functional=True, amount=1., type="production").save()
    node.save()

    for node in db:
        assert node['name'] == 'foo'
        assert node['database'] == "test database"
        assert node['code']
        assert node['type'] == "multifunctional"
