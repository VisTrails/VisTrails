"""A task system running a dynamic graph of tasks while respecting priorities.

This runs the task you add to it, which can in turn add new tasks, calling you
back when the tasks you are waiting on are done. It also respects priorities,
and can run tasks in a thread or process as well.
"""


import concurrent.futures
import multiprocessing
import Queue
import sys
import warnings


class DependentTask(object):
    """Structure used internally to keep track of a dependency.

    This stores a task and its dependencies, so that when every dependency has
    been dealt with, we can add the task, with the correct priority.
    """
    def __init__(self, callback, tasks, priority, inh_priority):
        self.callback = callback
        self.tasks = tasks
        self.priority = priority
        self.inh_priority = inh_priority

    def task_done(self, task):
        """Called when a task is done to remove the dependency.

        Returns True if this task has no more dependency; in this case, the
        dependent task should be added.
        """
        try:
            self.tasks.remove(task)
            return not self.tasks
        except KeyError:
            return False


class TaskRunner(object):
    """The main object keeping track of and running the tasks.

    A Task is either a Task instance (which allows for complex tasks, that are
    not done immediately, but can add more tasks and call done() when
    completed) or a callable (which is considered completed as soon as it
    returns).

    Tasks can be added via the add() method, which takes a bunch of tasks and a
    callback task.
    They can also be run in parallel via run_thread() and run_process(), via
    concurrent.futures.

    execute_tasks() starts the main loop, which will return when every task and
    thread have completed.
    """
    def __init__(self):
        self.tasks = Queue.PriorityQueue()
        self.tasks_ran = set()
        self.dependencies = dict()

        self.running_threads = 0
        # We'll create these when needed
        self._thread_pool = None
        self._process_pool = None

        self._inherited_priority = sys.maxint

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
        """Adds a group of tasks to be run, and a callback.

        The given 'tasks' will be run with the given 'priority'. When they all
        have completed, the 'callback' task will be added with the
        'cb_priority'. All priorities default to 100.

        Note that the given priority overrides any inherited priority, so that
        the priority of dependent tasks will only be considered to choose
        between tasks of the same explicit priority.

        If 'tasks' is empty, the 'callback' task will be added with
        'cb_priority' right away.
        """
        # Get keyword-only arguments
        callback = kwargs.pop('callback', None)
        priority = kwargs.pop('priority', 100)
        cb_priority = kwargs.pop('cb_priority', 100)
        inh_priority = kwargs.pop('inh_priority', None)
        if kwargs:
            raise TypeError

        # No tasks: add the callback
        if not tasks:
            if callback is not None:
                self.tasks.put(
                        (cb_priority, self._inherited_priority, callback))
            return

        # Compute inherited priority from the currently running task
        if inh_priority is None:
            inh_priority = min(cb_priority, self._inherited_priority)
        # Add tasks
        for task in tasks:
            self.tasks.put((priority, inh_priority, task))
        if callback is not None:
            dependent = DependentTask(callback, set(tasks),
                                      cb_priority, self._inherited_priority)
            for task in tasks:
                self.dependencies.setdefault(task, set()).add(dependent)

    def run_thread(self, callback, task, *args, **kwargs):
        """Runs a thread and add the callback task on completion.

        Note that there is no priority between threads, as they are submitted
        to the ThreadPoolExecutor right away.

        Also note that 'task' should be a callable, Task instances are not
        expected here.
        """
        priority = kwargs.pop('cb_priority', 100)
        future = self.thread_pool().submit(task, *args, **kwargs)
        self.running_threads += 1
        def done(runner):
            runner.running_threads -= 1
            callback(future)
        future.add_done_callback(lambda res: self.tasks.put(
                (priority, self._inherited_priority, done)))

    def run_process(self, callback, task, *args, **kwargs):
        """Runs a process and add the callback task on completion

        Note that there is no priority between processes, as they are submitted
        to the ProcessPoolExecutor right away.

        Also note that 'task' should be a callable, Task instances are not
        expected here. It should be pickleable, as multiprocessing needs it.
        """
        priority = kwargs.pop('cb_priority', 100)
        future = self.process_pool().submit(task, *args, **kwargs)
        self.running_threads += 1
        def done(runner):
            runner.running_threads -= 1
            callback(future)
        future.add_done_callback(lambda res: self.tasks.put(
                (priority, self._inherited_priority, done)))

    def execute_tasks(self):
        """Main loop executing tasks until there is nothing more to run.

        Will emit a RuntimeWarning if tasks remain at the end (if for some
        tasks, Task#done() was never called).
        """
        while True:
            try:
                prio, inh_prio, task = self.tasks.get(self.running_threads > 0)
            except Queue.Empty:
                break
            self._inherited_priority = inh_prio
            if isinstance(task, Task):
                self.tasks_ran.add(task)
                task.start(self)
            elif hasattr(task, '__call__'):
                task(self)
                self.task_done(task)
            else:
                raise RuntimeError("Something in task queue is not a task: "
                                   "%r" % (task,))

        for deps in self.dependencies.itervalues():
            if any(dep.tasks for dep in deps):
                warnings.warn("Some tasks were never completed, but we don't have "
                              "anything left to run (did you forget to call "
                              "done()?)",
                              RuntimeWarning,
                              stacklevel=2)
                break

    def task_done(self, task):
        """Internal method, called from Task#done().

        Update (and eventually, add) dependent tasks.
        """
        try:
            dependents = self.dependencies[task]
        except KeyError:
            return
        for dep in list(dependents):
            if dep.task_done(task):
                dependents.remove(dep)
                self.add(dep.callback,
                         priority=dep.priority, inh_priority=dep.inh_priority)
        if not self.dependencies[task]:
            del self.dependencies[task]

    def close(self):
        """Terminates the runner.

        This will shutdown the Executors and call reset() on the Tasks.
        """
        for task in self.tasks_ran:
            task.reset()
        if self._thread_pool is not None:
            self._thread_pool.shutdown()
        if self._process_pool is not None:
            self._process_pool.shutdown()
        self.dependencies = None


class Task(object):
    """Base class for the Tasks.

    TaskRunner also accepts callable objects instead.

    You just have to override run() to do what you want. You can add more
    tasks from run() using self._runner.add(); don't forget to call done() when
    the Task is completed so that callbacks get run.

    No matter how many times it is added, a Task will only be run once on a
    TaskRunner (it is reset by TaskRunner#close()).
    """
    def __init__(self):
        self.__has_been_run = False
        self._runner = None

    def start(self, runner):
        self._runner = runner
        if not self.__has_been_run:
            self.__has_been_run = True
            self.run()

    def run(self):
        """You should override this method. By default, just call done().
        """
        self.done()

    def done(self):
        """Indicates that this task has been completed and callback can run.
        """
        self._runner.task_done(self)

    def reset(self):
        """Called by TaskRunner#close().

        Resets the task so it can be run again.
        """
        self.__has_been_run = False
        self._runner = None
