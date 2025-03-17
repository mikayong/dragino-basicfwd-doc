===========
Credentials
===========

A LoRa Basics™ Station needs credentials to establish a secure connection to both LNS and CUPS.  A single credential definition consists of a group of up to four files which together form a *credential set*.  The *basename* describes the purpose of the credential set and the file extension defines the type of contents.

.. note::
    If no credential set for CUPS is provided, Station implicitly disables the CUPS functionality. In this case, at least one valid LNS credential set is required.

Files Types
-----------

The following four file types form a credential set and define the address of a server (either LNS or CUPS), how the server is authenticated by the Station, and how the Station authorizes its access to the server.  Some of the files may be absent or empty in some modes (see :doc:`authmodes`):

- ``*.uri``: The URI of the server to connect to.  This shall be a simple ASCII file. The URI is either ``http``, ``https``, ``ws``, or ``wss``.  If the URI indicates a non-TLS protocol scheme (i.e., ``http`` or ``ws``), the subsequent files SHALL be missing or, if present, be empty.  If a TLS-based scheme (i.e., ``https`` or ``wss``) is specified, some or all of the other files must be present.

- ``*.trust``: The server\'s CA certificate, which enables the Station to establish trust with the server.  If the URI indicates a TLS-based scheme, this file must be present and contain a PEM-encoded X509 certificate.

- ``*.crt``: The Station\'s own certificate, if TLS client authentication is being used.  If this is not empty, the corresponding key file must contain the private key matching this certificate.

- ``*.key``: The Station\'s private key matching the corresponding certificate (*.crt) file.  If the certificate file is missing or empty, this file, if present, shall contain an authorization token submitted in the HTTP header field *Authorization* when making requests to the server.


Categories and Sets
-------------------

Stations use two different credential categories for connecting to LNS (prefix ``tc``) and CUPS (prefix ``cups``) servers.  For each category there are three different sets of credentials:

- ``tc.\*`` / ``cups.\*``: Regular credentials used to connect to LNS or CUPS, respectively.  If these credentials are not available or do not work, the ``bak`` and ``boot`` variants will be tried.  These files may be part of a system image or may be updated by the Station process during an update session with a CUPS server.

- ``tc-bak.\*`` / ``cups-bak.\*``: Backup credentials are automatically created by the Station.  These are copies of the regular credentials that are made after a successful connection to the server. (This way they are known to have worked at some point in time.)  These credentials are used as a fallback in case an update damages the regular credentials.

- ``tc-boot.\*`` / ``cups-boot.\*``: Bootstrap credentials are optional, they are used for an initial connection to a server.  The server may limit the validity of bootstrap credentials after a few uses.  These credentials are again used as a fallback if the regular credentials fail to work, or if no regular credentials are available.  These credentials must be provided as part of the system image and may be replaced or updated as part of firmware updates.  The Station never modifies these files.


Intermediate Files
------------------

All credential files are updated atomically.  During this process some auxiliary files are used to mark certain stages in the transaction processing.  The following files are used:

- ``*-done.bak``: Backup credentials are complete and valid.  If this file is deleted, a new backup copy will be created.

- ``*-temp.cpy``: A backup copy is in progress and the ``bak`` files might be incomplete and inconsistent.  This file is automatically removed once a backup copy is completed.

- ``*-temp.{uri,trust,crt,key,upd}``: These are temporary files created during the credential update process with a CUPS server.