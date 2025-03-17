=================
The CUPS Protocol
=================

The LoRa Basics™ Station periodically queries the CUPS server for updates.  The protocol is HTTP/REST, using the client/server authentication methods described in :doc:`credentials`.  With each query, the Station provides information about its current state and receives a binary blob containing updates for its LNS and CUPS credentials, along with a generic data segment with arbitrary updates.

The format of the generic data segment is platform-dependent.  The Station simply executes this file after downloading it.  Usually it is a self-extracting shell script.  However, it may also be a binary executable.


.. image:: images/station-cupsproto.svg
   :width: 90%
   :alt: CUPS Protocol
   :align: center


HTTP POST Request
-----------------

The URI of the CUPS update end point is constructed from the contents of the ``cups.uri`` file (or one of its fallback alternatives as described in :doc:`credentials`).  The path ``/update-info`` is added and an HTTP POST request is submitted with the body.  The HTTP POST request contains the following JSON object:

.. code-block:: javascript

 {
   "router"      : ID6,
   "cupsUri"     : "URI",
   "tcUri"       : "URI",
   "cupsCredCrc" : INT,
   "tcCredCrc"   : INT,
   "station"     : STRING,
   "model"       : STRING,
   "package"     : STRING,
   "keys"        : [INT]
 }

The ``router`` field is the ID6 representation of the gateway's identity.

The values of the ``cupsUri`` and ``tcUri`` fields are the contents of the credential files ``cups.uri`` and ``tc.uri``, respectively.

The ``cupsCredCrc`` and ``tcCredCrc`` fields are CRC32 checksums calculated over the concatenated credentials files ``cups.{trust,cert,key}`` and ``tc.{trust,cert,key}``.

The ``station``, ``model``, and ``package`` fields describe the current version of the Station, the gateway model and the package version.  The package version may contain information about the state of the underlying system and its configuration.

The ``keys`` field contains an array of CRC32 checksums for each of the signing keys installed on the firmware where the Station is running.  The response from the server will provide a signed update, if available, with a signature matching one of these signing keys.


HTTP POST Response
------------------

The CUPS server shall respond with HTTP status code 200 and a binary response message. The ``Content-Type`` header is set to:

.. code-block::

  Content-Type: application/octet-stream

The response body shall be in the following binary format:

+-------+-------------+-----------------------------------------------------------------------+
| Bytes | Field       | Description                                                           |
+=======+=============+=======================================================================+
| 1     | cupsUriLen  | Length of CUPS URI (cun)                                              |
+-------+-------------+-----------------------------------------------------------------------+
| cun   | cupsUri     | CUPS URI (cups.uri)                                                   |
+-------+-------------+-----------------------------------------------------------------------+
| 1     | tcUriLen    | Length of LNS URI (tun)                                               |
+-------+-------------+-----------------------------------------------------------------------+
| tun   | tcUri       | LNS URI (tc.uri)                                                      |
+-------+-------------+-----------------------------------------------------------------------+
| 2     | cupsCredLen | Length of CUPS credentials (ccn)                                      |
+-------+-------------+-----------------------------------------------------------------------+
| ccn   | cupsCred    | Credentials blob                                                      |
+-------+-------------+-----------------------------------------------------------------------+
| 2     | tcCredLen   | Length of LNS credentials (tcn)                                       |
+-------+-------------+-----------------------------------------------------------------------+
| tcn   | tcCred      | Credentials blob                                                      |
+-------+-------------+-----------------------------------------------------------------------+
| 4     | sigLen      | Length of signature for update blob plus size of the keyCRC field (4) |
+-------+-------------+-----------------------------------------------------------------------+
| 4     | keyCRC      | CRC of the key used for the signature                                 |
+-------+-------------+-----------------------------------------------------------------------+
| sig   | sig         | Signature over the update blob                                        |
+-------+-------------+-----------------------------------------------------------------------+
| 4     | updLen      | Length of generic update data (udn)                                   |
+-------+-------------+-----------------------------------------------------------------------+
| udn   | updData     | Generic update data blob                                              |
+-------+-------------+-----------------------------------------------------------------------+


The length fields shall be encoded in little endian.  If any of the length fields is zero, there is no update for that particular component.  If CUPS returns a blob where all length fields are zero, there is no update pending.

.. note:: The CUPS `null` response consists of 14 zero bytes: (HEX) ``0000000000000000000000000000``.

The credentials blob is a concatenation of ``trust/cert/key``, which is able to encode client authentication using X509 certificates and using tokens.

For client authentication using X509 certificates, all credentials are encoded in DER format:

- ``trust`` is the certificate of the trusted certificate authority (CA)

- ``cert`` is the personal certificate for the gateway

- ``key`` is the personal private key for the gateway

For token-based authentication, ``trust`` is the same DER as above; however:

- the private ``cert`` is not required, and, if absent, the response will contain four "zero" octets for this part

- The ``key`` is an authorization token that must be added to the subsequent requests to CUPS as part of the headers for the HTTP POST request

The Station unpacks non-empty fields into their respective local credential files.  If generic update data is present and the signature is verified, the update gets saved into a file named ``update.bin`` and is executed once downloaded successfully.

This executable/script may replace the Station binary. It may then update the configuration file and the underlying system before restarting the Station process or rebooting the gateway.


Error Conditions
^^^^^^^^^^^^^^^^

The CUPS server may respond with an error condition. In an error response, the HTTP status code in the response shall not be 200 and the reason text in the status line is rendered in a log message and can be used to give a hint as to hwy the request failed. The message body of a non 200 response is discarded.