#!/usr/bin/env python

"""
This module provides general system information support for the
WAMP/WebSocket interface.
"""

# Local modules.
import api_ipc

def data_v1_proc_v1_read(request, details):
    """
    Read and return some or all of the general application information
    (depending on what was requested).
    """
    print "Invoking api_ipc.Request().process, request:", request
    return api_ipc.Request().process(request)

