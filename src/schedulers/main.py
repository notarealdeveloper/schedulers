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
    coros = [wrap(func(*args, **kwds)) for (func, args, kwds) in jobs]
    results += await asyncio.gather(*coros)
    return results

async def run_rate_limited(jobs, jobs_per_sec):
    results = []
    import time
    from collections import deque
    n = jobs_per_sec
    times = deque([], maxlen=n)
    sem = asyncio.Semaphore(n)
    global_start = time.time()
    num_done = 0
    async def limiter(coro, k):
        nonlocal num_done
        async with sem:
            result = await coro
            num_done += 1
            while True:
                total_secs = time.time() - global_start
                if (num_done < jobs_per_sec*total_secs):
                    break
                await asyncio.sleep(0)
        return result
    coros = [limiter(func(*args, **kwds), k) for k, (func, args, kwds) in enumerate(jobs)]
    results += await asyncio.gather(*coros)
    return results

# ==========

# this code is outside the library

async def fail(n):
    """ sometimes tasks fail """
    import random
    await asyncio.sleep(0)
    print(f"fail({n}): entering")
    if random.random() < 0.99:
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
    jobs = [(retry, (fail, n), {}) for n in range(100)]
    return await run_streamed(jobs, 10)

async def main():
    jobs = [(retry, (fail, n), {}) for n in range(100)]
    return await run_rate_limited(jobs, jobs_per_sec=10)

results = asyncio.run(main())

