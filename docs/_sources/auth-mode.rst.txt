====================
Authentication Modes
====================

LoRa Basics™ Station supports four different authentication modes.  Each authentication mode is configured by providing specific files with credentials that are defined by three types of files (``*`` denotes the credential category such as ``tc`` or ``cups``):

- ``*.trust``: The server\'s CA certificate, which enables the Station to establish trust with the LNS or CUPS server

- ``*.crt``: The Private Station certificate

- ``*.key``: The Private Station key


No Authentication
-----------------

In this mode, the Station establishes a plain WebSocket or HTTP connection with no authentication required.  All three files (``*.trust``, ``*.crt``, and ``*.key``) shall be missing or empty.


TLS Server Authentication
-------------------------

The Station authenticates the server (LNS or CUPS) by establishing a TLS connection (wss, https), using the ``*.trust`` file to verify that it is talking to the correct server.  The server does not attempt to verify the identity of the Station.  The ``*.crt``, and ``*.key`` files shall be absent or empty.


TLS Server and Client Authentication
------------------------------------

The Station authenticates the server (LNS or CUPS) as before, and the server verifies the identity of the Station by asking for its certificate, ``\*.crt``, as well as a signature with its private key: ``\*.key``.


TLS Server Authentication and Client Token
------------------------------------------

The Station authenticates the server (LNS or CUPS) as before, and the server verifies the identity of the Station by checking a security token provided by the Station.  The ``\*.crt`` file **shall** be missing or empty, and ``\*.key`` **must** contain one or more HTTP header fields that contain an authorization token such as

::

  Authorization: AZ385fgheuyuslo3due

It is possible to specify multiple lines. Lines must start with a HTTP header field followed by a COLON and one SPACE.
Lines can be terminated by either CRNL or NL.