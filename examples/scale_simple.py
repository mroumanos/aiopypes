"""
    This script will start off with a timed task (task0) that 
    emits at a rate of 100/s, but is processed by a limiting 
    task (task2) can only process 10/s (by sleeping for 0.1s).
    As a result, task2 will scale both up and down based on 
    the volume of the queue that's storing the buffered unprocessed 
    items. The algorithm uses hyperbolic tangent, tanh(x), whose 
    scaling steps ranges from -max_step_size to +max_step_size, 
    equilibriating when the queue size is 0. A printing task 
    (task2) prints out the current size of the queue.

    .. image:: _static/example_scale_simple.png

    .. code-block:: python

        import asyncio
        import aiopypes

        app = aiopypes.App()


        @app.task(interval=0.01)
        async def task0():
            return 0.1

        @app.task(scaler=aiopypes.scale.TanhTaskScaler())
        async def task1(stream):
            async for s in stream:
                await asyncio.sleep(s)
                yield stream.queue.qsize()

        @app.task()
        async def task2(stream):
            async for s in stream:
                print('queued tasks: %d%s' % (s,' '*(len(str(s)))), end="\\r")
                yield

        if __name__ == '__main__':

            pipeline = task0.map(task1).map(task2)

            pipeline.run()
"""
import asyncio
import aiopypes

app = aiopypes.App()


@app.task(interval=0.01)
async def task0():
    return 0.1

@app.task(scaler=aiopypes.scale.TanhTaskScaler())
async def task1(stream):
    async for s in stream:
        await asyncio.sleep(s)
        yield stream.queue.qsize()

@app.task()
async def task2(stream):
    async for s in stream:
        print('queued tasks: %d%s' % (s,' '*(len(str(s)))), end="\r")
        yield

if __name__ == '__main__':

    pipeline = task0.map(task1).map(task2)

    pipeline.run()