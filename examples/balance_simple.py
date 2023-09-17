"""
    This script demonstrates how balancing -- from the upstream 
    side -- differs from scaling -- from the downstream side. 
    Balancing is intended to be used to control where task results 
    are directed downstream. As demonstrated here, when a pipeline 
    task has multiple downstream tasks, it will rotate sending 
    results to all in a round-robin fashion. When all downstream 
    tasks process at the same rate, this should achieve maximum 
    throughput, but when they don't, there will be congestion built 
    in the slower-processing tasks. This script shows how that 
    buildup occurs when there's a single, slower task (task1) and 
    a scaled-up downstream task (task2) processing. The 
    slower-processing task (task1) will immediately build up a buffer 
    of incoming tasks where task2 will not.

    .. image:: _static/example_balance_simple.png

    .. code-block:: python

        import pypes

        import asyncio

        import time

        from pypes.balance import RoundRobinLoadBalancer

        app = pypes.App()


        @app.task(interval=0.01, balancer=RoundRobinLoadBalancer())
        async def hundred_per_second():
            return 0.1

        @app.task(scale=1)
        async def task1(input: pypes.Stream):
            async for sleep in input:
                await asyncio.sleep(5 * sleep)
                yield True, input.queue.qsize()

        @app.task(scale=50)
        async def task2(input: pypes.Stream):
            async for sleep in input:
                await asyncio.sleep(5 * sleep)
                yield False, input.queue.qsize()

        @app.task()
        async def receive(input: pypes.Stream):
            task1_proc = 0
            task1_size = 0
            task2_proc = 0
            task2_size = 0
            total_proc = 0
            total_size = 0
            start_time = time.monotonic()
            async for result, size in input:
                sample_time = time.monotonic()
                if result == True:
                    task1_proc += 1
                    task1_size = size
                elif result == False:
                    task2_proc += 1
                    task2_size = size
                else:
                    print("received bad data, returning")
                    return
                
                total_proc += 1
                total_size = task1_size + task2_size
                proc_speed = round(total_proc / (sample_time - start_time), 1)
                task1_perc = round(100 * (task1_proc + task1_size) / (total_proc + total_size), 1)
                task2_perc = round(100 * (task2_proc + task2_size) / (total_proc + total_size), 1)
                print(f"speed: {proc_speed}/s, distribution: {task1_perc}% / {task2_perc}%", end="\\r")
                yield


        if __name__ == '__main__':

            pipeline = every_second \\
                       .map(task1, task2) \\
                       .reduce(receive)

            pipeline.run()
"""
import pypes

import asyncio

import time

from pypes.balance import RoundRobinLoadBalancer

app = pypes.App()


@app.task(interval=0.01, balancer=RoundRobinLoadBalancer())
async def every_second():
    return 0.1

@app.task(scale=1)
async def task1(input: pypes.Stream):
    async for sleep in input:
        await asyncio.sleep(5 * sleep)
        yield True, input.queue.qsize()

@app.task(scale=50)
async def task2(input: pypes.Stream):
    async for sleep in input:
        await asyncio.sleep(5 * sleep)
        yield False, input.queue.qsize()

@app.task()
async def receive(input: pypes.Stream):
    task1_proc = 0
    task1_size = 0
    task2_proc = 0
    task2_size = 0
    total_proc = 0
    total_size = 0
    start_time = time.monotonic()
    async for result, size in input:
        sample_time = time.monotonic()
        if result == True:
            task1_proc += 1
            task1_size = size
        elif result == False:
            task2_proc += 1
            task2_size = size
        else:
            print("received bad data, returning")
            return
        
        total_proc += 1
        total_size = task1_size + task2_size
        proc_speed = round(total_proc / (sample_time - start_time), 1)
        task1_perc = round(100 * (task1_proc + task1_size) / (total_proc + total_size), 1)
        task2_perc = round(100 * (task2_proc + task2_size) / (total_proc + total_size), 1)
        print(f"speed: {proc_speed}/s, distribution: {task1_perc}% / {task2_perc}%", end="\r")
        yield


if __name__ == '__main__':

    pipeline = hundred_per_second \
               .map(task1, task2) \
               .reduce(receive)

    pipeline.run()