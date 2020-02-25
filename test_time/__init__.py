import time
import statistics as st
import signal
from functools import wraps
from errno import ETIME
import os
from decimal import Decimal as dec
import random, string
class timeTesterError(Exception):
    pass

def test_function_delete_later():
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(random.randrange(15,20)))

def test_function_2():
    if random.choices([True, False], weights=[0.2,0.8])[0]:
        raise timeTesterError
    return


def timeout(seconds=10, error_message=os.strerror(ETIME)):
    def decorator(func):
        if not seconds:
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

class tester():
    def __init__(self, method ,target=1,runtime=100, maxtime=10, error_time=0, return_type = 'mean'):
        self.function   = method
        try:
            self.runtime        = int(runtime)
            self.target         = dec(target)
            self.maxtime        = dec(maxtime)
            # error time must be at least 1 seconds
            self.error_time     = int(error_time)
            self.__average      = []
            self.type           = return_type
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
            else:
                self.type = 'mean'
                return str(dec(st.mean(self.__average)))
        except st.StatisticsError as e:
            return 'Run a time test before getting its time!'
        else:
            return 'An error occured'

    def run_tests(self, *args, **kwargs):
        def __raise_error(signum, frame):
            raise TimeoutError(f'Testrun #{i} took longer than selected time to respond.')

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
                self.__totalruntime += (beginning_time - time.time())
                self.__errorEncd += 1
                raise
            except Exception as e:
                self.__totalruntime += (beginning_time - time.time())
                self.__errorEncd += 1
                signal.alarm(0)
                raise
            __runtime_o = dec(time.time()-__starttime)
            if __runtime_o >= self.maxtime:
                self.__totalruntime += (beginning_time - time.time())
                self.__errorEncd += 1
                raise TimeoutError('Tests took longer than expected!')
            self.__average.append(__runtime_o)
            del __starttime, __runtime_o
        self.__totalruntime += (beginning_time - time.time())
        self.averagelistdel = self.__average

    def graph(self):
        try:
            from matplotlib import pyplot as plt
        except ImportError:
            print('Please make sure you have matplotlib module downloaded from pip!')
            return
        if self.__errorEncd >0:
            raise timeTesterError('Please make sure no error is encountered before actually showing the test time')
        if len(self.__average) ==0:
            raise timeTesterError('Please run tests before plotting the results!')
        plt.plot([x for x in range(len(self.__average))], self.__average, color = 'darkblue', linewidth=1, label="Actual time")
        actualaverage = st.mode(self.__average) if self.type == 'mode' else st.median(self.__average) if self.type == 'median' else st.mean(self.__average)
        plt.plot([x for x in range(len(self.__average))], [actualaverage for x in range(len(self.__average))], color='green',linewidth=1, label=f"{self.type}average")
        plt.legend()
        plt.xlabel('Times')
        plt.ylabel('Seconds')
        plt.xlim=(0,len(self.__average)*1.01)
        ylimit = 1.5*float(self.target) if self.target<max(self.__average) else float(max(self.__average)) if max(self.__average)< st.median(self.__average) * 3 else float(st.median(self.__average)) * 3
        plt.plot([x for x in range(len(self.__average))], [self.target for x in range(len(self.__average))], color='red', linewidth=1, label="target time") if self.target<= ylimit else None
        print(ylimit)
        plt.ylim(0, ylimit)
        plt.title('Average time')
        plt.show()



    def report(self):
        returnString = f'''\
Expected runs       : {self.__runs}
Target              : {self.target}
Maximum time        : {self.maxtime}(Total), {self.error_time}(Single run)
Successful runs     : {len(self.__average)}
Total time elapsed  : {self.__totalruntime}
Total errors        : {self.__errorEncd}
repr type           : {self.type}
Mean time           : {str(dec(st.mean(self.__average)))}
Median time         : {str(dec(st.median(self.__average)))}
Mode time           : {str(dec(st.median(self.__average)))}
Mode time appearance: {self.__average.count(dec(st.median(self.__average)))}
Harmonic mean time  : {str(dec(st.harmonic_mean(self.__average)))}
Meeting Target      : {True if dec(st.mean(self.__average))< self.target else False}
To target(mean)(abs): {abs(self.target-dec(st.mean(self.__average)))}
To target           : {-(self.target-dec(st.mean(self.__average)))}
Max time in run     : {max(self.__average)}
Max time index      : {self.__average.index(max(self.__average))}
Max time appearance : {self.__average.count(max(self.__average))}
Min time in run     : {min(self.__average)}
Min time index      : {self.__average.index(min(self.__average))}
Min time appearance : {self.__average.count(min(self.__average))}
'''
        return returnString





            



