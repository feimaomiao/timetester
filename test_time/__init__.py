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
from typing import NewType

class timeTesterError(Exception):
    pass

def test_function_delete_later(*args):
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(random.randrange(15,20)))

def test_function_2():
    if random.choices([True, False], weights=[0.2,0.8])[0]:
        raise timeTesterError
    return

# timeout function wrapper
def timeout(seconds=10, error_message=os.strerror(ETIME)):
    def decorator(func):
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

    return decorator

class timeTester():
    def __init__(self, method ,target=1,print_output = False,runtime=100, maxtime=10, error_time=0, return_type = 'mean'):
        self.function   = method
        try:
            self.runtime        = int(runtime)
            self.target         = dec(target)
            self.maxtime        = dec(maxtime)
            self.echo_result    = bool(print_output)
            self.type           = return_type
            # error time must be at least 1 seconds
            self.error_time     = int(error_time)
            self.__average      = []
            self.__errorEncd    = 0
            self.__totalruntime = 0
            self.__runs         = 0
        except TypeError:
            print('runtime, maxtime and errortime must be int')
            raise
        if runtime<=0 or target<=0 or maxtime<0 or error_time<0:
            raise timeTesterError('runtime, target, maxtime and errortime cannot be smaller than 0')
        if maxtime<self.error_time:
            raise timeTesterError('maxtime must be larger than error time!')

    def __repr__(self):
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
        def __raise_error(signum, frame):
            raise TimeoutError(f'Testrun #{i} took longer than selected time to respond.')
        try:
            self.runtime        = int(self.runtime)
            self.target         = dec(self.target)
            self.maxtime        = dec(self.maxtime)
            self.echo_result    = bool(self.echo_result)
            self.error_time     = round(int(self.error_time))
        except ValueError:
            raise timeTesterError('Please make sure the variables are assigned properly') from ValueError
        if not self.echo_result:
            text_trap = io.StringIO()
            sys.stdout = text_trap
        self.__runs += self.runtime
        beginning_time = time.time()
        for i in range(self.runtime):
            __starttime= time.time()
            signal.signal(signal.SIGALRM, __raise_error)
            try:
                signal.alarm(self.error_time)
                self.function(*args,**kwargs)
                signal.alarm(0)
            except TimeoutError:
                sys.stdout = sys.__stdout__
                signal.alarm(0)
                self.__totalruntime += (time.time()- beginning_time)
                self.__errorEncd += 1
                raise
            except Exception as e:
                sys.stdout = sys.__stdout__
                self.__totalruntime += (time.time()- beginning_time)
                self.__errorEncd += 1
                signal.alarm(0)
                raise 
            __runtime_o = dec(time.time()-__starttime)
            if __runtime_o >= self.maxtime:
                self.__totalruntime += (time.time()- beginning_time)
                self.__errorEncd += 1
                sys.stdout = sys.__stdout__
                raise timeTesterError('Tests took longer than expected!') from TimeoutError
            self.__average.append(__runtime_o)
            del __starttime, __runtime_o
        self.__totalruntime += (time.time()- beginning_time)
        self.averagelistdel = self.__average
        sys.stdout = sys.__stdout__
        return self.__totalruntime

    def initialise(self):
        self.__average      = []
        self.__errorEncd    = 0
        self.__totalruntime = 0
        self.__runs         = 0
        return

    def graph(self):
        try:
            from matplotlib import pyplot as plt
        except ImportError:
            raise timeTesterError('Module matplotlib is not imported in pip') from ImportError
        if self.__errorEncd >0:
            raise timeTesterError('Please make sure no error is encountered before actually showing the test time') from ValueError
        elif len(self.__average) ==0:
            raise timeTesterError('Please run tests before plotting the results!')
        plt.plot([x for x in range(len(self.__average))], self.__average, color = 'darkblue', linewidth=1, label="Actual time")
        actualaverage = st.mode(self.__average) if self.type == 'mode' else st.median(self.__average) if self.type == 'median' else st.mean(self.__average)
        plt.plot([x for x in range(len(self.__average))], [actualaverage for x in range(len(self.__average))], color='green',linewidth=1, label=f"{self.type} average")
        plt.xlabel('Times')
        plt.ylabel('Seconds')
        plt.xlim=(0,len(self.__average)*1.01)
        ylimit = 1.5*float(self.target) if self.target<max(self.__average) else float(max(self.__average)) if max(self.__average)< st.median(self.__average) * 3 else float(st.median(self.__average)) * 3
        plt.plot([x for x in range(len(self.__average))], [self.target for x in range(len(self.__average))], color='red', linewidth=1, label="target time") if self.target<= ylimit else None
        plt.ylim(0, ylimit)
        plt.title('Average time')
        plt.legend()
        plt.show()
        return plt.close()

    def report(self):
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
            raise timeTesterError('Please run tests before reporting!') from st.StatisticsError
        return returnString

def tester(*args):
    print(args)

def tester2(*args):
    print(args)

class compare():
    def __init__(self, *args):
        args= list(args)
        self.speedtime      = {}
        self.__amount       = len(args)
        self.__methods      = args
        self.looptime       = 2
        self.runtime        = 50
        self.errortime      = 0 
        self.print          = False
        self.meantype       ='harmonimean'
        try:
            for i in self.__methods:
                self.speedtime[i.__name__] = 0
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
        try:
            self.runtime    = int(self.runtime)
            self.looptime   = int(self.looptime) 
            self.print      = bool(self.print)
        except ValueError:
            raise timeTesterError('Please make sure your variables are set correspondingly') from ValueError
        for runs in range(self.looptime):
            for funcs in self.__methods:
                methodtime = timeTester(funcs, runtime=self.runtime, return_type=self.meantype, print_output=self.print, error_time=self.errortime)
                methodtime.runtests(*args, **kwargs)
                self.speedtime[funcs.__name__] += float(methodtime.__repr__())
        for r in self.speedtime:
            self.speedtime[r] = self.meanfunc([self.speedtime[r] for i in range(self.looptime)])()
        self.speedtime = dict(reversed(sorted(self.speedtime.items())))
        return self.speedtime

    def output_asfile(self):
        if len(self.speedtime) == 0:
            raise timeTesterError('Please run tests before outputing as file')
        import json
        json.dump(self.speedtime, open('timetest_report', 'w'))
        return self.speedtime








            



