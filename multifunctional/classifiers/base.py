from bw2data import Database, databases


class BaseMFClassifier:
    """Base multifunctional classifier that provides common functionality"""
    def label_functional_flows(cls, exchanges):
        pass

    def __call__(cls, db_obj):
        if isinstance(db_obj, str):
            if db_obj in databases:
                db_obj = Database(db_obj)
            else:
                raise ValueError(f"Given database '{db_obj}' doesn't exist")
        elif not isinstance(db_obj, Database):
            raise ValueError(f"Can't understand database input '{db_obj}'")
        functional_flows = cls.find_functional_flows(db_obj)
        cls.map_products(functional_flows)
        cls.map_virtual_activities()
        cls.label_functional_flows(functional_flows)
        db_obj.metadata['multifunctional'] = True
        # Flush metadata?
        db_obj.process()
