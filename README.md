
# test_time
Easy to use Python package to test a functions runtime

## Usage
- Timetester Object
```python
import timetester

def foo(arg):
	pass

k = timetester.timeTester(foo)
k.initialise()
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
	time.sleep(11)

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
## Default options
```python
import timetester
def foo():
	pass

def bar():
	pass

@timetester.timeout(seconds=10,error_message=os.strerror(errno.ETIME))	

k= timetester.timeTester(foo, target=1, print_output=False,runtime=100,maxtime=10,error_time=0,return_type='mean)


# compare object arguments must be methods
# variables can only be changed later
c = timetester.compare(foo,bar)

```

## timeTester object options
- target(float/int)
	> The target time you want the function to be at 
```Python
import timetester

def foo(arg):
	pass

k = timetester.timeTester(foo,target=0.005)
# or
k.target =0.05
```  
- - - - 
- runtime(int,float)
> How many times the function is ran before taking average
```python
import timetester

def foo(arg):
	pass

k= timetester.timeTester(foo, runtime=100)
# or 
k.runtime = 100
```
----
- print_output(bool)
	> disable all `print` function inside the provided function.
```Python
import timetester

def foo(arg):
	print(arg)

k= timetester.timeTester(foo, print_output=False)
# or
k.print_output = False
# Even though the function is intended to print arguments, no output will be printed during run tests
k.runtests('hi','bye')
# After runtests print functions will be normal.
print('hi')
```
  - - --
- maxtime(int/float)
	> Maximum time all functions would run
  
```python
import timetester

def foo(arg):
	sleep(1)

k=timetester.timeTester(foo,maxtime=1)
# or
k.maxtime = 1
k.runtests()
# When the total time is larger than 1 second error will be raised 
```
----
- return_type(choice)
> Type of value returned  

Types of possible values include:
<sub><sub>
1. 'mean'
2. 'mode'
3. 'median'
4. 'harmonicmean'
5. 'geometricmean'  
</sub></sub>
```python 
import timetester

def foo(arg):
	pass

k= timetester.timeTester(foo,return_type='geometricmean')
# or
k.type = 'geometricmean'
```

## timeTester object compatibility
Allows comparision with `int`, `float` and `decimal.Decimal` objects
Take this code below:
```python
import timetester
from decimal import Decimal

def foo(args):
	pass
	
k=timetester.timeTester(foo)
k.runtests()
# Lets say the return value of k (k.__repr__()) is 0.1
k==0.1 				# True
k<1 				# True
k>=Decimal(0.0001) 	# True
```  