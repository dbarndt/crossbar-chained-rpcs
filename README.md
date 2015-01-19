Problem statement:

When trying to chain WAMP RPC calls across realms, errors are encountered when trying to run an ApplicationRunner to connect to / access the second realm.

Project notes:
- Code has been run with latest Crossbar.io (0.10.0) and AutobahnPython (0.9.5).
- 'api' directory contains the Crossbar.io config and WAMP code.
- 'server' directory contains a WSGI Flask single-page web app that uses AutobahnJS (0.9.5) to call the WAMP code upon page load. Should only require the main Flask package.
- SSL/TLS has been removed; "http://localhost:8080" and "ws://localhost:8080/api" are the URLs for server and api, respectively.
- Ticket-based auth is still used in the WAMP code but it automatically authenticates instead of calling PAM.

Disclaimers:
- The code is nowhere near "good" in my mind. Only trying to illustrate the problem. Any recommendations about WAMP/Autobahn coding "best practices" are more than welcome!

Questions:
- In the api_ipc.py module:
  - Is everything running within one process? Do I need to synchronize access to the global "_results" array
    between the Server class writing to it and the Client class (and Request method) reading from it,
    using some kind of Lock?
