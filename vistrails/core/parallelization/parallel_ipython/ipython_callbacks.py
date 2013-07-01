from IPython.parallel import Client as _Client

import threading
import time
import contextlib


class Client(_Client):
    """Subclass of IPython.parallel.Client adding callbacks for AsyncResults.

    This adds an add_callback() method that can be used to safely get called
    back once a result becomes available. It is safe to wait on different
    results this way and to add callback from different threads.

    This MUST BE used when waiting on AsyncResults from different threads as
    ZeroMQ sockets are not thread-safe.
    """
    def __init__(self, *args, **kwargs):
        _Client.__init__(self, *args, **kwargs)

        self.__callback_thread = None
        self.__callback_condition = threading.Condition()
        self.__callbacks = None

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

        self.__callback_condition.acquire()

        if self.__callback_thread is None:
            self.__callbacks = [item]
            self.__callback_thread = threading.Thread(
                    target=self.__callback_loop)
            self.__callback_thread.start()
        else:
            self.__callbacks.append(item)
            self.__callback_condition.notify()

        self.__callback_condition.release()

    def __callback_loop(self):
        while True:
            self.__callback_condition.acquire()
            if self._closed:
                break
            if not self.__callbacks:
                self.__callback_condition.wait()

            if self.__callbacks:
                self.spin()
                i = 0
                while i < len(self.__callbacks):
                    msgs, res, cb = self.__callbacks[i]
                    msgs.intersection_update(self.outstanding)
                    if not msgs:
                        cb(res)
                        del self.__callbacks[i]
                    else:
                        i += 1

            self.__callback_condition.release()

            time.sleep(1e-3)

    def close(self):
        self.__callback_condition.acquire()
        _Client.close(self)
        self.__callback_condition.notify()
        self.__callback_condition.release()

    def _spin_every(self, *args, **kwargs):
        with self.lock():
            _Client._spin_every(self, *args, **kwargs)

    def lock(self):
        @contextlib.contextmanager
        def acquirelock():
            self.__callback_condition.acquire()
            try:
                yield
            finally:
                self.__callback_condition.release()
        return acquirelock()
