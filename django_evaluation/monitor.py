"""
This is an example code for restarting after code changes from
http://code.google.com/p/modwsgi/wiki/ReloadingSourceCode#Restarting_Daemon_Processes
"""

import atexit
import os
import queue
import signal
import sys
import threading

_interval = 1.0
_times = {}
_files = []

_running = False
_queue = queue.Queue()
_lock = threading.Lock()


def _restart(path=None):
    """
    The restart routine has been slightly modified to allow a restart by
    a super-user.
    """
    _queue.put(True)

    if path is None:
        prefix = "(pid=%d)" % os.getpid()
        print >> sys.stderr, "Restart process %s by super-user." % prefix
    else:
        prefix = "monitor (pid=%d):" % os.getpid()
        print >> sys.stderr, "%s Change detected to '%s'." % (prefix, path)
        print >> sys.stderr, "%s Triggering process restart." % prefix

    os.kill(os.getpid(), signal.SIGINT)


def _modified(path):
    try:
        # If path doesn't denote a file and were previously
        # tracking it, then it has been removed or the file type
        # has changed so force a restart. If not previously
        # tracking the file then we can ignore it as probably
        # pseudo reference such as when file extracted from a
        # collection of modules contained in a zip file.

        if not os.path.isfile(path):
            return path in _times

        # Check for when file last modified.

        mtime = os.stat(path).st_mtime
        if path not in _times:
            _times[path] = mtime

        # Force restart when modification time has changed, even
        # if time now older, as that could indicate older file
        # has been restored.

        if mtime != _times[path]:
            return True
    except:
        # If any exception occurred, likely that file has been
        # been removed just before stat(), so force a restart.

        return True

    return False


def _monitor():
    while 1:
        # Check modification times on all files in sys.modules.

        for module in sys.modules.values():
            if not hasattr(module, "__file__"):
                continue
            path = getattr(module, "__file__")
            if not path:
                continue
            if os.path.splitext(path)[1] in [".pyc", ".pyo", ".pyd"]:
                path = path[:-1]
            if _modified(path):
                return _restart(path)

        # Check modification times on files which have
        # specifically been registered for monitoring.

        for path in _files:
            if _modified(path):
                return _restart(path)

        # Go to sleep for specified interval.

        try:
            return _queue.get(timeout=_interval)
        except:
            pass


_thread = threading.Thread(target=_monitor)
_thread.setDaemon(True)


def _exiting():
    try:
        _queue.put(True)
    except:
        pass
    try:
        _thread.join()
    except RuntimeError:
        pass


atexit.register(_exiting)


def track(path):
    if path not in _files:
        _files.append(path)


def start(interval=1.0):
    global _interval
    if interval < _interval:
        _interval = interval

    global _running
    _lock.acquire()
    if not _running:
        prefix = "monitor (pid=%d):" % os.getpid()
        sys.stderr.write("%s Starting change monitor.\n" % prefix)
        _running = True
        _thread.start()
    _lock.release()
