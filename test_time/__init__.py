import time
import statistics as st
import signal
from functools import wraps
from errno import ETIME
import os
from decimal import Decimal as dec

def test_function_delete_later():
    import random, string
    password_characters = string.ascii_letters + string.digits
    return ''.join(random.choice(password_characters) for i in range(random.randrange(15,20)))

class timeTesterError(Exception):
    pass

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
    def __init__(self, method ,target=100000,runtime=100, maxtime=100, error_time=100, return_type = 'mean'):
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
            self.averagelistdel = []
        except TypeError:
            print('runtime, maxtime and errortime must be int')
            raise
        if runtime<=0 or target<=0 or maxtime<=0 or error_time<0:
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
                self.__errorEncd += 1
                raise
            except Exception as e:
                self.__errorEncd += 1
                signal.alarm(0)
                raise
            __runtime_o = dec(time.time()-__starttime)
            if __runtime_o >= self.maxtime:
                self.__errorEncd
                raise TimeoutError('Tests took longer than expected!')
            self.__average.append(__runtime_o)
            del __starttime, __runtime_o
        self.__totalruntime += (beginning_time - time.time())
        self.averagelistdel = self.__average

    def show_plot(self):
        try:
            from matplotlib import pyplot as plt
        except ImportError:
            print('Please make sure you have matplotlib module downloaded from pip!')
            return
        plt.plot([x for x in range(len(self.__average))], self.__average, color = 'darkblue', linewidth=1)
        plt.show()



    def report(self):
        returnString = f'''\
Expected runs       : {self.__runs}
Target              : {self.target}
Maximum time        : {self.maxtime}(Total), {self.error_time}(Single run)
Successful runs     : {len(self.__average)}
Total errors        : {self.__errorEncd}
repr type           : {self.type}
Mean time           : {str(dec(st.mean(self.__average)))}
Median time         : {str(dec(st.median(self.__average)))}
Mode time           : {str(dec(st.median(self.__average)))}
Mode time appearance: {self.__average.count(dec(st.median(self.__average)))}
Harmonic mean time  : {str(dec(st.harmonic_mean(self.__average)))}
Meeting Target      : {True if dec(st.mean(self.__average))< self.target else False}
To target(mean)(abs): {-abs(self.target-dec(st.mean(self.__average)))}
To target           : {self.target-dec(st.mean(self.__average))}
Max time in run     : {max(self.__average)}
Max time index      : {self.__average.index(max(self.__average))}
Max time appearance : {self.__average.count(max(self.__average))}
Min time in run     : {min(self.__average)}
Min time index      : {self.__average.index(min(self.__average))}
Min time appearance : {self.__average.count(min(self.__average))}
'''
        return returnString





            



