===================
Configuration Files
===================

LoRa Basics™ Station requires a configuration file named ``station.conf``, which contains settings for the configuration of the Station itself and the configuration of the radio concentrator boards.  If the Station has been built to operate multiple v1.5 concentrator boards, additional configuration files (``slave-0.conf`` .. ``slave-N.conf``) must be present as well, where *N+1* equals the number of concentrator boards available.

The basic layout of the ``station.conf`` file is shown below.  In its simplest form, the file may simply contain ``{}``.  In this case, all settings will revert back to their default values.

.. code-block:: javascript

 {
    "radio_conf": { .. }
    "station_conf": { .. }
 }

All of the ``station_conf`` fields are discussed in the following sections.  The layout of the ``radio_conf`` object depends on the type of concentrator design the Station is built for.  This is discussed in `Radio Configuration`_.


Logging Setup
-------------

Fields related to logging are as follows. (Their respective default values are shown below.)

.. code-block:: javascript

 {
    "station_conf": {
      ...
      "log_file":    "~temp/station.log"
      "log_level":   "INFO"
      "log_size":    10e6
      "log_rotate":  3
    }
    ...
 }

``log_file`` specifies the path and filename of the main log file.  The default place, ``~temp/``, is in a platform-specific directory, usually ``/var/tmp`` or ``/tmp``.

``log_level`` defines the level to which messages are to be logged.  Messages less important than the specified level are suppressed.  The value is a comma-separated sequence of one or more log definitions.  A *log definition* is a log level, optionally prefixed with a module name and a colon.

Available log levels, in order of increasing importance, are:

.. code-block:: javascript

  XDEBUG, DEBUG, VERBOSE, INFO, NOTICE, WARNING, ERROR, CRITICAL


Module names can be inferred from the log messages and are matched.  For level names, only the first four characters matter.  The matching of both module names and level names is case-insensitive.

Example:

.. code-block:: javascript

  "log_level": "DEBUG,SYS:INFO,RAL:XDEBUG"


The log file will be filled up to a size of approximately ``log_size`` bytes.  If the log file is full, it gets moved aside and a new, empty, log file is created.  The ``log_rotate`` field determines how many old log files are kept.  If the ``log_rotate`` field has a value of *N>0*, additional old log files ()``log_file.1``, .., ``log_file.N``) will be saved.

The settings in the **station.conf** configuration file can be overwritten by environment variables or command-line options.  Command-line options supersede environment variables. The command ``station --help`` lists all command-line options and the respective environment variable names.

The log level of a running Station can be changed using the FIFO file ``~/cmd.fifo``.  If such a FIFO file does not yet exist, it may be created in the Station's home directory (``~/``) next to the Station's configuration files.  The desired log level then may be written into the FIFO file as follows:

.. code-block:: shell

  cd $STATION_HOME
  mkfifo cmd.fifo
  echo "DEBUG" > cmd.fifo


Station Identity
----------------

A Station's *identity* is a 64-bit number.  This number uniquely identifies the Station to both LNS and CUPS.  While this can be any number, the identity is usually a 64-bit EUI, derived from the MAC of one of the gateways' network interfaces.

The following two fields control the forming of an identity:

.. code-block:: javascript

 {
    "station_conf": {
      ...
      "routerid":    ID6 | EUI | MAC | "filename"
      "euiprefix":   ID6 | EUI
    }
    ...
 }

If a ``routerid`` is set, it will be used.  If a ``euiprefix`` option is set, it will be used as a prefix when deriving the EUI64 identity (e.g., from the MAC address).  This allows you to control and separate single radio concentrator boards individually.


Time Synchronization Configuration
----------------------------------

Stations support two different methods for time synchronization:

1. With access to a PPS
2. Without a PPS

When available, the PPS can come from hardware, or it can be simulated using software by means of a FIFO file.  The configuration entry is as follows:

.. code-block:: javascript

 {
    "station_conf": {
      ...
      "gps": "DEVICEFILE" | "FIFO"
      "pps": "gps" | "fuzzy"
    }
 }

If the ``pps`` option specifies ``gps``, a PPS is expected. It must either come from a hardware device or be simulated from a file.  If the ``pps`` option specifies ``fuzzy``, Station assumes that PPS is a highly accurate 1Hz signal which is not aligned with GPS. The global GPS time is loosely tracked by timestamps contained in LNS messages.


Development/Debug Settings
--------------------------

If the Station is a development / debug build, the following fields can be used to tweak its behavior for testing purposes:

.. code-block:: javascript

 {
    "station_conf": {
      ...
      "nocca":   false
      "nodc":    false
      "nodwell": false
      PARAM: VALUE
    }
 }

If the fields ``nocca``, ``nodc``, and ``nodwell`` are present and are *true*, they will disable clear-channel analysis (e.g., listen before talk), duty cycle, and dwell-time limitations.  The ``PARAM`` field holds internal configuration parameters that can be used to fine tune performance and resource consumption.  The command ``station -p`` lists all of these parameters.


Radio Configuration
-------------------

Stations support the concentrator reference designs v1.5 and v2.  Currently, this decision is a compile-time option.  The actual layout of the ``radio_conf`` field depends on the type of concentrator design supported and is discussed elsewhere (:doc:`gw_v1.5` and :doc:`gw_v2`).

.. code-block:: javascript

 {
    "radio_conf": { .. }
    "station_conf": {
      ...
      "device":      "FILE" | "FILEPATTERN"
      "radio_init":  "FILE"
    }
 }

The ``device`` field is simply an alternate place to specify the path to the SPI device that enables access to the concentrator board.  In the case of multiple concentrator boards, the '?' character may be used as a wildcard for the concentrator board index.  The device can also be specified in the ``radio_conf`` object.

The ``radio_init`` field points to a file that is executed just before the concentrator boards are initialized.  This initialization happens every time the Station connects to the LNS.  This executable or script can toggle platform-specific GPIOs to reset the concentrator boards to ensure a consistent initial state.  It is called with the SPI device path and, if multiple concentrator boards are configured, with the index of the concentrator board.

These settings can be overridden by the environment variable ``STATION_RADIOINIT`` and the command-line option ``--radio-init``.


Class B Beaconing Settings
--------------------------

For class B beacon operation, proper time synchronization is required.
The parameters ``radio_conf.pps`` and ``station_conf.pps`` are used to
control the time synchronization. The parameter ``station_conf.gps``
can optionally be used to provide the source for gateway position
information from a connected GPS receiver. Additionally, the parameter
``station_conf.BEACON_INTVL`` can be used to override the default
beaconing interval setting. The format of the beacon frame and
broadcasting parameters are controlled by the ``bcning`` field in the
``router_config`` message from the LNS.

The typical scenario for class B beacons would be the availability of
a GPS receiver and PPS signal. Hence, ``radio_conf.pps: true`` and
``station_conf.pps: gps`` are the right set of parameters.

``radio_conf.pps``: BOOL
  If true, a PPS source is assumed to be present and wired to
  SX130x. Station will sync to absolute GPS time using PPS signal and
  timesync message exchange with LNS. If ``station_conf.pps`` is not set,
  ``gps`` is implied, i.e., the PPS source is assumed to be a GPS receiver
  with PPS edges aligned with global GPS time.

``station_conf.pps``: ``gps`` | ``fuzzy``
  Defines the quality of the existing PPS input. Only relevant if
  ``radio_conf.pps: true``. Ignored if ``radio_conf.pps: false``.  If
  not set ``gps`` is implied.  With ``gps`` the PPS edges are aligned
  to global GPS time. Station will try to infer global GPS time for
  observed PPS edges.  If set to ``fuzzy``, the PPS edges are not
  aligned to global GPS time. Station will not try to infer global GPS
  time for observed PPS edges.

``station_conf.gps``: FILE
  Defines the FILE or FIFO that emits NMEA messages from the GNSS
  receiver. Station uses this to extract LAT/LON coordinates of the
  gateway. This is optional for gateway operation. Station does not use
  the GNSS NMEA messages to infer any timing related
  information. Instead, time synchronization is established via timesync
  message exchange with the LNS.

``station_conf.BEACON_INTVL``: STRING
  Defines the beaconing interval. The default is ``128s`` and should
  not be changed for LoRaWAN-compliant operation. However, for test
  purposes, other intervals may be selected. The interval can be
  specified as an integer number followed by a unit (``d`` for days,
  ``h`` for hours, ``m`` for minutes, ``s`` for seconds, or ``ms`` for
  milliseconds).