"""Negros Occidental terminal master list and route stop sequences.

Scope rule for this module:

* Every terminal and every route is inside Negros Occidental. No Negros
  Oriental, Cebu, Panay, Luzon, or Mindanao stop is included.
* ``is_owned_terminal`` marks terminal hubs Vallacar itself operates.
  ``is_major_stop`` marks towns/barangays that a Vallacar route serves.
* The routes below mirror the fleet and demo services used by the tracker.
  Every route is marked ``source_compiled`` until a conductor validates the
  final barangay list.

Sources used:
* https://ceresliner.com/terminal (owned terminal addresses)
* https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)
  (Negros Occidental terminal hubs and published destinations)
* The ordered stop lists already used by the tracker's Negros Occidental
  demo fleet (Bacolod, Kabankalan, Sipalay, Narra, Candoni, Hinoba-an,
  San Carlos, Victorias, Sagay, Cadiz corridors).
"""

SCOPE_PROVINCE = 'Negros Occidental'


def _route_aliases(origin, destination):
    """Build the common spellings accepted for a route label."""
    return (
        f'{origin}-{destination}, {origin} - {destination}, '
        f'{origin} to {destination}, {origin}\u2013{destination}'
    )


# Negros Occidental terminals and major stops only.
TERMINAL_MASTER_LIST = [
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
        'name': 'Bago', 'code': 'BAGO',
        'city': 'Bago City', 'province': 'Negros Occidental',
        'lat': 10.5376, 'lng': 122.8389,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Bago City, Bago',
        'source': 'https://byahi.ph/negros/routes/NEG-BCD-DGT',
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
        'name': 'Cadiz', 'code': 'CAD',
        'city': 'Cadiz City', 'province': 'Negros Occidental',
        'lat': 10.9586, 'lng': 123.1321,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Cadiz City, Cadiz',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
    {
        'name': 'Calatrava', 'code': 'CAL',
        'city': 'Calatrava', 'province': 'Negros Occidental',
        'lat': 10.6000, 'lng': 123.4830,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Calatrava',
        'source': 'Terminal directory',
    },
    {
        'name': 'Candoni', 'code': 'CAND',
        'city': 'Candoni', 'province': 'Negros Occidental',
        'lat': 9.831044, 'lng': 122.642981,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Candoni',
        'source': 'Tracker Negros Occidental demo fleet',
    },
    {
        'name': 'Enrique B. Magalona', 'code': 'EBM',
        'city': 'Enrique B. Magalona', 'province': 'Negros Occidental',
        'lat': 10.8830, 'lng': 122.9670,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Saravia, E.B. Magalona, Enrique B. Magalona',
        'source': 'Terminal directory',
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
        'name': 'Hinoba-an', 'code': 'HINOB',
        'city': 'Hinoba-an', 'province': 'Negros Occidental',
        'lat': 9.5830, 'lng': 122.4670,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Hinobaan, Hinoba-an',
        'source': 'Tracker Negros Occidental demo fleet',
    },
    {
        'name': 'Ilog', 'code': 'ILOG',
        'city': 'Ilog', 'province': 'Negros Occidental',
        'lat': 10.0330, 'lng': 122.7670,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Ilog',
        'source': 'Tracker Negros Occidental demo fleet',
    },
    {
        'name': 'Isabela', 'code': 'ISAB',
        'city': 'Isabela', 'province': 'Negros Occidental',
        'lat': 10.2000, 'lng': 122.9830,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Isabela Negros',
        'source': 'Terminal directory',
    },
    {
        'name': 'Kabankalan', 'code': 'KAB',
        'city': 'Kabankalan City', 'province': 'Negros Occidental',
        'lat': 9.9917, 'lng': 122.8128,
        'is_owned_terminal': True, 'is_major_stop': True,
        'aliases': 'Kabankalan City Bus Terminal, Kabnakalan, Kabankalan',
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
        'name': 'La Castellana', 'code': 'LCAST',
        'city': 'La Castellana', 'province': 'Negros Occidental',
        'lat': 10.3500, 'lng': 123.0670,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'La Castellana',
        'source': 'Terminal directory',
    },
    {
        'name': 'Manapla', 'code': 'MAN',
        'city': 'Manapla', 'province': 'Negros Occidental',
        'lat': 10.9500, 'lng': 123.1200,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Manapla',
        'source': 'Terminal directory',
    },
    {
        'name': 'Moises Padilla', 'code': 'MPAD',
        'city': 'Moises Padilla', 'province': 'Negros Occidental',
        'lat': 10.2670, 'lng': 123.0830,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Moises Padilla',
        'source': 'Terminal directory',
    },
    {
        'name': 'Murcia', 'code': 'MUR',
        'city': 'Murcia', 'province': 'Negros Occidental',
        'lat': 10.6000, 'lng': 123.0300,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Murcia',
        'source': 'Terminal directory',
    },
    {
        'name': 'Narra', 'code': 'NAR',
        'city': 'Narra', 'province': 'Negros Occidental',
        'lat': 9.9670, 'lng': 122.6170,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Narra',
        'source': 'Tracker Negros Occidental demo fleet',
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
        'name': 'Pulupandan', 'code': 'PUL',
        'city': 'Pulupandan', 'province': 'Negros Occidental',
        'lat': 10.5170, 'lng': 122.8000,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Pulupandan',
        'source': 'Terminal directory',
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
        'name': 'Salvador Benedicto', 'code': 'SBEN',
        'city': 'Salvador Benedicto', 'province': 'Negros Occidental',
        'lat': 10.5500, 'lng': 123.2330,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Don Salvador Benedicto, Salvador Benedicto',
        'source': 'Terminal directory',
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
        'name': 'San Enrique', 'code': 'SENR',
        'city': 'San Enrique', 'province': 'Negros Occidental',
        'lat': 10.4170, 'lng': 122.8500,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'San Enrique',
        'source': 'Terminal directory',
    },
    {
        'name': 'Silay', 'code': 'SIL',
        'city': 'Silay City', 'province': 'Negros Occidental',
        'lat': 10.8000, 'lng': 122.9670,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Silay City, Silay',
        'source': 'Terminal directory',
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
        'name': 'Talisay', 'code': 'TAL',
        'city': 'Talisay City', 'province': 'Negros Occidental',
        'lat': 10.7330, 'lng': 122.9670,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Talisay City, Talisay Negros, Talisay',
        'source': 'Terminal directory',
    },
    {
        'name': 'Toboso', 'code': 'TOB',
        'city': 'Toboso', 'province': 'Negros Occidental',
        'lat': 10.7170, 'lng': 123.5170,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Toboso',
        'source': 'Terminal directory',
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
        'name': 'Victorias', 'code': 'VIC',
        'city': 'Victorias City', 'province': 'Negros Occidental',
        'lat': 10.9000, 'lng': 123.0667,
        'is_owned_terminal': False, 'is_major_stop': True,
        'aliases': 'Victorias City, Victorias',
        'source': 'https://en.wikipedia.org/wiki/Vallacar_Transit_Incorporated_(Ceres_Liner)',
    },
]


def _stops(*names):
    return [{'name': name, 'speed_kmh': 50} for name in names]


# All routes are within Negros Occidental. Distances are road kilometres where
# the published corridor supplies them; otherwise the seed calculates the
# distance from the terminal coordinates.
ROUTE_DEFINITIONS = [
    {
        'name': 'Bacolod-Kabankalan',
        'aliases': _route_aliases('Bacolod', 'Kabankalan'),
        'origin': 'Bacolod South',
        'destination': 'Kabankalan',
        'validation_status': 'source_compiled',
        'validation_note': (
            'Published southern Negros Occidental corridor via Bago, '
            'Valladolid, Pontevedra, Hinigaran, Binalbagan, and Himamaylan.'
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
        'aliases': _route_aliases('Kabankalan', 'Bacolod'),
        'origin': 'Kabankalan',
        'destination': 'Bacolod South',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the published Bacolod-Kabankalan corridor.',
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
        'name': 'Bacolod-Sipalay',
        'aliases': _route_aliases('Bacolod', 'Sipalay'),
        'origin': 'Bacolod South',
        'destination': 'Sipalay',
        'validation_status': 'source_compiled',
        'validation_note': 'Southern Negros Occidental service through Kabankalan and Hinoba-an.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops(
            'Bacolod South', 'Bago', 'Valladolid', 'Pontevedra', 'Hinigaran',
            'Binalbagan', 'Himamaylan', 'Kabankalan', 'Hinoba-an', 'Sipalay',
        ),
    },
    {
        'name': 'Sipalay-Bacolod',
        'aliases': _route_aliases('Sipalay', 'Bacolod'),
        'origin': 'Sipalay',
        'destination': 'Bacolod South',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the Bacolod-Sipalay service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops(
            'Sipalay', 'Hinoba-an', 'Kabankalan', 'Himamaylan', 'Binalbagan',
            'Hinigaran', 'Pontevedra', 'Valladolid', 'Bago', 'Bacolod South',
        ),
    },
    {
        'name': 'Narra-Bacolod',
        'aliases': _route_aliases('Narra', 'Bacolod'),
        'origin': 'Narra',
        'destination': 'Bacolod South',
        'validation_status': 'source_compiled',
        'validation_note': 'Narra-Ilog-Kabankalan corridor to Bacolod.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops(
            'Narra', 'Ilog', 'Kabankalan', 'Himamaylan', 'Binalbagan',
            'Hinigaran', 'Pontevedra', 'Valladolid', 'Bago', 'Bacolod South',
        ),
    },
    {
        'name': 'Bacolod-Narra',
        'aliases': _route_aliases('Bacolod', 'Narra'),
        'origin': 'Bacolod South',
        'destination': 'Narra',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the Narra-Bacolod service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops(
            'Bacolod South', 'Bago', 'Valladolid', 'Pontevedra', 'Hinigaran',
            'Binalbagan', 'Himamaylan', 'Kabankalan', 'Ilog', 'Narra',
        ),
    },
    {
        'name': 'Candoni-Bacolod',
        'aliases': _route_aliases('Candoni', 'Bacolod'),
        'origin': 'Candoni',
        'destination': 'Bacolod South',
        'validation_status': 'source_compiled',
        'validation_note': 'Candoni-Kabankalan corridor to Bacolod.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops(
            'Candoni', 'Kabankalan', 'Himamaylan', 'Binalbagan', 'Hinigaran',
            'Pontevedra', 'Valladolid', 'Bago', 'Bacolod South',
        ),
    },
    {
        'name': 'Bacolod-Candoni',
        'aliases': _route_aliases('Bacolod', 'Candoni'),
        'origin': 'Bacolod South',
        'destination': 'Candoni',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the Candoni-Bacolod service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops(
            'Bacolod South', 'Bago', 'Valladolid', 'Pontevedra', 'Hinigaran',
            'Binalbagan', 'Himamaylan', 'Kabankalan', 'Candoni',
        ),
    },
    {
        'name': 'Kabankalan-Candoni',
        'aliases': _route_aliases('Kabankalan', 'Candoni'),
        'origin': 'Kabankalan',
        'destination': 'Candoni',
        'validation_status': 'source_compiled',
        'validation_note': 'Short Kabankalan-Candoni service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops('Kabankalan', 'Candoni'),
    },
    {
        'name': 'Candoni-Kabankalan',
        'aliases': _route_aliases('Candoni', 'Kabankalan'),
        'origin': 'Candoni',
        'destination': 'Kabankalan',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the Kabankalan-Candoni service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops('Candoni', 'Kabankalan'),
    },
    {
        'name': 'Hinoba-an-Kabankalan',
        'aliases': _route_aliases('Hinoba-an', 'Kabankalan'),
        'origin': 'Hinoba-an',
        'destination': 'Kabankalan',
        'validation_status': 'source_compiled',
        'validation_note': 'Hinoba-an-Sipalay-Kabankalan service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops('Hinoba-an', 'Sipalay', 'Kabankalan'),
    },
    {
        'name': 'Kabankalan-Hinoba-an',
        'aliases': _route_aliases('Kabankalan', 'Hinoba-an'),
        'origin': 'Kabankalan',
        'destination': 'Hinoba-an',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the Hinoba-an-Kabankalan service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops('Kabankalan', 'Sipalay', 'Hinoba-an'),
    },
    {
        'name': 'Sipalay-Kabankalan',
        'aliases': _route_aliases('Sipalay', 'Kabankalan'),
        'origin': 'Sipalay',
        'destination': 'Kabankalan',
        'validation_status': 'source_compiled',
        'validation_note': 'Sipalay-Hinoba-an-Kabankalan service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops('Sipalay', 'Hinoba-an', 'Kabankalan'),
    },
    {
        'name': 'Kabankalan-Sipalay',
        'aliases': _route_aliases('Kabankalan', 'Sipalay'),
        'origin': 'Kabankalan',
        'destination': 'Sipalay',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the Sipalay-Kabankalan service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops('Kabankalan', 'Hinoba-an', 'Sipalay'),
    },
    {
        'name': 'San Carlos-Sipalay',
        'aliases': _route_aliases('San Carlos', 'Sipalay'),
        'origin': 'San Carlos',
        'destination': 'Sipalay',
        'validation_status': 'source_compiled',
        'validation_note': 'Northern hub to southern Negros Occidental service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops(
            'San Carlos', 'Bacolod North', 'Bago', 'Valladolid', 'Pontevedra',
            'Hinigaran', 'Binalbagan', 'Himamaylan', 'Kabankalan',
            'Hinoba-an', 'Sipalay',
        ),
    },
    {
        'name': 'Sipalay-San Carlos',
        'aliases': _route_aliases('Sipalay', 'San Carlos'),
        'origin': 'Sipalay',
        'destination': 'San Carlos',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the San Carlos-Sipalay service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops(
            'Sipalay', 'Hinoba-an', 'Kabankalan', 'Himamaylan', 'Binalbagan',
            'Hinigaran', 'Pontevedra', 'Valladolid', 'Bago', 'Bacolod North',
            'San Carlos',
        ),
    },
    {
        'name': 'Victorias-Hinoba-an',
        'aliases': _route_aliases('Victorias', 'Hinoba-an'),
        'origin': 'Victorias',
        'destination': 'Hinoba-an',
        'validation_status': 'source_compiled',
        'validation_note': 'Northern Victorias corridor to southern Hinoba-an.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops(
            'Victorias', 'Bacolod North', 'Bago', 'Valladolid', 'Pontevedra',
            'Hinigaran', 'Binalbagan', 'Himamaylan', 'Kabankalan', 'Sipalay',
            'Hinoba-an',
        ),
    },
    {
        'name': 'Hinoba-an-Victorias',
        'aliases': _route_aliases('Hinoba-an', 'Victorias'),
        'origin': 'Hinoba-an',
        'destination': 'Victorias',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the Victorias-Hinoba-an service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops(
            'Hinoba-an', 'Sipalay', 'Kabankalan', 'Himamaylan', 'Binalbagan',
            'Hinigaran', 'Pontevedra', 'Valladolid', 'Bago', 'Bacolod North',
            'Victorias',
        ),
    },
    {
        'name': 'Sagay-Kabankalan',
        'aliases': _route_aliases('Sagay', 'Kabankalan'),
        'origin': 'Sagay',
        'destination': 'Kabankalan',
        'validation_status': 'source_compiled',
        'validation_note': 'Sagay-Cadiz-Bacolod-Kabankalan service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops(
            'Sagay', 'Cadiz', 'Bacolod North', 'Bago', 'Valladolid',
            'Pontevedra', 'Hinigaran', 'Binalbagan', 'Himamaylan', 'Kabankalan',
        ),
    },
    {
        'name': 'Kabankalan-Sagay',
        'aliases': _route_aliases('Kabankalan', 'Sagay'),
        'origin': 'Kabankalan',
        'destination': 'Sagay',
        'validation_status': 'source_compiled',
        'validation_note': 'Reverse of the Sagay-Kabankalan service.',
        'source': 'Tracker Negros Occidental demo fleet',
        'stops': _stops(
            'Kabankalan', 'Himamaylan', 'Binalbagan', 'Hinigaran', 'Pontevedra',
            'Valladolid', 'Bago', 'Bacolod North', 'Cadiz', 'Sagay',
        ),
    },
]

FIXED_CONDUCTOR_PROMPT = (
    'Scan the bus QR, confirm the Current Bus Station, then select the Next Bus '
    'Stop. Only stops after the current station in the validated route sequence '
    'are shown. The ETA is calculated from the road distance and the average '
    'speed for that segment.'
)
