# test_time
Easy to use Python package to test a functions runtime

## Usage
- Timetester Object
```python
import timetester

def foo(arg):
	pass

k = timetester.timeTester(foo)
k.runtests()
k.graph()
print(k.report())
```
- Timeout Decorator
```python
import timetester
import time

# Raises error
@timetester.timeout(10)
def foo(bar):
	time.sleep(10)

```
- Compare object
```python
import timetester

def foo():
	pass

def bar():
	pass

k= timetester.compare(foo,bar)
k.compareFuncs()
k.graph()
k.output_asfile()
k.initialise()
```

