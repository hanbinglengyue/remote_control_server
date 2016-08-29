
import errno
import logging
import os
import signal
import sys
import tempfile
import time
import atexit
import traceback

from PyQt5 import QtCore
from PyQt5 import QtWidgets


_LOCK_FILE = os.path.join(tempfile.gettempdir(), "LarkClient.pid")

_timer = QtCore.QTimer()
_timer.start(1000)


def _touch():
    # _logger.debug("_touch")
    os.utime(_LOCK_FILE)


def _lock():
    if sys.platform == "linux":
        import fcntl
        f = open(_LOCK_FILE, "w")
        fcntl.lockf(f, fcntl.LOCK_EX | fcntl.LOCK_NB)
        atexit.register(os.unlink, _LOCK_FILE)
        atexit.register(fcntl.lockf, f, fcntl.LOCK_UN)
        f.write(str(os.getpid()))

    else:
        fd = os.open(_LOCK_FILE, os.O_CREAT | os.O_EXCL | os.O_RDWR)
        atexit.register(os.unlink, _LOCK_FILE)
        atexit.register(os.close, fd)
        os.write(fd, str(os.getpid()).encode())

    _timer.timeout.connect(_touch)


def _kill():
    with open(_LOCK_FILE) as f:
        pid = int(f.read())
    os.kill(pid, signal.SIGTERM)

try:
    try:
        _lock()
    except OSError as e:
        if e.errno != errno.EEXIST:
            raise

        if os.path.getmtime(_LOCK_FILE) + 5 > time.time():
            raise

        try:
            try:
                _kill()
            except PermissionError:
                pass
        except OSError as e:
            if e.errno != errno.EINVAL:
                print(errno.errorcode[e.errno])
                raise

        timeout = time.time() + 2
        while time.time() < timeout:
            # _logger.debug("wait")
            try:
                os.unlink(_LOCK_FILE)
            except OSError as e:
                if e.errno == errno.ENOENT:
                    break
                if e.errno != errno.EACCES:
                    print(errno.errorcode[e.errno])
                    raise
            time.sleep(0.1)
        _lock()
except Exception as e:
    #text = "".join(traceback.format_exception(*sys.exc_info()))
    #for line in text.strip().split("\n"):
        #Sprint(line)

    QtWidgets.QMessageBox.critical(None, "警告", "远程桌面已启动!")

    sys.exit(0)
