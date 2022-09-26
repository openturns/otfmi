# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""
"""

import time

path_log = "%s_fmupool.log" % time.strftime("%y-%m-%d_%H-%M-%S", time.gmtime())


def log(text, record_time=True, path_log=path_log):
    """Append text to log file.

    Parameters
    ----------
    text : String, text to write.

    record_time : Boolean, whether to prepend time before text.

    path_log : String, path to log file.

    """

    if record_time:
        text = "[%s] %s" % (current_time(), text)
    with open(path_log, "a") as f:
        f.write(text + "\n")


def current_time():
    """Format current time as a string."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())
