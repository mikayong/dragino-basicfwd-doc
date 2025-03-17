==============================
Concentrator Design (Corecell)
==============================

LoRa Basics™ Station supports the Semtech concentrator reference design `SX1302CxxxGW1 (Corecell) <https://www.semtech.com/products/wireless-rf/lora-gateways/sx1302cxxxgw1>`_ as a compile-time option.  The JSON configuration is very similar to the `Semtech SX1302 Packet Forwarder <https://github.com/Lora-net/sx1302_hal/tree/master/packet_forwarder>`_.

Currently, support for the Corecell design comes in single-board compile-time variants.

Stations can also contain a statically-linked version of the `lora_gateway library <https://github.com/Lora-net/sx1302_hal/tree/master/libloragw>`_, so it can interact with the concentrator boards.

This topic lists the available object types and fields, with their possible values, as understood by a Station when parsing configuration files.  The semantics of the fields is discussed in the documentation for each of the respective radio boards.  Only the additional fields or extensions specific to the Station are briefly explained here.

A configuration need not specify any frequencies or enablement for ``RFCONF`` objects.  This information is submitted by the LNS based on the channel plan assigned to a gateway.  The channel-plan settings are merged with the local configuration before the concentrator board is initialized.

The concentrator configuration is embedded in the ``station.conf`` files in the following way:

.. code-block:: javascript

 {
   ...                    // possibly other fields e.g. "station_conf"
   "radio_conf"  : CONF
   "sx130x_conf" : CONF   // alias for radio_conf
   "SX130x_conf" : CONF   // alias for radio_conf
 }



CONF Object
-----------

.. code-block:: javascript

 {
   "device"        : STRING   // station-specific
   "pps"           : BOOL     // station-specific
   "lorawan_public": BOOL
   "clksrc"        : INT
   "antenna_gain"  : INT
   "full_duplex"   : BOOL
   "radio_0"       : RFCONF
   "radio_1"       : RFCONF
 }

The ``device`` field specifies the device path that is used to communicate with the radio board. The device path can be prefixed with ``spi:`` or ``usb:`` to select SPI or USB as communication type. By default, SPI communication is assumed. If multiple radio boards are used, the wildcard character (``?``) is replaced with the actual board index.  The board index is inferred from the name of the slave configuration file ``slave-N.conf``.

If the gateway has a PPS (for example, a GPS device or some other source), the concentrator board that has access to this signal must have the ``pps`` field set to *true*.  One and only one board must have this field set to *true*.

Station targets a specific output power to be dissipated.  The value of the ``antenna_gain`` field is subtracted from this target value to account for any gains by the antenna and any losses by the cable.

Currently ``full_duplex`` needs to be set to *false* because it is not being validated by lora_gateway library.

.. note::

	Stations do not require access to a GPS device to maintain a global GPS time for Class B operations.  A PPS, aligned with the GPS time, is sufficient.

RFCONF Object
-------------

.. code-block:: javascript

 {
   "type"          : "SX1250"
   "tx_enable"     : BOOL
   "freq"          : INT
   "rssi_offset"   : INT
   "rssi_tcomp"    : [ RSSSI_TCOMP, .. ]
   "tx_gain_lut"   : [ TX_GAIN_LUT, .. ]

 }

TX_GAIN_LUT Object
------------------

.. code-block:: javascript

 {
   "rf_power" : INT[-128..127]
   "pa_gain": INT[0..1]
   "pwr_idx": INT[1..22]
 }

RSSSI_TCOMP Object
------------------

.. code-block:: javascript

 {
   "coeff_a": INT
   "coeff_b": INT
   "coeff_c": INT
   "coeff_d": INT
   "coeff_e": INT
 }


All of the ``RFCONF`` fields are optional.  Absent fields are read as *false* or 0.  If ``type`` is absent, the value is undefined.


Single-Board Sample Configuration
---------------------------------

Here is a sample configuration for a single board:

.. code-block:: javascript

  {
    ...
    "radio_conf": {                  /* Actual channel plan is controlled by the server */
        "lorawan_public": true,      /* is default */
        "clksrc": 0,                 /* radio_0 provides clock to concentrator */
        "device": "spidev",          /* default SPI device is platform specific */
        "antenna_gain": 0,           /* antenna gain, in dBi */
        "full_duplex": false,
            "radio_0": {
                /* freq/enable provided by LNS - only hardware-specific settings are listed here */
                "type": "SX1250",
                "rssi_offset": -215.4,
            "rssi_tcomp": {"coeff_a": 0, "coeff_b": 0, "coeff_c": 20.41, "coeff_d": 2162.56, "coeff_e": 0},
                "tx_enable": true,
                "tx_gain_lut":[
                    {"rf_power": 12, "pa_gain": 0, "pwr_idx": 15},
                    {"rf_power": 13, "pa_gain": 0, "pwr_idx": 16},
                    {"rf_power": 14, "pa_gain": 0, "pwr_idx": 17},
                    {"rf_power": 15, "pa_gain": 0, "pwr_idx": 19},
                    {"rf_power": 16, "pa_gain": 0, "pwr_idx": 20},
                    {"rf_power": 17, "pa_gain": 0, "pwr_idx": 22},
                    {"rf_power": 18, "pa_gain": 1, "pwr_idx": 1},
                    {"rf_power": 19, "pa_gain": 1, "pwr_idx": 2},
                    {"rf_power": 20, "pa_gain": 1, "pwr_idx": 3},
                    {"rf_power": 21, "pa_gain": 1, "pwr_idx": 4},
                    {"rf_power": 22, "pa_gain": 1, "pwr_idx": 5},
                    {"rf_power": 23, "pa_gain": 1, "pwr_idx": 6},
                    {"rf_power": 24, "pa_gain": 1, "pwr_idx": 7},
                    {"rf_power": 25, "pa_gain": 1, "pwr_idx": 9},
                    {"rf_power": 26, "pa_gain": 1, "pwr_idx": 11},
                    {"rf_power": 27, "pa_gain": 1, "pwr_idx": 14}
                ]
            },
    "radio_1": {
            "type": "SX1250",
            "rssi_offset": -215.4,
            "rssi_tcomp": {"coeff_a": 0, "coeff_b": 0, "coeff_c": 20.41, "coeff_d": 2162.56, "coeff_e": 0},
            "tx_enable": false
        }
        /* chan_multiSF_X, chan_Lora_std, chan_FSK provided by LNS */
    }
    ...
 }


The configuration contains only board-specific settings.  All parameters related to a channel plan are omitted because they are provided by the LNS and are merged on the fly.