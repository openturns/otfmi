# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""
"""

import sys
import time

path_log = "%s_fmupool.log" % time.strftime("%y-%m-%d_%H-%M-%S", time.gmtime())


def log(text, record_time=True, path_log=path_log):
    """Append text to log file.

    Parameters
    ----------
    text : str
        text to write.
    record_time : bool
        whether to prepend time before text.
    path_log : str
        path to log file.
    """

    if record_time:
        text = "[%s] %s" % (current_time(), text)

    try:
        with open(path_log, "a") as f:
            f.write(text + "\n")
    except Exception:
        sys.stderr.write(f"otfmi could not write to {path_log}\n")


def current_time():
    """Format current time as a string."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
