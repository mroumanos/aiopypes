import asyncio


class Pipeline:

    def __init__(self,
                 loop: asyncio.BaseEventLoop,
                 tasks: list = []):
        """
        The `__init__` function initializes an object with a given event loop and a list of tasks, and
        sets up some instance variables.
        
        Args:
          loop (asyncio.BaseEventLoop): The `loop` parameter is an instance of the
        `asyncio.BaseEventLoop` class. It represents the event loop that drives the execution of
        asynchronous tasks in your code. The event loop is responsible for scheduling and executing
        coroutines, callbacks, and other asynchronous operations.
          tasks (list): The `tasks` parameter is a list of tasks that will be executed by the code. Each
        task is represented as a dictionary with various properties.
        """
        self.loop = loop
        self.scope = []
        self.tasks = []
        self.jobs = []
        self.lock = asyncio.Lock(loop=loop)
        if tasks:
            for task in tasks:
                t = task.copy()
                t.lock = self.lock
                self.tasks.append(t)
                self.scope.append(t)

    def map(self, *tasks, routes: list = []):
        """
        The `map` function takes a list of tasks and routes, creates new tasks based on the input tasks,
        and adds them to the scope.
        
        Args:
          routes (list): The `routes` parameter is a list that specifies the routes that the tasks should
        follow. It is an optional parameter and its default value is an empty list.
        
        Returns:
          The `map` method is returning `self`.
        """

        new_scope = []

        for scope in self.scope:
            for task in tasks:
                t = task.copy()
                t.lock = self.lock
                t.routes = routes
                new_scope.append(t)
                self.tasks.append(t)
                scope.output.append(t)
        
        self.scope = new_scope
        
        return self

    def reduce(self, *tasks, routes: list = []):
        """
        The `reduce` function adds tasks to a pipeline and connects them together by setting their output to
        be the input for the next task.
        
        Args:
          routes (list): The `routes` parameter is a list that specifies the routing of the output of each
        task to the input of the next task in the pipeline. Each element in the `routes` list represents a
        connection between two tasks. The format of each element is `(task_index_1, task_index_2
        
        Returns:
          The `reduce` method returns `self`, which allows for method chaining.
        """
        new_scope = []

        for task in tasks:
            t = task.copy()
            t.lock = self.lock
            t.routes = routes
            new_scope.append(t)
            self.tasks.append(t)
            for scope in self.scope:
                scope.output.append(t)
        
        self.scope = new_scope

        return self

    def merge(self, *pipelines):
        """
        The `merge` function takes multiple pipelines as input and merges their tasks into a single
        pipeline.
        
        Returns:
          The `merge` method is returning `self`, which refers to the instance of the class that the method
        is being called on.
        """

        for pipeline in pipelines:
            for task in pipeline.tasks:
                self.tasks.append(task)
                task.lock = self.lock #  add killswitch
        
        return self
    
    async def graph(self):
        """
        The above function uses the curses library to display information about tasks and their runners in
        a terminal window.
        """
        import curses
        stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()

        """
        [0] task1 (30)
         |
         *--> [5] task2 (30)
         *--> [10] task3 (30)
               |
               *--> [10] task4 (1)
        """
        try:
            while not self.lock.locked():
                pointer = set()
                pointer.add(self.tasks[0])
                v_offset = 0
                h_offset = 0
                while pointer:
                    new_pointer = set()
                    if v_offset > 0:
                        stdscr.addstr(v_offset, h_offset-6, "|")
                        v_offset += 1
                    for task in list(pointer):
                        if h_offset > 0:
                            stdscr.addstr(v_offset, h_offset-6, "*-->")
                        stdscr.addstr(v_offset, h_offset, f"[{task.input.queue.qsize()}] {task.name} (n={len(task.runners)})")
                        for o in task.output:
                            new_pointer.add(o)
                        v_offset += 1
                    h_offset += 7
                    pointer = new_pointer
                stdscr.addstr(v_offset, h_offset, f"\n")
                stdscr.refresh()
                await asyncio.sleep(1)
        finally:
            curses.echo()
            curses.nocbreak()
            curses.endwin()

    def run(self, graph: bool = False):
        """
        The `run` function runs a series of tasks asynchronously and handles graceful closure of the tasks.
        """
        try:
            for task in self.tasks:
                job = self.loop.create_task(task.run_async())
                self.jobs.append(job)
            
            if graph:
                job = self.loop.create_task(self.graph())
                self.jobs.append(job)
            print("Application started (press Ctrl+C to close)")
            self.loop.run_forever()
        except KeyboardInterrupt:
            print("Exiting from program...")
        finally:
            try:
                print("Closing tasks gracefully")
                self.loop.run_until_complete(self.lock.acquire())
                closures = [asyncio.wait_for(job, timeout=10) for job in self.jobs]
                self.loop.run_until_complete(asyncio.gather(*closures))
                print("All tasks closed gracefully")
            except asyncio.TimeoutError:
                print("Failed to close jobs gracefully, force closing")
                for job in self.jobs:
                    job.cancel()
                waits = [asyncio.wait_for(job, timeout=10) for job in self.jobs]
                self.loop.run_until_complete(asyncio.gather(*waits))
                print("Jobs force closed")