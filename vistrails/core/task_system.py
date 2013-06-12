import concurrent.futures
import multiprocessing
import Queue
import warnings


class DependentTask(object):
    def __init__(self, callback, tasks):
        self.callback = callback
        self.tasks = tasks

    def task_done(self, task):
        try:
            self.tasks.remove(task)
            return not self.tasks
        except KeyError:
            return False


def default_prio(prio, task):
    if isinstance(task, (tuple, list)):
        return task
    else:
        return prio, task


def remove_prio(task):
    if isinstance(task, (tuple, list)):
        return task[1]
    else:
        return task


class UsageWarning(UserWarning):
    pass


def remove_prio_warn(task, stacklevel=2):
    if isinstance(task, (tuple, list)):
        warnings.warn(
                "Got unexpected (prio, task) pair, ignoring priority",
                UsageWarning,
                stacklevel=stacklevel+1)
        return task[1]
    else:
        return task


class TaskRunner(object):
    def __init__(self):
        self.tasks = Queue.PriorityQueue()
        self.tasks_ran = set()
        self.dependencies = dict()

        self.running_threads = 0
        self.thread_pool = concurrent.futures.ThreadPoolExecutor(
                multiprocessing.cpu_count())

    def add(self, *tasks, **kwargs):
        callback = kwargs.pop('callback', None)
        if kwargs:
            raise TypeError
        if not tasks:
            if callback is not None:
                prio, callback = default_prio(100, callback)
                self.tasks.put((prio, callback))
            return
        for task in tasks:
            prio, task = default_prio(100, task)
            self.tasks.put((prio, task))
        if callback is not None:
            tasks = [remove_prio(task) for task in tasks]
            dependent = DependentTask(callback, set(tasks))
            for task in tasks:
                self.dependencies.setdefault(task, set()).add(dependent)

    def run_thread(self, callback, task, *args, **kwargs):
        task = remove_prio_warn(task)
        prio, callback = default_prio(100, callback)
        future = self.thread_pool.submit(task, *args, **kwargs)
        self.running_threads += 1
        def done(runner):
            runner.running_threads -= 1
            callback(future)
        future.add_done_callback(lambda res: self.tasks.put((prio, done)))

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
                self.add(dep.callback)
        if not self.dependencies[task]:
            del self.dependencies[task]

    def close(self):
        for task in self.tasks_ran:
            task.reset()


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
