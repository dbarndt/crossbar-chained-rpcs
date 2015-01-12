#!/usr/bin/env python

"""
This module provides a component for the WAMP router (ex. Crossbar.io) to
authenticate WAMP client connections/sessions. It is instantiated by the WAMP
router when the router starts. See the router configuration file
(.crossbar/config.json) for details.

Exports:
    Authenticator
        WAMP router authentication component class.
"""

# WAMP-related modules.
from autobahn.twisted.wamp import ApplicationSession
from autobahn.wamp.exception import ApplicationError
from twisted.internet.defer import inlineCallbacks


# Authentication Procedure URI.
PROC_URI = "com.lojack.wamp.proc.v1.authenticate"


class Authenticator(ApplicationSession):

    """
    Extend the WAMP application component class to register an authentication
    procedure with the WAMP router that instantiated the class/component.
    """

    @inlineCallbacks
    def onJoin(self, details):
        """
        Invoked after the WAMP router starts the application component and
        joins the component to its configured realm.
        """

        def authenticate(realm, authid, ticket):
            """
            Authenticate the specified WAMP authid (user) and ticket (password).
            """
            # User authenticated! Return the authorized role for this
            # user (which is just their username).
            return authid

        # Register the above authentication procedure and the URI that
        # will be used to invoke it (must match the configured URI in
        # the router configuration; see .crossbar/config.json).
        try:
            reg = yield self.register(
                            authenticate,
                            PROC_URI)
            print(
                "Registered procedure '{}' with ID {}".format(
                    PROC_URI,
                    reg.id))
        except Exception as e:
            raise ApplicationError(
                      "com.lojack.wamp.error.register_proc",
                      "Could not register procedure '{}': {}".format(
                          PROC_URI,
                          str(e)))

