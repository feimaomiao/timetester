import time
import statistics as st
import signal
from functools import wraps
from errno import ETIME
import os
from decimal import Decimal as dec
import io
import sys
import json
import random, string


# Main error raised in test_time
class timeTesterError(Exception):
    pass

# timeout function wrapper
def timeout(seconds=10, error_message=os.strerror(ETIME)):
    def dec(func):
        if not bool(seconds):
            return func
        def _handle_timeout(signum, frame):
            raise TimeoutError(error_message)

        def wrapper(*args, **kwargs):
            signal.signal(signal.SIGALRM, _handle_timeout)
            signal.alarm(seconds)
            try:
                result = func(*args, **kwargs)
            finally:
                signal.alarm(0)
            return result
        return wraps(func)(wrapper)

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
        # Prevents from 
        if maxtime<error_time:
            raise timeTesterError('maxtime must be larger than error time!')
        self.function   = method
        try:
            self.runtime        = int(runtime)
            self.target         = dec(target)
            self.maxtime        = dec(maxtime)
            self.echo_result    = bool(print_output)
            self.type           = return_type
            # error time must be at least 1 seconds
            self.error_time     = int(error_time)
            # Private variables
            self.__average      = []
            self.__errorEncd    = 0
            self.__totalruntime = 0
            self.__runs         = 0
        # When user inputs something other than integer or float
        except TypeError:
            print('runtime, maxtime and errortime must be int')
            raise

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
            return 'Run a time test before getting its time!'
        else:
            return 'An error occured'


    def runtests(self, *args, **kwargs):
    # Run tests for said function.
    # Usage:
    #     k = timeTester(func)
    #     k.runtests(args, kwargs)
    # Both positional and required args can be provided

    # Functino that raises error
        def __raise_error(signum, frame):
            raise TimeoutError(f'Testrun #{i} took longer than selected time to respond.')

        try:
            # Checks if variables are assigned to the correct type
            self.runtime        = int(self.runtime)
            self.target         = dec(self.target)
            self.maxtime        = dec(self.maxtime)
            self.echo_result    = bool(self.echo_result)
            self.error_time     = round(int(self.error_time))
        except ValueError:
            raise timeTesterError('Please make sure the variables are assigned properly') from ValueError

        # redirects stdout to a texttrap if user decides not to print outputs
        if not self.echo_result:
            text_trap = io.StringIO()
            sys.stdout = text_trap
        # Check how many runs should be ran
        self.__runs += self.runtime
        beginning_time = time.time()
        # initialises signal and error
        signal.signal(signal.SIGALRM, __raise_error)
        for i in range(self.runtime):
            __starttime= time.time()
            try:
                # Set alarm time
                signal.alarm(self.error_time)
                # Runs function
                self.function(*args,**kwargs)
                # Ends the alarm, prevents from raising error
                signal.alarm(0)
            except timeTesterError:
                # Timeout
                # Redirects print back to stdout
                sys.stdout = sys.__stdout__
                # Ends alarm
                signal.alarm(0)
                self.__totalruntime += (time.time()- beginning_time)
                self.__errorEncd += 1
                raise
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
            # Total run time
            __runtime_o = dec(time.time()-__starttime)
            # Raise timeTesterError if the function took longer than expected
            if __runtime_o >= self.maxtime:
                self.__totalruntime += (time.time()- beginning_time)
                self.__errorEncd += 1
                sys.stdout = sys.__stdout__
                raise timeTesterError('Tests took longer than expected!') from TimeoutError
            # Adds average to total runtime list
            self.__average.append(__runtime_o)
        # Adds total runtime of function
        self.__totalruntime += (time.time()- beginning_time)
        # redirects print to stdout
        sys.stdout = sys.__stdout__
        # Returns the time the function took
        return self.__totalruntime

    def initialise(self):
        # Imagine it as a restart to the funciton
        self.__average      = []
        self.__errorEncd    = 0
        self.__totalruntime = 0
        self.__runs         = 0
        return

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
        # Plot function time
        plt.plot([x for x in range(len(self.__average))], self.__average, color = 'darkblue', linewidth=1, label="Actual time")
        # Gets user averages
        actualaverage = st.mode(self.__average) if self.type == 'mode' else st.median(self.__average) if self.type == 'median' else st.harmonic_mean(self.__average) if self.type=='harmonimean' else st.geometric_mean(self.__average) if self.type == 'geometricmean' else st.mean(self.__average)
        # Plots average
        plt.plot([x for x in range(len(self.__average))], [actualaverage for x in range(len(self.__average))], color='green',linewidth=1, label=f"{self.type} average")
        # Set x and y labels
        plt.xlabel('Times')
        plt.ylabel('Seconds')
        # Set x and y limits
        plt.xlim=(0,len(self.__average)*1.01)
        ylimit = 1.5*float(self.target) if self.target<max(self.__average) else float(max(self.__average)) if max(self.__average)< st.median(self.__average) * 3 else float(st.median(self.__average)) * 3
        # plot target after checking if target>min
        plt.plot([x for x in range(len(self.__average))], [self.target for x in range(len(self.__average))], color='red', linewidth=1, label="target time") if self.target<= ylimit else None
        # plot ylimit
        plt.ylim(0, ylimit)
        plt.title('Average time')
        plt.legend()
        plt.show()
        # close window and return
        return plt.close()

    def report(self):
        # Function that reports a string that describes the function and its runs
        try:
            returnString = f'''\
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
        return returnString

class compare():
    # object that compares different function's runspeed
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
        self.speedtime      = {}
        self.looptime       = 2
        self.runtime        = 50
        self.errortime      = 0 
        self.print          = False
        self.meantype       ='harmonimean'
        self.__amount       = len(args)
        self.__methods      = args
        self.__averages     = {}
        try:
            for i in self.__methods:
                print(i.__name__)
                self.speedtime[i.__name__] = 0
                self.__averages[i.__name__] = []
        except AttributeError:
            try:
                raise timeTesterError(f'{i.__repr__()} does not have a __name__ attribute') from AttributeError
            except AttributeError:
                raise timeTesterError(f'I dont know what {i} is') from AttributeError
        if self.__amount<2:
            raise timeTesterError('Compare requires at least 2 functions')
        elif len(self.speedtime)< len(args):
            raise timeTesterError('Function is provided more than once')
        else:
            for i in self.__methods:
                if not callable(i):
                    raise timeTesterError(f'{i} is not a function')

    def __repr__(self):
        return str(self.speedtime)

    def meanfunc(self, ll):
        l = {'mode': st.mode, 'median': st.median, 'harmonicmean':st.harmonic_mean, 'geometricmean':st.geometric_mean}
        return lambda: l.get(self.meantype, st.mean)(ll)

    def compareFuncs(self, *args, **kwargs):
        for i in self.speedtime:
            self.speedtime[i] = 0
        try:
            self.runtime    = int(self.runtime)
            self.looptime   = int(self.looptime) 
            self.print      = bool(self.print)
        except ValueError:
            raise timeTesterError('Please make sure your variables are set correspondingly') from ValueError
        for runs in range(self.looptime):
            for funcs in self.__methods:
                methodtime = timeTester(funcs, runtime=self.runtime, return_type=self.meantype, print_output=self.print, error_time=self.errortime)
                try:
                    methodtime.runtests(*args, **kwargs)
                except Exception as e:
                    for i in self.speedtime:
                        self.speedtime[i] =0 
                    raise
                self.speedtime[funcs.__name__] += float(methodtime.__repr__())
                self.__averages[funcs.__name__].append(float(methodtime.__repr__()))
        for r in self.speedtime:
            self.speedtime[r] = self.meanfunc([self.speedtime[r] for i in range(self.looptime)])()
        self.speedtime = {k: v for k, v in sorted(self.speedtime.items(), key=lambda item: item[1])}
        return list(self.speedtime.keys())[0]

    def output_asfile(self):
        if any([x == 0 for x in self.speedtime.values()]):
            raise timeTesterError('Please run tests before outputing as file')
        import json
        json.dump(self.speedtime, open('timetest_report.json', 'w'))
        return self.speedtime

    def graph(self):
        # Graphs average time
        try:
            from matplotlib import pyplot as plt
        except (ImportError, ModuleNotFoundError) as e:
            raise timeTesterError('Module matplotlib is not imported in pip') 
        if any([len(x) == 0 for x in self.__averages]):
            raise timeTesterError('Please run compare before graphing!')
        plt.clf()
        for i in self.__averages:
            plt.plot([x for x in range(len(self.__averages[i]))], self.__averages[i], linewidth=1, label=str(i), color=random.choice(['blue','red','green','darkblue','black']))
        plt.title('Average time')
        plt.legend()
        plt.show()
        # close window and return
        return plt.close()


def test_fund(*args):
    print(args)
    return

def test_func(*args):
    print(args)
    return

def test_fune(*args):
    print(args)
    return

def test_funf(*args):
    print(args)
    return









            



