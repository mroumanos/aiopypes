import asyncio

from .signal import Signal


class Stream:
    """_summary_
    """

    def __init__(self,
                 loop: asyncio.BaseEventLoop = None):
        """_summary_

        Args:
            loop (asyncio.BaseEventLoop, optional): _description_. Defaults to None.
        """
        self.loop = loop
        self.queue = asyncio.Queue(loop=loop)

    async def enqueue(self, val: object) -> None:
        """_summary_

        Args:
            val (object): _description_

        Returns:
            _type_: _description_
        """
        return await self.queue.put(val)

    async def dequeue(self) -> object:
        """_summary_

        Returns:
            _type_: _description_
        """
        return await self.queue.get()

    def __aiter__(self):
        return self

    async def __anext__(self):
        """_summary_

        Raises:
            StopAsyncIteration: _description_

        Returns:
            _type_: _description_
        """
        o = await self.dequeue()

        if o == Signal.TERM:
            raise StopAsyncIteration
        else:
            return o