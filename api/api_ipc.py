#!/usr/bin/env python

"""
This module provides the internal IPC interface component for the
WAMP/WebSocket interface. It is instantiated by the WAMP router when the router
starts. See the router configuration file (.crossbar/config.json) for more
information.

Exports:
    Server
        WAMP/WebSocket interface internal IPC component class.
"""

# System modules.
import copy
import uuid

# WAMP-related modules.
from autobahn.twisted.util import sleep
from autobahn.twisted.wamp import ApplicationSession, ApplicationRunner
from autobahn.wamp.exception import ApplicationError
from twisted.internet.defer import inlineCallbacks

# Local modules.
import api_rpc_config


# IPC "Send Message" Procedure URI.
PROC_URI_SEND = "com.lojack.ipc.proc.v1.send"

# IPC "Receive Message" Topic URI.
TOPIC_URI_RECEIVE = "com.lojack.ipc.topic.v1.receive"


_dummy = []

class Server(ApplicationSession):

    """
    Extend the WAMP application component class to handle communications with
    the rest of the system via the internal IPC mechanism.
    """

    @inlineCallbacks
    def onJoin(self, details):
        """
        Invoked after the WAMP router starts the application component and
        joins the component to its configured realm.
        """
        global _dummy

        def send_message(message_info):
            """
            Sends the specified messages to the specified destination.
            """
            # Dummy code to mimic sending to the rest of the system; just
            # append the specified request in the _dummy variable to be picked
            # up by the publish code below.
            global _dummy
            _dummy.append(message_info)

        try:
            # Register the procedure to send requests to other IPC components.
            reg = yield self.register(
                            send_message,
                            PROC_URI_SEND)
            print(
                "Registered procedure '{}' with ID {}".format(
                    PROC_URI_SEND,
                    reg.id))
        except Exception as e:
            raise ApplicationError(
                      "com.lojack.rtu.error.register_proc",
                      "Could not register procedure '{}': {}".format(
                          PROC_URI_SEND,
                          str(e)))
        # Process incoming messages from the IPC interface, forever.
        while True:
			# Allow other processing (i.e., sending of messages) to occur.
            yield sleep(1)
            # Get a dummy counter message every second.
            if len(_dummy) > 0:
                try:
                    message = _dummy.pop(0)
                except Exception as e:
                    raise ApplicationError(
                              "com.lojack.ipc.error.mailbox.receive",
                              "Could not read from IPC interface: "
                                  "{}".format(str(e)))
                else:
                    # Publish the received message.
                    yield self.publish(
                              TOPIC_URI_RECEIVE,
                              message)


_results = {}
_results_procs = {}

class Client(ApplicationSession):

    next_request_id = 0

    def _get_next_request_id(self):
        result = Client.next_request_id
        Client.next_request_id += 1
        if Client.next_request_id == 1000000000:
            Client.next_request_id = 0
        return result

    def _get_resource(self, uri):
        uri_resource_fields = \
            uri.split(
                api_rpc_config.DATA_URI_PREFIX)[-1].split(
                    ".")[2:]
        return {
            "main": uri_resource_fields[0],
            "sub": uri_resource_fields[1:]}

    def _create_ipc_message_general(self, request, resource_sub):
        message_info = {
            "destination": "system_monitor",
            "message": {}}
        if len(resource_sub) > 0:
            message_info["message"]["sub"] = resource_sub[0]
        return message_info

    def _create_ipc_message(self, request):
        global _results_procs
        resource = self._get_resource(request["uri"])
        func = "_".join(["", "create", "ipc", "message", resource["main"]])
        message_info = \
            getattr(
                self,
                func)(
                    request,
                    resource["sub"])
        self.request_id = self._get_next_request_id()
        message_info["message"]["source"] = "www_api"
        message_info["message"]["request_id"] = self.request_id
        _results_procs[self.request_id] = resource["main"]
        return message_info

    def _process_ipc_event_general(self, event):
        result = event
        result["site_id"] = "XX"
        return result

    def _process_ipc_event(self, event):
        global _results
        if hasattr(event, "request_id") and \
           event["request_id"] == self.request_id:
            tmp = event["source"]
            event["source"] = event["destination"]
            event["destination"] = tmp
            func = "_".join(["", "process", "ipc", "event", _results_procs[self.request_id]])
            _results[self.config.extra["result_id"]] = \
                getattr(
                    self,
                    func)(event)
            self.leave()

    @inlineCallbacks
    def onJoin(self, details):
        print "in Client.onJoin, subscribing to:", TOPIC_URI_RECEIVE
        yield self.subscribe(
                  self._process_ipc_event,
                  TOPIC_URI_RECEIVE)
        print "in Client.onJoin, invoking:", PROC_URI_SEND
        yield self.call(
                  PROC_URI_SEND,
                  self._create_ipc_message(self.config.extra["request"]))


class Request(object):

    def process(self, request):
        global _results
        result_id = uuid.uuid4().hex
        print "api_ipc.Request.process: Creating ApplicationRunner"
        runner = ApplicationRunner(
                     "wss://127.0.0.1/api",
                     "ipc",
                     extra = {
                         "request": request,
                         "result_id": result_id})
        print "api_ipc.Request.process: Running ApplicationRunner"
        runner.run(Client)
        print "api_ipc.Request.process: back from ApplicationRunner; "
        print " results:", _results[result_id]
        result = copy.deepcopy(_results[result_id])
        del _results[result_id]
        return result

