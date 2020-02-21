import time
import statistics as st
import signal
from functools import wraps
from errno import ETIME
import os
from decimals import Decimals as dec

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
    def __init__(self, method ,target=10,runtime=100, maxtime=100, error_time=100, return_type = 'mean'):
        self.function   = method
        try:
            self.runtime        = int(runtime)
            self.target         = int(target)
            self.maxtime        = int(maxtime)
            self.error_time     = int(error_time)
            self.__average      = []
            self.type           = return_type
            self.__maxallowance = self.runtime*self.error_time
        except TypeError:
            print('runtime, maxtime and errortime must be ints')
            raise
        if runtime<=0 or target<=0 or maxtime<=0 or error_time<=0:
            raise timeTesterError('runtime, target, maxtime and errortime cannot be smaller than 0')

    def __repr__(self):
        try:
            if self.type == 'mode':
                return str(dec(st.mode(self.__average)))
            elif self.type == 'median':
                return str(dec(st.median(self.__average)))
            else:
                return str(dec(st.mean(self.__average)))
        except st.StatisticsError as e:
            return 'Run a time test before getting its time!'
        else:
            return 'An error occured'

    def run_tests(self, *args, **kwargs):
        beginning_time = time.time()
        for i in range(self.runtime):
            starttime= time.time()
            try:
                self.function(*args,**kwargs)
            except Exception as e:
                raise timeTesterError('Your program ran into a problem,', e)
            run_time = time.time()-starttime
            if run_time >= self.maxtime:
                raise os.strerror(ETIME)
            self.__average.append(run_time)
            del starttime, run_time




            



