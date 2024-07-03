def prepare_multifunctional_for_writing(data: dict) -> dict:
    """Add `input` values to each functional exchange if not already present."""
    for key, ds in data.items():
        for exc in ds.get("exchanges", []):
            if exc.get("functional") and "input" not in exc:
                exc["input"] = key
    return data
