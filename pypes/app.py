import asyncio

from .task import Task


class App:

    def __init__(self,
                 loop=None):
        """
        Initializes a class instance with an event loop, using the default event loop if none
        is provided.
        
        Args:
          loop: An asyncio event loop to run all child tasks off. If a loop is not provided, it will use the default event loop obtained
        from `asyncio.get_event_loop()`.
        """

        if not loop:
            loop = asyncio.get_event_loop()
        self.loop = loop

    def task(self, **kwargs):
        """
        A decorator to be used to wrap around an async generator method that takes
        a `pypes.Stream` argument. This returns a `Task` object to run independently
        when the pipelines starts.

        .. code-block:: python

          app = App()

          @app.task()
          async def task(input: pypes.Stream):
            async for i in input:
              print(i)
              yield i
        
        Returns:
          A decorator function returning a `Task` object.
        """

        def decorator(function):

            return Task(
                name=function.__name__,
                function=function,
                loop=self.loop,
                **kwargs
            )

        return decorator
