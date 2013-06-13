import concurrent.futures
import multiprocessing
import Queue


class DependentTask(object):
    def __init__(self, callback, tasks, priority):
        self.callback = callback
        self.tasks = tasks
        self.priority = priority

    def task_done(self, task):
        try:
            self.tasks.remove(task)
            return not self.tasks
        except KeyError:
            return False


class TaskRunner(object):
    def __init__(self):
        self.tasks = Queue.PriorityQueue()
        self.tasks_ran = set()
        self.dependencies = dict()

        self.running_threads = 0
        # We'll create these when needed
        self._thread_pool = None
        self._process_pool = None

    def thread_pool(self):
        if self._thread_pool is None:
            self._thread_pool = concurrent.futures.ThreadPoolExecutor(
                    multiprocessing.cpu_count())
        return self._thread_pool

    def process_pool(self):
        if self._process_pool is None:
            self._process_pool = concurrent.futures.ProcessPoolExecutor(
                    multiprocessing.cpu_count())
        return self._process_pool

    def add(self, *tasks, **kwargs):
        callback = kwargs.pop('callback', None)
        priority = kwargs.pop('priority', 100)
        cb_priority = kwargs.pop('cb_priority', 100)
        if kwargs:
            raise TypeError
        if not tasks:
            if callback is not None:
                self.tasks.put((cb_priority, callback))
            return
        for task in tasks:
            self.tasks.put((priority, task))
        if callback is not None:
            dependent = DependentTask(callback, set(tasks), cb_priority)
            for task in tasks:
                self.dependencies.setdefault(task, set()).add(dependent)

    def run_thread(self, callback, task, *args, **kwargs):
        priority = kwargs.pop('cb_priority', 100)
        future = self.thread_pool().submit(task, *args, **kwargs)
        self.running_threads += 1
        def done(runner):
            runner.running_threads -= 1
            callback(future)
        future.add_done_callback(lambda res: self.tasks.put((priority, done)))

    def run_process(self, callback, task, *args, **kwargs):
        priority = kwargs.pop('cb_priority', 100)
        future = self.process_pool().submit(task, *args, **kwargs)
        self.running_threads += 1
        def done(runner):
            runner.running_threads -= 1
            callback(future)
        future.add_done_callback(lambda res: self.tasks.put((priority, done)))

    def execute_tasks(self):
        while True:
            try:
                prio, task = self.tasks.get(self.running_threads > 0)
            except Queue.Empty:
                break
            if isinstance(task, Task):
                self.tasks_ran.add(task)
                task.start(self)
            elif hasattr(task, '__call__'):
                task(self)
                self.task_done(task)
            else:
                raise RuntimeError("Something in task queue is not a task: "
                                   "%r" % (task,))

    def task_done(self, task):
        try:
            dependents = self.dependencies[task]
        except KeyError:
            return
        for dep in list(dependents):
            if dep.task_done(task):
                dependents.remove(dep)
                self.add(dep.callback, priority=dep.priority)
        if not self.dependencies[task]:
            del self.dependencies[task]

    def close(self):
        for task in self.tasks_ran:
            task.reset()
        if self._thread_pool is not None:
            self._thread_pool.shutdown()
        if self._process_pool is not None:
            self._process_pool.shutdown()


class Task(object):
    def __init__(self):
        self.__has_been_run = False
        self._runner = None

    def start(self, runner):
        self._runner = runner
        if not self.__has_been_run:
            self.__has_been_run = True
            self.run()

    def run(self):
        self.done()

    def done(self):
        self._runner.task_done(self)

    def reset(self):
        self.__has_been_run = False
        self._runner = None
