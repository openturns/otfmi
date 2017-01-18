# -*- coding: utf-8 -*-
# Copyright 2016 EDF. This software was developed with the collaboration of
# Phimeca Engineering (Sylvain Girard, girard@phimeca.com).
"""
"""

#§
import time
# import gmtime, strftime

path_log = "fmupool.log"

def log(text, record_time=True, path_log=path_log):
    """Append text to log file.

    Parameters:
    ----------
    text : String, text to write.

    record_time : Boolean, wether to prepend time before text.

    path_log : String, path to log file.

    """

    if record_time:
        text = "%s: %s" % (current_time(), text)
    with open(path_log, "a") as f:
        f.write(text + "\n")

def current_time():
    """Format current time as a string."""
    return time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())



#§
# Local Variables:
# tmux-temp-file: "/home/girard/.tmp/tmux_buffer"
# tmux-repl-window: "fmot"
# End:
