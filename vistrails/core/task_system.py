"""A task system running a dynamic graph of tasks while respecting priorities.

This runs the task you add to it, which can in turn add new tasks, calling you
back when the tasks you are waiting on are done. It also respects priorities.
"""


import Queue
import warnings


@apply
class empty_contextmanager(object):
    def __enter__(self):
        pass
    def __exit__(self, exc_type, exc_value, traceback):
        pass
    def __call__(self):
        return self


class DependentTask(object):
    """Structure used internally to keep track of a dependency.

    This stores a task and its dependencies, so that when every dependency has
    been dealt with, we can add the task, with the correct priority.
    """
    def __init__(self, callback, tasks, priority, inh_priority):
        self.callback = callback
        self.tasks = tasks
        self.priority = priority
        # Tuple of priorities of upstream tasks' callbacks for the callback
        # task
        # This allows us to get to more urgent callbacks first
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


class AsyncTask(object):
    """Keeps the execution context to execute another task later.

    Tasks that run in the background without the TaskRunner managing them
    should call make_async_task() to signal that a task is yet to finish.
    It will store the current context so that callback() can add a task
    correctly.

    When the background task is finished, call callback() with the wanted
    callback function. It will signal the TaskRunner that there is no
    background task anymore, and will call the given callback on the main
    thread.

    This is intended to be used with futures, for instance:
    future = executor.submit(somefunc)
    async_task = runner.make_async_task()
    future.add_done_callback(lambda: async_task.callback(more_stuff))
    """
    def __init__(self, runner, inherited_priority):
        self.runner = runner
        self.runner.running_threads += 1
        self.inherited_priority = inherited_priority

    def callback(self, callback, priority=100):
        self.runner.running_threads -= 1
        self.runner.tasks.put((priority, self.inherited_priority, callback))
        self.runner = None


class TaskRunner(object):
    """The main object keeping track of and running the tasks.

    A Task is either a Task instance (which allows for complex tasks, that are
    not done immediately, but can add more tasks and call done() when
    completed) or a callable (which is considered completed as soon as it
    returns).

    Tasks can be added via the add() method, which takes a bunch of tasks and a
    callback task.

    execute_tasks() starts the main loop, which will return when every task and
    thread have completed.
    """
    def __init__(self):
        self.tasks = Queue.PriorityQueue()
        self.tasks_ran = set()
        self.dependencies = dict()

        self.running_threads = 0

        self._inherited_priority = ()

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
            inh_priority = self._inherited_priority
        inh_priority += (cb_priority,)
        # Add tasks
        for task in tasks:
            self.tasks.put((priority, inh_priority, task))
        if callback is not None:
            dependent = DependentTask(callback, set(tasks),
                                      cb_priority, self._inherited_priority)
            for task in tasks:
                self.dependencies.setdefault(task, set()).add(dependent)

    def make_async_task(self):
        return AsyncTask(self, self._inherited_priority)

    def execute_tasks(self, task_hook=empty_contextmanager):
        """Main loop executing tasks until there is nothing more to run.

        Will emit a RuntimeWarning if tasks remain at the end (if for some
        tasks, Task#done() was never called).

        task_hook is an optional context manager generator that is used around
        task execution. It can be used to catch some exceptions and allow the
        runner to continue; else, exceptions are propagated and end the
        execution.
        Note that the object will be called before being used as a context
        manager:
        with task_hook(): # note the ()
        """
        while True:
            try:
                prio, inh_prio, task = self.tasks.get(self.running_threads > 0)
            except Queue.Empty:
                break
            self._inherited_priority = inh_prio
            if isinstance(task, Task):
                self.tasks_ran.add(task)
                with task_hook():
                    task.start(self)
            elif hasattr(task, '__call__'):
                done = False
                with task_hook():
                    task()
                    done = True
                if done:
                    self.task_done(task)
            else:
                raise RuntimeError("Something in task queue is not a task: "
                                   "%r" % (task,))

        # This is now disabled since task_hook was added, because as it can
        # catch exceptions, we can continue executing while tasks failed
        # These failed tasks prevent their dependent tasks from running, and it
        # is intended
        if False:
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
                self.tasks.put((dep.priority, dep.inh_priority, dep.callback))
        if not self.dependencies[task]:
            del self.dependencies[task]

    def close(self):
        """Terminates the runner.

        This will shutdown the Executors and call reset() on the Tasks.
        """
        for task in self.tasks_ran:
            task.reset()
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
        self.__started = False
        self.__finished = False
        self._runner = None

    def start(self, runner):
        self._runner = runner
        if not self.__started:
            self.__started = True
            self.run()
        elif self.__finished:
            self.done()

    def run(self):
        """You should override this method. By default, just call done().
        """
        self.done()

    def done(self):
        """Indicates that this task has been completed and callback can run.
        """
        self.__finished = True
        self._runner.task_done(self)

    def reset(self):
        """Called by TaskRunner#close().

        Resets the task so it can be run again.
        """
        self.__started = False
        self.__finished = False
        self._runner = None

###############################################################################


import unittest
import time


class TestNode(Task):
    prio = 100

    def __init__(self, name, exe_list, upstream=[]):
        self.name = name
        Task.__init__(self)
        self.exe_list = exe_list
        self.upstream = upstream

    def run(self):
        self.exe_list.append('init %s' % self)
        self._runner.add(*self.upstream, callback=self.upstream_done,
                         priority=10,
                         cb_priority=self.prio)

    def upstream_done(self):
        self.exe_list.append('compute %s' % self)
        self.done()

    def __str__(self):
        return self.name
    __repr__ = __str__
    def __eq__(self, other):
        return self is other
    def __lt__(self, other):
        return self.name < other.name


class TestPrioNode(TestNode):
    prio = 50

    def upstream_done(self):
        self.exe_list.append('compute %s' % self)
        self.done()


class TestBackgroundNode(TestPrioNode):
    def upstream_done(self):
        self.exe_list.append('compute_start %s' % self)
        future = TestScheduler.thread_pool.submit(lambda: time.sleep(0.5))
        async_task = self._runner.make_async_task()

        def done_task():
            self.exe_list.append('compute_end %s' % self)
            self.done()
        def thread_done(result):
            async_task.callback(done_task)
        future.add_done_callback(thread_done)


class TestScheduler(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from concurrent.futures.thread import ThreadPoolExecutor
        cls.thread_pool = ThreadPoolExecutor(4)

    @classmethod
    def tearDownClass(cls):
        cls.thread_pool.shutdown()

    def run_graph(self, *sinks):
        runner = TaskRunner()
        runner.add(*sinks, priority=10)
        runner.execute_tasks()
        runner.close()

    def test_simple_1(self):
        l = []
        self.run_graph(
            TestNode('5m', l, [
                TestNode('3m', l, [
                    TestNode('1m', l),
                ]),
                TestPrioNode('4t', l, [
                    TestNode('2m', l),
                ]),
            ]),
         )
        self.assertEqual(l, [
                'init 5m',
                'init 3m',
                'init 4t',
                'init 2m',
                'init 1m',
                'compute 2m',
                'compute 4t',
                'compute 1m',
                'compute 3m',
                'compute 5m'])

    def test_simple_2(self):
        l = []
        self.run_graph(
            TestNode('5m', l, [
                TestPrioNode('3t', l, [
                    TestNode('1m', l),
                ]),
                TestNode('4m', l, [
                    TestNode('2m', l),
                ]),
            ]),
        )
        self.assertEqual(l, [
                'init 5m',
                'init 3t',
                'init 4m',
                'init 1m',
                'init 2m',
                'compute 1m',
                'compute 3t',
                'compute 2m',
                'compute 4m',
                'compute 5m'])

    def test_long(self):
        l = []
        self.run_graph(
            TestNode('8m', l, [
                TestPrioNode('2t', l, [
                    TestNode('1m', l),
                ]),
                TestNode('4m', l, [
                    TestNode('3m', l),
                ]),
                TestNode('7m', l, [
                    TestPrioNode('6t', l, [
                        TestNode('5m', l),
                    ]),
                ]),
            ]),
        )
        self.assertEqual(l, [
                'init 8m',
                'init 2t',
                'init 4m',
                'init 7m',
                'init 1m',
                'init 3m',
                'init 6t',
                'init 5m',
                'compute 1m',
                'compute 2t',
                'compute 5m',
                'compute 6t',
                'compute 3m',
                'compute 4m',
                'compute 7m',
                'compute 8m'])

    def test_threaded(self):
        l = []
        self.run_graph(
            TestNode('5m', l, [
                TestBackgroundNode('3t', l, [
                    TestNode('1m', l),
                ]),
                TestNode('4m', l, [
                    TestNode('2m', l),
                ]),
            ]),
        )
        self.assertEqual(l, [
                'init 5m',
                'init 3t',
                'init 4m',
                'init 1m',
                'init 2m',
                'compute 1m',
                'compute_start 3t',
                'compute 2m',
                'compute 4m',
                'compute_end 3t',
                'compute 5m'])
