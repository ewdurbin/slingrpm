
import inspect
import hashlib

from functools import wraps


def hash_func(func, *args, **kwargs):
    """
    create a hash to identify unique function call
    """
    string = ''.join([str(inspect.getmodule(func)), func.__name__,
                      str(args), str(kwargs)])
    return int(hashlib.md5(string).hexdigest(), 16)


"""
throttle helper taken directly from https://gist.github.com/mattrobenolt/472597490fbb1c4d524d
with permission from @mattrobenolt via https://storify.com/EWDurbin/i-dunno-lawyers
"""

def throttle(interval=1):
    """
    Decorator to throttle task execution rate, uniqued by args/kwargs.

    Within the interval, a decorated task will only be executed once, subsequent
    calls within the interval are ignored, and one gets queued up to run at the
    start of the next interval period.
    This follows the pattern seen here: http://benalman.com/images/projects/jquery-throttle-debounce/throttle.png

    Example:
    Interval is 10s.
    Second 0:  task called
               task runs
    Second 2:  task called
               task queues up for 8 seconds from now
    Second 3:  task called
               task ignored
    Second 4:  task called
               task ignored
    Second 10: Reqeued task executes
    """
    def wrapped(func):
        @wraps(func)
        def _wrapped(*args, **kwargs):
            ident = hash_func(func, *args, **kwargs)
            lock_key = 'celery:throttle:lock:%d' % ident
            now = int(time.time())
            # Check if there is a lock claimed for this task
            if cache.add(lock_key, now, interval):
                # Nope! Run the actual task
                return func(*args, **kwargs)
            # There is a lock, so we want to check the second lock,
            # which I'm calling the queue lock.
            queue_key = 'celery:throttle:queue:%d' % ident
            # We get what time the actual lock was acquired
            locked = cache.get(lock_key) or now
            delay = interval - (now - locked)
            # Check a lock to see if there's already a task within
            # the interval that is queued
            if cache.add(queue_key, 1, delay):
                # Nope, let's retry this task in the next interval period
                current_task.retry(countdown=delay)
            # The interval period is already locked, and a task is queued.
            # Drop this like a hot potato.
        return _wrapped
    return wrapped


def hash_file(afile, blocksize=65536):
    hasher = hashlib.md5()
    buf = afile.read(blocksize)
    while len(buf) > 0:
        hasher.update(buf)
        buf = afile.read(blocksize)
    return hasher.hexdigest()
