"""
    This combines the congestion-based load balancing and 
    round-robin load balancing script in one, to directly 
    compare the two approaches.

    .. code-block:: python

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

            class Observer:
                task1_proc = 0
                task1_size = 0
                task2_proc = 0
                task2_size = 0
                total_proc = 0
                total_size = 0

                def __init__(self, start_time):
                    self.start_time = start_time
                    self.sample_time = None
                    self.proc_speed = None
                    self.task1_perc = None
                    self.task2_perc = None

                def proc(self, task, size):
                    if task == 1:
                        self.task1_proc += 1
                        self.task1_size = size
                    elif task == 2:
                        self.task2_proc += 1
                        self.task2_size = size
                    else:
                        raise Exception("received bad data, returning")
                    
                    self.total_proc += 1
                    self.total_size = self.task1_size + self.task2_size
                    self.sample_time = time.monotonic()

                    self.proc_speed = round(self.total_proc / (self.sample_time - self.start_time), 1)
                    self.task1_perc = round(100 * (self.task1_proc + self.task1_size) / (self.total_proc + self.total_size), 1)
                    self.task2_perc = round(100 * (self.task2_proc + self.task2_size) / (self.total_proc + self.total_size), 1)

                def stats(self):
                    return self.proc_speed, self.task1_perc, self.task2_perc
            

            start_time = time.monotonic()
            a_observer = Observer(start_time)
            b_observer = Observer(start_time)

            print("Load Balancing Performance: RoundRobin vs. Congestion (speed,dist)")

            async for router, task, size in input:

                if router == 'A':
                    a_observer.proc(task, size)
                elif router == 'B':
                    b_observer.proc(task, size)
                
                a_speed, a_1_perc, a_2_perc = a_observer.stats()
                b_speed, b_1_perc, b_2_perc = b_observer.stats()

                print(f"RoundRobin: {a_speed}/s, {a_1_perc}/{a_2_perc}%"
                    f" | Congestion: {b_speed}/s, {b_1_perc}/{b_2_perc}%", end="\\r")
                yield


        if __name__ == '__main__':

            pipeline = every_second \\
                       .map(route_a, route_b) \\
                       .map(task1, task2) \\
                       .reduce(receive)

            pipeline.run()
"""
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

    class Observer:
        task1_proc = 0
        task1_size = 0
        task2_proc = 0
        task2_size = 0
        total_proc = 0
        total_size = 0

        def __init__(self, start_time):
            self.start_time = start_time
            self.sample_time = None
            self.proc_speed = None
            self.task1_perc = None
            self.task2_perc = None

        def proc(self, task, size):
            if task == 1:
                self.task1_proc += 1
                self.task1_size = size
            elif task == 2:
                self.task2_proc += 1
                self.task2_size = size
            else:
                raise Exception("received bad data, returning")
            
            self.total_proc += 1
            self.total_size = self.task1_size + self.task2_size
            self.sample_time = time.monotonic()

            self.proc_speed = round(self.total_proc / (self.sample_time - self.start_time), 1)
            self.task1_perc = round(100 * (self.task1_proc + self.task1_size) / (self.total_proc + self.total_size), 1)
            self.task2_perc = round(100 * (self.task2_proc + self.task2_size) / (self.total_proc + self.total_size), 1)

        def stats(self):
            return self.proc_speed, self.task1_perc, self.task2_perc
    

    start_time = time.monotonic()
    a_observer = Observer(start_time)
    b_observer = Observer(start_time)

    print("Load Balancing Performance: RoundRobin vs. Congestion (speed,dist)")

    async for router, task, size in input:

        if router == 'A':
            a_observer.proc(task, size)
        elif router == 'B':
            b_observer.proc(task, size)
        
        a_speed, a_1_perc, a_2_perc = a_observer.stats()
        b_speed, b_1_perc, b_2_perc = b_observer.stats()

        print(f"RoundRobin: {a_speed}/s, {a_1_perc}/{a_2_perc}%"
              f" | Congestion: {b_speed}/s, {b_1_perc}/{b_2_perc}%", end="\r")
        yield


if __name__ == '__main__':

    pipeline = every_second \
               .map(route_a, route_b) \
               .map(task1, task2) \
               .reduce(receive)

    pipeline.run()