from __future__ import absolute_import, division

import contextlib
import io
import logging
import os
import urllib

from vistrails.core import debug
from vistrails.core.bundles import py_import
from vistrails.core.modules.basic_modules import PathObject
from vistrails.core.modules.config import ModuleSettings
from vistrails.core.modules.vistrails_module import Module, ModuleError, \
    ModuleSuspended
from vistrails.core.vistrail.job import JobMixin


tej = py_import('tej', {'pip': 'tej'})


assert __name__.endswith('.init')
this_pkg = __name__[:-5]


class ServerLogger(tej.ServerLogger):
    def __init__(self):
        self.hidden = False
        tej.ServerLogger.__init__(self)

    @contextlib.contextmanager
    def hide_output(self):
        self.hidden = True
        try:
            yield
        finally:
            self.hidden = False

    def message(self, data):
        if self.hidden:
            debug.debug("tej server: %s" % data)
        else:
            debug.warning("tej server: %s" % data)

ServerLogger = ServerLogger()


class RemoteQueue(tej.RemoteQueue):
    def server_logger(self):
        return ServerLogger


class QueueCache(object):
    """A global cache of RemoteQueue objects.
    """
    def __init__(self):
        self._cache = {}

    def get(self, destination, queue):
        key = destination, queue
        if key in self._cache:
            return self._cache[key]
        else:
            queue = RemoteQueue(destination, queue)
            self._cache[key] = queue
            return queue

QueueCache = QueueCache()


class Queue(Module):
    """A connection to a queue on a remote server.

    `hostname` can be a hostname or a full destination in the format:
    ``[ssh://][user@]server[:port]``, e.g. ``vistrails@nyu.edu``.
    """
    _input_ports = [('hostname', '(basic:String)'),
                    ('username', '(basic:String)',
                     {'optional': True}),
                    ('port', '(basic:Integer)',
                     {'optional': True, 'defaults': "['22']"}),
                    ('queue', '(basic:String)',
                     {'optional': True, 'defaults': "['~/.tej']"})]
    _output_ports = [('queue', '(org.vistrails.extra.tej:Queue)')]

    def compute(self):
        destination_str = self.get_input('hostname')
        if self.has_input('username') or self.has_input('port'):
            destination = {'hostname': destination_str,
                           'username': self.get_input('username'),
                           'port': self.get_input('port')}
            destination_str = tej.destination_as_string(destination)

        queue = self.get_input('queue')
        self.set_output('queue', QueueCache.get(destination_str, queue))


class RemoteJob(object):
    def __init__(self, queue, job_id):
        self.queue = queue
        self.job_id = job_id

    def finished(self):
        try:
            with ServerLogger.hide_output():
                status, target, arg = self.queue.status(self.job_id)
        except tej.JobNotFound:
            # We signal that we are done
            # The Module will raise an error on resume, as intended
            return True
        return status == tej.RemoteQueue.JOB_DONE


class Job(Module):
    """A reference to a job in a queue.

    Objects represented by this type only represent completed jobs, since else,
    the creating module would have failed/suspended.

    You probably won't use this module directly since it references a
    pre-existing job by name.
    """
    _input_ports = [('id', '(basic:String)'),
                    ('queue', Queue)]
    _output_ports = [('job', '(org.vistrails.extra.tej:Job)'),
                     ('exitcode', '(basic:Integer)')]

    def compute(self):
        queue = self.get_input('queue')
        job_id = self.get_input('id')

        # Check job status
        try:
            with ServerLogger.hide_output():
                status, target, arg = queue.status(job_id)
        except tej.JobNotFound:
            raise ModuleError(self, "Job not found")

        # Create job object
        job = RemoteJob(queue=queue, job_id=job_id)

        if status == tej.RemoteQueue.JOB_DONE:
            self.set_output('job', job)
            self.set_output('exitcode', int(arg))
        elif status == tej.RemoteQueue.JOB_RUNNING:
            raise ModuleSuspended(self, "Remote job is running",
                                  handle=job)
        else:
            raise ModuleError(self, "Invalid job status %r" % status)


class BaseSubmitJob(JobMixin, Module):
    """Starts a job on a server.

    Thanks to the suspension/job tracking mechanism, this module does much more
    than start a job. If the job is running, it will suspend again. If the job
    is finished, you can obtain files from it.
    """
    _settings = ModuleSettings(abstract=True)
    _input_ports = [('queue', Queue)]
    _output_ports = [('job', '(org.vistrails.extra.tej:Job)'),
                     ('exitcode', '(basic:Integer)')]

    def make_id(self):
        """Makes a default identifier, using the pipeline signature.

        Unused if we have an explicit identifier.
        """
        if not hasattr(self, 'signature'):
            raise ModuleError(self,
                              "No explicit job ID and module has no signature")
        return "vistrails_module_%s" % self.signature

    def job_read_inputs(self):
        """Reads the input ports.
        """
        return {'destination': self.get_input('queue').destination_string,
                'queue': str(self.get_input('queue').queue),
                'job_id': self.make_id()}

    def job_start(self, params):
        """Submits a job.

        Reimplement in subclasses to actually submit a job.
        """
        raise NotImplementedError

    def job_get_handle(self, params):
        """Gets a RemoteJob object to monitor a runnning job.
        """
        queue = QueueCache.get(params['destination'], params['queue'])
        return RemoteJob(queue, params['job_id'])

    def job_finish(self, params):
        """Finishes job.

        Gets the exit code from the server.
        """
        queue = QueueCache.get(params['destination'], params['queue'])
        status, target, arg = queue.status(params['job_id'])
        assert status == tej.RemoteQueue.JOB_DONE
        params['exitcode'] = int(arg)
        return params

    def job_set_results(self, params):
        """Sets the output ports once the job is finished.
        """
        queue = QueueCache.get(params['destination'], params['queue'])
        self.set_output('exitcode', params['exitcode'])
        self.set_output('job', RemoteJob(queue, params['job_id']))


class SubmitJob(BaseSubmitJob):
    """Submits a generic job (a directory).
    """
    _input_ports = [('job', '(basic:Directory)'),
                    ('script', '(basic:String)',
                     {'optional': True, 'defaults': "['start.sh']"})]

    def job_start(self, params):
        """Sends the directory and submits the job.
        """
        queue = QueueCache.get(params['destination'], params['queue'])

        # First, check if job already exists
        try:
            with ServerLogger.hide_output():
                queue.status(params['job_id'])
        except (tej.JobNotFound, tej.QueueDoesntExist):
            pass
        else:
            return params

        # Alright, submit a new job
        queue.submit(params['job_id'],
                     self.get_input('job').name,
                     self.get_input('script'))
        return params


class SubmitShellJob(BaseSubmitJob):
    """Submits a shell script.
    """
    _settings = ModuleSettings(configure_widget=(
            '%s.widgets' % this_pkg, 'ShellSourceConfigurationWidget'))
    _input_ports = [('source', '(basic:String)')]
    _output_ports = [('stderr', '(basic:File)'),
                     ('stdout', '(basic:File)')]

    _job_interpreter = '/bin/sh'

    def job_start(self, params):
        """Creates a temporary job with the given source, upload and submit it.
        """
        queue = QueueCache.get(params['destination'], params['queue'])

        # First, check if job already exists
        try:
            with ServerLogger.hide_output():
                queue.status(params['job_id'])
        except (tej.JobNotFound, tej.QueueDoesntExist):
            pass
        else:
            return params

        # Alright, submit a new job
        directory = self.interpreter.filePool.create_directory(
                prefix='vt_tmp_shelljob_').name
        # We use io.open() here because we could be writing scripts on Windows
        # before uploading them to a POSIX server
        source = urllib.unquote(self.get_input('source'))
        if isinstance(source, bytes):
            kwargs = {'mode': 'wb'}
        else:
            kwargs = {'mode': 'w', 'newline': '\n'}
        with io.open(os.path.join(directory, 'vistrails_source.sh'),
                     **kwargs) as fp:
            fp.write(source)
        with io.open(os.path.join(directory, 'start.sh'), 'w',
                     newline='\n') as fp:
            fp.write(u'%s '
                     u'vistrails_source.sh '
                     u'>_stdout.txt '
                     u'2>_stderr.txt\n' % self._job_interpreter)

        queue.submit(params['job_id'], directory)

        return params

    def job_set_results(self, params):
        """Gets stderr and stdout.
        """
        super(SubmitShellJob, self).job_set_results(params)

        temp_dir = self.interpreter.filePool.create_directory(
                prefix='vt_tmp_shelljobout_').name
        queue = QueueCache.get(params['destination'], params['queue'])
        queue.download(params['job_id'], ['_stderr.txt', '_stdout.txt'],
                       directory=temp_dir)
        self.set_output('stderr',
                        PathObject(os.path.join(temp_dir, '_stderr.txt')))
        self.set_output('stdout',
                        PathObject(os.path.join(temp_dir, '_stdout.txt')))


class DownloadFile(Module):
    """Downloads a file from a remote job.
    """
    _input_ports = [('job', Job),
                    ('filename', '(basic:String)')]
    _output_ports = [('file', '(basic:File)')]

    def compute(self):
        job = self.get_input('job')
        assert isinstance(job, RemoteJob)

        destination = self.interpreter.filePool.create_file(
                prefix='vt_tmp_shelljobout_')
        job.queue.download(job.job_id,
                           self.get_input('filename'),
                           destination=destination.name,
                           recursive=False)

        self.set_output('file', destination)


class DownloadDirectory(Module):
    """Downloads a directory from a remote job.
    """
    _input_ports = [('job', Job),
                    ('pathname', '(basic:String)')]
    _output_ports = [('directory', '(basic:Directory)')]

    def compute(self):
        job = self.get_input('job')
        assert isinstance(job, RemoteJob)

        destination = self.interpreter.filePool.create_directory(
                prefix='vt_tmp_shelljobout_').name
        target = os.path.join(destination, 'dir')
        job.queue.download(job.job_id,
                           self.get_input('pathname'),
                           destination=target,
                           recursive=True)

        self.set_output('directory', PathObject(target))


_tej_log_handler = None


class _VisTrailsTejLogHandler(logging.Handler):
    def emit(self, record):
        msg = "tej: %s" % self.format(record)
        if record.levelno >= logging.CRITICAL:
            debug.critical(msg)
        elif record.levelno >= logging.WARNING:
            debug.warning(msg)
        elif record.levelno >= logging.INFO:
            debug.log(msg)
        else:
            debug.debug(msg)


def initialize():
    # Route tej log messages to VisTrails
    global _tej_log_handler
    _tej_log_handler = _VisTrailsTejLogHandler()
    tej_logger = logging.getLogger('tej')
    tej_logger.propagate = False
    tej_logger.addHandler(_tej_log_handler)
    tej_logger.setLevel(logging.DEBUG)


def finalize():
    # Unregister logging handler; useful for reloading support
    global _tej_log_handler
    tej_logger = logging.getLogger('tej')
    if _tej_log_handler is not None:
        tej_logger.removeHandler(_tej_log_handler)
        _tej_log_handler = None
    tej_logger.propagate = True


_modules = [Queue,
            Job, BaseSubmitJob, SubmitJob, SubmitShellJob,
            DownloadFile, DownloadDirectory]
