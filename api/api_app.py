#!/usr/bin/env python

"""
This module is instantiated by the WAMP router when the router starts. See
the router configuration file (.crossbar/config.json) for more information.

Exports:
    Application
        WAMP/WebSocket interface application component class.
"""

# WAMP-related modules.
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
from autobahn.wamp.types import RegisterOptions
from twisted.internet.defer import inlineCallbacks

# Local modules.
import api_rpc


class Application(ApplicationSession):

    """
    Extend the WAMP application component class to register the application's
    RPC procedures with the WAMP router that instantiated the class/component.
    """

    @inlineCallbacks
    def onJoin(self, details):
        """
        Invoked after the WAMP router starts the application component and
        joins the component to its configured realm.
        """
        # Register each configured application WAMP RPC procedure.
        # (see api_rpc.py and api_rpc_config.py modules).
        for proc in api_rpc.PROCS:
            try:
                # Each procedure registration must specify a reference to the
                # procedure and the URI that will be used to invoke it. All
                # procedures are registered with the ability to return
                # in-progress results in addition to a final result.
                reg = yield self.register(
                                proc["proc"],
                                proc["uri"],
                                RegisterOptions(details_arg = "details"))
                print(
                    "Registered procedure {} for URI '{}' with ID {}".format(
                        proc["proc"],
                        proc["uri"],
                        reg.id))
            except Exception as e:
                raise ApplicationError(
                          "com.lojack.rtu.error.register_proc",
                          "Could not register procedure {} "
                              "for URI '{}': {}".format(
                                  proc["proc"],
                                  proc["uri"],
                                  str(e)))

