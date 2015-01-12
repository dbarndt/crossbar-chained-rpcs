Problem statement:

When trying to chain WAMP RPC calss across realms, errors are encountered when trying to run an ApplicatioRunner to connect to / access the second realm.

Project notes:
- api contains the Crossbar.io config and WAMP code.
- server contains a Flask single-page web app that uses AutobahnJS to call the WAMP code upon page load. Should only require the main Flask package.
- IP port for both api and server is 8080.
- To simplify things:
  - SSL/TLS has been removed; "http://localhost:8080" and "ws://localhost:8080/api" are the URLs for server and api, respectively.
  - Ticket-based auth is still used in the WAMP code but it automatically authenticates instead of calling PAM.

Disclaimers:
- The code is nowhere near "good" in my mind. Only trying a proof-of-concept that chaining RPCs from one realm to
  another can work. That said, any comments about "best practices" are more than welcome.

Questions:
- In the api_ipc code:
  - Is everything run within one process? Do I need to synchronize access to the global "_results" array
    between the Server class writing to it and the Client class (and Request method) reading from it,
    using some kind of Lock?
