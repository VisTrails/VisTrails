import threading

##############################################################################

_lock = threading.Lock()
def get_interpreter_lock():
    return _lock
