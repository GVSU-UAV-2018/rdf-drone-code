from __future__ import print_function

"""
Watchdog module.

This module terminates the program if it detects abnormal performance.
"""

import inspect
import signal
import time
import sys

last_keep_alive = None

def on_SIGALRM(_, __):
    print("keep_alive was not called. Last call:", last_keep_alive, file=sys.stderr)
    sys.exit(-1)

signal.signal(signal.SIGALRM, on_SIGALRM)

def keep_alive(seconds):
    """
    Once keep_alive has been called, it must be called repeatedly to avoid
    killing the program. Calling keep_alive(t) keeps the program alive for at
    least t more seconds.

    This turns deadlock, unintended long loops, or severely degraded processing
    performance into an exit condition.
    """
    global last_keep_alive
    old_alarm_seconds = signal.alarm(seconds)
    if old_alarm_seconds > seconds:
        signal.alarm(old_alarm_seconds)

    last_keep_alive = (
        time.clock(),
        inspect.getframeinfo(inspect.currentframe().f_back))