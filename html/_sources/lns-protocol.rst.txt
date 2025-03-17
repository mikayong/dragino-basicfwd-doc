================
The LNS Protocol
================

Connecting a LoRa Basics™ Station to a LoRaWAN® Network Server (LNS) is a two-step process which uses WebSocket as transport protocol for exchanging text records containing JSON-encoded objects.

First, the Station queries the LNS for the URI of the actual connection endpoint of the LNS.  Second, it establishes a data connection with that endpoint to receive setup information. From then on, LoRa® uplink and downlink frames are exchanged through that connection.  This way, an LNS may dynamically assign gateways to different data connection endpoints in order to, for example, distribute load or favor geographical proximity.

.. note::
    The LNS service assigning data connection endpoints can be separate from the LNS. Also, the service can run on servers separate from the LNS connection endpoints, which may be distributed across different servers.

.. image:: images/station-tcproto.svg
   :width: 90%
   :alt: LNS Protocol
   :align: center


Querying the LNS Connection endpoint (Discovery)
-------------------------------------------------

By default, the URI of the initial query is constructed from the contents of the file ``tc.uri`` by appending the path ``/router-info`` (see :doc:`credentials` for other options).  This forms a WebSocket endpoint to which the following JSON object is submitted:

.. code-block:: javascript

 {
   "router": ID6 | EUI | integer
 }

Here the Station is simply declaring its identity and asking for directions regarding the LNS connection endpoint it shall connect to.  The identity is a 64-bit EUI provided in the field ``router``, either in the form of a string encoding the EUI in :term:`ID6` or :term:`EUI` format, or as an integer value representing the EUI.

Depending on the authorization scheme (see :doc:`authmodes`), the LNS shall verify that the declared identity matches the supplied credentials and shall answer with the following JSON object, immediately closing the connection afterwards:

.. code-block:: javascript

 {
   "router": ID6,
   "muxs"  : ID6,
   "uri"   : "URI",
   "error" : STRING   // only in case of error
 }

The field ``router`` contains the normalized gateway identity. The ``muxs`` field contains the identity of the LNS connection endpoint selected by the LNS, and the field ``uri`` contains the address of this connection endpoint. The Station then connects to this URI to establish a data connection with the LNS.

If the gateway cannot be identified, or if there are other problems, the response object contains an ``error`` field describing the problem.  It may be that the fields ``muxs`` and ``uri`` are missing.


Connecting to an LNS
--------------------

After a successful query of the LNS data connection endpoint, the Station will connect to the endpoint URI it obtained, using the currently-configured credentials.  As mentioned before, the established link is a WebSocket that connects the Station and LNS exchange JSON objects.  Each JSON object, whether an uplink (i.e., from Station to LNS) or a downlink (i.e., from LNS to Station), must have a field named ``msgtype`` which identifies the type of message and determines the structure of the JSON object.

Right after the WebSocket connection has been established, the Station sends a ``version`` message. Next, the LNS shall respond with a ``router_config`` message.  Afterwards, normal operation begins with uplink/downlink messages as described below.


*version* Message
^^^^^^^^^^^^^^^^^

The first message sent by the Station is a ``version`` message which reports its version information to the LNS (i.e., ``station``, ``firmware``, ``model``), the protocol version (the constant ``2``, for now), and a list of optional features supported by the gateway. That is:

.. code-block:: javascript

 {
   "msgtype"   : "version"
   "station"   : STRING
   "firmware"  : STRING
   "package"   : STRING
   "model"     : STRING
   "protocol"  : INT
   "features"  : STRING
 }

The ``features`` string is space-separated list of some of the following keywords:

- ``rmtsh``:
  The Station supports remote-shell access through the WebSocket link established with the LNS.

- ``prod``:
  The Station has been built at production level, that is, certain testing and debugging features may be disabled.

- ``gps``
  The Station has access to a GPS device.


*router_config* Message
^^^^^^^^^^^^^^^^^^^^^^^

The LNS SHALL respond to a ``version`` message with a ``router_config`` message to specify a channel plan for the Station and define some basic operation modes:

.. code-block:: javascript

 {
   "msgtype"    : "router_config"
   "NetID"      : [ INT, .. ]
   "JoinEui"    : [ [INT,INT], .. ]  // ranges: beg,end inclusive
   "region"     : STRING             // optional, e.g. "EU868", "US915", ..
   "max_eirp"   : FLOAT              // optional
   "hwspec"     : STRING
   "freq_range" : [ INT, INT ]       // min, max (hz)
   "DRs"        : [ [INT,INT,INT], .. ]   // sf,bw,dnonly
   "sx1301_conf": [ SX1301CONF, .. ]
   "bcning":    : BCNCONF
   "nocca"      : BOOL
   "nodc"       : BOOL
   "nodwell"    : BOOL
 }

The fields ``NetID`` and ``JoinEui`` are used to filter LoRa frames received by the Station.  ``NetID`` is a list of NetID values that are accepted.  Any LoRa data frame carrying a NetID other than those listed will be dropped.  ``JoinEui`` is a list of pairs of integer values encoding ranges of join EUIs.  Join request frames will be dropped by the Station unless the field ``JoinEui`` in the message satisfies the condition *BegEui\ <=\ JoinEui\ <=\ EndEui* for at least one pair *[BegEui,EndEui]*.

The fields ``nocca``, ``nodc``, and ``nodwell`` are only available in debug builds of a Station. Their purpose is to disable certain regulatory transmission constraints, namely clear channel assessment, duty-cycle limitations, and dwell-time limitations.

The ``region`` field specifies the region of the channel plan. It controls certain regulatory behavior such as clear channel assessment, duty-cycle limitations and dwell-time limitations.  Valid names are compatible with the common names noted in the LoRaWAN Regional Parameters specification. In addition, for backward compatibility, the following names are excepted and are mapped to the respective names in braces: EU863(EU868), US902(US915). If this field is omitted then station will operate in an region agnostic mode.

The ``max_eirp`` field specifies a maxmimum output power. If this field is absent then the region-specific max EIRP value is used. In case of an absent region specifier, it defaults to 14. If ``max_eirp`` is present, it is only adopted if it lowers the region-specific value.

The ``hwspec`` field describes the concentrator hardware needed to operate the channel plan delivered in the ``router_config`` message.  The assigned string must have the following form: ``sx1301/N``, where *N* denotes the number of SX1301 concentrator chips required to operate the channel plan.  The Station will check this requirement against its hardware capabilities.

The ``freq_range`` field defines the upper- and lower-boundaries of the available spectrum for the region set.  The Station will **NOT** allow downlink transmissions outside of this frequency range.

The ``DRs`` field defines the available data rates within the channel plan.  It must be an array of 16 entries.  Each entry is an array of three (3) integers encoding the spreading factor (``SF``), the bandwidth (``BW``), as well as a ``DNONLY`` flag.  ``SF`` must be in the *7-12* range for LoRa®, or *0* for FSK.  ``BW`` must be one of the following numbers: 125, 250, or 500. ``BW`` is ignored for FSK.

.. note::
	``DNONLY`` must be *1* if the data rate is valid for downlink frames only, and *0* if not.

The ``sx1301_conf`` field defines how the channel plan maps to the individual SX1301 chips.  Its value is an array of SX1301CONF objects. The number of array elements must be in accordance with the value of the ``hwspec`` field.

The layout of a ``SX1301CONF`` object looks like this:

.. code-block:: javascript

 {
   "radio_0": { .. } // same structure as radio_1
   "radio_1": {
     "enable": BOOL,
     "freq"  : INT
   },
   "chan_FSK": {
     "enable": BOOL,
     "radio": 0|1,
     "if": INT
   },
   "chan_Lora_std": {
     "enable": BOOL,
     "radio": 0|1,
     "if": INT,
     "bandwidth": INT,
     "spread_factor": INT
   },
   "chan_multiSF_0": { .. }  // _0 .. _7 all have the same structure
   ..
   "chan_multiSF_7": {
     "enable": BOOL,
     "radio": 0|1,
     "if": INT
   }
 }

The ``bcning`` field is either ``None`` or a BCNCONF object with the following layout:

.. code-block:: javascript

 {
   "DR"    : INT
   "layout": [INT,INT,INT]
   "freqs":  [ INT, .. ]
 }

Values for these fields can be extracted from the Regional Paramters specification of the LoRaWAN standard.
The ``DR`` field defines the data rate to be used for the beacons.
The ``layout`` field specifies the octet offsets for insertion of the message fields ``Time`` and ``GwSpecific``, followed by the length of the beacom PDU.
The ``freqs`` field defines the frequencies for broadcasting the beacons.
A typical setting would be {"DR":3, "layout":[2,8,17], "freqs":[869525000] for region EU868.


Uplink Messages
---------------

Uplink messages can be grouped into two categories:

	1. Messages that reflect the reception of LoRaWAN radio frames.
	2. Management messages that interact with the LoRaWAN network server.

Both share a common set of fields described in the next section. Subsequent sections describe the individual message types encoding radio and management messages, respectively.


Radio Metadata
^^^^^^^^^^^^^^^

The following fields are part of all messages that encode LoRaWAN radio frames.  These fields reflect the metadata and timing information accompanying any radio frame:

.. code-block:: javascript

 {
   ...
   "DR"    : INT,
   "Freq"  : INT,
   "upinfo": {
     "rctx"    : INT64,
     "xtime"   : INT64,
     "gpstime" : INT64,
     "rssi"    : FLOAT,
     "snr"     : FLOAT
   }
 }

The ``DR`` field is the data rate at which the frame was received; possible values are integers in the range of 0 to 15.  The ``Freq`` field encodes the reception frequency in Hz. The possible values of ``DR`` and ``Freq`` depend on the current channel plan.

The ``upinfo`` object contains some context required by the Station to process a subsequent matching downlink frame.  The fields ``rctx`` and ``xtime`` are passed along through the LNS and must be added to matching Class A downlink messages.

The ``gpstime`` field is the reception timestamp of the frame, expressed in microseconds since the GPS epoch.  If the Station does not have access to a PPS synchronized to GPS time, the value of this field is 0.


LoRaWAN Join Requests
^^^^^^^^^^^^^^^^^^^^^

Join request frames are parsed and the individual parts are sent back in fields as shown below.  Messages of this type also carry fields discussed in `Radio Metadata`_.

.. code-block:: javascript

 {
   "msgtype" : "jreq",
   "MHdr"    : UINT,
   "JoinEui" : EUI,
   "DevEui"  : EUI,
   "DevNonce": UINT,
   "MIC"     : INT32,
   ..
 }

.. note:: The field ``MIC`` is represented as a 32-bit signed integer.


LoRaWAN Data Frames
^^^^^^^^^^^^^^^^^^^

Data frames are parsed and the individual parts are sent back in fields as shown below.  Messages of this type also carry fields discussed in the Section `Radio Metadata`_.

.. code-block:: javascript

 {
   "msgtype"   : "updf",
   "MHdr"      : UINT,
   "DevAddr"   : INT32,
   "FCtrl"     : UINT,
   "FCnt",     : UINT,
   "FOpts"     : "HEX",
   "FPort"     : INT(-1..255),
   "FRMPayload": "HEX",
   "MIC"       : INT32,
   ..
 }

If the frame does not contain a port, the value of the field ``FPort`` is *-1*.  If the frame does not carry options or data, the value of the fields ``FOpts`` or ``FRMPayload`` will be empty strings, respectively.  Otherwise those fields contain strings of hexadecimal characters.

.. note:: The fields ``DevAddr`` and ``MIC`` are represented as 32-bit signed integers.


LoRaWAN Proprietary Frames
^^^^^^^^^^^^^^^^^^^^^^^^^^

Frames marked as proprietary are forwarded in the following form, whereby the entire frame payload is passed along uninterpreted. Messages of this type also carry fields discussed in the `Radio Metadata`_ topic.

.. code-block:: javascript

 {
   "msgtype"   : "propdf",
   "FRMPayload": "HEX",
   ..
 }

.. note:: The field ``FRMPayload`` contains the whole LoRaWAN ``PHYPayload`` in the case of ``msgtype:propdf``

Transmit Confirmation
^^^^^^^^^^^^^^^^^^^^^

The Station acknowledges transmit requests from the LNS with a message of type ``dntxed``.  This message is only sent when a frame has been put on-air.  There is no feedback to the LNS if a frame could not be sent (e.g., because it was too late, there was a conflict with an ongoing transmission, or the gateway's duty cycle was exhausted).  These conditions are summarized in health status messages and do not trigger individual responses.

.. code-block:: javascript

 {
   "msgtype"  : "dntxed",
   "diid"     : INT64,
   "DevEui"   : "EUI",
   "rctx"     : INT64,
   "xtime"    : INT64,
   "txtime"   : FLOAT,
   "gpstime"  : INT64
 }

The ``diid`` field is a copy of the ``diid`` field in the ``dnmsg`` message.  It identifies a particular device interaction and is used by the LNS to reference some internal state.  It is passed along unchanged by the Station.

The ``rctx`` field specifies the antenna used for transmission, and the ``xtime`` field is the exact internal time when the frame was put on-air.


Downlink Messages
-----------------

This section covers all message types used by the LNS to transmit LoRaWAN data frames.

Single-frame downlinks are either a response to a Class A or Class C uplink frame, or are unsolicited downlink frames for a Class B or Class C interaction. Multiframe downlinks are used to schedule a sequence of multicast frames.


Single Frame Downlink
^^^^^^^^^^^^^^^^^^^^^

Stations support downlinks of Class A, B, and C.  For all three classes, the same message type is used, but different fields need to be present.

A **Class A downlink** frame is a response to a previously-sent uplink.  The layout for Class A requires the following fields:

.. code-block:: javascript

 {
   "msgtype"  : "dnmsg",
   "DevEui"   : "EUI",
   "dC"       : 0,          // Class A
   "diid"     : INT64,
   "pdu"      : "HEX",
   "RxDelay"  : INT(0..15),
   "RX1DR"    : INT(0..15),
   "RX1Freq"  : INT,
   "RX2DR"    : INT(0..15),
   "RX2Freq"  : INT,
   "priority" : INT(0..255),
   "xtime"    : INT64,
   "rctx"     : INT64
 }

The ``diid`` field is a number issued by the LNS to identify a particular device interaction.  Both, ``diid`` and ``DevEui`` are passed along by the Station in ``dntxed`` messages. ``DevEui`` can be used in cases where the LNS maintains  ``diid`` as a device-specific identifier. Also, knowing the ``DevEUI`` to which a particular downlink belongs can be helpful for inspecting gateway logs. The LNS can choose to set ``DevEUI`` to any non-zero value. The ``pdu`` field is the radio frame as it will be put on-air.

The Station will choose either RX1 or RX2 transmission parameters, where RX1 is preferred.  If the frame arrives too late, or the transmission spot is blocked, it will try RX2. To force a decision, the LNS can omit either the RX1 or the RX2 parameters. In any case, ``RxDelay`` is the delay between end of uplink transmission and start of the RX1 receive window of the device. The exact transmission end time is implicitly encoded in ``xtime``. ``RxDelay`` should have the same value as the ``RxDelay`` field in the join accept message. Station will automatically infer the RX2 delay by adding one second.

The ``priority`` field is used when conflicting transmission requests are encountered.  The LNS can give higher priority to frames that carry an acknowledgement or some important MAC commands.  If two frames are in conflict, the one with the higher ``priority`` value is preferred.

The ``xtime`` and ``rctx`` fields contain values that originate from the corresponding uplink message.  Those values must be passed along without being changed by the LNS. They are used by Station to manage proper transmit timing and to handle antenna associations.

A **Class C downlink** frame that answers an uplink and is aimed at RX1, looks almost identical to Class A ``dnmsg`` messages.  The only difference is the field ``dC``, which declares a Class C interaction.  If the transmission cannot make the RX1 opportunity, the Station will switch over to RX2 parameters and choose a convenient time to send the frame.  There is a maximum time Station will postpone transmission before the frame is dropped. Since RX2 downlink opportunities are arbitrary for class C devices, ``RxDelay`` is only used to calculate the RX1 opportunity in this case.

.. code-block:: javascript

 {
   "msgtype"  : "dnmsg",
   "DevEui"   : "EUI",
   "dC"       : 2,         // Class C
   "diid"     : INT64,
   "pdu"      : "HEX",
   "RxDelay"  : INT(0..15),
   "RX1DR"    : INT(0..15),
   "RX1Freq"  : INT,
   "RX2DR"    : INT(0..15),
   "RX2Freq"  : INT,
   "priority" : INT(0..255),
   "xtime"    : INT64,
   "rctx"     : INT64
 }


A **Class C downlink** frame not answering an uplink must have the fields indicated in the example below.  The transmission will be delayed until the Station finds a convenient time slot.  If there is no such opportunity, the frame will be dropped after some configurable time; the default is one (1) second.

Although the ``rctx`` field is optional, it may be used to select an antenna preference.  The LNS can copy this field from a previous Class A uplink and guide the Station to use the same antenna which received that Class A uplink.

.. code-block:: javascript

 {
   "msgtype"  : "dnmsg",
   "DevEui"   : "EUI",
   "dC"       : 2,          // Class C
   "diid"     : INT64,
   "pdu"      : "HEX",
   "RX2DR"    : INT(0..15),
   "RX2Freq"  : INT,
   "priority" : INT(0..255),
   "rctx"     : INT64
 }


A **Class B downlink** frame requires the following fields:

.. code-block:: javascript

 {
   "msgtype"  : "dnmsg",
   "DevEui"   : "EUI",
   "dC"       : 1,           // Class B
   "diid"     : INT64,
   "pdu"      : "HEX",
   "DR"       : INT(0..15),
   "Freq"     : INT,
   "priority" : INT(0..255),
   "gpstime"  : INT64,
   "rctx"     : INT64
 }

The transmission of a Class B frame requires that the LNS provides a GPS-aligned time.  The value is expressed in microseconds since the GPS epoch.

The optional ``rctx`` field may be used to select an antenna preference.  The LNS may copy this field from a previous Class A uplink and guide the Station to use the same antenna which received that Class A uplink.

.. note:: The ``DevEui`` field in all ``dnmsg`` messages must not be zero. Zero is a reserved value.

Multicast Schedule
^^^^^^^^^^^^^^^^^^

Messages of type ``dnsched`` can be used to schedule a set of multicast messages.  Each of the message elements needs to specify a GPS time at which it shall be sent.  This type of transmission does not generate ``dntxed`` responses from the Station.

.. code-block:: javascript

 {
   "msgtype"  : "dnsched",
   "schedule" : [
     {
       "pdu"      : "HEX",
       "DR"       : INT(0..15),
       "Freq"     : INT,
       "priority" : INT(0..255),
       "gpstime"  : INT64,
       "rctx"     : INT64
     },
     ...
   ]
 }

The optional ``rctx`` field may be used to select an antenna preference.  The LNS may copy this field from a previous Class A uplink and guide the Station to use the same antenna which received that Class A uplink.


Monitoring Round-trip Times
---------------------------

The message exchange between a Station and the LNS allows for monitoring round-trip times by piggy-backing certain fields onto normal message exchanges.  The LNS may add the ``MuxTime`` field to every downlink sent to a Station:

.. code-block:: javascript

 {
   "msgtype" : ".."
   "MuxTime" : FLOAT    // downlink
   ..
 }

The ``MuxTime`` field contains a float value that represents a UTC timestamp, with fractional seconds, and marks the time when the message was sent by the LNS.  The Station will respond by adding the field ``RefTime``:

.. code-block:: javascript

 {
   "msgtype" : ".."
   "RefTime" : FLOAT  // uplink
   ..
 }

The ``RefTime`` field is calculated from the last received ``MuxTime``, adjusted by the time interval on the router between the arrival of ``MuxTime`` and the sending of ``RefTime``.  Since downlink traffic is less frequent than uplink messages, it is likely that a ``MuxTime`` may be reused to construct multiple ``RefTime`` fields.  This means that round-trip measurements are composed of the latency of the last downlink message and the most recent uplink message.

Time Synchronization
--------------------

There are two modes of operation for time synchronization:

#. With access to a PPS
#. Independent of a PPS.

.. _timesyncproto:

Synchronizing PPS to GPS Time
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

If a Station has access to a PPS that is aligned to GPS seconds, it will infer the synchronization to GPS time by running a protocol with the LNS.  To infer the correct GPS time label for a given PPS pulse, the Station will keep sending ``timesync`` uplink messages to the LNS which should be promptly answered with a downstream ``timesync`` message.

Format of an upstream message:

.. code-block:: javascript

 {
   "msgtype"  : "timesync"
   "txtime"   : INT64,
 }

The downstream response should be sent by the LNS immediately after it receives the corresponding upstream ``timesync``.  The LNS will insert the ``gpstime`` field and pass through the ``txtime`` field as received from the Station, where ``txtime`` is some unspecified time local to the Station.

The field ``gpstime`` marks the instant of time when the LNS processes the ``timesync`` message.  Its value is the time in microseconds since the GPS epoch.

.. code-block:: javascript

 {
   "msgtype"  : "timesync"
   "txtime"   : INT64,
   "gpstime"  : INT64
 }


Transferring GPS Time
^^^^^^^^^^^^^^^^^^^^^

The LNS shall periodically send the following message to the Station to transfer GPS time.

.. code-block:: javascript

 {
   "msgtype"  : "timesync"
   "xtime"    : INT64,
   "gpstime"  : INT64
 }

The field ``xtime`` is particular to the Station and the GPS time is inferred from overlapping upstream frames arriving at the LNS.


Remote Commands
---------------

Stations support two mechanisms for running remote commands on the gateway:

.. code-block:: javascript

 {
   "msgtype"  : "runcmd"
   "command"  : STRING,
   "arguments": [ STRING, ... ]
 }

The ``command`` field contains the actual command to execute.  Based on its content, the Station will behave as follows:

- If the executable flag is set, the Station runs the command with the specified set of arguments.
- If it is a file but not executable, the Station treats it as a file containing a shell script and passes it, together with the arguments, to the system's local shell for interpretation.
- If none of the above is true, the Station assumes the ``command`` value represents shell statements.  It runs the local shell and passes the value as statements together with the arguments for execution.

The ``arguments`` field is optional and may be absent or an empty array. If present and not empty, these arguments are passed along with the command.

Remote Shell
------------

Stations support a remote shell session tunneling through the WebSocket to the LNS.  The session is initiated by a command as shown below.  After the session is established, the input data to the shell and the output data generated by the shell and its commands are tunneled through the WebSocket as binary records.  A Station can maintain multiple sessions. This being the case, the first byte of the binary record is the session index.  The remaining bytes of a binary record are the input/output data.  The encoding is transparent to the WebSocket transport.

To query, initiate, or stop a session, the LNS must send the following message:

.. code-block:: javascript

 {
   "msgtype"  : "rmtsh",
   "user"     : STRING,
   "term"     : STRING,
   "start"    : INT,
   "stop"     : INT
 }

If the fields ``start`` and ``stop`` are absent, the current session state is queried.  Otherwise, only one of the two fields shall be present, indicating a session start or stop, respectively.

The value of the ``term`` field is the value of the ``TERM`` environment variable.  It is set before the local shell is started.

The ``user`` field describes the user who is operating the session.  For the Station this is just informational context data.

The Station will respond with the following message describing the current state of all sessions:

.. code-block:: javascript

 {
   "msgtype"  : "rmtsh",
   "rmtsh"    : [
     {
       "user"     : STRING,
       "started"  : BOOL,
       "age"      : INT,
       "pid"      : INT
     },
     ..
   ]
 }

The ``age`` field is the time in seconds since the input/output action on this remote shell session.

The ``pid`` field is the local process identifier of the started shell.

The ``started`` field indicates that the shell process is actually running.