#!/usr/bin/env python

"""
This module provides the Remote Procedure Call (RPC) support for the
WAMP/WebSocket interface.

This module dynamically creates the RPC procedures based on information in the
api_rpc_config module. This information consists of two main parts:

  1) Procedure resources. These include the interface version to which a
     procedure belongs and a unique procedure name. The final procedure name
     is constructed from both pieces of information. For example, specifying
     a version of "v1" and a name of "read" results in the dynamic creation
     of a procedure named "v1_read" belonging to this module. All created
     procedures are required to take a dictionary as an argument; the
     dictionary must contain the data URI upon which the procedure is to
     operate, as well as any additional parameters needed for the operation.
     All created procedures are also registered with the possibility of
     returning in-progress results to the caller (see the "In-Progress Results"
     section below).

     Example:

         Configuration (api_rpc_config.py):
             PROC_URI_PREFIX = "com.lojack.rtu.proc"
             PROCS = {"v1": ["create", "read", "update", "delete"]}

         Procedure URIs created:
             "com.lojack.rtu.proc.v1.create"
             "com.lojack.rtu.proc.v1.read"
             "com.lojack.rtu.proc.v1.update"
             "com.lojack.rtu.proc.v1.delete"

         RPC procedures created:
             api_rpc.v1_create
             api_rpc.v1_read
             api_rpc.v1_update
             api_rpc.v1_delete

         Example subsequent RPC procedure argument:
             {"uri": "com.lojack.rtu.data.v2.config", "access_level": "ljadmin"}

  2) Data resources. These include the interface version to which a data
     resource belongs, a unique data resource name, and the procedures
     created above which are supported by the data resource. These are used
     to determine the name of the Python module and methods that should invoked
     to manipulate the data. For example, if "v2" of a "config" data resource
     supports the "v1" "read" procedure, then there should be a "uri_config"
     module with a "v2_v1_read" method implemented.

     Example:

         Configuration (rpc_config.py):
             DATA_URI_PREFIX = "com.lojack.rtu.data"
             DATA_PROCS = {"v2": {"config": {"v1": ["read", "update"]}}}

         URI supported:
             "com.lojack.rtu.data.v2.config"

         Procedures invoked for the above URI:
             uri_config.v2_v1_read
             uri_config.v2_v1_update

Exports:
    All procedures configured via the api_rpc_config module's PROCS list,
    exported via this module's PROCS list. Each member of this module's PROCS
    list specifies the URI for the procedure and the actual procedure to be
    invoked.

    Example:

        PROCS = [{"proc": api_rpc.v1_read,
                  "uri": "com.lojack.rtu.proc.v1.read"}]

In-Progress Results:
    Note that any procedure can (but is not required to) implement and return
    in-progress results by implementing a "details" argument after the main
    "data" object argument. This "details" argument should have a "progress"
    property that the procedure checks.

    Example:

        Module: my_module

        def my_func(data, details):
            if details.progress:
                # Client requested in-progress results; return 5 in-progress
                # results with the value of i as the payload.
                for i in range(5):
                    details.progress(i)
                    yield sleep(1)
                # Return a final result
                final_result = "in-progress done"
            else:
                # Client did not request progress;
                # return a single result
                final_result = "normal done"
            return final_result
"""

# System modules.
import sys

# WAMP-related modules.
from autobahn.wamp.exception import ApplicationError

# Local modules.
import api_rpc_config


def _exec_proc(proc_version, proc_name, proc_uri, data, details):
    """
    Internal procedure invoked from all exported, dynamically-generated
    RPC procedures.
    """
    # Ensure that a data URI has been specified.
    if not isinstance(data, dict) or \
       not "uri" in data:
        raise ApplicationError(
                  "com.lojack.rtu.error.rpc_data_uri_missing",
                  "RPC calls must specify a dictionary with a 'uri' "
                      "property specifying a data URI")
    # Ensure that the specified data URI is supported (defined in the RPC
    # configuration).
    for data_version, \
        data_resources_info in api_rpc_config.DATA_PROCS.iteritems():
        # ex. data_version = "v2",
        #     data_resources_info =
        #         {"config": {"procs": {"v1": ["read", "update"]}}}
        for data_resource_name, \
            data_resource_info in data_resources_info.iteritems():
            # ex. data_resource_name = "config",
            #     data_resource_info =
            #         {"procs": {"v1": ["read", "update"]}}
            data_uri = \
                ".".join([
                    api_rpc_config.DATA_URI_PREFIX,
                    data_version,
                    data_resource_name])
            if data_uri != data["uri"]:
                if "data" in data_resource_info:
                    # This resource contains "sub-resources" that could match
                    # the specified data URI; for example:
                    # "com.lojack.rtu.data.v2.general.site_id"
                    #                         ^^^^^^^ ^^^^^^^
                    #                         main    sub-resource
                    for data_resource_name_sub in data_resource_info["data"]:
                        data_uri = \
                            ".".join([
                                api_rpc_config.DATA_URI_PREFIX,
                                data_version,
                                data_resource_name,
                                data_resource_name_sub])
                        if data_uri == data["uri"]:
                            break
            # ex. data_uri = "com.lojack.rtu.data.v2.config"
            if data_uri == data["uri"]:
                # Found the specified data URI in the internal configuration;
                # ensure the configuration indicates this procedure is
                # supported for this data URI.
                for data_proc_version, \
                    data_proc_names in data_resource_info["procs"].iteritems():
                    if proc_version == data_proc_version and \
                        proc_name in data_proc_names:
                        # This procedure is supported for this data URI; import
                        # the module and ensure it implements the procedure.
                        try:
                            print "Dynamically importing 'uri_{}' module".format(
                                      data_resource_name)
                            data_proc_module = \
                                __import__("uri_" + data_resource_name)
                        except Exception as e:
                            raise ApplicationError(
                                      "com.lojack.rtu.error.rpc_module_import",
                                      "Could not import the 'uri_{}' module "
                                          "(data URI: '{}'): "
                                          "{}".format(
                                              data_resource_name,
                                              data_uri,
                                              str(e)))
                        data_proc_name_versioned = \
                            "_".join([
                                "data",
                                data_version,
                                "proc",
                                proc_version,
                                proc_name])
                        if hasattr(data_proc_module, data_proc_name_versioned):
                            # The procedure is implemented; invoke it, passing
                            # along the specified data (and possible in-progress
                            # results enabler), and return the result.
                            print "Invoking 'uri_{}.{}' method; " \
                                      " data = {}".format(
                                          data_resource_name,
                                          data_proc_name_versioned,
                                          data)
                            return getattr(
                                       data_proc_module,
                                       data_proc_name_versioned)(
                                           data,
                                           details)
                        raise ApplicationError(
                                  "com.lojack.rtu.error.rpc_not_implemented",
                                  "Could not process the data URI '{}' "
                                      "for the '{}' procedure: A '{}' "
                                      "procedure is not implemented in the "
                                      "'uri_{}' module".format(
                                          data_uri,
                                          proc_uri,
                                          data_proc_name_versioned,
                                          data_resource))
                raise ApplicationError(
                          "com.lojack.rtu.error.rpc_not_implemented",
                          "Could not process the data URI '{}' "
                              "for the '{}' procedure: A '{}' '{}'"
                              "procedure is not specified in the internal "
                              "RPC configuration for the '{}' module".format(
                                  data_uri,
                                  proc_uri,
                                  proc_version,
                                  proc_name,
                                  data_resource))
    raise ApplicationError(
              "com.lojack.rtu.error.rpc_data_uri_unsupported",
              "Data URI '{}' is not supported by the "
                  "'{}' procedure".format(
                      data["uri"],
                      proc_uri))

def _make_proc(proc_version, proc_name, proc_uri):
    """
    Internal procedure to dynamically create a procedure with a versioned
    name, to be associated with the specified procedure URI.
    """
    # Create a closure and name it with the versioned procedure name.
    def _proc_template(data, details = None):
        return _exec_proc(proc_version, proc_name, proc_uri, data, details)
    _proc_template.__name__ = "_".join([proc_version, proc_name])
    return _proc_template


# Procedures exported from this module.
PROCS = []

# Create the procedures to be exported from this module, based on the
# configuration.
this_module = sys.modules[__name__]
for proc_version, proc_names in api_rpc_config.PROCS.iteritems():
    # ex. proc_version = "v1",
    #     proc_names = ["create", "read", "update", "delete"]
    proc_uri_prefix_versioned = \
        ".".join([
            api_rpc_config.PROC_URI_PREFIX,
            proc_version])
    # ex. proc_uri_prefix = "com.lojack.rtu.proc.v1"
    for proc_name in proc_names:
        proc_name_versioned = \
            "_".join([
                proc_version,
                proc_name])
        # ex. proc_name_versioned = "v1_read"
        proc_uri = \
            ".".join([
                proc_uri_prefix_versioned,
                proc_name])
        # ex. proc_uri = "com.lojack.rtu.proc.v1.read"
        setattr(
            this_module,
            proc_name_versioned,
            _make_proc(
                proc_version,
                proc_name,
                proc_uri))
        # ex. api_rpc.v1_read() has been created; associate it with the
        # URI "com.lojack.rtu.proc.v1.read"
        PROCS.append({
            "proc": getattr(
                        this_module,
                        proc_name_versioned),
            "uri": proc_uri})

