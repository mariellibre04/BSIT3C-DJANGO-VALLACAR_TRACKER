"""Vallacar terminal master list and route stop sequences.

Data rules for this module:

* Only places that appear in a published Vallacar/Ceres terminal list or a
  source-backed route description are listed. No terminal is invented.
* ``is_owned_terminal`` marks terminal hubs Vallacar itself operates.
  ``is_major_stop`` marks towns/barangays that a Vallacar route serves.
* The Kabankalan -> Dumaguete sequence below is deliberately *not* copied from
  the Bacolod -> Dumaguete sequence. Only stops explicitly described for the
  Kabankalan/Mabinay corridor are used. Every route is marked
  ``source_compiled`` until a conductor validates the final barangay list.

Sources used:
* https://ceresliner.com/terminal (owned terminal addresses)
* https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)
  (bases, terminal hubs, and published destinations)
* https://byahi.ph/negros/routes/NEG-BCD-DGT (Bacolod-Dumaguete via Mabinay
  corridor, used only to cross-check the Mabinay-Bais-Tanjay-Dumaguete road)
* Route notes for the Bais-Binalbagan/Kabankalan-Mabinay service, including the
  Dumaguete-Sibulan-Tanjay-Bais-Mabinay-Kabankalan distance table.
"""

TERMINAL_MASTER_LIST = [
    # ------------------------------------------------------------------
    # Terminal hubs operated by Vallacar (owned terminals)
    # ------------------------------------------------------------------
    {
        'name': 'PITX', 'code': 'PITX',
        'city': 'Parañaque', 'province': 'Metro Manila',
        'lat': 14.5106, 'lng': 120.9918,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Parañaque Integrated Terminal Exchange, PITX',
        'source': 'https://ceresliner.com/terminal',
    },
    {
        'name': 'Cubao', 'code': 'CUBAO',
        'city': 'Quezon City', 'province': 'Metro Manila',
        'lat': 14.6197, 'lng': 121.0530,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Araneta City Bus Terminal, Cubao',
        'source': 'https://ceresliner.com/terminal',
    },
    {
        'name': 'Pasay', 'code': 'PASAY',
        'city': 'Pasay', 'province': 'Metro Manila',
        'lat': 14.5547, 'lng': 121.0244,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Buendia, Pasay',
        'source': 'https://ceresliner.com/terminal',
    },
    {
        'name': 'Batangas', 'code': 'BAT',
        'city': 'Batangas City', 'province': 'Batangas',
        'lat': 13.7565, 'lng': 121.0583,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Batangas Grand Terminal, Batangas City',
        'source': 'https://ceresliner.com/terminal',
    },
    {
        'name': 'Cebu South', 'code': 'CSBT',
        'city': 'Cebu City', 'province': 'Cebu',
        'lat': 10.2958, 'lng': 123.8934,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Cebu South Bus Terminal, CSBT',
        'source': 'https://ceresliner.com/terminal',
    },
    {
        'name': 'Cebu North', 'code': 'CNBT',
        'city': 'Cebu City', 'province': 'Cebu',
        'lat': 10.3157, 'lng': 123.8854,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Cebu North Bus Terminal, CNBT',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Kalibo', 'code': 'KAL',
        'city': 'Kalibo', 'province': 'Aklan',
        'lat': 11.7061, 'lng': 122.3686,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Kalibo Terminal',
        'source': 'https://ceresliner.com/terminal',
    },
    {
        'name': 'Sagay', 'code': 'SAG',
        'city': 'Sagay City', 'province': 'Negros Occidental',
        'lat': 10.8917, 'lng': 123.4150,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Sagay Terminal',
        'source': 'https://ceresliner.com/terminal',
    },
    {
        'name': 'Bacolod North', 'code': 'BCDN',
        'city': 'Bacolod City', 'province': 'Negros Occidental',
        'lat': 10.6765, 'lng': 122.9509,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Bacolod North Bus Terminal, Bacolod North',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Bacolod South', 'code': 'BCDS',
        'city': 'Bacolod City', 'province': 'Negros Occidental',
        'lat': 10.6550, 'lng': 122.9550,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Bacolod South Bus Terminal, Bacolod South, Bacolod, Bacolod City',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Iloilo Jaro', 'code': 'ILO',
        'city': 'Iloilo City', 'province': 'Iloilo',
        'lat': 10.7333, 'lng': 122.5667,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Ceres Terminal Jaro, Iloilo Jaro',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Iloilo Molo', 'code': 'MOLO',
        'city': 'Iloilo City', 'province': 'Iloilo',
        'lat': 10.7000, 'lng': 122.5500,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Molo Terminal, Iloilo Molo',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Festive Walk', 'code': 'FWT',
        'city': 'Iloilo City', 'province': 'Iloilo',
        'lat': 10.7146, 'lng': 122.5468,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Festive Walk Transport Terminal',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Pavia', 'code': 'PAV',
        'city': 'Pavia', 'province': 'Iloilo',
        'lat': 10.7833, 'lng': 122.5333,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Pavia Transport Terminal',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Dumaguete', 'code': 'DGT',
        'city': 'Dumaguete City', 'province': 'Negros Oriental',
        'lat': 9.3072, 'lng': 123.3080,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Dumaguete Ceres Bus Terminal, Dumaguete',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Kabankalan', 'code': 'KAB',
        'city': 'Kabankalan City', 'province': 'Negros Occidental',
        'lat': 9.9917, 'lng': 122.8128,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Kabankalan City Bus Terminal, Kabnakalan, Kabankalan',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },

    # ------------------------------------------------------------------
    # Major stops / provincial terminals served by Vallacar routes
    # ------------------------------------------------------------------
    {
        'name': 'Mabinay', 'code': 'MAB',
        'city': 'Mabinay', 'province': 'Negros Oriental',
        'lat': 9.7264, 'lng': 122.9256,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Mabinay Bus Terminal, Mabinay',
        'source': 'https://byahi.ph/negros/routes/NEG-BCD-DGT',
    },
    {
        'name': 'Bais', 'code': 'BAIS',
        'city': 'Bais City', 'province': 'Negros Oriental',
        'lat': 9.5917, 'lng': 123.1222,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Bais City, Bais',
        'source': 'Route notes for the Bais-Binalbagan / Kabankalan-Mabinay service',
    },
    {
        'name': 'Tanjay', 'code': 'TAN',
        'city': 'Tanjay City', 'province': 'Negros Oriental',
        'lat': 9.5167, 'lng': 123.1583,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Tanjay City, Tanjay',
        'source': 'Route notes for the Bais-Binalbagan / Kabankalan-Mabinay service',
    },
    {
        'name': 'Sibulan', 'code': 'SIB',
        'city': 'Sibulan', 'province': 'Negros Oriental',
        'lat': 9.3500, 'lng': 123.2833,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Sibulan',
        'source': 'Route notes for the Bais-Binalbagan / Kabankalan-Mabinay service',
    },
    {
        'name': 'San Carlos', 'code': 'SCC',
        'city': 'San Carlos City', 'province': 'Negros Occidental',
        'lat': 10.4966, 'lng': 123.4224,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'San Carlos City, San Carlos',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Cadiz', 'code': 'CAD',
        'city': 'Cadiz City', 'province': 'Negros Occidental',
        'lat': 10.9586, 'lng': 123.1321,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Cadiz City, Cadiz',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Victorias', 'code': 'VIC',
        'city': 'Victorias City', 'province': 'Negros Occidental',
        'lat': 10.9000, 'lng': 123.0667,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Victorias City, Victorias',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Escalante', 'code': 'ESC',
        'city': 'Escalante City', 'province': 'Negros Occidental',
        'lat': 10.8333, 'lng': 123.5000,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Escalante City, Escalante',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Sipalay', 'code': 'SIP',
        'city': 'Sipalay City', 'province': 'Negros Occidental',
        'lat': 9.7500, 'lng': 122.4000,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Sipalay City, Sipalay',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Himamaylan', 'code': 'HIM',
        'city': 'Himamaylan City', 'province': 'Negros Occidental',
        'lat': 10.1003, 'lng': 122.8702,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Himamaylan City, Himamaylan',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Hinigaran', 'code': 'HIN',
        'city': 'Hinigaran', 'province': 'Negros Occidental',
        'lat': 10.0417, 'lng': 122.8567,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Hinigaran',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Binalbagan', 'code': 'BIN',
        'city': 'Binalbagan', 'province': 'Negros Occidental',
        'lat': 10.0739, 'lng': 122.8667,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Binalbagan',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Bayawan', 'code': 'BAY',
        'city': 'Bayawan City', 'province': 'Negros Oriental',
        'lat': 9.3667, 'lng': 122.8000,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Bayawan City, Bayawan',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Canlaon', 'code': 'CAN',
        'city': 'Canlaon City', 'province': 'Negros Oriental',
        'lat': 10.3833, 'lng': 123.2000,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Canlaon City, Canlaon',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'La Carlota', 'code': 'LAC',
        'city': 'La Carlota City', 'province': 'Negros Occidental',
        'lat': 10.4167, 'lng': 122.9167,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'La Carlota City, La Carlota',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Guihulngan', 'code': 'GUI',
        'city': 'Guihulngan City', 'province': 'Negros Oriental',
        'lat': 10.1167, 'lng': 123.2667,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Guihulngan City, Guihulngan',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Bago', 'code': 'BAGO',
        'city': 'Bago City', 'province': 'Negros Occidental',
        'lat': 10.5376, 'lng': 122.8389,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Bago City, Bago',
        'source': 'https://byahi.ph/negros/routes/NEG-BCD-DGT',
    },
    {
        'name': 'Valladolid', 'code': 'VAL',
        'city': 'Valladolid', 'province': 'Negros Occidental',
        'lat': 10.4667, 'lng': 122.8333,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Valladolid',
        'source': 'https://byahi.ph/negros/routes/NEG-BCD-DGT',
    },
    {
        'name': 'Pontevedra', 'code': 'PON',
        'city': 'Pontevedra', 'province': 'Negros Occidental',
        'lat': 10.3667, 'lng': 122.8667,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Pontevedra',
        'source': 'https://byahi.ph/negros/routes/NEG-BCD-DGT',
    },
    {
        'name': 'Amlan', 'code': 'AML',
        'city': 'Amlan', 'province': 'Negros Oriental',
        'lat': 9.4333, 'lng': 123.2167,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Amlan',
        'source': 'https://byahi.ph/negros/routes/NEG-BCD-DGT',
    },
    {
        'name': 'San Jose', 'code': 'SJN',
        'city': 'San Jose', 'province': 'Negros Oriental',
        'lat': 9.4167, 'lng': 123.2500,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'San Jose Negros Oriental, San Jose',
        'source': 'https://byahi.ph/negros/routes/NEG-BCD-DGT',
    },
    {
        'name': 'Talisay (Cebu)', 'code': 'TAL',
        'city': 'Talisay City', 'province': 'Cebu',
        'lat': 10.2447, 'lng': 123.8494,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Talisay City Cebu, Talisay Cebu',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'Minglanilla', 'code': 'MIN',
        'city': 'Minglanilla', 'province': 'Cebu',
        'lat': 10.2444, 'lng': 123.7964,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Minglanilla',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'Naga (Cebu)', 'code': 'NAG',
        'city': 'City of Naga', 'province': 'Cebu',
        'lat': 10.2089, 'lng': 123.7581,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'City of Naga Cebu, Naga Cebu',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'San Fernando (Cebu)', 'code': 'SFC',
        'city': 'San Fernando', 'province': 'Cebu',
        'lat': 10.1622, 'lng': 123.7075,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'San Fernando Cebu',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'Carcar', 'code': 'CAR',
        'city': 'Carcar City', 'province': 'Cebu',
        'lat': 10.1061, 'lng': 123.6400,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Carcar City, Carcar',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'Sibonga', 'code': 'SIBO',
        'city': 'Sibonga', 'province': 'Cebu',
        'lat': 10.0167, 'lng': 123.6167,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Simala, Sibonga',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'Argao', 'code': 'ARG',
        'city': 'Argao', 'province': 'Cebu',
        'lat': 9.8833, 'lng': 123.6000,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Argao',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'Dalaguete', 'code': 'DAL',
        'city': 'Dalaguete', 'province': 'Cebu',
        'lat': 9.7611, 'lng': 123.5347,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Dalaguete',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'Alcoy', 'code': 'ALC',
        'city': 'Alcoy', 'province': 'Cebu',
        'lat': 9.7086, 'lng': 123.5069,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Alcoy',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'Boljoon', 'code': 'BOL',
        'city': 'Boljoon', 'province': 'Cebu',
        'lat': 9.6289, 'lng': 123.4786,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Boljoon',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'Oslob', 'code': 'OSL',
        'city': 'Oslob', 'province': 'Cebu',
        'lat': 9.4833, 'lng': 123.3833,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Oslob',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'Santander', 'code': 'SAN',
        'city': 'Santander', 'province': 'Cebu',
        'lat': 9.4167, 'lng': 123.3333,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Santander',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'Liloan Port', 'code': 'LIL',
        'city': 'Santander', 'province': 'Cebu',
        'lat': 9.4167, 'lng': 123.3333,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Liloan Port Santander, Liloan Port',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
    {
        'name': 'Sibulan Port', 'code': 'SIBP',
        'city': 'Sibulan', 'province': 'Negros Oriental',
        'lat': 9.3500, 'lng': 123.2833,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Sibulan Port, Sibulan',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
    },
]


# The Kabankalan -> Dumaguete service uses the Kabankalan-Mabinay mountain road
# and then the Mabinay-Bais-Tanjay-Sibulan-Dumaguete corridor. Distances are
# road kilometres from the published Dumaguete-Sibulan-Tanjay-Bais-Mabinay-
# Kabankalan distance table. The route is source-compiled, not conductor-
# validated yet, so the UI tells the conductor to verify the final stop list.
ROUTE_DEFINITIONS = [
    {
        'name': 'Kabankalan-Dumaguete',
        'aliases': (
            'Kabankalan-Dumaguete, Kabankalan - Dumaguete, '
            'Kabankalan to Dumaguete, Kabankalan–Dumaguete'
        ),
        'origin': 'Kabankalan',
        'destination': 'Dumaguete',
        'validation_status': 'source_compiled',
        'validation_note': (
            'Confirmed anchors: Kabankalan and Mabinay. The Mabinay-Bais-Tanjay-'
            'Sibulan-Dumaguete stops are compiled from published route notes. '
            'Intermediate barangays must be confirmed by a conductor before '
            'deployment. Bacolod-Dumaguete-only stops were not copied into this '
            'route.'
        ),
        'source': (
            'Byahi NEG-BCD-DGT cross-check; Bais-Binalbagan / Kabankalan-'
            'Mabinay route notes'
        ),
        'stops': [
            {'name': 'Kabankalan', 'distance_km': 0, 'speed_kmh': 40},
            {'name': 'Mabinay', 'distance_km': 39.7, 'speed_kmh': 40},
            {'name': 'Bais', 'distance_km': 41.7, 'speed_kmh': 40},
            {'name': 'Tanjay', 'distance_km': 13.8, 'speed_kmh': 50},
            {'name': 'Sibulan', 'distance_km': 25.3, 'speed_kmh': 50},
            {'name': 'Dumaguete', 'distance_km': 5.5, 'speed_kmh': 50},
        ],
    },
    {
        'name': 'Dumaguete-Kabankalan',
        'aliases': (
            'Dumaguete-Kabankalan, Dumaguete - Kabankalan, '
            'Dumaguete to Kabankalan, Dumaguete–Kabankalan'
        ),
        'origin': 'Dumaguete',
        'destination': 'Kabankalan',
        'validation_status': 'source_compiled',
        'validation_note': (
            'Reverse of the source-compiled Kabankalan-Dumaguete sequence. '
            'Conductor validation of intermediate barangays is still required.'
        ),
        'source': (
            'Byahi NEG-DGT-BCD cross-check; Bais-Binalbagan / Kabankalan-'
            'Mabinay route notes'
        ),
        'stops': [
            {'name': 'Dumaguete', 'distance_km': 0, 'speed_kmh': 50},
            {'name': 'Sibulan', 'distance_km': 5.5, 'speed_kmh': 50},
            {'name': 'Tanjay', 'distance_km': 25.3, 'speed_kmh': 50},
            {'name': 'Bais', 'distance_km': 13.8, 'speed_kmh': 50},
            {'name': 'Mabinay', 'distance_km': 41.7, 'speed_kmh': 40},
            {'name': 'Kabankalan', 'distance_km': 39.7, 'speed_kmh': 40},
        ],
    },
    {
        'name': 'Bacolod-Dumaguete',
        'aliases': (
            'Bacolod-Dumaguete, Bacolod - Dumaguete, Bacolod to Dumaguete, '
            'Bacolod–Dumaguete, Bacolod South-Dumaguete'
        ),
        'origin': 'Bacolod South',
        'destination': 'Dumaguete',
        'validation_status': 'source_compiled',
        'validation_note': (
            'Stop list from the published Bacolod-Dumaguete via Mabinay route. '
            'This is a separate route from Kabankalan-Dumaguete; do not reuse '
            'this list for the Kabankalan service without conductor validation.'
        ),
        'source': 'https://byahi.ph/negros/routes/NEG-BCD-DGT',
        'stops': [
            {'name': 'Bacolod South', 'distance_km': 0, 'speed_kmh': 50},
            {'name': 'Bago', 'distance_km': 22.0, 'speed_kmh': 50},
            {'name': 'Valladolid', 'distance_km': 8.0, 'speed_kmh': 50},
            {'name': 'Pontevedra', 'distance_km': 12.0, 'speed_kmh': 50},
            {'name': 'Hinigaran', 'distance_km': 12.0, 'speed_kmh': 50},
            {'name': 'Binalbagan', 'distance_km': 10.0, 'speed_kmh': 50},
            {'name': 'Himamaylan', 'distance_km': 8.0, 'speed_kmh': 50},
            {'name': 'Kabankalan', 'distance_km': 19.0, 'speed_kmh': 50},
            {'name': 'Mabinay', 'distance_km': 39.7, 'speed_kmh': 40},
            {'name': 'Bais', 'distance_km': 41.7, 'speed_kmh': 40},
            {'name': 'Tanjay', 'distance_km': 13.8, 'speed_kmh': 50},
            {'name': 'Amlan', 'distance_km': 11.0, 'speed_kmh': 50},
            {'name': 'San Jose', 'distance_km': 4.0, 'speed_kmh': 50},
            {'name': 'Sibulan', 'distance_km': 7.0, 'speed_kmh': 50},
            {'name': 'Dumaguete', 'distance_km': 5.5, 'speed_kmh': 50},
        ],
    },
    {
        'name': 'Dumaguete-Bacolod',
        'aliases': (
            'Dumaguete-Bacolod, Dumaguete - Bacolod, Dumaguete to Bacolod, '
            'Dumaguete–Bacolod'
        ),
        'origin': 'Dumaguete',
        'destination': 'Bacolod South',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the published Bacolod-Dumaguete via Mabinay route.',
        'source': 'https://byahi.ph/negros/routes/NEG-BCD-DGT',
        'stops': [
            {'name': 'Dumaguete', 'distance_km': 0, 'speed_kmh': 50},
            {'name': 'Sibulan', 'distance_km': 5.5, 'speed_kmh': 50},
            {'name': 'San Jose', 'distance_km': 7.0, 'speed_kmh': 50},
            {'name': 'Amlan', 'distance_km': 4.0, 'speed_kmh': 50},
            {'name': 'Tanjay', 'distance_km': 11.0, 'speed_kmh': 50},
            {'name': 'Bais', 'distance_km': 13.8, 'speed_kmh': 50},
            {'name': 'Mabinay', 'distance_km': 41.7, 'speed_kmh': 40},
            {'name': 'Kabankalan', 'distance_km': 39.7, 'speed_kmh': 40},
            {'name': 'Himamaylan', 'distance_km': 19.0, 'speed_kmh': 50},
            {'name': 'Binalbagan', 'distance_km': 8.0, 'speed_kmh': 50},
            {'name': 'Hinigaran', 'distance_km': 10.0, 'speed_kmh': 50},
            {'name': 'Pontevedra', 'distance_km': 12.0, 'speed_kmh': 50},
            {'name': 'Valladolid', 'distance_km': 12.0, 'speed_kmh': 50},
            {'name': 'Bago', 'distance_km': 8.0, 'speed_kmh': 50},
            {'name': 'Bacolod South', 'distance_km': 22.0, 'speed_kmh': 50},
        ],
    },
    {
        'name': 'Bacolod-Kabankalan',
        'aliases': (
            'Bacolod-Kabankalan, Bacolod - Kabankalan, Bacolod to Kabankalan, '
            'Bacolod–Kabankalan'
        ),
        'origin': 'Bacolod South',
        'destination': 'Kabankalan',
        'validation_status': 'source_compiled',
        'validation_note': (
            'First leg of the published Bacolod-Dumaguete via Mabinay corridor.'
        ),
        'source': 'https://byahi.ph/negros/routes/NEG-BCD-DGT',
        'stops': [
            {'name': 'Bacolod South', 'distance_km': 0, 'speed_kmh': 50},
            {'name': 'Bago', 'distance_km': 22.0, 'speed_kmh': 50},
            {'name': 'Valladolid', 'distance_km': 8.0, 'speed_kmh': 50},
            {'name': 'Pontevedra', 'distance_km': 12.0, 'speed_kmh': 50},
            {'name': 'Hinigaran', 'distance_km': 12.0, 'speed_kmh': 50},
            {'name': 'Binalbagan', 'distance_km': 10.0, 'speed_kmh': 50},
            {'name': 'Himamaylan', 'distance_km': 8.0, 'speed_kmh': 50},
            {'name': 'Kabankalan', 'distance_km': 19.0, 'speed_kmh': 50},
        ],
    },
    {
        'name': 'Kabankalan-Bacolod',
        'aliases': (
            'Kabankalan-Bacolod, Kabankalan - Bacolod, Kabankalan to Bacolod, '
            'Kabankalan–Bacolod'
        ),
        'origin': 'Kabankalan',
        'destination': 'Bacolod South',
        'validation_status': 'source_compiled',
        'validation_note': (
            'Reverse of the first leg of the published Bacolod-Dumaguete via '
            'Mabinay corridor.'
        ),
        'source': 'https://byahi.ph/negros/routes/NEG-BCD-DGT',
        'stops': [
            {'name': 'Kabankalan', 'distance_km': 0, 'speed_kmh': 50},
            {'name': 'Himamaylan', 'distance_km': 19.0, 'speed_kmh': 50},
            {'name': 'Binalbagan', 'distance_km': 8.0, 'speed_kmh': 50},
            {'name': 'Hinigaran', 'distance_km': 10.0, 'speed_kmh': 50},
            {'name': 'Pontevedra', 'distance_km': 12.0, 'speed_kmh': 50},
            {'name': 'Valladolid', 'distance_km': 12.0, 'speed_kmh': 50},
            {'name': 'Bago', 'distance_km': 8.0, 'speed_kmh': 50},
            {'name': 'Bacolod South', 'distance_km': 22.0, 'speed_kmh': 50},
        ],
    },
    {
        'name': 'Cebu South-Dumaguete',
        'aliases': (
            'Cebu South-Dumaguete, Cebu-Dumaguete, Cebu South to Dumaguete, '
            'Cebu–Dumaguete'
        ),
        'origin': 'Cebu South',
        'destination': 'Dumaguete',
        'validation_status': 'source_compiled',
        'validation_note': (
            'Published Cebu South-Dumaguete route via Bato and Oslob. Distances '
            'are computed from stop coordinates when no published segment '
            'distance is available.'
        ),
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
        'stops': [
            {'name': 'Cebu South', 'distance_km': 0, 'speed_kmh': 50},
            {'name': 'Talisay (Cebu)', 'speed_kmh': 50},
            {'name': 'Minglanilla', 'speed_kmh': 50},
            {'name': 'Naga (Cebu)', 'speed_kmh': 50},
            {'name': 'San Fernando (Cebu)', 'speed_kmh': 50},
            {'name': 'Carcar', 'speed_kmh': 50},
            {'name': 'Sibonga', 'speed_kmh': 50},
            {'name': 'Argao', 'speed_kmh': 50},
            {'name': 'Dalaguete', 'speed_kmh': 50},
            {'name': 'Alcoy', 'speed_kmh': 50},
            {'name': 'Boljoon', 'speed_kmh': 50},
            {'name': 'Oslob', 'speed_kmh': 50},
            {'name': 'Santander', 'speed_kmh': 50},
            {'name': 'Liloan Port', 'speed_kmh': 40},
            {'name': 'Sibulan Port', 'speed_kmh': 40},
            {'name': 'Dumaguete', 'speed_kmh': 50},
        ],
    },
    {
        'name': 'Dumaguete-Cebu South',
        'aliases': (
            'Dumaguete-Cebu South, Dumaguete-Cebu, Dumaguete to Cebu South, '
            'Dumaguete–Cebu'
        ),
        'origin': 'Dumaguete',
        'destination': 'Cebu South',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the published Cebu South-Dumaguete route.',
        'source': 'https://byahi.ph/cebu/routes/CEB-CSBT-DGT',
        'stops': [
            {'name': 'Dumaguete', 'distance_km': 0, 'speed_kmh': 50},
            {'name': 'Sibulan Port', 'speed_kmh': 40},
            {'name': 'Liloan Port', 'speed_kmh': 40},
            {'name': 'Santander', 'speed_kmh': 50},
            {'name': 'Oslob', 'speed_kmh': 50},
            {'name': 'Boljoon', 'speed_kmh': 50},
            {'name': 'Alcoy', 'speed_kmh': 50},
            {'name': 'Dalaguete', 'speed_kmh': 50},
            {'name': 'Argao', 'speed_kmh': 50},
            {'name': 'Sibonga', 'speed_kmh': 50},
            {'name': 'Carcar', 'speed_kmh': 50},
            {'name': 'San Fernando (Cebu)', 'speed_kmh': 50},
            {'name': 'Naga (Cebu)', 'speed_kmh': 50},
            {'name': 'Minglanilla', 'speed_kmh': 50},
            {'name': 'Talisay (Cebu)', 'speed_kmh': 50},
            {'name': 'Cebu South', 'speed_kmh': 50},
        ],
    },
    {
        'name': 'Dumaguete-Bais',
        'aliases': (
            'Dumaguete-Bais, Dumaguete - Bais, Dumaguete to Bais, '
            'Dumaguete–Bais'
        ),
        'origin': 'Dumaguete',
        'destination': 'Bais',
        'validation_status': 'source_compiled',
        'validation_note': (
            'Published Dumaguete-Bais service using the Dumaguete-Sibulan-'
            'Tanjay-Bais corridor.'
        ),
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
        'stops': [
            {'name': 'Dumaguete', 'distance_km': 0, 'speed_kmh': 50},
            {'name': 'Sibulan', 'distance_km': 5.5, 'speed_kmh': 50},
            {'name': 'Tanjay', 'distance_km': 25.3, 'speed_kmh': 50},
            {'name': 'Bais', 'distance_km': 13.8, 'speed_kmh': 50},
        ],
    },
    {
        'name': 'Bais-Dumaguete',
        'aliases': (
            'Bais-Dumaguete, Bais - Dumaguete, Bais to Dumaguete, '
            'Bais–Dumaguete'
        ),
        'origin': 'Bais',
        'destination': 'Dumaguete',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the published Dumaguete-Bais service.',
        'source': 'https://ph.commutetour.com/travel/transport/bus/ceres-transport/',
        'stops': [
            {'name': 'Bais', 'distance_km': 0, 'speed_kmh': 50},
            {'name': 'Tanjay', 'distance_km': 13.8, 'speed_kmh': 50},
            {'name': 'Sibulan', 'distance_km': 25.3, 'speed_kmh': 50},
            {'name': 'Dumaguete', 'distance_km': 5.5, 'speed_kmh': 50},
        ],
    },
    {
        'name': 'Dumaguete-Mabinay',
        'aliases': (
            'Dumaguete-Mabinay, Dumaguete - Mabinay, Dumaguete to Mabinay, '
            'Dumaguete–Mabinay'
        ),
        'origin': 'Dumaguete',
        'destination': 'Mabinay',
        'validation_status': 'source_compiled',
        'validation_note': (
            'Published Dumaguete-Mabinay service using the Dumaguete-Sibulan-'
            'Tanjay-Bais-Mabinay corridor.'
        ),
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
        'stops': [
            {'name': 'Dumaguete', 'distance_km': 0, 'speed_kmh': 50},
            {'name': 'Sibulan', 'distance_km': 5.5, 'speed_kmh': 50},
            {'name': 'Tanjay', 'distance_km': 25.3, 'speed_kmh': 50},
            {'name': 'Bais', 'distance_km': 13.8, 'speed_kmh': 50},
            {'name': 'Mabinay', 'distance_km': 41.7, 'speed_kmh': 40},
        ],
    },
    {
        'name': 'Mabinay-Dumaguete',
        'aliases': (
            'Mabinay-Dumaguete, Mabinay - Dumaguete, Mabinay to Dumaguete, '
            'Mabinay–Dumaguete'
        ),
        'origin': 'Mabinay',
        'destination': 'Dumaguete',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the published Dumaguete-Mabinay service.',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
        'stops': [
            {'name': 'Mabinay', 'distance_km': 0, 'speed_kmh': 40},
            {'name': 'Bais', 'distance_km': 41.7, 'speed_kmh': 40},
            {'name': 'Tanjay', 'distance_km': 13.8, 'speed_kmh': 50},
            {'name': 'Sibulan', 'distance_km': 25.3, 'speed_kmh': 50},
            {'name': 'Dumaguete', 'distance_km': 5.5, 'speed_kmh': 50},
        ],
    },
]

FIXED_CONDUCTOR_PROMPT = (
    'Scan the bus QR, confirm the Current Bus Station, then select the Next Bus '
    'Stop. Only stops after the current station in the validated route sequence '
    'are shown. The ETA is calculated from the road distance and the average '
    'speed for that segment.'
)
