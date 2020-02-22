import time
import statistics as st
import signal
from functools import wraps
from errno import ETIME
import os
from decimal import Decimal as dec

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
            self.target         = int(target)
            self.maxtime        = int(maxtime)
            self.error_time     = int(error_time)
            self.__average      = []
            self.type           = return_type
            self.__errorEncd    = 0
            self.__totalruntime = 0
        except TypeError:
            print('runtime, maxtime and errortime must be int')
            raise
        if runtime<=0 or target<=0 or maxtime<=0 or error_time<=0:
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

        beginning_time = time.time()
        for i in range(self.runtime):
            starttime= time.time()
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
            run_time = time.time()-starttime
            if run_time >= self.maxtime:
                self.__errorEncd
                raise TimeoutError('Tests took longer than expected!')
            self.__average.append(run_time)
            del starttime, run_time
        self.__totalruntime += (beginning_time - time.time())

    def report(self):
        returnString = f'''\
Expected runs       : {self.runtime}
Target              : {self.target}
Maximum time        : {self.maxtime}(Total), {self.error_time}(Single run)
Successful runs     : {len(self.__average)}
Total errors        : {self.__errorEncd}
repr type           : {self.type}
Mean time           : {str(dec(st.mean(self.__average)))}
Median time         : {str(dec(st.median(self.__average)))}
Mode time           : {str(dec(st.median(self.__average)))}
Harmonic mean time  : {str(dec(st.harmonic_mean(self.__average)))}
Meeting Target      : {True if dec(st.mean(self.__average))< self.target else False}
To target(mean)     : {abs(self.target-dec(st.mean(self.__average)))}
'''
        return returnString





            



