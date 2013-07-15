from IPython.parallel import Client

import threading
import time
import contextlib


class SafeClient(object):
    """Wrapper for IPython.parallel.Client adding callbacks for AsyncResults.

    This adds an add_callback() method that can be used to safely get called
    back once a result becomes available. It is safe to wait on different
    results this way and to add callback from different threads.

    This MUST BE used when waiting on AsyncResults from different threads as
    ZeroMQ sockets are not thread-safe.
    """
    def __init__(self, *args, **kwargs):
        self.client = Client(*args, **kwargs)

        self._callback_thread = None
        self._callback_condition = threading.Condition()
        self._callbacks = None

    def add_callback(self, asyncresult, callback):
        """Adds a callback for an AsyncResult.

        The given callback will be called with the asyncresult as argument once
        it becomes available.
        This provides a safe way to wait on several AsyncResult objects from
        different threads, which is impossible otherwise as ZeroMQ is not
        thread-safe.

        A single thread will be started when this method is first called
        """
        item = (set(asyncresult.msg_ids), asyncresult, callback)

        self._callback_condition.acquire()

        if self._callback_thread is None:
            self._callbacks = [item]
            self._callback_thread = threading.Thread(
                    target=self._callback_loop)
            self._callback_thread.start()
        else:
            self._callbacks.append(item)
            self._callback_condition.notify()

        self._callback_condition.release()

    def _callback_loop(self):
        while True:
            self._callback_condition.acquire()
            if self.client._closed:
                break
            if not self._callbacks:
                self._callback_condition.wait()

            if self._callbacks:
                self.client.spin()
                i = 0
                while i < len(self._callbacks):
                    msgs, res, cb = self._callbacks[i]
                    msgs.intersection_update(self.client.outstanding)
                    if not msgs:
                        cb(res)
                        del self._callbacks[i]
                    else:
                        i += 1

            self._callback_condition.release()

            time.sleep(1e-3)

    def close(self):
        self._callback_condition.acquire()
        self.client.close()
        self._callback_condition.notify()
        self._callback_condition.release()

    def lock(self):
        @contextlib.contextmanager
        def acquirelock():
            self._callback_condition.acquire()
            try:
                yield
            finally:
                self._callback_condition.release()
        return acquirelock()

    @property
    def ids(self):
        return self.client.ids

    def direct_view(self, targets='all'):
        @contextlib.contextmanager
        def wrapper():
            self._callback_condition.acquire()
            try:
                yield self.client.direct_view(targets=targets)
            finally:
                self._callback_condition.release()
        return wrapper()

    def load_balanced_view(self, targets='all'):
        @contextlib.contextmanager
        def wrapper():
            self._callback_condition.acquire()
            try:
                yield self.client.load_balanced_view(targets=targets)
            finally:
                self._callback_condition.release()
        return wrapper()

    def shutdown(self, *args, **kwargs):
        self.client.shutdown(*args, **kwargs)
        self.close()
