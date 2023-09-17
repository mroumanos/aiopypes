import pypes

import asyncio

import time

from pypes.balance import CongestionLoadBalancer, RoundRobinLoadBalancer


app = pypes.App()

@app.task(interval=0.01)
async def every_second():
    return 0.1


@app.task(balancer=RoundRobinLoadBalancer())
async def route_a(input: pypes.Stream):
    async for sleep in input:
        yield 'A', sleep

@app.task(balancer=CongestionLoadBalancer())
async def route_b(input: pypes.Stream):
    async for sleep in input:
        yield 'B', sleep

@app.task(scale=1)
async def task1(input: pypes.Stream):
    async for router, sleep in input:
        await asyncio.sleep(5 * sleep)
        yield router, 1, input.queue.qsize()

@app.task(scale=50)
async def task2(input: pypes.Stream):
    async for router, sleep in input:
        await asyncio.sleep(5 * sleep)
        yield router, 2, input.queue.qsize()

@app.task()
async def receive(input: pypes.Stream):

    async for router, task, size in input:
        yield


if __name__ == '__main__':

    pipeline = every_second \
               .map(route_a, route_b) \
               .map(task1, task2) \
               .reduce(receive)

    pipeline.run(graph=True)