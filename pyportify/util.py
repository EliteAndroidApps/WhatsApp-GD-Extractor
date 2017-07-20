import itertools
import sys


def uprint(*objects, sep=' ', end='\n', file=sys.stdout):
    enc = file.encoding
    if enc == 'UTF-8':
        print(*objects, sep=sep, end=end, file=file)
    else:
        def f(obj):
            return str(obj) \
                .encode(enc, errors='backslashreplace') \
                .decode(enc)
        print(*map(f, objects), sep=sep, end=end, file=file)


def grouper(iterable, n):
    it = iter(iterable)
    while True:
        chunk = tuple(itertools.islice(it, n))
        if not chunk:
            return
        yield chunk
