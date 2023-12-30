API
=============

.. code-block:: python

   import asyncio
   import aiopypes

   app = aiopypes.App()

   @app.task(interval=0.01)
   async def task0():
      return 0.1

   @app.task(scaler=aiopypes.TanhTaskScaler())
   async def task1(stream):
      async for s in stream:
         yield await asyncio.sleep(s)

   pipeline = task0 \
              .map(task1)

   # task1 will scale up to
   # approximately 10 tasks
   pipeline.run()

.. image:: _static/pipeline_simple.png

app
----------------

.. automodule:: aiopypes.app
   :members:
   :undoc-members:
   :show-inheritance:

balance
--------------------

.. automodule:: aiopypes.balance
   :members:
   :undoc-members:
   :show-inheritance:

pipeline
---------------------

.. automodule:: aiopypes.pipeline
   :members:
   :undoc-members:
   :show-inheritance:

scale
------------------

.. automodule:: aiopypes.scale
   :members:
   :undoc-members:
   :show-inheritance:

signal
-------------------

.. automodule:: aiopypes.signal
   :members:
   :undoc-members:
   :show-inheritance:

stream
-------------------

.. automodule:: aiopypes.stream
   :members:
   :undoc-members:
   :show-inheritance:

task
-----------------

.. automodule:: aiopypes.task
   :members:
   :undoc-members:
   :show-inheritance:
