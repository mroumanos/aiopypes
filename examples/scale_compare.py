"""
    This script demonstrates the benefit of autoscaling in *aiopypes*. 
    Similar to the simple script, a timed task (hundred_per_second) 
    emits results at a rate faster than the downstream tasks (tortoise, 
    hare) can initially process. The hare immediately scaled to the 
    projected number of tasks needed (10), whereas the tortoise starts 
    with just 1. However, the tortoise can catch up with the hare 
    after the scaler (hyperbolic-tangent scaler) scales up to the 
    number of tasks needed. The final task (score) prints out the 
    relative positions of the two.

    .. image:: _static/example_scale_compare.png

    .. code-block:: python

        import aiopypes

        import asyncio

        app = aiopypes.App()


        @app.task(interval=0.01)
        async def hundred_per_second():
            return 0.1

        @app.task(scaler=aiopypes.scale.TanhTaskScaler())
        async def tortoise(input: aiopypes.Stream):
            async for sleep in input:
                await asyncio.sleep(sleep)
                yield True

        @app.task(scale=10)
        async def hare(input: aiopypes.Stream):
            async for sleep in input:
                await asyncio.sleep(sleep)
                yield False

        @app.task()
        async def score(input: aiopypes.Stream):
            tortoise_pos = 0
            hare_pos = 0
            async for result in input:
                if result:
                    tortoise_pos += 1
                else:
                    hare_pos += 1

                max_index = 50
                track = ['-' for _ in range(max_index + 1)]
                if hare_pos > tortoise_pos:
                    hare_index = max_index
                    tortoise_index = int(max_index * tortoise_pos / hare_pos)
                elif tortoise_pos > hare_pos:
                    tortoise_index = max_index
                    hare_index = int(max_index * hare_pos / tortoise_pos)
                else:
                    tortoise_index = max_index
                    hare_index = max_index

                if tortoise_index == hare_index:
                    track[tortoise_index] = 'X'
                    track[hare_index] = 'X'
                else:
                    track[tortoise_index] = 'T'
                    track[hare_index] = 'H'
                print(f"tortoise={tortoise_pos}, hare={hare_pos}: {''.join(track)}", end="\\r")
                yield


        if __name__ == '__main__':

            pipeline = hundred_per_second \\
                       .map(tortoise, hare) \\
                       .reduce(score)

            pipeline.run()
"""
import aiopypes

import asyncio

app = aiopypes.App()


@app.task(interval=0.01)
async def hundred_per_second():
    return 0.1

@app.task(scaler=aiopypes.scale.TanhTaskScaler())
async def tortoise(input: aiopypes.Stream):
    async for sleep in input:
        await asyncio.sleep(sleep)
        yield True

@app.task(scale=30)
async def hare(input: aiopypes.Stream):
    async for sleep in input:
        await asyncio.sleep(sleep)
        yield False

@app.task()
async def score(input: aiopypes.Stream):
    tortoise_pos = 0
    hare_pos = 0
    async for result in input:
        if result:
            tortoise_pos += 1
        else:
            hare_pos += 1

        max_index = 50
        track = ['-' for _ in range(max_index + 1)]
        if hare_pos > tortoise_pos:
            hare_index = max_index
            tortoise_index = int(max_index * tortoise_pos / hare_pos)
        elif tortoise_pos > hare_pos:
            tortoise_index = max_index
            hare_index = int(max_index * hare_pos / tortoise_pos)
        else:
            tortoise_index = max_index
            hare_index = max_index

        if tortoise_index == hare_index:
            track[tortoise_index] = 'X'
            track[hare_index] = 'X'
        else:
            track[tortoise_index] = 'T'
            track[hare_index] = 'H'
        print(f"tortoise={tortoise_pos}, hare={hare_pos}: {''.join(track)}", end="\r")
        yield


if __name__ == '__main__':

    pipeline = hundred_per_second \
               .map(tortoise, hare) \
               .reduce(score)

    pipeline.run()