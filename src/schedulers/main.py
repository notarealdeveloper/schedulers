#!/usr/bin/env python3

import asyncio

# ==========

# this code is inside the library

def retry(coro, times=float('inf')):
    n = 0
    while n < times:
        try:
            return await coro
        except:
            n += 1
            continue

# ==========

# this code is outside the library

async def failer(n):
    """ sometimes tasks fail """
    import random
    if random.random() < 0.99:
        raise RuntimeError("no")

# ==========
