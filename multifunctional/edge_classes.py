from bw2data.backends.proxies import Exchange, Exchanges


class ReadOnlyExchange(Exchange):
    def save(self):
        raise NotImplemented("Read-only exchange")

    def delete(self):
        raise NotImplemented("Read-only exchange")

    def _set_output(self, value):
        raise NotImplemented("Read-only exchange")

    def _set_input(self, value):
        raise NotImplemented("Read-only exchange")

    def __setitem__(self, key, value):
        raise NotImplemented("Read-only exchange")


class ReadOnlyExchanges(Exchanges):
    def delete(self):
        raise NotImplemented("Exchanges are read-only")

    def __iter__(self):
        for obj in self._get_queryset():
            yield ReadOnlyExchange(obj)
