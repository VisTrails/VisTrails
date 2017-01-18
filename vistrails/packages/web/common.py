import random


class _Finalizer(object):
    def __init__(self):
        self._funcs = set()

    def add_function(self, func):
        self._funcs.add(func)

    def finalize(self):
        for func in self._funcs:
            func()
        self._funcs = set()

finalizer = _Finalizer()


def random_strings():
    """Generates unique sequences of characters.
    """
    characters = ("abcdefghijklmnopqrstuvwxyz"
                  "0123456789")
    characters = [characters[i:i + 1] for i in xrange(len(characters))]
    rng = random.Random()
    while True:
        letters = [rng.choice(characters) for i in xrange(10)]
        yield ''.join(letters)

random_strings = random_strings()
