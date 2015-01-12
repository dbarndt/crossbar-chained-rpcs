api contains the Crossbar.io config and WAMP code.

server contains a Flask single-page web app that uses AutobahnJS to call the WAMP code upon page load. Depends
on Flask and flask-compress.

Port for both is 8080.

To simplify things:
- SSL/TLS has been removed.
- Ticket-based auth is still used in the WAMP code but it automatically authenticates instead of calling PAM.

Disclaimers:
- The code is nowhere near "good" in my mind. Only trying a proof-of-concept that chaining RPCs from one realm to
  another can work. That said, any comments about "best practices" are welcome.

Questions:
- In the api_ipc code:
  - Is everything run within one process? Do I need to synchronize access to the global "_results" array
    between the Server class writing to it and the Client class (and Request method) reading from it,
    using some kind of Lock?
