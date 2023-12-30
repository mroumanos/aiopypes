![a-i-o-p-y-p-e-s](https://raw.githubusercontent.com/mroumanos/aiopypes/e4af0f031ca56ac53c3e9ab15fd7c15bab084030/docs/_static/logo.png)

<h3 align="center">(pronounced "a-i-o-pipes")</h3>

<div align="center">

[![Status](https://img.shields.io/badge/status-active-success.svg)]()
[![GitHub Issues](https://img.shields.io/github/issues/mroumanos/aiopypes)](https://github.com/mroumanos/aiopypes/issues)
[![GitHub Pull Requests](https://img.shields.io/github/issues-pr/mroumanos/aiopypes)](https://github.com/mroumanos/aiopypes/pulls)
[![License](https://img.shields.io/badge/license-MIT-blue.svg)](/LICENSE)

</div>

---

<p align="center"> Scalable asyncio pipelines in Python, made easy.
    <br> 
</p>

## 📝 Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Built Using](#built_using)
- [TODO](#todo)
- [Contributing](../CONTRIBUTING.md)
- [Authors](#authors)
- [Acknowledgments](#acknowledgement)

## 🧐 About <a name = "about"></a>

This package is designed to make building asynchronous streams that balance and 
scale automatically *easy*. Built on pure Python -- no dependencies -- this 
framework can be used for variable, decoupled, task-based workloads like 
web scraping, database management operations, and more. Scale this out-of-the-box, 
with minimal hardware and coding, to process 10k+/s on production loads.

Simple pipelines
```
import aiopypes

app = aiopypes.App()

@app.task(interval=1.0)
async def every_second():
    return datetime.utcnow()

@app.task()
async def task1(stream):
    async for s in stream:
        print(f"streaming from task1: {s}")
        yield obj

if __name__ == '__main__':

    pipeline = every_second \
               .map(task1)

    pipeline.run()
```

To scaled pipelines
```
import aiopypes
import aiohttp

app = aiopypes.App()

@app.task(interval=0.1)
async def every_second():
    return "http://www.google.com"

@app.task(scaler=aiopypes.scale.TanhTaskScaler()) #  this scales workers automatically to consume incoming requests
async def task1(stream):
    async for s in stream:
        yield await aiohttp.get(s)

async def task2(stream):
    async for s in stream:
        if s.response_code != 200:
            print("failed request: {s}")
        yield

if __name__ == '__main__':

    pipeline = every_second \
               .map(task1)
               .reduce(task2)

    pipeline.run()
```

## 🏁 Getting Started <a name = "getting_started"></a>

Start with a simple pipeline, and build out from there!
```
import aiopypes

app = aiopypes.App()

@app.task(interval=1.0)
async def every_second():
    return datetime.utcnow()

@app.task()
async def task1(stream):
    async for s in stream:
        print(f"streaming from task1: {s}")
        yield obj

if __name__ == '__main__':

    pipeline = every_second \
               .map(task1)

    pipeline.run()
```
For more, see [readthedocs](https://aiopypes.readthedocs.io)

### Prerequisites

`aiopypes` is based on pure Python (3.5+) and does not require other dependencies.

### Installing
Available on PyPi [here](https://pypi.org/project/aiopypes), installed with pip:

```
pip install aiopypes
```

## 🔧 Running the tests <a name = "tests"></a>

To be created!

### Break down into end to end tests

To be created!

### And coding style tests

To be created!

## 🎈 Usage <a name="usage"></a>

Import the library
```
import aiopypes
```

Create an App object
```
app = aiopypes.App()
```

Create a trigger task
```
@app.task(interval=1.0)
async def every_second():
    return 1
```

Create downtream tasks
```
@app.task()
async def task_n(stream):
    async for s in stream:
        # process "s" here
        yield
```

Create + configure the pipeline
```
pipeline = every_second \
            .map(task_n)
```

Run the pipeline
```
pipeline.run()
```

This will run continuously until interrupted.

## ⛏️ Built Using <a name = "built_using"></a>

- [Python](https://www.python.org/)
- [asyncio](https://docs.python.org/3/library/asyncio.html)

## ✔️ TODO <a name = "todo"></a>

- [ ] Extend to multithreads
- [ ] Extend to multiprocess
- [ ] Build visualization server
- [ ] Add pipeline pipe functions (join, head, ...)

## ✍️ Authors <a name = "authors"></a>

- [@mroumanos](https://github.com/mroumanos)
- Contributors: you?

## 🎉 Acknowledgements <a name = "acknowledgement"></a>

- [faust streaming](https://github.com/faust-streaming/faust)
