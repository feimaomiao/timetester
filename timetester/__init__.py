from decimal import Decimal as dec
from errno import ETIME
from functools import wraps
import json
from math import ceil as mathceil
import os
import statistics as st
import signal
import sys
import time

__all__ = ['timeout','timeTesterError','timeTester','compare']

# Main error raised in test_time
class timeTesterError(Exception):
    pass

# timeout function wrapper
def timeout(seconds=10, error_message=os.strerror(ETIME)):
    def dec(func):
        if not bool(seconds):
            return func
        def _raise_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrp(*args, **kwargs):
            signal.signal(signal.SIGALRM, _raise_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wraps(func)(wrp)

    return dec

"""
time tester object for one function.
usage:
    k = tester(function)
    k.runtests()
    print(k.report())
"""
class timeTester():
    def __init__(self, method ,target=1,print_output = False,runtime=100, maxtime=10, error_time=0, return_type = 'mean'):
        # Check if any said inputted variablaes would distrupt the tester
        if runtime<=0 or target<=0 or maxtime<0 or error_time<0:
            raise timeTesterError('runtime, target, maxtime and errortime cannot be smaller than 0')
         # Prevents from not balanced time values
        if maxtime<error_time:
            raise timeTesterError('maxtime must be larger than error time!')
        self.function   = method
        try:
            self.runtime        = abs(int(runtime))
            self.target         = dec(abs(target))
            self.maxtime        = dec(abs(maxtime))
            self.print_output   = bool(print_output)
            self.type           = return_type
            self.error_time     = dec(abs(error_time))
            # Private variables
            self.__errt         = mathceil(error_time)
            self.__average      = []
            self.__errorEncd    = 0
            self.__totalruntime = 0
            self.__runs         = 0
            self.__returnString = ''
         # When user inputs something other than integer or float
        except TypeError:
            raise timeTesterError('runtime, maxtime and errortime must be int') from TypeError

    def __repr__(self):
    # Return string. Used when you print(timeTester)
        try:
            if self.type == 'mode':
                return str(dec(st.mode(self.__average)))
            elif self.type == 'median':
                return str(dec(st.median(self.__average)))
            elif self.type == 'harmonimean':
                return str(dec(st.harmonic_mean(self.__average)))
            elif self.type == 'geometricmean':
                return str(dec(st.geometric_mean(self.__average)))
            else:
                self.type = 'mean'
                return str(dec(st.mean(self.__average)))
        except st.StatisticsError as e:
            return ('Run a time test before getting its time!')
        else:
            return 'An error occured!'

    def __hash__(self):
        return hash((self.runtime, self.target, self.maxtime, self.print_output, self.type, self.error_time))

    def __str__(self):
        return str(self.__repr__())

    def __bytes__(self):
        return bytes(str(self.__repr__()), 'utf-32')

    # Functions used to compare different objects
    def __eq__(self, other):
        if not isinstance(other, (timeTester, int, float, dec)):
            return 'Not Implemented'
        try:
            if self.__runs==0 or other.__runs == 0:
                raise timeTesterError('One of the objects has not been tested!')
        except AttributeError:
            pass
        return round(dec(self.__repr__()),6) == round(dec(other.__repr__()),6)

    def __ne__(self, other):
        return not self.__eq__(other)

    def __lt__(self,other):
        if not isinstance(other, (timeTester, int, float, dec)):
            return 'Not Implemented'
        try:
            if self.__runs==0 or other.__runs == 0:
                raise timeTesterError('One of the objects has not been tested!')
        except AttributeError:
            pass
        return round(dec(self.__repr__()),6)< round(dec(other.__repr__()),6)

    def __gt__(self,other):
        if not isinstance(other, (timeTester, int, float, dec)):
            return 'Not Implemented'
        try:
            if self.__runs==0 or other.__runs == 0:
                raise timeTesterError('One of the objects has not been tested!')
        except AttributeError:
            pass
        return round(dec(self.__repr__()),6)> round(dec(other.__repr__()),6)

    def __ge__(self, other):
        return not self.__lt__(other)

    def __le__(self,other):
        return not self.__gt__(other)

    def runtests(self, *args, **kwargs):
        # Run tests for said function.
        # Usage:
        #     k = timeTester(func)
        #     k.runtests(args, kwargs)
        # Both positional and required args can be provided


        def __raise_error(signum, frame):
            raise timeTesterError(f'Testrun #{i} took longer than selected time to respond.') from TimeoutError

        try:
            # Checks if variables are assigned to the correct type
            self.runtime        = round(int(self.runtime))
            self.target         = dec(abs(self.target))
            self.maxtime        = dec(abs(self.maxtime))
            self.print_output   = bool(self.print_output)
            self.error_time     = dec(abs(self.error_time))
            self.__errt         = mathceil(self.error_time)
        except ValueError:
            raise timeTesterError('Please make sure the variables are assigned properly') from ValueError

         # redirects stdout to a text trap if user decides not to print outputs
        if not self.print_output:
            sys.stdout = None
         # Check how many runs should be ran
        self.__runs += self.runtime
        beginning_time = time.time()
         # initialises signal and error
        signal.signal(signal.SIGALRM, __raise_error)
        for i in range(self.runtime):
            __starttime= time.time()
            try:
                # Set alarm time
                signal.alarm(self.__errt)
                # Runs function
                self.function(*args,**kwargs)
                __endtime = time.time()
                # Ends the alarm, prevents from raising error
                signal.alarm(0)    
            except Exception as e:
                # Function raised an error
                # Redirect print function back to normal
                sys.stdout = sys.__stdout__
                # Add total run time
                self.__totalruntime += (time.time()- beginning_time)
                self.__errorEncd += 1
                signal.alarm(0)
                # re-raise error
                raise 
            # Raise timeTesterError if the function took longer than expected
            if ((time.time()-__starttime) > self.error_time and self.error_time > 0) or (time.time()-beginning_time) > self.maxtime:
                self.__totalruntime += (time.time()- beginning_time)
                self.__errorEncd += 1
                sys.stdout = sys.__stdout__
                return __raise_error(signum=None, frame=None)
            # Adds average to total runtime list
            self.__average.append(__endtime-__starttime)
         # Adds total runtime of function
        self.__totalruntime += (time.time()- beginning_time)
         # redirects print to stdout
        sys.stdout = sys.__stdout__
         # Returns the time the function took
        del beginning_time, __endtime, __starttime
        return self

    def initialise(self):
        self.__average      = []
        self.__errorEncd    = 0
        self.__totalruntime = 0
        self.__runs         = 0
        self.__returnString = ''
        return self


    def graph(self):
         # Graphs average time
        try:
            from matplotlib import pyplot as plt
        except ImportError:
            raise timeTesterError('Module matplotlib is not imported in pip') from ImportError
         # Does not output average time if the program rain into an error
        if self.__errorEncd >0:
            raise timeTesterError('Please make sure no error is encountered before actually showing the test time') from ValueError
        # Also does not output when the user hasn't ran tests yet
        elif len(self.__average) ==0:
            raise timeTesterError('Please run tests before plotting the results!')
        # plot function itme
        plt.plot(list(range(len(self.__average))), self.__average, color = 'darkblue', linewidth=1, label="Actual time")
         # Gets user averages
        actualaverage = st.mode(self.__average) if self.type == 'mode' else st.median(self.__average) if self.type == 'median' else st.harmonic_mean(self.__average) if self.type=='harmonimean' else st.geometric_mean(self.__average) if self.type == 'geometricmean' else st.mean(self.__average)
        # Plots average
        plt.plot(list(range(len(self.__average))), [actualaverage for x in range(len(self.__average))], color='green',linewidth=1, label=f"{self.type} average")
        # Set x and y labels
        plt.xlabel('Times')
        plt.ylabel('Seconds')
        # Set x and y limits
        plt.xlim=(0,len(self.__average)*1.01)
        ylimit = float(st.median(self.__average))*3
        # plot target after checking if target>min
        plt.plot(list(range(len(self.__average))), [self.target for x in range(len(self.__average))], color='red', linewidth=1, label="target time") if self.target<= ylimit else None
        # plot ylimit
        plt.ylim(0, ylimit)
        plt.title('Average time')
        plt.legend()
        plt.show()
        # close window and return
        plt.close()
        return self

    def report(self):
        #Function that reports a string that describes the function and its runs
        try:
            self.__returnString = f'''\
Expected runs       : {self.__runs}
Target              : {self.target}
Maximum time        : {round(self.maxtime, 15)}(Total), {self.error_time}(Single run)
Successful runs     : {len(self.__average)}
Total time elapsed  : {self.__totalruntime}
Total errors        : {self.__errorEncd}
repr type           : {self.type}
Mean time           : {str(dec(st.mean(self.__average)))}
Median time         : {str(dec(st.median(self.__average)))}
Mode time           : {str(dec(st.median(self.__average)))}
Mode time appearance: {self.__average.count(dec(st.median(self.__average)))}
Harmonic mean time  : {str(dec(st.harmonic_mean(self.__average)))}
Geometric mean time : {str(dec(st.geometric_mean(self.__average)))}
Meeting Target      : {dec(st.mean(self.__average))< self.target}
To target(mean)(abs): {abs(self.target-dec(st.mean(self.__average)))}
To target           : {(self.target-dec(st.mean(self.__average)))}
Max time in run     : {max(self.__average)}
Max time index      : {self.__average.index(max(self.__average))}
Max time appearance : {self.__average.count(max(self.__average))}
Min time in run     : {min(self.__average)}
Min time index      : {self.__average.index(min(self.__average))}
Min time appearance : {self.__average.count(min(self.__average))}'''
        except st.StatisticsError:
            # When user returned report before running tests
            raise timeTesterError('Please run tests before reporting!') from st.StatisticsError
        print(self.__returnString)
        return self

class compare():
    # object that compares different function's runspeed
    # functions should have the same arguments
    # usage:
    #     k = compare(func1, func2, func3)
    # Change the attributes after creating class
    #     k.looptime  = 3
    #     k.runtime   = 100
    #     k.errortime = 1
    #     k.print     = True
    #     k.meantype  = 'geometricmean'
    # Compare the functions
    #     k.compareFuncs(arg1, arg2)
    # Save output as a json file
    #     k.output_asfile()

    # All args should be functions
    def __init__(self, *args):
        args= list(args)
        # Set variables
        self.speedtime      = {}
        self.looptime       = 2
        self.runtime        = 50
        self.errortime      = 0 
        self.print          = False
        self.meantype       ='harmonimean'
        self.__amount       = len(args)
        self.__methods      = args
        self.__averages     = {}
        self.__encErr       = False
        # Check if arguments have __name__ attribute
        try:
            for i in self.__methods:
                self.speedtime[i.__name__] = 0
                self.__averages[i.__name__] = []
        except AttributeError:
            try:
                raise timeTesterError(f'{i.__repr__()} does not have a __name__ attribute') from AttributeError
            except AttributeError:
                raise timeTesterError(f'I dont know what {i} is') from AttributeError
        # Check if there are 2 functions given
        if self.__amount<2:
            raise timeTesterError('Compare requires at least 2 functions')
        # Check if more than one same function is provided
        elif len(self.speedtime)< len(args):
            raise timeTesterError('Function is provided more than once')
         # Check if i is is a function
        else:
            for i in self.__methods:
                if not callable(i):
                    raise timeTesterError(f'{i} is not a function')

    # String that is returned if print(object) is stated
    def __repr__(self):
        return list(self.speedtime.keys())[0]

    # Restart 
    def initialise(self):
         # Empty dictionary
        for i in self.__methods:
            self.speedtime[i.__name__] = 0
            self.__averages[i.__name__] = []
        self.looptime       = 2
        self.runtime        = 50
        self.errortime      = 0
        self.print          = False
        self.meantype       ='harmonicmean'
        self.__encErr       = False
        return self


    # Check and return the mean function.
    def __meanfunc(self, ll):
        l = {'mode': st.mode, 'median': st.median, 'harmonicmean':st.harmonic_mean, 'geometricmean':st.geometric_mean}
        return lambda: l.get(self.meantype, st.mean)(ll)

   # Run compare functions
    def compareFuncs(self, *args, **kwargs):
        self.__encErr = False
        for i in self.speedtime:
            self.speedtime[i] = 0
        try:
            # Check if values are initialised correctly
            self.runtime    = abs(int(self.runtime))
            self.looptime   = abs(int(self.looptime))
            self.print      = bool(self.print)
            self.errortime  = abs(dec(self.errortime))
         # ValueError is derived if the value is not an intended value
        except ValueError:
            self.__encErr = True
            raise timeTesterError('Please make sure your variables are set correspondingly') from ValueError
         # Runs for looptime times
        for runs in range(self.looptime):
            for funcs in self.__methods:
                # Create methodtime object
                methodtime = timeTester(funcs, runtime=self.runtime, return_type=self.meantype, print_output=self.print, error_time=self.errortime)
                try:
                    # runtests
                    methodtime.runtests(*args, **kwargs)
                except Exception as e:
                    # Either timeTesterError or error the function itself raised
                    for i in self.speedtime:
                        self.speedtime[i] =0 
                    # Set variable encountered error to true
                    self.__encErr = True
                    raise
                # appends speedtime to both averages and add to average
                self.speedtime[funcs.__name__] += float(methodtime.__repr__())
                self.__averages[funcs.__name__].append(float(methodtime.__repr__()))
            # Reverse call to eliminate call time differences
            for funcs in reversed(self.__methods):
                methodtime = timeTester(funcs, runtime=self.runtime, return_type=self.meantype, print_output=self.print, error_time=self.errortime)
                try:
                    methodtime.runtests(*args, **kwargs)
                except Exception as e:
                    for i in self.speedtime:
                        self.speedtime[i] =0 
                    self.__encErr = True
                    raise
                self.speedtime[funcs.__name__] += float(methodtime.__repr__())
                self.__averages[funcs.__name__].append(float(methodtime.__repr__()))
         # Add time to dictionary
        for r in self.speedtime:
            self.speedtime[r] = self.__meanfunc([self.speedtime[r] for i in range(self.looptime)])()
        self.speedtime = {k: v for k, v in sorted(self.speedtime.items(), key=lambda item: item[1])}
         # returns the fastest function
        return self

    def sort(self):
        for k,v in self.speedtime.items():
            print(f'{k:10}||{round(dec(v),20):20}')
        return self

    def output_as_file(self):
         # Outputs file as json
        if self.__encErr:
            raise timeTesterError('You have an error encountered')
        if any([x == 0 for x in self.speedtime.values()]):
            raise timeTesterError('Please run tests before outputing as file')
        json.dump(self.speedtime, open('timetest_report.json', 'w'))
        return self

    def graph(self):
         # Graphs average time
        try:
            from matplotlib import pyplot as plt
        except (ImportError, ModuleNotFoundError) as e:
            raise timeTesterError('Module matplotlib is not imported in pip') 
        if self.__encErr:
            raise timeTesterError('You have an error encountered')
        if any([len(x) == 0 for x in self.__averages]):
            raise timeTesterError('Please run compare before graphing!')
         # Empty plot
        plt.clf()
        for count, i in enumerate(self.__averages):
            # Plot times
            plt.plot(list(range(len(self.__averages[i]))), self.__averages[i], linewidth=1, label=str(i), color=['blue','red','green','darkblue','black','brown','darkorange','lawngreen','cyan','dodgerblue','blueviolet','hotpink'][count % 12])
        plt.title('Average time')
        plt.legend()
        plt.show()
         # close window and return
        plt.close()
        return self