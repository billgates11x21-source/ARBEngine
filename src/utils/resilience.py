import time, functools
from requests.adapters import HTTPAdapter
from requests import Session
from urllib3.util.retry import Retry

class SmartSession(Session):
    def __init__(self, retries=3, backoff=0.5, status_forcelist=(500,502,503,504)):
        super().__init__()
        retry = Retry(total=retries, backoff_factor=backoff, status_forcelist=status_forcelist)
        self.mount('https://', HTTPAdapter(max_retries=retry))
        self.mount('http://', HTTPAdapter(max_retries=retry))

class CircuitBreaker:
    def __init__(self, threshold=3, recovery=10):
        self.failures=0; self.threshold=threshold; self.recovery=recovery
        self.opened=False; self.last_failure=0
    def __call__(self, fn):
        @functools.wraps(fn)
        def wrapper(*args,**kwargs):
            if self.opened and time.time()-self.last_failure < self.recovery:
                raise Exception('Circuit open')
            try:
                result=fn(*args,**kwargs)
                self.failures=0; return result
            except Exception:
                self.failures+=1; self.last_failure=time.time()
                if self.failures>=self.threshold: self.opened=True
                raise
        return wrapper
