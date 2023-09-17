"""
    Default balancing will direct results emitted from the task 
    to *all* downstream tasks. This is a common use case, but 
    should only be used when downstream tasks won't conflict 
    when processing the same result.

    .. image:: _static/example_balance_default.png

    .. code-block:: python

        import pypes

        import asyncio

        import time

        app = pypes.App()


        @app.task(interval=0.01)
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

app = pypes.App()


@app.task(interval=0.01)
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
        print(f"speed: {proc_speed}/s, distribution: {task1_perc}% / {task2_perc}%", end="\r")
        yield


if __name__ == '__main__':

    pipeline = hundred_per_second \
               .map(task1, task2) \
               .reduce(receive)

    pipeline.run()