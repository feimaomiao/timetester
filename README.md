
# timetester
Feed it a method and it tells you the average time.

## Downloads
`pip install timetester`  
or   
`python3 -m pip install timetester`

## Usage
- Timetester Object
```python
import timetester

def foo(arg):
    print(arg)
    pass

k = timetester.timeTester(foo)
# NOT NECESSARY. Only use if you encountered an error and reloaded the object
k.initialise()
# Run tests
k.runtests(*args,**kwargs)
# Graph the average time taken
k.graph()
# Print a report of how the function did
k.report()
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
> The compared functions should have the same intended purpose and the same arguments
```python
import timetester

def foo():
    pass

def bar():
    pass

k= timetester.compare(foo,bar)
# NOT NECESSARY. Only use if you encountered an error and reloaded the function
k.initialise()
# Arguments are passed in here
k.compareFuncs(*args,**kwargs)
# Outputs a graph comparing the time
k.graph()
# Creates a json file consising of the time took for each function to run
k.output_asfile()
# Prints each function on the screen
k.sort()
```
- Usage in Real-Time IDE(Terminal)
>  Joining of functions are generally allowed for timeTester object
>  However, you have to run the actual test function first
```python
import timetester

def foo(args):
    pass

def bar(args):
    pass

# Allowed
timetester.timeTester(foo).initialise().runtests().graph().report()
timetester.timeTester(foo).runtests().graph().report()
timetester.compare(foo,bar).initialise().compareFuncs().graph().sort().output_asfile()
timetester.compare(foo,bar).compareFuncs().output_asfile().graph()

# Not allowed -- You have to run tests first
timetester.timeTester(foo).graph().report()
timetester.timeTester(foo).report()
timetester.compare(foo,bar).initialise().graph().sort().output_asfile()
timetester.compare(foo,bar).graph().sort()

```
## Default options
```python
import timetester
def foo():
    pass

def bar():
    pass

@timetester.timeout(seconds=10,error_message=os.strerror(errno.ETIME))  

k= timetester.timeTester(foo, target=1, print_output=False,runtime=100,maxtime=10,error_time=0,return_type='mean')


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
```
<sub>Lets say the return value of k (k.\_\_repr__()) is 0.1</sub>
```python
k==0.1              # True(float)
k<1                 # True(int)
k>=Decimal(0.0001)  # True(Decimal object)
k==0.002            # False(float)
k>1                 # False(int)
k<=Decimal(0.00001) # False(Decimal object)
```  
## Compare object options
- When creating the object,  the arguments must all be functions
- Variables can only be changed later  
So let's say this is the initial code:  
```python
import timetester
def foo():
    pass
def bar():
    pass
k=timetester.compare(foo,bar)
```
----
- looptime(int)
> Changes how many 'loops' would be ran everytime compareFuncs() would return
```python
# Default
k.looptime
>>2
# Change
k.looptime = 10
setattr(k, 'looptime',10)
# Restart
k.initialise()
```
----
- runtime(int)
> Acts like timeTester.runtime option
```python
# Default
k.runtime
>>50
# Change
k.runtime=100
setattr(k, 'looptime',100)
# Restart
k.initialise()
```
----
- errortime(int,float, decimal.Decimal object)
> Acts as timetester.error_time option
```python
# Default
k.errortime
>>0 # off
# Change
k.errortime = 0.0001
setattr(k,'errortime',0.0001)
# Restart
k.initialise()
```
----
- print(bool)
> Acts as the timetester.print_output option
```python
# Default
k.print
>>False
# Change
k.print = False
setattr(k, 'print',False)
# Restart
k.initialise()
```
- meantype(string)
> Acts as the timetester.type option
```python
# Default
k.meantype
>>'harmonicmean'
# Change
k.meantype = 'median'
setattr(k, 'meantype','median')
# Restart
k.initialise()
```
