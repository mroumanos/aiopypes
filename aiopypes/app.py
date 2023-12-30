import asyncio

from .task import Task


class App:

    def __init__(self):
        """
        Initializes a class instance. Since event loop is no longer required, this is
        an empty constructor.
        """
        pass

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
                **kwargs
            )

        return decorator
