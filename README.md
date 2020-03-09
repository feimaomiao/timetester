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

## Options
- Timetester object:
	- target(decimal/int)
	> The target time you want the function to be at 
```Python
import timetester

def foo(arg):
	pass

k = timetester.timeTester(foo,target=0.005)
# or
k.target =0.05
```
	- print_output(bool)
	> disable all `print` function inside the provided function.
```Python
import timetester

def foo(arg):
	print(arg)

k= timetester.timeTester(foo, print_output=False)
# Even though the function is intended to print arguments, no output will be printed during run tests
k.runtests('hi','bye')
# After runtests print functions will be normal.
print('hi')
```
	- maxtime
	> Maximum time all functions would run


