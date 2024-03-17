from functools import wraps
import time


def stop_watch(func):
    @wraps(func)
    def wrapper(*args, **kargs):
        start = time.perf_counter()
        result = func(*args, **kargs)
        elapsed_time = time.perf_counter() - start
        print(f"Processing time of [{func.__name__}] : {elapsed_time:.6f}sec")
        return result
    return wrapper
