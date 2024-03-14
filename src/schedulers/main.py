#!/usr/bin/env python3

import sys
import asyncio

# ==========

# this code is inside the library

def coroutine(func):
    co = func.__code__
    func.__code__ = co.replace(co_flags=co.co_flags | 0x100)
    return func

@coroutine
def suspend():
    yield


async def retry(func, *args, **kwds):
    while True:
        try:
            coro = func(*args, **kwds)
            return await coro
        except:
            await suspend()
            print(f"error: {coro.__name__}(args={args}, kwds={kwds})", file=sys.stderr)
            continue

# ==========

# this code is outside the library

async def fail(n):
    """ sometimes tasks fail """
    import random
    if random.random() < 0.99:
        raise RuntimeError("no")
    return n

async def main():
    coros = [retry(fail, n) for n in range(100)]
    return await asyncio.gather(*coros)

results = asyncio.run(main())

