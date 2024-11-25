from time import perf_counter
from typing import Any
from multifunctional import MultifunctionalDatabase, check_property_for_allocation, list_available_properties
from bw2data.tests import bw2test


@bw2test
def test_check_property_for_allocation_failure_boolean():
    DATA_REPEAT = 15
    data = {}
    for i in range(DATA_REPEAT):
        data.update(_data(i))

    print(f"\n\nDATA SIZE: {len(data)}\n")

    db = MultifunctionalDatabase("internal")
    db.register(default_allocation="price")
    db.write(data)

    # Increases with a check_property_for_allocation time for every new property
    s = perf_counter()
    result = list_available_properties("internal")
    e = perf_counter()
    print(f"List time: {(e-s)*1000:.2f} {len(result)=}")

    # Relatively fast
    s = perf_counter()
    result = check_property_for_allocation("internal", "mass")
    e = perf_counter()
    print(f"Check time: {(e-s)*1000:.2f}")

    # About 3 times slower due to the message composition for the missing properties
    s = perf_counter()
    result = check_property_for_allocation("internal", "missing3")
    e = perf_counter()
    print(f"Check time: {(e-s)*1000:.2f}")

    # Very slow, 500ms on the sample db in AB. Not affected by missing properties.
    s = perf_counter()
    db.process()
    e = perf_counter()
    print(f"Process time: {(e-s)*1000:.2f}")

def _data(index: int) -> dict[tuple[str, str], Any]:
    return {
        ("internal", f"{index}.a"): {
            "name": f"{index}.flow - a",
            "unit": "kg",
            "type": "emission",
            "categories": ("air",),
            "properties": {
                "missing2": 7,
            },
        },
        ("internal", f"{index}.😼"): {
            "type": "product",
            "name": f"{index}.meow",
            "unit": "kg",
            "properties": {
                "price": 12,
                "mass": 4,
                "missing1": 4,
            },
        },
        ("internal", f"{index}.🐶"): {
            "type": "product",
            "name": f"{index}.woof",
            "unit": "kg",
        },
        ("internal", f"{index}.1"): {
            "name": f"{index}.process - 1",
            "location": "first",
            "type": "multifunctional",
            "exchanges": [
                {
                    "functional": True,
                    "type": "production",
                    "input": ("internal", f"{index}.😼"),
                    "amount": 4,
                    "properties": {
                        "price": 7,
                        "mass": 6,
                    },
                },
                {
                    "functional": True,
                    "type": "production",
                    "name": f"{index}.second product - 1",
                    "unit": "megajoule",
                    "desired_code": f"{index}.first - generated",
                    "amount": 6,
                    "properties": {
                        "price": 12,
                        "mass": 4,
                        "missing3": 2,
                    },
                },
                {
                    "type": "biosphere",
                    "name": f"{index}.flow - a",
                    "amount": 10,
                    "input": ("internal", f"{index}.a"),
                },
            ],
        },
        ("internal", f"{index}.2"): {
            "name": f"{index}.process - 2",
            "code": f"{index}.2",
            "location": "second",
            "type": "multifunctional",
            "exchanges": [
                {
                    "functional": True,
                    "type": "production",
                    "input": ("internal", f"{index}.🐶"),
                    "amount": 40,
                    "properties": {
                        "price": 2.5,
                        "mass": 6,
                    },
                },
                {
                    "functional": True,
                    "type": "production",
                    "name": f"{index}.second product - 1",
                    "desired_code": f"{index}.second - generated",
                    "unit": "megajoule",
                    "amount": 50,
                    "properties": {
                        "price": 2,
                        "mass": 4,
                    },
                },
                {
                    "type": "technosphere",
                    "amount": 10,
                    "input": ("internal", f"{index}.first - generated"),
                },
                {
                    "type": "technosphere",
                    "amount": 100,
                    "input": ("internal", f"{index}.😼"),
                },
            ],
        },
    }
