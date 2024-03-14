#!/usr/bin/env python3

import sys
import asyncio

# ==========

# singular
# these functions upgrade *individual* coroutines
# * retry me on failure
# * print before and after calling me
# * these are *decorators for coroutine functions*

async def retry(func, *args, **kwds):
    while True:
        try:
            coro = func(*args, **kwds)
            return await coro
        except:
            continue

# ==========

# plural
# these functions upgrade the process of running a *list* of coroutines
# * run all at once
# * run in batches and block until each is done

async def run(jobs):
    coros = [func(*args, **kwds) for (func, args, kwds) in jobs]
    return await asyncio.gather(*coros)

async def run_batched(jobs, n):
    results = []
    while jobs:
        batch = jobs[:n]
        coros = [func(*args, **kwds) for (func, args, kwds) in batch]
        results += await asyncio.gather(*coros)
        jobs = jobs[n:]
    return results

async def run_streamed(jobs, n):
    results = []
    sem = asyncio.Semaphore(n)
    async def wrap(coro):
        async with sem:
            return await coro
    while jobs:
        batch = jobs[:n]
        coros = [wrap(func(*args, **kwds)) for (func, args, kwds) in batch]
        results += await asyncio.gather(*coros)
        jobs = jobs[n:]
    return results

# ==========

# this code is outside the library

async def fail(n):
    """ sometimes tasks fail """
    import random
    await asyncio.sleep(0)
    print(f"fail({n}): entering")
    if random.random() < 0.50:
        print(f"fail({n}): failed")
        raise RuntimeError("no")
    print(f"fail({n}): finished")
    return n

async def succeed(n):
    """ sometimes tasks succeed """
    print(f"succeed({n}): entering")
    await asyncio.sleep(0)
    print(f"succeed({n}): finished")
    return n

async def main():
    jobs = [(retry, (fail, n), {}) for n in range(100)]
    return await run(jobs)

async def main():
    jobs = [(retry, (fail, n), {}) for n in range(100)]
    return await run_batched(jobs, 10)

async def main():
    from slower import Slower
    seconds = 1
    async def wrap(coro, s):
        await s.acquire()
        return await coro
    async with Slower(5, seconds) as s:
        #jobs = [(retry, (fail, n), {}) for n in range(100)]
        jobs = [wrap(fail(n), s) for n in range(100)]
        return await asyncio.gather(*jobs)

results = asyncio.run(main())

